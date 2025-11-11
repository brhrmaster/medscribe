using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using Dapper;
using FluentAssertions;
using MedScribe.DataApi.Models;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;
using Npgsql;
using Xunit;

namespace MedScribe.DataApi.Tests.Integration;

// Note: Integration tests require a running PostgreSQL database
// Set TEST_DATABASE_URL environment variable or use default connection string
[Collection("Integration")]
public class ProgramTests : IClassFixture<WebApplicationFactory<Program>>, IAsyncLifetime
{
    private readonly WebApplicationFactory<Program> _factory;
    private readonly HttpClient _client;
    private readonly string _testConnectionString;
    private NpgsqlDataSource? _dataSource;

    public ProgramTests(WebApplicationFactory<Program> factory)
    {
        // Use test database connection string
        _testConnectionString = Environment.GetEnvironmentVariable("TEST_DATABASE_URL") 
            ?? "Host=localhost;Port=5432;Database=medscribe_test;Username=postgres;Password=postgres";
        
        // Set environment variable BEFORE creating the factory, so Program.cs can read it
        Environment.SetEnvironmentVariable("DATABASE_URL", _testConnectionString);
        
        _factory = factory.WithWebHostBuilder(builder =>
        {
            // Override configuration for testing
            builder.UseEnvironment("Testing");
            
            // Ensure DATABASE_URL is available during host building
            builder.ConfigureAppConfiguration((context, config) =>
            {
                // Add environment variable provider first
                config.AddEnvironmentVariables();
                
                // Then add in-memory configuration as override
                config.AddInMemoryCollection(new Dictionary<string, string?>
                {
                    { "DATABASE_URL", _testConnectionString },
                    { "ConnectionStrings:Database", _testConnectionString }
                });
            });
        });
        
        _client = _factory.CreateClient();
    }

    public async Task InitializeAsync()
    {
        // Check if database is available before proceeding
        if (!await IsDatabaseAvailableAsync())
        {
            // Skip tests if database is not available
            return;
        }

        // Setup test database if needed
        _dataSource = NpgsqlDataSource.Create(_testConnectionString);
        await SeedTestDataAsync();
    }

    private static async Task<bool> IsDatabaseAvailableAsync()
    {
        try
        {
            var testConnectionString = Environment.GetEnvironmentVariable("TEST_DATABASE_URL") 
                ?? "Host=localhost;Port=5432;Database=medscribe_test;Username=postgres;Password=postgres";
            
            await using var testDataSource = NpgsqlDataSource.Create(testConnectionString);
            await using var conn = await testDataSource.OpenConnectionAsync();
            await using var cmd = conn.CreateCommand();
            cmd.CommandText = "SELECT 1";
            await cmd.ExecuteScalarAsync();
            return true;
        }
        catch
        {
            // Database not available
            return false;
        }
    }

    public async Task DisposeAsync()
    {
        await CleanupTestDataAsync();
        if (_dataSource != null)
        {
            await _dataSource.DisposeAsync();
        }
        _client.Dispose();
        _factory.Dispose();
    }

    private async Task SeedTestDataAsync()
    {
        if (_dataSource == null) return;

        await using var conn = await _dataSource.OpenConnectionAsync();
        
        // Insert test document
        var documentId = Guid.Parse("11111111-1111-1111-1111-111111111111");
        await conn.ExecuteAsync("""
            INSERT INTO documents (id, tenant, object_key, status, pages, sha256, model_version, created_at, updated_at)
            VALUES (@id, @tenant, @objectKey, @status, @pages, @sha256, @modelVersion, @createdAt, @updatedAt)
            ON CONFLICT (id) DO NOTHING
        """, new
        {
            id = documentId,
            tenant = "test-tenant",
            objectKey = "test-tenant/test-doc.pdf",
            status = "DONE",
            pages = 3,
            sha256 = "test-hash-123",
            modelVersion = "1.0.0",
            createdAt = DateTime.UtcNow,
            updatedAt = DateTime.UtcNow
        });

        // Insert test fields
        await conn.ExecuteAsync("""
            INSERT INTO document_fields (document_id, field_name, field_value, confidence, page, bbox, created_at)
            VALUES (@documentId, @fieldName, @fieldValue, @confidence, @page, @bbox, @createdAt)
            ON CONFLICT DO NOTHING
        """, new[]
        {
            new
            {
                documentId,
                fieldName = "patient_name",
                fieldValue = "John Doe",
                confidence = 0.95m,
                page = 1,
                bbox = JsonSerializer.Serialize(new { x = 100, y = 200, w = 300, h = 400 }),
                createdAt = DateTime.UtcNow
            },
            new
            {
                documentId,
                fieldName = "crm",
                fieldValue = "12345",
                confidence = 0.98m,
                page = 1,
                bbox = JsonSerializer.Serialize(new { x = 100, y = 250, w = 200, h = 50 }),
                createdAt = DateTime.UtcNow
            }
        });
    }

    private async Task CleanupTestDataAsync()
    {
        if (_dataSource == null) return;

        await using var conn = await _dataSource.OpenConnectionAsync();
        var documentId = Guid.Parse("11111111-1111-1111-1111-111111111111");
        await conn.ExecuteAsync("DELETE FROM document_fields WHERE document_id = @id", new { id = documentId });
        await conn.ExecuteAsync("DELETE FROM documents WHERE id = @id", new { id = documentId });
    }

    [SkipIfNoDatabase]
    public async Task HealthCheck_ShouldReturnOk()
    {

        // Act
        var response = await _client.GetAsync("/healthz");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var content = await response.Content.ReadAsStringAsync();
        content.Should().Contain("ok");
        content.Should().Contain("data-api");
    }

    [SkipIfNoDatabase]
    public async Task GetDocument_WithValidId_ShouldReturnDocument()
    {
        // Arrange
        var documentId = Guid.Parse("11111111-1111-1111-1111-111111111111");

        // Act
        var response = await _client.GetAsync($"/documents/{documentId}");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var document = await response.Content.ReadFromJsonAsync<Document>();
        document.Should().NotBeNull();
        document!.Id.Should().Be(documentId);
        document.Tenant.Should().Be("test-tenant");
        document.Status.Should().Be("DONE");
    }

    [SkipIfNoDatabase]
    public async Task GetDocument_WithInvalidId_ShouldReturnNotFound()
    {
        // Arrange
        var invalidId = Guid.NewGuid();

        // Act
        var response = await _client.GetAsync($"/documents/{invalidId}");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }

    [SkipIfNoDatabase]
    public async Task GetDocumentFields_WithValidId_ShouldReturnFields()
    {
        // Arrange
        var documentId = Guid.Parse("11111111-1111-1111-1111-111111111111");

        // Act
        var response = await _client.GetAsync($"/documents/{documentId}/fields");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var fields = await response.Content.ReadFromJsonAsync<List<DocumentField>>();
        fields.Should().NotBeNull();
        fields!.Count.Should().BeGreaterThan(0);
        fields.Should().Contain(f => f.FieldName == "patient_name");
        fields.Should().Contain(f => f.FieldName == "crm");
    }

    [SkipIfNoDatabase]
    public async Task GetDocumentFields_WithInvalidId_ShouldReturnEmptyList()
    {
        // Arrange
        var invalidId = Guid.NewGuid();

        // Act
        var response = await _client.GetAsync($"/documents/{invalidId}/fields");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var fields = await response.Content.ReadFromJsonAsync<List<DocumentField>>();
        fields.Should().NotBeNull();
        fields!.Count.Should().Be(0);
    }

    [SkipIfNoDatabase]
    public async Task ListDocuments_WithoutFilters_ShouldReturnDocuments()
    {
        // Act
        var response = await _client.GetAsync("/documents");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var result = await response.Content.ReadFromJsonAsync<JsonElement>();
        result.GetProperty("data").GetArrayLength().Should().BeGreaterThan(0);
        result.GetProperty("pagination").Should().NotBeNull();
    }

    [SkipIfNoDatabase]
    public async Task ListDocuments_WithStatusFilter_ShouldReturnFilteredDocuments()
    {
        // Act
        var response = await _client.GetAsync("/documents?status=DONE");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var result = await response.Content.ReadFromJsonAsync<JsonElement>();
        var documents = result.GetProperty("data").EnumerateArray();
        documents.Should().OnlyContain(d => d.GetProperty("status").GetString() == "DONE");
    }

    [SkipIfNoDatabase]
    public async Task ListDocuments_WithTenantFilter_ShouldReturnFilteredDocuments()
    {
        // Act
        var response = await _client.GetAsync("/documents?tenant=test-tenant");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var result = await response.Content.ReadFromJsonAsync<JsonElement>();
        var documents = result.GetProperty("data").EnumerateArray();
        documents.Should().OnlyContain(d => d.GetProperty("tenant").GetString() == "test-tenant");
    }

    [SkipIfNoDatabase]
    public async Task ListDocuments_WithPagination_ShouldReturnPaginatedResults()
    {
        // Act
        var response = await _client.GetAsync("/documents?page=1&pageSize=10");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var result = await response.Content.ReadFromJsonAsync<JsonElement>();
        result.GetProperty("pagination").GetProperty("page").GetInt32().Should().Be(1);
        result.GetProperty("pagination").GetProperty("pageSize").GetInt32().Should().Be(10);
        result.GetProperty("data").GetArrayLength().Should().BeLessThanOrEqualTo(10);
    }

    [SkipIfNoDatabase]
    public async Task ListDocuments_WithInvalidPage_ShouldDefaultToPage1()
    {
        // Act
        var response = await _client.GetAsync("/documents?page=0&pageSize=10");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var result = await response.Content.ReadFromJsonAsync<JsonElement>();
        result.GetProperty("pagination").GetProperty("page").GetInt32().Should().Be(1);
    }

    [SkipIfNoDatabase]
    public async Task ListDocuments_WithPageSizeExceedingMax_ShouldClampTo500()
    {
        // Act
        var response = await _client.GetAsync("/documents?page=1&pageSize=1000");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var result = await response.Content.ReadFromJsonAsync<JsonElement>();
        result.GetProperty("pagination").GetProperty("pageSize").GetInt32().Should().Be(500);
    }

    [SkipIfNoDatabase]
    public async Task Metrics_ShouldReturnPrometheusMetrics()
    {
        // Act
        var response = await _client.GetAsync("/metrics");

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var content = await response.Content.ReadAsStringAsync();
        content.Should().NotBeNullOrWhiteSpace();
        // Prometheus metrics typically start with # HELP or # TYPE or metric names
        content.Should().Match(c => c.Contains("#") || c.Contains("http_"));
    }
}

