from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


def setup_tracing():
    """
    Initialize and register OpenTelemetry tracing with an OTLP gRPC exporter and attach a batch span processor.
    
    This configures a new TracerProvider, registers it as the global provider, creates an OTLPSpanExporter targeting http://localhost:4317 (insecure), wraps it in a BatchSpanProcessor added to the provider, and returns a tracer scoped to this module.
    
    Returns:
        tracer (opentelemetry.trace.Tracer): Tracer for the current module namespace.
    """
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",
        insecure=True,
    )

    span_processor = BatchSpanProcessor(exporter)

    # IMPORTANT: call add_span_processor on the provider
    provider.add_span_processor(span_processor)

    return trace.get_tracer(__name__)