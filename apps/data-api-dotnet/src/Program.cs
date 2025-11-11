using System.Text.Json;
using Dapper;
using MedScribe.DataApi.Data;
using MedScribe.DataApi.Models;
using MedScribe.DataApi.Observability;
using Npgsql;
using Prometheus;
using System.Diagnostics;

var builder = WebApplication.CreateBuilder(args);

// Database
var dbConnString = Environment.GetEnvironmentVariable("DATABASE_URL")
    ?? builder.Configuration.GetConnectionString("Database")
    ?? throw new InvalidOperationException("DATABASE_URL not configured");

var dataSource = Db.CreateDataSource(dbConnString);
builder.Services.AddSingleton(dataSource);
builder.Services.AddSingleton<Db>(sp => new Db(sp.GetRequiredService<NpgsqlDataSource>()));

// Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Observability
Tracing.Configure(builder);

// JSON options
builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
});

var app = builder.Build();

// Metrics
app.MapMetrics("/metrics");

// Swagger
app.UseSwagger();
app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "MedScribe Data API v1"));

// Health check
app.MapGet("/healthz", () => Results.Ok(new { ok = true, service = "data-api", version = "1.0.0" }))
    .WithName("HealthCheck")
    .WithTags("Health");

// Get document by ID
app.MapGet("/documents/{id:guid}", async (Guid id, NpgsqlDataSource ds) =>
{
    using var conn = await ds.OpenConnectionAsync();
    var doc = await conn.QueryFirstOrDefaultAsync<Document>(SqlQueries.GetDocumentById, new { id });
    
    if (doc == null)
    {
        return Results.NotFound(new { error = "Document not found" });
    }
    
    return Results.Ok(doc);
})
.WithName("GetDocument")
.WithTags("Documents")
.Produces<Document>(StatusCodes.Status200OK)
.Produces(StatusCodes.Status404NotFound);

// Get document fields
app.MapGet("/documents/{id:guid}/fields", async (Guid id, NpgsqlDataSource ds) =>
{
    using var conn = await ds.OpenConnectionAsync();
    var fields = await conn.QueryAsync<DocumentField>(SqlQueries.GetDocumentFields, new { documentId = id });
    
    // Log para debug
    var fieldsList = fields.ToList();
    Console.WriteLine($"Found {fieldsList.Count} fields for document {id}");
    
    return Results.Ok(fieldsList);
})
.WithName("GetDocumentFields")
.WithTags("Documents")
.Produces<IEnumerable<DocumentField>>(StatusCodes.Status200OK);

// List documents with filters and pagination
app.MapGet("/documents", async (
    NpgsqlDataSource ds,
    string? status = null,
    string? tenant = null,
    int page = 1,
    int pageSize = 50) =>
{
    page = Math.Max(1, page);
    pageSize = Math.Clamp(pageSize, 1, 500);
    var offset = (page - 1) * pageSize;

    using var conn = await ds.OpenConnectionAsync();
    
    var documents = await conn.QueryAsync<Document>(
        SqlQueries.ListDocuments,
        new { status, tenant, pageSize, offset }
    );
    
    var total = await conn.QuerySingleAsync<long>(
        SqlQueries.CountDocuments,
        new { status, tenant }
    );

    return Results.Ok(new
    {
        data = documents,
        pagination = new
        {
            page,
            pageSize,
            total,
            totalPages = (int)Math.Ceiling(total / (double)pageSize)
        }
    });
})
.WithName("ListDocuments")
.WithTags("Documents")
.Produces(StatusCodes.Status200OK);

app.Run();

// Make Program class available for testing
public partial class Program { }
