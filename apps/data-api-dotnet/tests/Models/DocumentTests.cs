using FluentAssertions;
using MedScribe.DataApi.Models;
using Xunit;

namespace MedScribe.DataApi.Tests.Models;

public class DocumentTests
{
    [Fact]
    public void Document_ShouldHaveAllProperties()
    {
        // Arrange
        var document = new Document
        {
            Id = Guid.NewGuid(),
            Tenant = "test-tenant",
            ObjectKey = "tenant/document-id.pdf",
            Status = "DONE",
            Pages = 5,
            Sha256 = "abc123def456",
            ModelVersion = "1.0.0",
            ErrorMessage = null,
            ProcessingTimeSeconds = 12.5m,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        // Act & Assert
        document.Should().NotBeNull();
        document.Id.Should().NotBeEmpty();
        document.Tenant.Should().Be("test-tenant");
        document.ObjectKey.Should().Be("tenant/document-id.pdf");
        document.Status.Should().Be("DONE");
        document.Pages.Should().Be(5);
        document.Sha256.Should().Be("abc123def456");
        document.ModelVersion.Should().Be("1.0.0");
        document.ErrorMessage.Should().BeNull();
        document.ProcessingTimeSeconds.Should().Be(12.5m);
    }

    [Fact]
    public void Document_ShouldInitializeWithDefaultValues()
    {
        // Arrange & Act
        var document = new Document();

        // Assert
        document.Should().NotBeNull();
        document.Tenant.Should().BeEmpty();
        document.ObjectKey.Should().BeEmpty();
        document.Status.Should().BeEmpty();
        document.Sha256.Should().BeEmpty();
        document.Pages.Should().Be(0);
        document.ModelVersion.Should().BeNull();
        document.ErrorMessage.Should().BeNull();
        document.ProcessingTimeSeconds.Should().BeNull();
    }

    [Theory]
    [InlineData("RECEIVED")]
    [InlineData("PROCESSING")]
    [InlineData("DONE")]
    [InlineData("FAILED")]
    public void Document_ShouldAcceptValidStatuses(string status)
    {
        // Arrange & Act
        var document = new Document
        {
            Status = status
        };

        // Assert
        document.Status.Should().Be(status);
    }

    [Fact]
    public void Document_ShouldSupportNullModelVersion()
    {
        // Arrange & Act
        var document = new Document
        {
            ModelVersion = null
        };

        // Assert
        document.ModelVersion.Should().BeNull();
    }

    [Fact]
    public void Document_ShouldSupportNullErrorMessage()
    {
        // Arrange & Act
        var document = new Document
        {
            ErrorMessage = null
        };

        // Assert
        document.ErrorMessage.Should().BeNull();
    }

    [Fact]
    public void Document_ShouldSupportNullProcessingTimeSeconds()
    {
        // Arrange & Act
        var document = new Document
        {
            ProcessingTimeSeconds = null
        };

        // Assert
        document.ProcessingTimeSeconds.Should().BeNull();
    }

    [Fact]
    public void Document_ShouldCompareObjectsUsingFluentAssertions()
    {
        // Arrange
        var expectedDocument = new Document
        {
            Id = Guid.Parse("12345678-1234-1234-1234-123456789012"),
            Tenant = "test-tenant",
            ObjectKey = "tenant/doc.pdf",
            Status = "DONE",
            Pages = 3,
            Sha256 = "hash123",
            ModelVersion = "1.0.0",
            CreatedAt = new DateTime(2024, 1, 1, 0, 0, 0, DateTimeKind.Utc),
            UpdatedAt = new DateTime(2024, 1, 1, 0, 0, 0, DateTimeKind.Utc)
        };

        var actualDocument = new Document
        {
            Id = Guid.Parse("12345678-1234-1234-1234-123456789012"),
            Tenant = "test-tenant",
            ObjectKey = "tenant/doc.pdf",
            Status = "DONE",
            Pages = 3,
            Sha256 = "hash123",
            ModelVersion = "1.0.0",
            CreatedAt = new DateTime(2024, 1, 1, 0, 0, 0, DateTimeKind.Utc),
            UpdatedAt = new DateTime(2024, 1, 1, 0, 0, 0, DateTimeKind.Utc)
        };

        // Act & Assert - FluentAssertions provides deep object comparison
        actualDocument.Should().BeEquivalentTo(expectedDocument);
    }
}

