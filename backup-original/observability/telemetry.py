from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


def setup_tracing():
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