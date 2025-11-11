FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema (Tesseract, Poppler, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    poppler-utils \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY src/ ./src/

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Expor porta (Celery não precisa, mas mantém padrão)
EXPOSE 8080

# Comando para iniciar o worker
CMD ["celery", "-A", "src.worker", "worker", "--loglevel=info", "--concurrency=4", "-Q", "process_document"]

