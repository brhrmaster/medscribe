using System;
using Npgsql;
using Xunit;

namespace MedScribe.DataApi.Tests.Integration;

/// <summary>
/// Custom attribute to skip integration tests when database is not available.
/// This prevents tests from failing when PostgreSQL is not running.
/// </summary>
public class SkipIfNoDatabaseAttribute : FactAttribute
{
    public SkipIfNoDatabaseAttribute()
    {
        if (!IsDatabaseAvailable())
        {
            Skip = "Database not available. Set TEST_DATABASE_URL or ensure PostgreSQL is running.";
        }
    }

    private static bool IsDatabaseAvailable()
    {
        try
        {
            var testConnectionString = Environment.GetEnvironmentVariable("TEST_DATABASE_URL") 
                ?? "Host=localhost;Port=5432;Database=medscribe_test;Username=postgres;Password=postgres";
            
            using var testDataSource = Npgsql.NpgsqlDataSource.Create(testConnectionString);
            using var conn = testDataSource.OpenConnection();
            using var cmd = conn.CreateCommand();
            cmd.CommandText = "SELECT 1";
            cmd.ExecuteScalar();
            return true;
        }
        catch
        {
            // Database not available
            return false;
        }
    }
}

