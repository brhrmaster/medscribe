# Arquitetura do MedScribe

## Visão Geral

MedScribe é um sistema distribuído para processamento de documentos médicos escaneados, construído com arquitetura de microserviços em Kubernetes.

## Componentes Principais

### 1. Upload API (FastAPI)
- **Responsabilidade**: Recepção de PDFs e enfileiramento
- **Tecnologia**: Python 3.12, FastAPI
- **Armazenamento**: DigitalOcean Spaces (S3-compatible)
- **Mensageria**: RabbitMQ

### 2. Doc Worker (Celery)
- **Responsabilidade**: Processamento OCR/HTR de documentos
- **Tecnologia**: Python 3.12, Celery
- **Pipeline**: Rasterização → Pré-processamento → OCR → HTR → Mapeamento → Persistência
- **Escalabilidade**: KEDA (auto-scaling baseado em fila)

### 3. Data API (.NET 8)
- **Responsabilidade**: Consulta de dados processados
- **Tecnologia**: .NET 8, ASP.NET Core Minimal APIs
- **Banco**: PostgreSQL (via Dapper + Npgsql)
- **Observabilidade**: Prometheus metrics, OpenTelemetry tracing

### 4. RabbitMQ
- **Responsabilidade**: Broker de mensagens
- **Fila**: `process_document`

### 5. PostgreSQL
- **Responsabilidade**: Armazenamento de metadados e campos extraídos
- **Tabelas**: `documents`, `document_fields`

## Fluxo de Dados

```
[Cliente] → [Upload API] → [DO Spaces] → [RabbitMQ]
                                      ↓
                              [Doc Worker] → [PostgreSQL]
                                      ↓
                              [Data API] ← [Cliente]
```

## Escalabilidade

- **Upload API**: HPA baseado em CPU/Memória
- **Doc Worker**: KEDA baseado em profundidade da fila RabbitMQ
- **Data API**: HPA baseado em CPU/Memória

## Observabilidade

- **Métricas**: Prometheus
- **Logs**: JSON estruturado
- **Tracing**: OpenTelemetry (opcional)

