namespace MedScribe.DataApi.Data;

public static class SqlQueries
{
    public const string GetDocumentById = """
        SELECT id, tenant, object_key, status, pages, sha256, model_version, 
               error_message, processing_time_seconds, created_at, updated_at
        FROM documents
        WHERE id = @id
    """;

    public const string GetDocumentFields = """
        SELECT 
            id AS Id,
            document_id AS DocumentId,
            field_name AS FieldName,
            field_value AS FieldValue,
            CASE 
                WHEN confidence > 1 THEN confidence / 100.0 
                ELSE confidence 
            END AS Confidence,
            page AS Page,
            bbox AS Bbox,
            created_at AS CreatedAt
        FROM document_fields
        WHERE document_id = @documentId
        ORDER BY field_name, page
    """;

    public const string ListDocuments = """
        SELECT id, tenant, object_key, status, pages, sha256, model_version,
               error_message, processing_time_seconds, created_at, updated_at
        FROM documents
        WHERE (@status IS NULL OR status = @status)
          AND (@tenant IS NULL OR tenant = @tenant)
        ORDER BY created_at DESC
        LIMIT @pageSize OFFSET @offset
    """;

    public const string CountDocuments = """
        SELECT COUNT(*)
        FROM documents
        WHERE (@status IS NULL OR status = @status)
          AND (@tenant IS NULL OR tenant = @tenant)
    """;
}

