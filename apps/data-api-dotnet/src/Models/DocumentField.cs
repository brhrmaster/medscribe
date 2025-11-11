namespace MedScribe.DataApi.Models;

public class DocumentField
{
    public long Id { get; set; }
    public Guid DocumentId { get; set; }
    public string FieldName { get; set; } = string.Empty;
    public string? FieldValue { get; set; }
    public decimal? Confidence { get; set; }
    public int? Page { get; set; }
    public Dictionary<string, object>? Bbox { get; set; }
    public DateTime CreatedAt { get; set; }
}

