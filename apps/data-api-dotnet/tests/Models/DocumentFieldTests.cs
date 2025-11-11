using FluentAssertions;
using MedScribe.DataApi.Models;
using Xunit;

namespace MedScribe.DataApi.Tests.Models;

public class DocumentFieldTests
{
    [Fact]
    public void DocumentField_ShouldHaveAllProperties()
    {
        // Arrange
        var documentId = Guid.NewGuid();
        var bbox = new Dictionary<string, object>
        {
            { "x", 100 },
            { "y", 200 },
            { "w", 300 },
            { "h", 400 }
        };

        var field = new DocumentField
        {
            Id = 1,
            DocumentId = documentId,
            FieldName = "patient_name",
            FieldValue = "John Doe",
            Confidence = 0.95m,
            Page = 1,
            Bbox = bbox,
            CreatedAt = DateTime.UtcNow
        };

        // Act & Assert
        field.Should().NotBeNull();
        field.Id.Should().Be(1);
        field.DocumentId.Should().Be(documentId);
        field.FieldName.Should().Be("patient_name");
        field.FieldValue.Should().Be("John Doe");
        field.Confidence.Should().Be(0.95m);
        field.Page.Should().Be(1);
        field.Bbox.Should().NotBeNull();
        field.Bbox!["x"].Should().Be(100);
        field.Bbox["y"].Should().Be(200);
        field.Bbox["w"].Should().Be(300);
        field.Bbox["h"].Should().Be(400);
    }

    [Fact]
    public void DocumentField_ShouldInitializeWithDefaultValues()
    {
        // Arrange & Act
        var field = new DocumentField();

        // Assert
        field.Should().NotBeNull();
        field.Id.Should().Be(0);
        field.DocumentId.Should().BeEmpty();
        field.FieldName.Should().BeEmpty();
        field.FieldValue.Should().BeNull();
        field.Confidence.Should().BeNull();
        field.Page.Should().BeNull();
        field.Bbox.Should().BeNull();
    }

    [Fact]
    public void DocumentField_ShouldSupportNullFieldValue()
    {
        // Arrange & Act
        var field = new DocumentField
        {
            FieldValue = null
        };

        // Assert
        field.FieldValue.Should().BeNull();
    }

    [Fact]
    public void DocumentField_ShouldSupportNullConfidence()
    {
        // Arrange & Act
        var field = new DocumentField
        {
            Confidence = null
        };

        // Assert
        field.Confidence.Should().BeNull();
    }

    [Fact]
    public void DocumentField_ShouldSupportNullPage()
    {
        // Arrange & Act
        var field = new DocumentField
        {
            Page = null
        };

        // Assert
        field.Page.Should().BeNull();
    }

    [Fact]
    public void DocumentField_ShouldSupportNullBbox()
    {
        // Arrange & Act
        var field = new DocumentField
        {
            Bbox = null
        };

        // Assert
        field.Bbox.Should().BeNull();
    }

    [Fact]
    public void DocumentField_ShouldSupportEmptyBbox()
    {
        // Arrange & Act
        var field = new DocumentField
        {
            Bbox = new Dictionary<string, object>()
        };

        // Assert
        field.Bbox.Should().NotBeNull();
        field.Bbox.Should().BeEmpty();
    }

    [Fact]
    public void DocumentField_ShouldCompareObjectsUsingFluentAssertions()
    {
        // Arrange
        var documentId = Guid.Parse("12345678-1234-1234-1234-123456789012");
        var bbox = new Dictionary<string, object> { { "x", 100 }, { "y", 200 } };

        var expectedField = new DocumentField
        {
            Id = 1,
            DocumentId = documentId,
            FieldName = "patient_name",
            FieldValue = "John Doe",
            Confidence = 0.95m,
            Page = 1,
            Bbox = bbox,
            CreatedAt = new DateTime(2024, 1, 1, 0, 0, 0, DateTimeKind.Utc)
        };

        var actualField = new DocumentField
        {
            Id = 1,
            DocumentId = documentId,
            FieldName = "patient_name",
            FieldValue = "John Doe",
            Confidence = 0.95m,
            Page = 1,
            Bbox = bbox,
            CreatedAt = new DateTime(2024, 1, 1, 0, 0, 0, DateTimeKind.Utc)
        };

        // Act & Assert - FluentAssertions provides deep object comparison
        actualField.Should().BeEquivalentTo(expectedField);
    }

    [Theory]
    [InlineData(0.0)]
    [InlineData(0.5)]
    [InlineData(0.95)]
    [InlineData(1.0)]
    public void DocumentField_ShouldAcceptValidConfidenceValues(decimal confidence)
    {
        // Arrange & Act
        var field = new DocumentField
        {
            Confidence = confidence
        };

        // Assert
        field.Confidence.Should().Be(confidence);
    }

    [Theory]
    [InlineData(1)]
    [InlineData(5)]
    [InlineData(10)]
    public void DocumentField_ShouldAcceptValidPageNumbers(int page)
    {
        // Arrange & Act
        var field = new DocumentField
        {
            Page = page
        };

        // Assert
        field.Page.Should().Be(page);
    }
}

