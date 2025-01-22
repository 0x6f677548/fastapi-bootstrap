from opentelemetry.instrumentation.asgi import (
    OpenTelemetryMiddleware as BaseOpenTelemetryMiddleware,
)
from opentelemetry.trace import Span


class OtelSpanAttributesMiddleware(BaseOpenTelemetryMiddleware):

    def _server_request_hook(self, span: Span, scope: dict):
        """
        This function is called by the FastAPI instrumentation when a request is received.
        It is used to inject the request id into the span
        This is important as we will auto instrument the application, and a span will already
        be in-progress when the routers are called.
        """

        # TODO: this can be done dynamically by using config somehow # pylint: disable=fixme
        # ex: what if we want to inject the user id into the span?
        if span and span.is_recording():
            # inject request_id into span
            if "state" in scope:
                state = scope["state"]
                if "request_id" in state:
                    request_id = state["request_id"]
                    span.set_attribute("X-Request-ID", request_id)

            # inject headers into span
            headers_to_inject = ["x-forwarded-for", "x-real-ip", "origin"]
            if scope["headers"]:
                for header in scope["headers"]:
                    _header_name = header[0].decode("utf-8")
                    if _header_name in headers_to_inject:
                        _header_value = header[1].decode("utf-8")
                        span.set_attribute(_header_name, _header_value)

    def __init__(self, app):
        super().__init__(app, server_request_hook=self._server_request_hook)
