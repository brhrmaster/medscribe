using AutoFixture;
using AutoFixture.Xunit2;
using FluentAssertions;
using MedScribe.DataApi.Models;
using Xunit;

namespace MedScribe.DataApi.Tests.Models;

/// <summary>
/// Exemplos de testes usando AutoFixture para facilitar a criação de objetos no Arrange.
/// AutoFixture reduz a quantidade de código boilerplate necessário para criar objetos de teste.
/// </summary>
public class DocumentTestsAutoFixture
{
    private readonly Fixture _fixture;

    public DocumentTestsAutoFixture()
    {
        _fixture = new Fixture();
        // Configurar AutoFixture para não gerar valores aleatórios para propriedades específicas
        _fixture.Customize<Document>(c => c
            .With(d => d.Status, "DONE")
            .With(d => d.Tenant, "test-tenant"));
    }

    [Fact]
    public void Document_ShouldBeCreatedWithAutoFixture()
    {
        // Arrange - AutoFixture cria automaticamente um Document com valores preenchidos
        var document = _fixture.Create<Document>();

        // Act & Assert
        document.Should().NotBeNull();
        document.Id.Should().NotBeEmpty();
        document.Status.Should().Be("DONE");
        document.Tenant.Should().Be("test-tenant");
    }

    [Fact]
    public void Document_ShouldCreateMultipleInstancesWithAutoFixture()
    {
        // Arrange - AutoFixture pode criar múltiplas instâncias facilmente
        var documents = _fixture.CreateMany<Document>(5).ToList();

        // Act & Assert
        documents.Should().HaveCount(5);
        documents.Should().OnlyContain(d => d.Status == "DONE");
        documents.Should().OnlyContain(d => d.Tenant == "test-tenant");
        documents.Should().OnlyContain(d => d.Id != Guid.Empty);
    }

    [Theory, AutoData]
    public void Document_ShouldAcceptCustomValuesWithAutoDataAttribute(
        string tenant,
        string status,
        int pages)
    {
        // Arrange - AutoData injeta automaticamente valores nos parâmetros
        var document = _fixture.Build<Document>()
            .With(d => d.Tenant, tenant)
            .With(d => d.Status, status)
            .With(d => d.Pages, pages)
            .Create();

        // Act & Assert
        document.Tenant.Should().Be(tenant);
        document.Status.Should().Be(status);
        document.Pages.Should().Be(pages);
    }

    [Fact]
    public void Document_ShouldBuildWithSpecificProperties()
    {
        // Arrange - Build permite criar objetos com propriedades específicas
        var document = _fixture.Build<Document>()
            .With(d => d.Status, "PROCESSING")
            .With(d => d.Pages, 10)
            .Without(d => d.ErrorMessage) // Garantir que ErrorMessage seja null
            .Create();

        // Act & Assert
        document.Status.Should().Be("PROCESSING");
        document.Pages.Should().Be(10);
        document.ErrorMessage.Should().BeNull();
    }

    [Fact]
    public void Document_ShouldCreateWithFrozenInstances()
    {
        // Arrange - Freeze garante que o mesmo valor seja usado em múltiplos lugares
        // Criar um fixture sem a customização de tenant para este teste
        var fixtureWithoutCustomization = new Fixture();
        var tenant = fixtureWithoutCustomization.Freeze<string>();
        
        var document1 = fixtureWithoutCustomization.Build<Document>()
            .With(d => d.Tenant, tenant)
            .Create();
        var document2 = fixtureWithoutCustomization.Build<Document>()
            .With(d => d.Tenant, tenant)
            .Create();

        // Act & Assert - Ambos documentos terão o mesmo tenant
        document1.Tenant.Should().Be(tenant);
        document2.Tenant.Should().Be(tenant);
        document1.Tenant.Should().Be(document2.Tenant);
    }
}

