using Npgsql;

namespace MedScribe.DataApi.Data;

public class Db
{
    private readonly NpgsqlDataSource _dataSource;

    public Db(NpgsqlDataSource dataSource)
    {
        _dataSource = dataSource;
    }

    public NpgsqlDataSource DataSource => _dataSource;

    public static NpgsqlDataSource CreateDataSource(string connectionString)
    {
        var builder = new NpgsqlDataSourceBuilder(connectionString);
        builder.EnableParameterLogging(false);
        return builder.Build();
    }
}

