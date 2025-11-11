# Dicionário de Dados

## Tabela: documents

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | Identificador único do documento |
| tenant | TEXT | Tenant/multi-tenancy |
| object_key | TEXT | Chave do objeto no S3/Spaces |
| status | TEXT | Status: RECEIVED, PROCESSING, DONE, FAILED |
| pages | INT | Número de páginas do documento |
| sha256 | TEXT | Hash SHA256 do arquivo PDF |
| model_version | TEXT | Versão do modelo de processamento usado |
| error_message | TEXT | Mensagem de erro (se status = FAILED) |
| processing_time_seconds | NUMERIC | Tempo de processamento em segundos |
| created_at | TIMESTAMPTZ | Data de criação |
| updated_at | TIMESTAMPTZ | Data de última atualização |

## Tabela: document_fields

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | BIGSERIAL | Identificador único do campo |
| document_id | UUID | FK para documents.id |
| field_name | TEXT | Nome do campo extraído |
| field_value | TEXT | Valor extraído |
| confidence | NUMERIC | Confiança (0.0 a 1.0) |
| page | INT | Número da página onde foi encontrado |
| bbox | JSONB | Bounding box: {"x": float, "y": float, "w": float, "h": float} |
| created_at | TIMESTAMPTZ | Data de criação |

## Campos Comuns Extraídos

- `patient_name`: Nome do paciente
- `cpf`: CPF do paciente
- `crm`: CRM do médico
- `date`: Data do laudo
- `phone`: Telefone

