using FluentAssertions;
using MedScribe.DataApi.Data;
using Xunit;

namespace MedScribe.DataApi.Tests.Data;

public class SqlQueriesTests
{
    [Fact]
    public void GetDocumentById_ShouldContainSelectStatement()
    {
        // Arrange & Act
        var query = SqlQueries.GetDocumentById;

        // Assert
        query.Should().NotBeNullOrWhiteSpace();
        query.ToUpperInvariant().Should().Contain("SELECT");
        query.ToUpperInvariant().Should().Contain("FROM DOCUMENTS");
        query.ToUpperInvariant().Should().Contain("WHERE ID = @ID");
    }

    [Fact]
    public void GetDocumentById_ShouldSelectAllRequiredFields()
    {
        // Arrange & Act
        var query = SqlQueries.GetDocumentById;

        // Assert
        var upperQuery = query.ToUpperInvariant();
        upperQuery.Should().Contain("ID");
        upperQuery.Should().Contain("TENANT");
        upperQuery.Should().Contain("OBJECT_KEY");
        upperQuery.Should().Contain("STATUS");
        upperQuery.Should().Contain("PAGES");
        upperQuery.Should().Contain("SHA256");
        upperQuery.Should().Contain("MODEL_VERSION");
        upperQuery.Should().Contain("CREATED_AT");
        upperQuery.Should().Contain("UPDATED_AT");
    }

    [Fact]
    public void GetDocumentFields_ShouldContainSelectStatement()
    {
        // Arrange & Act
        var query = SqlQueries.GetDocumentFields;

        // Assert
        query.Should().NotBeNullOrWhiteSpace();
        var upperQuery = query.ToUpperInvariant();
        upperQuery.Should().Contain("SELECT");
        upperQuery.Should().Contain("FROM DOCUMENT_FIELDS");
        upperQuery.Should().Contain("WHERE DOCUMENT_ID = @DOCUMENTID");
        upperQuery.Should().Contain("ORDER BY");
    }

    [Fact]
    public void GetDocumentFields_ShouldSelectAllRequiredFields()
    {
        // Arrange & Act
        var query = SqlQueries.GetDocumentFields;

        // Assert
        var upperQuery = query.ToUpperInvariant();
        upperQuery.Should().Contain("ID");
        upperQuery.Should().Contain("DOCUMENT_ID");
        upperQuery.Should().Contain("FIELD_NAME");
        upperQuery.Should().Contain("FIELD_VALUE");
        upperQuery.Should().Contain("CONFIDENCE");
        upperQuery.Should().Contain("PAGE");
        upperQuery.Should().Contain("BBOX");
        upperQuery.Should().Contain("CREATED_AT");
    }

    [Fact]
    public void GetDocumentFields_ShouldNormalizeConfidence()
    {
        // Arrange & Act
        var query = SqlQueries.GetDocumentFields;

        // Assert
        var upperQuery = query.ToUpperInvariant();
        upperQuery.Should().Contain("CASE");
        upperQuery.Should().Contain("CONFIDENCE > 1");
        upperQuery.Should().Contain("CONFIDENCE / 100.0");
    }

    [Fact]
    public void ListDocuments_ShouldContainSelectStatement()
    {
        // Arrange & Act
        var query = SqlQueries.ListDocuments;

        // Assert
        query.Should().NotBeNullOrWhiteSpace();
        var upperQuery = query.ToUpperInvariant();
        upperQuery.Should().Contain("SELECT");
        upperQuery.Should().Contain("FROM DOCUMENTS");
        upperQuery.Should().Contain("ORDER BY CREATED_AT DESC");
        upperQuery.Should().Contain("LIMIT");
        upperQuery.Should().Contain("OFFSET");
    }

    [Fact]
    public void ListDocuments_ShouldSupportOptionalFilters()
    {
        // Arrange & Act
        var query = SqlQueries.ListDocuments;

        // Assert
        var upperQuery = query.ToUpperInvariant();
        upperQuery.Should().Contain("@STATUS IS NULL OR STATUS = @STATUS");
        upperQuery.Should().Contain("@TENANT IS NULL OR TENANT = @TENANT");
    }

    [Fact]
    public void CountDocuments_ShouldContainCountStatement()
    {
        // Arrange & Act
        var query = SqlQueries.CountDocuments;

        // Assert
        query.Should().NotBeNullOrWhiteSpace();
        var upperQuery = query.ToUpperInvariant();
        upperQuery.Should().Contain("SELECT COUNT(*)");
        upperQuery.Should().Contain("FROM DOCUMENTS");
    }

    [Fact]
    public void CountDocuments_ShouldSupportOptionalFilters()
    {
        // Arrange & Act
        var query = SqlQueries.CountDocuments;

        // Assert
        var upperQuery = query.ToUpperInvariant();
        upperQuery.Should().Contain("@STATUS IS NULL OR STATUS = @STATUS");
        upperQuery.Should().Contain("@TENANT IS NULL OR TENANT = @TENANT");
    }

    [Fact]
    public void AllQueries_ShouldBeConstants()
    {
        // Arrange & Act
        var getDocumentById = SqlQueries.GetDocumentById;
        var getDocumentFields = SqlQueries.GetDocumentFields;
        var listDocuments = SqlQueries.ListDocuments;
        var countDocuments = SqlQueries.CountDocuments;

        // Assert
        getDocumentById.Should().NotBeNullOrWhiteSpace();
        getDocumentFields.Should().NotBeNullOrWhiteSpace();
        listDocuments.Should().NotBeNullOrWhiteSpace();
        countDocuments.Should().NotBeNullOrWhiteSpace();
    }
}

