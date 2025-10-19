"""Observability configuration (Sentry, OpenTelemetry)."""

import os

from .logger import get_logger

logger = get_logger(__name__)


def setup_sentry(
    dsn: str | None = None,
    environment: str = "production",
    traces_sample_rate: float = 0.1,
) -> bool:
    """
    Setup Sentry for error tracking.

    Args:
        dsn: Sentry DSN (defaults to SENTRY_DSN env var)
        environment: Environment name
        traces_sample_rate: Percentage of transactions to trace (0.0 to 1.0)

    Returns:
        True if Sentry was initialized, False otherwise
    """
    dsn = dsn or os.getenv("SENTRY_DSN")

    if not dsn:
        logger.info("Sentry DSN not configured, skipping Sentry setup")
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            traces_sample_rate=traces_sample_rate,
            integrations=[
                FlaskIntegration(),
            ],
            # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            profiles_sample_rate=traces_sample_rate,
            # Capture user context
            send_default_pii=False,  # Set to True if you want to capture user IP, etc.
        )

        logger.info(f"Sentry initialized for environment: {environment}")
        return True

    except ImportError:
        logger.warning("sentry-sdk not installed, skipping Sentry setup")
        return False
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False


def setup_opentelemetry(
    service_name: str = "autogen-research",
    otlp_endpoint: str | None = None,
) -> bool:
    """
    Setup OpenTelemetry for distributed tracing.

    Args:
        service_name: Service name for traces
        otlp_endpoint: OTLP endpoint URL (defaults to OTEL_EXPORTER_OTLP_ENDPOINT env var)

    Returns:
        True if OpenTelemetry was initialized, False otherwise
    """
    otlp_endpoint = otlp_endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    if not otlp_endpoint:
        logger.info("OTLP endpoint not configured, skipping OpenTelemetry setup")
        return False

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import SERVICE_NAME, Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        # Create resource with service name
        resource = Resource(attributes={SERVICE_NAME: service_name})

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Create OTLP exporter
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)

        # Add span processor
        processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(processor)

        # Set global tracer provider
        trace.set_tracer_provider(provider)

        logger.info(f"OpenTelemetry initialized for service: {service_name}")
        return True

    except ImportError:
        logger.warning("OpenTelemetry packages not installed, skipping setup")
        return False
    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry: {e}")
        return False


def instrument_flask_app(app) -> None:
    """
    Instrument a Flask app with OpenTelemetry.

    Args:
        app: Flask application instance
    """
    try:
        from opentelemetry.instrumentation.flask import FlaskInstrumentor

        FlaskInstrumentor().instrument_app(app)
        logger.info("Flask app instrumented with OpenTelemetry")
    except ImportError:
        logger.warning("OpenTelemetry Flask instrumentation not available")
    except Exception as e:
        logger.error(f"Failed to instrument Flask app: {e}")


def get_tracer(name: str = __name__):
    """
    Get an OpenTelemetry tracer.

    Args:
        name: Tracer name (typically module name)

    Returns:
        Tracer instance
    """
    try:
        from opentelemetry import trace

        return trace.get_tracer(name)
    except ImportError:
        # Return a no-op tracer if OpenTelemetry not installed
        class NoOpTracer:
            def start_as_current_span(self, name, **kwargs):
                from contextlib import nullcontext

                return nullcontext()

        return NoOpTracer()


def capture_exception(error: Exception, context: dict = None) -> None:
    """
    Capture an exception with optional context.

    Args:
        error: Exception to capture
        context: Additional context dictionary
    """
    try:
        import sentry_sdk

        with sentry_sdk.push_scope() as scope:
            if context:
                for key, value in context.items():
                    scope.set_context(key, value)
            sentry_sdk.capture_exception(error)
    except ImportError:
        # Sentry not installed, just log
        logger.error(f"Exception: {error}", exc_info=True, extra=context)
    except Exception as e:
        logger.error(f"Failed to capture exception in Sentry: {e}")
