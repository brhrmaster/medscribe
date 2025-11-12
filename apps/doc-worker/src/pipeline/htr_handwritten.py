"""HTR para texto manuscrito usando TrOCR (ONNX)."""
import logging
import os
from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    import onnxruntime as ort
    from transformers import AutoProcessor

try:
    import numpy as np
    from PIL import Image
    import onnxruntime as ort
    from transformers import AutoProcessor
    ONNX_AVAILABLE = True
except ImportError as e:
    ONNX_AVAILABLE = False
    # Criar tipos stub para type checking
    class _StubInferenceSession:
        pass
    ort = type('Module', (), {'InferenceSession': _StubInferenceSession})()
    AutoProcessor = None

from ..settings import settings

logger = logging.getLogger(__name__)

# Cache global para modelos e tokenizer
_onnx_encoder_session: Optional['ort.InferenceSession'] = None
_onnx_decoder_session: Optional['ort.InferenceSession'] = None
_tokenizer: Optional['AutoProcessor'] = None


def _load_onnx_models() -> Tuple['ort.InferenceSession', 'ort.InferenceSession']:
    """
    Carrega modelos ONNX do TrOCR (encoder e decoder) de forma lazy.
    
    Returns:
        Tupla (encoder_session, decoder_session)
    """
    global _onnx_encoder_session, _onnx_decoder_session
    
    if _onnx_encoder_session is not None and _onnx_decoder_session is not None:
        return _onnx_encoder_session, _onnx_decoder_session
    
    encoder_path = settings.htr_onnx_encoder_path
    decoder_path = settings.htr_onnx_decoder_path
    
    # Verificar se os arquivos existem
    if not os.path.exists(encoder_path):
        raise FileNotFoundError(f"Modelo encoder ONNX não encontrado: {encoder_path}")
    if not os.path.exists(decoder_path):
        raise FileNotFoundError(f"Modelo decoder ONNX não encontrado: {decoder_path}")
    
    # Configurações otimizadas para CPU
    sess_options = ort.SessionOptions()
    sess_options.intra_op_num_threads = 4
    sess_options.inter_op_num_threads = 2
    sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    
    # Providers: CPU apenas (conforme requisito do projeto)
    providers = ['CPUExecutionProvider']
    
    try:
        logger.info(f"Carregando encoder ONNX de {encoder_path}")
        _onnx_encoder_session = ort.InferenceSession(
            encoder_path,
            sess_options=sess_options,
            providers=providers
        )
        
        logger.info(f"Carregando decoder ONNX de {decoder_path}")
        _onnx_decoder_session = ort.InferenceSession(
            decoder_path,
            sess_options=sess_options,
            providers=providers
        )
        
        logger.info("Modelos TrOCR ONNX carregados com sucesso")
        return _onnx_encoder_session, _onnx_decoder_session
        
    except Exception as e:
        logger.error(f"Erro ao carregar modelos ONNX: {e}")
        raise


def _load_tokenizer():
    """
    Carrega o tokenizer/processor do TrOCR de forma lazy.
    
    Returns:
        AutoProcessor do transformers
    """
    global _tokenizer
    
    if not ONNX_AVAILABLE:
        raise ImportError("onnxruntime ou transformers não estão disponíveis")
    
    if _tokenizer is not None:
        return _tokenizer
    
    try:
        logger.info(f"Carregando tokenizer: {settings.htr_onnx_tokenizer_name}")
        _tokenizer = AutoProcessor.from_pretrained(settings.htr_onnx_tokenizer_name)
        logger.info("Tokenizer carregado com sucesso")
        return _tokenizer
    except Exception as e:
        logger.error(f"Erro ao carregar tokenizer: {e}")
        raise


def _preprocess_image(img: 'Image.Image') -> 'np.ndarray':
    """
    Pré-processa imagem para o formato esperado pelo TrOCR.
    
    Args:
        img: Imagem PIL
        
    Returns:
        Array numpy normalizado no formato (1, 3, H, W)
    """
    # Converter para RGB se necessário
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Redimensionar mantendo aspect ratio, depois fazer crop/pad para tamanho fixo
    target_size = settings.htr_onnx_image_size
    img.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
    
    # Criar imagem quadrada com padding
    new_img = Image.new('RGB', (target_size, target_size), (255, 255, 255))
    paste_x = (target_size - img.width) // 2
    paste_y = (target_size - img.height) // 2
    new_img.paste(img, (paste_x, paste_y))
    
    # Converter para array e normalizar [0, 1]
    img_array = np.array(new_img, dtype=np.float32) / 255.0
    
    # Normalizar usando mean e std do ImageNet (padrão do TrOCR)
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(1, 1, 3)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(1, 1, 3)
    img_array = (img_array - mean) / std
    
    # Transpor para formato CHW e adicionar dimensão de batch: (1, 3, H, W)
    img_array = np.transpose(img_array, (2, 0, 1))
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array


def _run_encoder_inference(encoder_session: 'ort.InferenceSession', pixel_values: 'np.ndarray') -> 'np.ndarray':
    """
    Executa inferência no encoder para obter features da imagem.
    
    Args:
        encoder_session: Sessão ONNX do encoder
        pixel_values: Array pré-processado da imagem
        
    Returns:
        Features do encoder (hidden states)
    """
    input_name = encoder_session.get_inputs()[0].name
    outputs = encoder_session.run(None, {input_name: pixel_values})
    
    # Retornar o primeiro output (normalmente são os hidden states)
    return outputs[0]


def _run_decoder_inference(
    decoder_session: 'ort.InferenceSession',
    encoder_hidden_states: 'np.ndarray',
    input_ids: 'np.ndarray',
    attention_mask: Optional['np.ndarray'] = None
) -> Tuple['np.ndarray', 'np.ndarray']:
    """
    Executa inferência no decoder para gerar tokens.
    
    Args:
        decoder_session: Sessão ONNX do decoder
        encoder_hidden_states: Features do encoder
        input_ids: IDs dos tokens de entrada (sequência parcial)
        attention_mask: Máscara de atenção (opcional)
        
    Returns:
        Tupla (logits, probabilidades)
    """
    input_names = [inp.name for inp in decoder_session.get_inputs()]
    inputs = {}
    
    # Mapear inputs conforme esperado pelo decoder
    if 'encoder_hidden_states' in input_names:
        inputs['encoder_hidden_states'] = encoder_hidden_states
    elif len(input_names) > 0:
        inputs[input_names[0]] = encoder_hidden_states
    
    if 'input_ids' in input_names:
        inputs['input_ids'] = input_ids
    elif len(input_names) > 1:
        inputs[input_names[1]] = input_ids
    
    if attention_mask is not None and 'attention_mask' in input_names:
        inputs['attention_mask'] = attention_mask
    
    outputs = decoder_session.run(None, inputs)
    
    # Logits são normalmente o primeiro output
    logits = outputs[0]
    
    # Calcular probabilidades usando softmax
    # Aplicar softmax na última dimensão (vocab_size)
    exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
    probs = exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
    
    return logits, probs


def _beam_search_decode(
    decoder_session: 'ort.InferenceSession',
    encoder_hidden_states: 'np.ndarray',
    tokenizer: 'AutoProcessor',
    beam_size: int = 5,
    max_length: int = 256
) -> Tuple[str, float]:
    """
    Decodifica texto usando beam search.
    
    Args:
        decoder_session: Sessão ONNX do decoder
        encoder_hidden_states: Features do encoder
        tokenizer: Processor/tokenizer do TrOCR
        beam_size: Tamanho do beam
        max_length: Comprimento máximo da sequência
        
    Returns:
        Tupla (texto_decodificado, confiança_média)
    """
    # Tokens especiais
    tokenizer_obj = tokenizer.tokenizer if hasattr(tokenizer, 'tokenizer') else tokenizer
    pad_token_id = tokenizer_obj.pad_token_id if hasattr(tokenizer_obj, 'pad_token_id') else 0
    bos_token_id = getattr(tokenizer_obj, 'bos_token_id', None) or getattr(tokenizer_obj, 'cls_token_id', None) or 0
    eos_token_id = getattr(tokenizer_obj, 'eos_token_id', None) or getattr(tokenizer_obj, 'sep_token_id', None) or 1
    
    # Inicializar beam com sequência vazia (apenas BOS)
    beams = [([bos_token_id], 0.0)]  # (sequence, score)
    
    for step in range(max_length):
        new_beams = []
        
        for sequence, score in beams:
            # Se já terminou (EOS), manter como está
            if sequence and sequence[-1] == eos_token_id:
                new_beams.append((sequence, score))
                continue
            
            # Preparar input_ids
            input_ids = np.array([sequence], dtype=np.int64)
            
            # Executar decoder
            logits, probs = _run_decoder_inference(decoder_session, encoder_hidden_states, input_ids)
            
            # Obter probabilidades do último token
            next_token_probs = probs[0, -1, :]  # (vocab_size,)
            
            # Manter top-k tokens
            top_k_indices = np.argsort(next_token_probs)[-beam_size:][::-1]
            
            for token_id in top_k_indices:
                token_prob = float(next_token_probs[token_id])
                new_score = score + np.log(token_prob + 1e-10)  # Log probability
                new_sequence = sequence + [int(token_id)]
                new_beams.append((new_sequence, new_score))
        
        # Se não há novos beams, parar
        if not new_beams:
            break
        
        # Manter apenas top beam_size
        new_beams.sort(key=lambda x: x[1], reverse=True)
        beams = new_beams[:beam_size]
        
        # Se todos terminaram, parar
        if all(seq and seq[-1] == eos_token_id for seq, _ in beams):
            break
    
    # Escolher melhor beam
    if not beams:
        return "", 0.0
    
    best_sequence, best_score = beams[0]
    
    # Remover BOS e EOS
    if best_sequence and len(best_sequence) > 0:
        if best_sequence[0] == bos_token_id:
            best_sequence = best_sequence[1:]
        if best_sequence and best_sequence[-1] == eos_token_id:
            best_sequence = best_sequence[:-1]
    
    # Decodificar para texto
    try:
        # Usar o método decode do tokenizer
        if hasattr(tokenizer, 'decode'):
            text = tokenizer.decode(best_sequence, skip_special_tokens=True)
        elif hasattr(tokenizer, 'tokenizer') and hasattr(tokenizer.tokenizer, 'decode'):
            text = tokenizer.tokenizer.decode(best_sequence, skip_special_tokens=True)
        else:
            # Fallback: converter IDs para texto manualmente
            text = "".join([chr(id) if 32 <= id < 127 else "" for id in best_sequence])
    except Exception as e:
        logger.warning(f"Erro ao decodificar tokens: {e}")
        text = ""
    
    # Calcular confiança média (normalizar score)
    # Score é log probability, converter para confiança [0, 1]
    # Normalizar pelo comprimento da sequência
    seq_length = max(len(best_sequence), 1)
    confidence = min(1.0, max(0.0, np.exp(best_score / seq_length)))
    
    return text, confidence


def htr_handwritten(img: 'Image.Image') -> tuple[str, float]:
    """
    Extrai texto manuscrito de uma imagem usando TrOCR via ONNX.
    
    Args:
        img: Imagem PIL
        
    Returns:
        Tupla (texto_extraído, confiança)
    """
    if not settings.htr_onnx_enable:
        logger.debug("HTR ONNX desabilitado")
        return "", 0.0
    
    if not ONNX_AVAILABLE:
        logger.warning("onnxruntime não está disponível. HTR desabilitado.")
        return "", 0.0
    
    try:
        # Carregar modelos (lazy loading)
        encoder_session, decoder_session = _load_onnx_models()
        tokenizer = _load_tokenizer()
        
        # Pré-processar imagem
        pixel_values = _preprocess_image(img)
        
        # Executar encoder
        encoder_hidden_states = _run_encoder_inference(encoder_session, pixel_values)
        
        # Executar decoder com beam search
        text, confidence = _beam_search_decode(
            decoder_session,
            encoder_hidden_states,
            tokenizer,
            beam_size=settings.htr_onnx_beam_size,
            max_length=settings.htr_onnx_max_length
        )
        
        if text:
            logger.debug(f"HTR manuscrito: {len(text)} caracteres extraídos, confiança: {confidence:.2f}")
        else:
            logger.debug("HTR manuscrito: nenhum texto extraído")
        
        return text.strip(), confidence
        
    except FileNotFoundError as e:
        logger.warning(f"Modelos ONNX não encontrados: {e}. HTR desabilitado.")
        return "", 0.0
    except Exception as e:
        logger.error(f"Erro no HTR manuscrito: {e}", exc_info=True)
        return "", 0.0


def load_onnx_model(model_path: str) -> Optional['ort.InferenceSession']:
    """
    Carrega modelo TrOCR ONNX (função auxiliar para compatibilidade).
    
    Args:
        model_path: Caminho para o arquivo .onnx
        
    Returns:
        Sessão ONNX ou None se não for possível carregar
    """
    if not ONNX_AVAILABLE:
        logger.error("onnxruntime não está disponível")
        return None
    
    try:
        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = 4
        sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        
        session = ort.InferenceSession(
            model_path,
            sess_options=sess_options,
            providers=['CPUExecutionProvider']
        )
        logger.info(f"Modelo ONNX carregado: {model_path}")
        return session
    except Exception as e:
        logger.error(f"Erro ao carregar modelo ONNX {model_path}: {e}")
        return None

