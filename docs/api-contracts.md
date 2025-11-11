# Contratos de API

## Upload API

### POST /upload
Upload de documento PDF.

**Request:**
- Content-Type: multipart/form-data
- Body: arquivo PDF

**Response:**
```json
{
  "document_id": "uuid",
  "status": "ACCEPTED",
  "tenant": "default",
  "created_at": "2025-11-10T22:00:00Z"
}
```

### GET /healthz
Health check.

**Response:**
```json
{
  "ok": true,
  "service": "medscribe-upload-api",
  "version": "1.0.0"
}
```

## Data API

### GET /documents/{id}
Obter documento por ID.

**Response:**
```json
{
  "id": "uuid",
  "tenant": "default",
  "objectKey": "default/uuid.pdf",
  "status": "DONE",
  "pages": 1,
  "sha256": "hash",
  "modelVersion": "1.0.0",
  "createdAt": "2025-11-10T22:00:00Z",
  "updatedAt": "2025-11-10T22:01:00Z"
}
```

### GET /documents/{id}/fields
Obter campos extraídos de um documento.

**Response:**
```json
[
  {
    "id": 1,
    "documentId": "uuid",
    "fieldName": "patient_name",
    "fieldValue": "João Silva",
    "confidence": 0.95,
    "page": 1,
    "bbox": {"x": 100, "y": 200, "w": 150, "h": 20}
  }
]
```

### GET /documents
Listar documentos com filtros e paginação.

**Query Parameters:**
- `status` (opcional): Filtrar por status
- `tenant` (opcional): Filtrar por tenant
- `page` (default: 1): Número da página
- `pageSize` (default: 50): Tamanho da página

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "pageSize": 50,
    "total": 100,
    "totalPages": 2
  }
}
```

### GET /healthz
Health check.

### GET /metrics
Métricas Prometheus.

### GET /swagger
Interface Swagger UI.

