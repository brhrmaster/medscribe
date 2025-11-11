# MedScribe Data API Tests

This directory contains unit and integration tests for the MedScribe Data API using xUnit and ExpectedObjects following TDD best practices.

## Test Structure

### Unit Tests

- **Models/** - Tests for domain models (`Document`, `DocumentField`)
- **Data/** - Tests for data access layer (`Db`, `SqlQueries`)

### Integration Tests

- **Integration/** - End-to-end tests for API endpoints

## Running Tests

### Run All Tests

```bash
dotnet test
```

### Run Specific Test Project

```bash
dotnet test apps/data-api-dotnet/tests/MedScribe.DataApi.Tests.csproj
```

### Run Tests with Coverage

```bash
dotnet test --collect:"XPlat Code Coverage"
```

**Nota:** Os testes de integração são automaticamente pulados (ignorados) quando o PostgreSQL não está disponível, usando o atributo `[SkipIfNoDatabase]`. Isso permite executar code coverage sem erros mesmo sem o banco rodando. Os testes serão marcados como "Ignorado" em vez de "Falhou".

### Run Specific Test Class

```bash
dotnet test --filter "FullyQualifiedName~DocumentTests"
```

### Run Integration Tests

Integration tests require a running PostgreSQL database. Set the `TEST_DATABASE_URL` environment variable:

```bash
export TEST_DATABASE_URL="Host=localhost;Port=5432;Database=medscribe_test;Username=postgres;Password=postgres"
dotnet test --filter "FullyQualifiedName~ProgramTests"
```

Or on Windows:

```powershell
$env:TEST_DATABASE_URL="Host=localhost;Port=5432;Database=medscribe_test;Username=postgres;Password=postgres"
dotnet test --filter "FullyQualifiedName~ProgramTests"
```

**Note:** Integration tests are automatically skipped when PostgreSQL is not available (using `[SkipIfNoDatabase]` attribute). They will be marked as "Ignored" instead of "Failed", allowing code coverage to run successfully without a database.

### Run Only Unit Tests (Exclude Integration)

To run only unit tests and skip integration tests:

```bash
dotnet test --filter "FullyQualifiedName!~ProgramTests"
```

## Test Libraries

- **xUnit** - Testing framework
- **FluentAssertions** - Fluent assertions library with deep object comparison (`BeEquivalentTo`)
- **AutoFixture** - Automatically creates test objects, reducing Arrange boilerplate
- **AutoFixture.Xunit2** - xUnit integration for AutoFixture (AutoData attribute)
- **Moq** - Mocking framework
- **Microsoft.AspNetCore.Mvc.Testing** - Integration testing for ASP.NET Core

### AutoFixture Benefits

AutoFixture facilita a criação de objetos no Arrange dos testes:

```csharp
// Sem AutoFixture - muito código boilerplate
var document = new Document
{
    Id = Guid.NewGuid(),
    Tenant = "test-tenant",
    ObjectKey = "tenant/doc.pdf",
    Status = "DONE",
    Pages = 5,
    Sha256 = "abc123",
    // ... muitas linhas
};

// Com AutoFixture - código conciso
var fixture = new Fixture();
var document = fixture.Create<Document>();

// Com AutoFixture e customizações
var document = fixture.Build<Document>()
    .With(d => d.Status, "DONE")
    .With(d => d.Tenant, "test-tenant")
    .Create();
```

Veja exemplos completos em:
- `Models/DocumentTests.AutoFixture.cs`
- `Models/DocumentFieldTests.AutoFixture.cs`

## Test Best Practices

1. **TDD Approach**: Tests are written following Test-Driven Development principles
2. **Arrange-Act-Assert**: All tests follow the AAA pattern
3. **ExpectedObjects**: Used for object comparison in model tests
4. **FluentAssertions**: Used for readable assertions
5. **Isolation**: Each test is independent and can run in any order
6. **Integration Tests**: Marked with `[Collection("Integration")]` to separate from unit tests

## Example Test

```csharp
[Fact]
public void Document_ShouldHaveAllProperties()
{
    // Arrange
    var document = new Document
    {
        Id = Guid.NewGuid(),
        Tenant = "test-tenant",
        Status = "DONE"
    };

    // Act & Assert
    document.Should().NotBeNull();
    document.Tenant.Should().Be("test-tenant");
    document.Status.Should().Be("DONE");
}
```

