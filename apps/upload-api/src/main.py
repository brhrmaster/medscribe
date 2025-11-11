"""Upload API - FastAPI application."""
import uuid
import hashlib
import logging
from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.responses import JSONResponse
from .settings import settings
from .s3_client import s3_client
from .mq_publisher import mq_publisher
from .db_client import db_client
from .schemas import UploadResponse, HealthResponse

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s", "service": "upload-api"}'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MedScribe Upload API",
    description="API para upload de documentos médicos (PDFs)",
    version=settings.app_version
)


@app.on_event("startup")
async def startup():
    """Inicializa conexões ao iniciar a aplicação."""
    await db_client.initialize()


@app.get("/healthz", response_model=HealthResponse)
async def healthz():
    """Health check endpoint."""
    return HealthResponse(
        ok=True,
        service=settings.app_name,
        version=settings.app_version
    )


@app.post("/upload", response_model=UploadResponse, status_code=202)
async def upload(file: UploadFile = File(...)):
    """
    Endpoint para upload de PDF.
    
    Recebe um arquivo PDF, valida, armazena no Spaces e enfileira para processamento.
    """
    # Validação de tipo de conteúdo
    if file.content_type not in settings.allowed_content_types:
        raise HTTPException(
            status_code=415,
            detail=f"Tipo de arquivo não permitido. Aceito apenas: {', '.join(settings.allowed_content_types)}"
        )
    
    # Ler dados do arquivo
    try:
        data = await file.read()
    except Exception as e:
        logger.error(f"Erro ao ler arquivo: {e}")
        raise HTTPException(status_code=400, detail="Erro ao ler arquivo")
    
    # Validação de tamanho
    max_size_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(data) > max_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo muito grande. Tamanho máximo: {settings.max_file_size_mb}MB"
        )
    
    # Gerar ID e hash
    document_id = str(uuid.uuid4())
    sha256 = hashlib.sha256(data).hexdigest()
    tenant = settings.tenant_default
    
    # Chave no S3: {tenant}/{document_id}.pdf
    object_key = f"{tenant}/{document_id}.pdf"
    
    # Armazenar no Spaces
    if not s3_client.put_object(object_key, data, content_type=file.content_type):
        raise HTTPException(status_code=500, detail="Erro ao armazenar arquivo no Spaces")
    
    # Criar documento no banco de dados
    if not await db_client.create_document(document_id, tenant, object_key, sha256):
        logger.warning(f"Documento {document_id} não pôde ser criado no banco (pode já existir)")
    
    # Publicar mensagem no RabbitMQ
    message = {
        "document_id": document_id,
        "tenant": tenant,
        "object_key": object_key,
        "sha256": sha256,
        "file_size": len(data),
        "content_type": file.content_type
    }
    
    if not mq_publisher.publish_message(message):
        logger.error(f"Erro ao publicar mensagem para documento {document_id}")
        # TODO: Considerar rollback do arquivo no S3 em caso de falha
        raise HTTPException(status_code=500, detail="Erro ao enfileirar documento para processamento")
    
    logger.info(f"Documento aceito: {document_id} (sha256: {sha256[:16]}...)")
    
    return UploadResponse(
        document_id=document_id,
        status="ACCEPTED",
        tenant=tenant
    )


@app.on_event("shutdown")
async def shutdown():
    """Cleanup ao encerrar a aplicação."""
    await db_client.close()
    mq_publisher.close()
    logger.info("Upload API encerrada")

