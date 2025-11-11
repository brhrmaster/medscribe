namespace MedScribe.DataApi.Models;

public class Document
{
    public Guid Id { get; set; }
    public string Tenant { get; set; } = string.Empty;
    public string ObjectKey { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public int Pages { get; set; }
    public string Sha256 { get; set; } = string.Empty;
    public string? ModelVersion { get; set; }
    public string? ErrorMessage { get; set; }
    public decimal? ProcessingTimeSeconds { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
}

