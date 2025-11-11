using AutoFixture;
using AutoFixture.Xunit2;
using FluentAssertions;
using MedScribe.DataApi.Models;
using Xunit;

namespace MedScribe.DataApi.Tests.Models;

/// <summary>
/// Exemplos de testes usando AutoFixture para DocumentField.
/// Demonstra como AutoFixture facilita a criação de objetos complexos com coleções e valores aninhados.
/// </summary>
public class DocumentFieldTestsAutoFixture
{
    private readonly Fixture _fixture;

    public DocumentFieldTestsAutoFixture()
    {
        _fixture = new Fixture();
        // Configurar AutoFixture para criar Bbox como Dictionary
        _fixture.Customize<DocumentField>(c => c
            .With(f => f.Confidence, 0.95m)
            .With(f => f.Page, 1));
    }

    [Fact]
    public void DocumentField_ShouldBeCreatedWithAutoFixture()
    {
        // Arrange - AutoFixture cria automaticamente um DocumentField
        var field = _fixture.Create<DocumentField>();

        // Act & Assert
        field.Should().NotBeNull();
        field.DocumentId.Should().NotBeEmpty();
        field.FieldName.Should().NotBeNullOrEmpty();
        field.Confidence.Should().Be(0.95m);
        field.Page.Should().Be(1);
    }

    [Fact]
    public void DocumentField_ShouldCreateWithCustomBbox()
    {
        // Arrange - Build permite criar objetos com propriedades complexas
        var bbox = new Dictionary<string, object>
        {
            { "x", 100 },
            { "y", 200 },
            { "w", 300 },
            { "h", 400 }
        };

        var field = _fixture.Build<DocumentField>()
            .With(f => f.Bbox, bbox)
            .With(f => f.FieldName, "patient_name")
            .With(f => f.FieldValue, "John Doe")
            .Create();

        // Act & Assert
        field.Bbox.Should().NotBeNull();
        field.Bbox!["x"].Should().Be(100);
        field.Bbox["y"].Should().Be(200);
        field.Bbox["w"].Should().Be(300);
        field.Bbox["h"].Should().Be(400);
        field.FieldName.Should().Be("patient_name");
        field.FieldValue.Should().Be("John Doe");
    }

    [Theory, AutoData]
    public void DocumentField_ShouldAcceptCustomValuesWithAutoData(
        string fieldName,
        string fieldValue,
        decimal confidence)
    {
        // Arrange - AutoData injeta valores automaticamente
        var field = _fixture.Build<DocumentField>()
            .With(f => f.FieldName, fieldName)
            .With(f => f.FieldValue, fieldValue)
            .With(f => f.Confidence, confidence)
            .Create();

        // Act & Assert
        field.FieldName.Should().Be(fieldName);
        field.FieldValue.Should().Be(fieldValue);
        field.Confidence.Should().Be(confidence);
    }

    [Fact]
    public void DocumentField_ShouldCreateMultipleFieldsForDocument()
    {
        // Arrange - Criar múltiplos campos facilmente
        var documentId = Guid.NewGuid();
        var fields = _fixture.Build<DocumentField>()
            .With(f => f.DocumentId, documentId)
            .With(f => f.Confidence, 0.95m) // Garantir que todos tenham o mesmo confidence
            .CreateMany(3)
            .ToList();

        // Act & Assert
        fields.Should().HaveCount(3);
        fields.Should().OnlyContain(f => f.DocumentId == documentId);
        fields.Should().OnlyContain(f => f.Confidence == 0.95m);
    }

    [Fact]
    public void DocumentField_ShouldHandleNullValues()
    {
        // Arrange - Without garante que propriedades sejam null
        var field = _fixture.Build<DocumentField>()
            .Without(f => f.FieldValue)
            .Without(f => f.Bbox)
            .Create();

        // Act & Assert
        field.FieldValue.Should().BeNull();
        field.Bbox.Should().BeNull();
    }
}

