-- Schema do banco de dados PostgreSQL para MedScribe

-- Tabela de documentos
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY,
    tenant TEXT NOT NULL,
    object_key TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('RECEIVED', 'PROCESSING', 'DONE', 'FAILED')),
    pages INT NOT NULL DEFAULT 0,
    sha256 TEXT NOT NULL,
    model_version TEXT,
    error_message TEXT,
    processing_time_seconds NUMERIC,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Tabela de campos extraídos
CREATE TABLE IF NOT EXISTS document_fields (
    id BIGSERIAL PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    field_name TEXT NOT NULL,
    field_value TEXT,
    confidence NUMERIC,
    page INT,
    bbox JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_tenant ON documents(tenant);
CREATE INDEX IF NOT EXISTS idx_documents_sha256 ON documents(sha256);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_document_fields_doc_id ON document_fields(document_id);
CREATE INDEX IF NOT EXISTS idx_document_fields_doc_name ON document_fields(document_id, field_name);
CREATE INDEX IF NOT EXISTS idx_document_fields_name ON document_fields(field_name);

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para atualizar updated_at
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

