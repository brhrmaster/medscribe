using Prometheus;

namespace MedScribe.DataApi.Observability;

public static class Metrics
{
    public static readonly Counter RequestsTotal = Prometheus.Metrics
        .CreateCounter("medscribe_data_api_requests_total", "Total number of requests", new[] { "method", "endpoint", "status" });

    public static readonly Histogram RequestDuration = Prometheus.Metrics
        .CreateHistogram("medscribe_data_api_request_duration_seconds", "Request duration in seconds", new[] { "method", "endpoint" });

    public static readonly Gauge ActiveConnections = Prometheus.Metrics
        .CreateGauge("medscribe_data_api_db_connections_active", "Active database connections");
}

