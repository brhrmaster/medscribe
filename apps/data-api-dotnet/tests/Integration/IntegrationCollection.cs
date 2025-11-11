using Xunit;

namespace MedScribe.DataApi.Tests.Integration;

[CollectionDefinition("Integration")]
public class IntegrationCollection : ICollectionFixture<IntegrationFixture>
{
    // This class has no code, and is never created. Its purpose is simply
    // to be the place to apply [CollectionDefinition] and all the
    // ICollectionFixture<> interfaces.
}

public class IntegrationFixture : IAsyncLifetime
{
    public async Task InitializeAsync()
    {
        // Setup integration test environment if needed
        await Task.CompletedTask;
    }

    public async Task DisposeAsync()
    {
        // Cleanup integration test environment if needed
        await Task.CompletedTask;
    }
}

