from opentelemetry import trace
from opentelemetry.trace.status import Status, StatusCode

import logging

_logger = logging.getLogger(__name__)


# region span helpers
def _if_span_valid(span, f):
    if span is not None and span is not trace.INVALID_SPAN:
        f()


def current_span_set_attribute(attribute_name: str, attribute_value: str):
    _span = trace.get_current_span()
    _if_span_valid(_span, lambda: _span.set_attribute(attribute_name, attribute_value))


def current_span_add_warning_event(event_name: str, message: str):
    _span = trace.get_current_span()
    _if_span_valid(_span, lambda: _span.add_event(event_name, {"message": message}))
    _if_span_valid(_span, lambda: _span.set_attribute("warning", "true"))


def current_span_set_error(e: Exception):
    _span = trace.get_current_span()
    _if_span_valid(_span, lambda: _span.set_status(Status(StatusCode.ERROR)))
    _if_span_valid(_span, lambda: _span.record_exception(e))


# endregion
