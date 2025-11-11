# Ambiente Local - MedScribe

Este diretório contém a configuração Docker Compose para executar o MedScribe localmente.

## Pré-requisitos

- Docker Desktop (ou Docker Engine + Docker Compose)
- Pelo menos 8GB de RAM disponível
- Portas disponíveis: 5432, 5672, 15672, 9000, 9001, 8000, 8001

## Serviços

### Infraestrutura

- **PostgreSQL 17** (porta 5432)
  - Usuário: `medscribe`
  - Senha: `medscribe123`
  - Database: `medscribe`

- **RabbitMQ** (portas 5672, 15672)
  - Usuário: `medscribe`
  - Senha: `medscribe123`
  - Management UI: http://localhost:15672

- **MinIO** (portas 9000, 9001)
  - S3-compatible storage (substitui DigitalOcean Spaces localmente)
  - Access Key: `minioadmin`
  - Secret Key: `minioadmin123`
  - Console UI: http://localhost:9001
  - Bucket: `medical-reports` (criado automaticamente)

### Aplicações

- **Upload API** (porta 8000)
  - Endpoint: http://localhost:8000
  - Health: http://localhost:8000/healthz
  - Swagger: http://localhost:8000/docs

- **Doc Worker**
  - Worker Celery que processa documentos da fila
  - Sem porta exposta (processa internamente)

- **Data API** (porta 8001)
  - Endpoint: http://localhost:8001
  - Health: http://localhost:8001/healthz
  - Swagger: http://localhost:8001/swagger
  - Metrics: http://localhost:8001/metrics

## Como Usar

### 1. Iniciar todos os serviços

```bash
cd localhost
docker-compose up -d
```

### 2. Verificar status dos serviços

```bash
docker-compose ps
```

### 3. Ver logs

```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f upload-api
docker-compose logs -f doc-worker
docker-compose logs -f data-api-dotnet
```

### 4. Parar serviços

```bash
docker-compose down
```

### 5. Parar e remover volumes (limpar dados)

```bash
docker-compose down -v
```

## Inicialização do Banco de Dados

O schema SQL é executado automaticamente na primeira inicialização do PostgreSQL através do volume montado em `/docker-entrypoint-initdb.d/`.

## Testando o Sistema

### 1. Upload de documento

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@/caminho/para/documento.pdf"
```

### 2. Verificar status do documento

```bash
# Substituir {document_id} pelo ID retornado no upload
curl http://localhost:8001/documents/{document_id}
```

### 3. Ver campos extraídos

```bash
curl http://localhost:8001/documents/{document_id}/fields
```

### 4. Listar documentos

```bash
curl http://localhost:8001/documents
```

## Acessos

- **RabbitMQ Management**: http://localhost:15672 (medscribe/medscribe123)
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin123)
- **Upload API Swagger**: http://localhost:8000/docs
- **Data API Swagger**: http://localhost:8001/swagger

## Troubleshooting

### Serviço não inicia

Verifique os logs:
```bash
docker-compose logs [nome-do-servico]
```

### Banco de dados não inicializa

Verifique se o arquivo `schema.sql` existe:
```bash
ls -la ../apps/doc-worker/src/db/schema.sql
```

### Worker não processa documentos

1. Verifique se o RabbitMQ está saudável
2. Verifique os logs do worker: `docker-compose logs -f doc-worker`
3. Verifique se há mensagens na fila via RabbitMQ Management UI

### Erro de conexão S3

O MinIO pode levar alguns segundos para inicializar. Aguarde o healthcheck passar antes de fazer uploads.

## Variáveis de Ambiente

Para modificar configurações, edite o arquivo `docker-compose.yaml` ou crie um arquivo `.env` na pasta `localhost/`.

## Notas

- Os dados são persistidos em volumes Docker
- Para desenvolvimento, você pode montar volumes com o código fonte para hot-reload (não configurado por padrão)
- O MinIO é usado apenas para desenvolvimento local. Em produção, use DigitalOcean Spaces ou AWS S3

