# OpenTelemetry Instrumentation for Satellite

This document describes the OpenTelemetry (OTEL) instrumentation setup for the satellite infrastructure, including model servers, agent, and observability backend.

## Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐
│  Model Server 1 │────▶│                 │
└─────────────────┘     │                 │
                        │  OTEL Collector │────▶ ┌──────────────┐
┌─────────────────┐     │  (Port 4317/18) │      │  GreptimeDB  │
│  Model Server 2 │────▶│                 │      │  (TSDB)      │
└─────────────────┘     │                 │      └──────────────┘
                        └─────────────────┘
┌─────────────────┐              ▲
│ Satellite Agent │──────────────┘
└─────────────────┘

```

### Components

1. **Model Servers**: Instrumented with OpenTelemetry to collect traces and metrics
2. **Satellite Agent**: Instrumented to monitor deployment operations and API requests
3. **OpenTelemetry Collector**: Centralized collector that receives telemetry from all services
4. **GreptimeDB**: Time-series database that stores metrics, logs, and traces

## Configuration

### Environment Variables

Configure OpenTelemetry via environment variables in your `.env` file:

```bash
# Enable/disable OpenTelemetry instrumentation
OTEL_ENABLED=true

# OTLP collector endpoint (gRPC)
OTEL_ENDPOINT=http://otel-collector:4317

# Service name for the satellite agent
OTEL_SERVICE_NAME=satellite-agent
```

### Docker Compose Services

The `docker-compose.yml` includes:

- **greptimedb**: Time-series database with OTLP support
  - HTTP API: `http://localhost:4000`
  - gRPC API: `http://localhost:4001`
  - MySQL protocol: `localhost:4002`
  - PostgreSQL protocol: `localhost:4003`
  - OTLP gRPC: `localhost:4317`
  - OTLP HTTP: `localhost:4318`

- **otel-collector**: OpenTelemetry Collector
  - OTLP gRPC receiver: `localhost:4317`
  - OTLP HTTP receiver: `localhost:4318`
  - Prometheus metrics: `http://localhost:8889`
  - Health endpoint: `http://localhost:8888`

## What Gets Instrumented

### Satellite Agent

- **FastAPI application**: Automatic tracing of all HTTP endpoints
- **HTTP client requests**: Traces for all outgoing HTTP requests (via httpx)
- **Deployment operations**: Custom spans for deployment tasks
- **Docker operations**: Container lifecycle events

### Model Servers

- **HTTP client requests**: Traces for outgoing HTTP requests
- **Model inference**: Custom spans for model compute operations
- **Health checks**: Monitoring of server health status

## Telemetry Data Flow

1. **Collection**: Model servers and agent send telemetry to OTEL Collector via OTLP gRPC
2. **Processing**: OTEL Collector processes and batches the data
3. **Storage**: Data is exported to GreptimeDB for long-term storage
4. **Query**: Use GreptimeDB's HTTP API, SQL, or PromQL to query telemetry data

## Accessing Telemetry Data

### GreptimeDB HTTP API

Query metrics and traces via HTTP:

```bash
# Query metrics
curl -X POST http://localhost:4000/v1/promql \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'query=up'

# Query via SQL
curl -X POST http://localhost:4000/v1/sql \
  -H 'Content-Type: application/json' \
  -d '{"sql": "SELECT * FROM metrics LIMIT 10"}'
```

### MySQL Protocol

Connect using any MySQL client:

```bash
mysql -h 127.0.0.1 -P 4002 -u greptime_user -p
# Password: greptime_pwd
```

### PostgreSQL Protocol

Connect using any PostgreSQL client:

```bash
psql -h 127.0.0.1 -p 4003 -U greptime_user
# Password: greptime_pwd
```

## OTEL Collector Configuration

The collector configuration (`otel-collector-config.yaml`) includes:

### Receivers
- OTLP gRPC (port 4317)
- OTLP HTTP (port 4318)

### Processors
- `batch`: Batches telemetry data for efficient export
- `memory_limiter`: Prevents out-of-memory issues
- `resourcedetection`: Adds host and container information
- `resource`: Adds satellite-specific attributes

### Exporters
- `otlp/greptimedb-traces`: Exports traces to GreptimeDB
- `otlp/greptimedb-metrics`: Exports metrics to GreptimeDB
- `otlp/greptimedb-logs`: Exports logs to GreptimeDB
- `debug`: Console output for troubleshooting
- `prometheus`: Exposes collector's own metrics

## Monitoring the Collector

Check collector health:

```bash
curl http://localhost:8888/
```

View collector metrics:

```bash
curl http://localhost:8889/metrics
```

## Disabling OpenTelemetry

To disable OpenTelemetry instrumentation:

1. Set `OTEL_ENABLED=false` in your `.env` file
2. Or comment out the `otel-collector` and `greptimedb` services in `docker-compose.yml`

## Custom Instrumentation

### Adding Custom Spans (Agent)

```python
from agent.telemetry import get_tracer

tracer = get_tracer()

with tracer.start_as_current_span("my_operation") as span:
    span.set_attribute("key", "value")
    # Your code here
```

### Adding Custom Metrics (Agent)

```python
from agent.telemetry import get_meter

meter = get_meter()
counter = meter.create_counter("my_counter")
counter.add(1, {"label": "value"})
```

### Model Server Instrumentation

Model servers automatically get instrumented when they start. The instrumentation includes:

- Deployment ID in resource attributes
- HTTP client tracing
- Custom spans can be added in compute functions

## Troubleshooting

### Check if telemetry is being sent

1. Check collector logs:
   ```bash
   docker logs otel-collector
   ```

2. Check GreptimeDB logs:
   ```bash
   docker logs greptimedb
   ```

3. Enable debug exporter in collector config (already enabled by default)

### Common Issues

**Issue**: Model servers not sending telemetry
- **Solution**: Ensure `OTEL_ENABLED=true` and `OTEL_ENDPOINT` is correctly set in the agent environment

**Issue**: Collector can't reach GreptimeDB
- **Solution**: Check that GreptimeDB is healthy: `docker ps` and verify health checks pass

**Issue**: Port conflicts
- **Solution**: Adjust port mappings in `docker-compose.yml` if needed

## Performance Considerations

- **Batch Size**: Default 1024, configurable in `otel-collector-config.yaml`
- **Export Interval**: Default 10s for batching
- **Memory Limit**: Collector limited to 512MB RAM
- **Metric Export**: Every 60 seconds from instrumented services

## Security Notes

- All connections are currently insecure (TLS disabled) for development
- For production, enable TLS in the collector configuration
- GreptimeDB default credentials: `greptime_user / greptime_pwd`
- Change credentials in production via the `--user-provider` flag

## Further Reading

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [GreptimeDB Documentation](https://docs.greptime.com/)
- [OTEL Collector Documentation](https://opentelemetry.io/docs/collector/)
