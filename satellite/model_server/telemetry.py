"""OpenTelemetry instrumentation setup for the satellite model server."""

import logging
import os
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = logging.getLogger(__name__)


def setup_telemetry(
    service_name: str | None = None,
    deployment_id: str | None = None,
    otlp_endpoint: str | None = None,
    enable_console: bool = False,
) -> None:
    """
    Setup OpenTelemetry instrumentation for the model server.

    Args:
        service_name: Name of the service for telemetry (defaults to "model-server")
        deployment_id: Deployment ID to add to resource attributes
        otlp_endpoint: OTLP collector endpoint (e.g., "http://otel-collector:4317")
        enable_console: Whether to enable console exporter for debugging
    """
    # Get configuration from environment if not provided
    if otlp_endpoint is None:
        otlp_endpoint = os.getenv("OTEL_ENDPOINT", "http://otel-collector:4317")

    if service_name is None:
        service_name = "model-server"

    if deployment_id is None:
        deployment_id = os.getenv("DEPLOYMENT_ID", "unknown")

    # Check if OTEL is enabled
    otel_enabled = os.getenv("OTEL_ENABLED", "true").lower() == "true"
    if not otel_enabled:
        logger.info("OpenTelemetry disabled via OTEL_ENABLED environment variable")
        return

    if not otlp_endpoint:
        logger.info("OpenTelemetry disabled: no OTLP endpoint configured")
        return

    logger.info(f"Setting up OpenTelemetry with endpoint: {otlp_endpoint}")

    # Create resource with service information
    resource = Resource.create(
        attributes={
            "service.name": service_name,
            "service.version": "0.1.0",
            "deployment.environment": "satellite",
            "deployment.id": deployment_id,
        }
    )

    # Setup Tracing
    setup_tracing(resource, otlp_endpoint, enable_console)

    # Setup Metrics
    setup_metrics(resource, otlp_endpoint, enable_console)

    # Instrument libraries
    instrument_libraries()

    logger.info("OpenTelemetry instrumentation configured successfully")


def setup_tracing(
    resource: Resource, otlp_endpoint: str, enable_console: bool = False
) -> None:
    """Setup tracing with OTLP exporter."""
    trace_provider = TracerProvider(resource=resource)

    # Add OTLP exporter
    otlp_trace_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    trace_provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))

    # Optionally add console exporter for debugging
    if enable_console:
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        console_exporter = ConsoleSpanExporter()
        trace_provider.add_span_processor(BatchSpanProcessor(console_exporter))

    trace.set_tracer_provider(trace_provider)
    logger.info("Tracing configured with OTLP exporter")


def setup_metrics(
    resource: Resource, otlp_endpoint: str, enable_console: bool = False
) -> None:
    """Setup metrics with OTLP exporter."""
    # Create OTLP metric exporter
    otlp_metric_exporter = OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True)

    # Create metric reader with periodic export
    metric_reader = PeriodicExportingMetricReader(
        otlp_metric_exporter, export_interval_millis=60000  # Export every 60 seconds
    )

    # Optionally add console exporter for debugging
    readers = [metric_reader]
    if enable_console:
        from opentelemetry.sdk.metrics.export import ConsoleMetricExporter

        console_metric_exporter = ConsoleMetricExporter()
        console_reader = PeriodicExportingMetricReader(
            console_metric_exporter, export_interval_millis=60000
        )
        readers.append(console_reader)

    # Set up meter provider
    meter_provider = MeterProvider(resource=resource, metric_readers=readers)
    metrics.set_meter_provider(meter_provider)
    logger.info("Metrics configured with OTLP exporter")


def instrument_libraries() -> None:
    """Instrument common libraries used by the model server."""
    # Instrument httpx for HTTP client tracing
    HTTPXClientInstrumentor().instrument()
    logger.info("Instrumented httpx client")


def get_tracer(name: str = "model-server") -> trace.Tracer:
    """Get a tracer instance for manual instrumentation."""
    return trace.get_tracer(name)


def get_meter(name: str = "model-server") -> metrics.Meter:
    """Get a meter instance for custom metrics."""
    return metrics.get_meter(name)
