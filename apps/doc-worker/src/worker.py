"""Worker Celery para processamento de documentos."""
import logging
import time
import json
import asyncio
from celery import Celery
from celery.exceptions import Retry
from .settings import settings
from .pipeline.file_loader import file_loader
from .pipeline.rasterizer import rasterizer
from .pipeline.preprocess import preprocess_image
from .pipeline.ocr_printed import ocr_printed
from .pipeline.htr_handwritten import htr_handwritten
from .pipeline.mapping import field_mapper
from .pipeline.persistence import persistence
from .models import MedicalReport, DocumentField

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "doc-worker"}'
)
logger = logging.getLogger(__name__)

# Criar app Celery
celery_app = Celery(
    'doc_worker',
    broker=settings.rabbitmq_uri,
    backend='rpc://',
    task_acks_late=settings.task_acks_late,
    task_reject_on_worker_lost=settings.task_reject_on_worker_lost,
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    task_default_queue='process_document',
    task_routes={
        'src.worker.process_document': {'queue': 'process_document'},
    },
)

# Inicializar pool de conexões uma vez
_persistence_initialized = False


def ensure_persistence_initialized():
    """Garante que o pool de conexões está inicializado."""
    global _persistence_initialized
    if not _persistence_initialized:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if not persistence.conn_pool:
            loop.run_until_complete(persistence.initialize())
        _persistence_initialized = True


@celery_app.task(name='process_document', bind=True, max_retries=3, default_retry_delay=60)
def process_document(self, message: dict):
    """
    Task principal para processar um documento.
    
    Args:
        message: Dicionário com document_id, tenant, object_key, sha256
    """
    document_id = message.get('document_id')
    tenant = message.get('tenant')
    object_key = message.get('object_key')
    sha256 = message.get('sha256')
    
    start_time = time.time()
    logger.info(f"Iniciando processamento: {document_id}")
    
    try:
        # Garantir que persistência está inicializada
        ensure_persistence_initialized()
        
        # Obter loop de eventos
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Criar documento na base se não existir
        created = loop.run_until_complete(
            persistence.create_document(document_id, tenant, object_key, sha256)
        )
        if not created:
            # Verificar se já existe (pode ser reprocessamento)
            exists = loop.run_until_complete(persistence.document_exists(document_id))
            if not exists:
                logger.warning(f"Documento {document_id} não encontrado na base e não pôde ser criado")
                return {"status": "error", "message": "Document not found and could not be created"}
        
        # Atualizar status para PROCESSING
        loop.run_until_complete(
            persistence.update_document_status(document_id, "PROCESSING")
        )
        
        # Determinar tipo de arquivo baseado no object_key ou content_type
        content_type = message.get('content_type', '')
        file_type = file_loader.get_file_type(object_key)
        
        # Se não conseguir determinar pela extensão, tentar pelo content_type
        if not file_type:
            if 'pdf' in content_type.lower():
                file_type = 'pdf'
            elif any(img_type in content_type.lower() for img_type in ['png', 'jpeg', 'jpg', 'image']):
                file_type = 'image'
        
        images = []
        
        if file_type == 'image':
            # 1. Baixar imagem diretamente do S3
            logger.info(f"Processando imagem: {object_key}")
            img = file_loader.download_image(object_key)
            if not img:
                raise Exception("Erro ao baixar imagem do S3")
            
            # Validar imagem
            file_data = file_loader.download_file(object_key)
            if file_data:
                is_valid, error_msg = file_loader.validate_image(file_data)
                if not is_valid:
                    raise Exception(f"Imagem inválida: {error_msg}")
                
                # Verificar hash
                calculated_hash = file_loader.calculate_sha256(file_data)
                if calculated_hash != sha256:
                    logger.warning(f"Hash mismatch para {document_id}")
            
            # Imagem já está pronta, não precisa rasterizar
            images = [img]
            logger.info(f"Imagem carregada diretamente: {img.size}")
            
        else:
            # 1. Baixar PDF do S3
            logger.info(f"Processando PDF: {object_key}")
            pdf_data = file_loader.download_pdf(object_key)
            if not pdf_data:
                raise Exception("Erro ao baixar PDF do S3")
            
            # Validar PDF
            is_valid, error_msg = file_loader.validate_pdf(pdf_data)
            if not is_valid:
                raise Exception(f"PDF inválido: {error_msg}")
            
            # Verificar hash
            calculated_hash = file_loader.calculate_sha256(pdf_data)
            if calculated_hash != sha256:
                logger.warning(f"Hash mismatch para {document_id}")
            
            # 2. Rasterizar PDF
            images = rasterizer.pdf_to_images(pdf_data)
            if not images:
                raise Exception("Nenhuma página encontrada no PDF")
        
        # 3. Processar cada página
        all_fields = []
        for page_num, img in enumerate(images, start=1):
            logger.info(f"Processando página {page_num}/{len(images)}")
            
            # Pré-processar
            processed_img = preprocess_image(img)
            
            # OCR impresso
            printed_text, printed_conf = ocr_printed(processed_img)
            logger.info(f"OCR página {page_num}: {len(printed_text)} caracteres extraídos, confiança: {printed_conf:.2f}")
            if printed_text:
                logger.debug(f"Texto OCR (primeiros 200 chars): {printed_text[:200]}")
            
            # HTR manuscrito (se habilitado)
            handwritten_text, handwritten_conf = htr_handwritten(processed_img)
            if handwritten_text:
                logger.info(f"HTR página {page_num}: {len(handwritten_text)} caracteres extraídos")
            
            # Combinar textos
            combined_text = f"{printed_text}\n{handwritten_text}".strip()
            combined_conf = max(printed_conf, handwritten_conf) if handwritten_conf > 0 else printed_conf
            
            logger.info(f"Texto combinado página {page_num}: {len(combined_text)} caracteres")
            
            # Mapear campos
            fields = field_mapper.extract_fields(
                combined_text,
                page=page_num,
                confidence=combined_conf
            )
            logger.info(f"Campos extraídos página {page_num}: {len(fields)}")
            if fields:
                for field in fields:
                    logger.info(f"  - {field.field_name}: {field.field_value} (conf: {field.confidence:.2f})")
            all_fields.extend(fields)
        
        # 4. Persistir campos
        loop.run_until_complete(
            persistence.save_document_fields(document_id, all_fields)
        )
        
        # 5. Atualizar status para DONE
        processing_time = time.time() - start_time
        loop.run_until_complete(
            persistence.update_document_status(
                document_id,
                "DONE",
                pages=len(images),
                processing_time=processing_time
            )
        )
        
        logger.info(f"Processamento concluído: {document_id} ({processing_time:.2f}s)")
        
        return {
            "status": "success",
            "document_id": document_id,
            "pages": len(images),
            "fields_count": len(all_fields),
            "processing_time": processing_time
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar documento {document_id}: {e}", exc_info=True)
        
        # Atualizar status para FAILED
        try:
            ensure_persistence_initialized()
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if persistence.conn_pool:
                loop.run_until_complete(
                    persistence.update_document_status(
                        document_id,
                        "FAILED",
                        error_message=str(e)
                    )
                )
        except Exception as update_error:
            logger.error(f"Erro ao atualizar status para FAILED: {update_error}")
        
        # Retry se ainda houver tentativas
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)
        
        return {
            "status": "error",
            "document_id": document_id,
            "error": str(e)
        }


if __name__ == '__main__':
    celery_app.start()

