FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY src/ ./src/

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expor porta
EXPOSE 8080

# Comando para iniciar a aplicação
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]

