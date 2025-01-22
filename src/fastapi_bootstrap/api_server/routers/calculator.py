import logging
from fastapi import APIRouter, Depends, Request, HTTPException, status, Form
from fastapi.openapi.models import APIKey
from fastapi_bootstrap.api_server.routers.authentication import get_api_key, is_turnstile_valid
from opentelemetry import trace, metrics
from opentelemetry.trace import Tracer
from fastapi_bootstrap.api_server.monitoring.instrumentation import (
    current_span_add_warning_event,
)
from pydantic import BaseModel
from typing import Annotated


# region ----------------- router setup -----------------

router = APIRouter(prefix="/calculator", tags=["calculator"])
# Get the logger for this module
_logger: logging.Logger = logging.getLogger(__name__)
# Creates a tracer from the global tracer provider
_tracer: Tracer = trace.get_tracer(__name__)
# Creates a meter from the global meter provider
_meter = metrics.get_meter(__name__)

# metric counters example
_calculations_done_counter = _meter.create_counter(
    "calculator.calculations", description="Number of calculations done", unit="1"
)

# endregion


# region ----------------- request id -----------------
def _get_request_id(request: Request):
    from uuid import uuid4

    # check if we have request_id in the request state. if not, log a warning
    if not hasattr(request.state, "request_id"):
        _logger.warning(
            "Request id not found in request state. This should not happen. "
            "Please check middleware configuration. "
            "Generating a request id to ensure logging consistency..."
        )
        request.state.request_id = str(uuid4())
    return request.state.request_id


# endregion


# region ------------------ exception handling ------------------
def _raise_http_exception(status_code: int, message: str):
    current_span_add_warning_event("exception", message)
    raise HTTPException(status_code=status_code, detail=message)


# endregion


# region --------------------- ROUTES --------------------------------


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.get("/version")
async def version():
    from fastapi_bootstrap import __version__

    return {"version": __version__}


class CalculationInput(BaseModel):
    a: float
    b: float


class CalculationOutput(BaseModel):
    result: float


def _divisor_not_zero(input_data: CalculationInput):
    if input_data.b == 0:
        _raise_http_exception(status.HTTP_400_BAD_REQUEST, "Division by zero is not allowed.")
    return input_data


def _divisor_not_zero_form(b: float = Form(...)):
    if b == 0:
        _raise_http_exception(status.HTTP_400_BAD_REQUEST, "Division by zero is not allowed.")
    return b


def _not_zero(b: float):
    if b == 0:
        _raise_http_exception(status.HTTP_400_BAD_REQUEST, "Division by zero is not allowed.")
    return b


def _do_calculation(description: str, request: Request, a: float, b: float, func):
    with _tracer.start_as_current_span(description):
        request_id = _get_request_id(request)
        request_path = request.url.path
        _calculations_done_counter.add(1, {"request_path": request_path, "operation": description})
        _logger.info("Request id %s: %s %s and %s", request_id, description, a, b)
    calculation_output = CalculationOutput(result=func(a, b))
    _logger.info("Request id %s: Result: %s", request_id, calculation_output.result)
    return calculation_output


@router.post("/divide")
async def divide(
    request: Request,
    input_data: CalculationInput = Depends(_divisor_not_zero),
    api_key: APIKey = Depends(get_api_key),  # noqa: ARG001
) -> CalculationOutput:
    """
    Divides two numbers.
    Requires a valid api key
    """

    return _do_calculation("divide", request, input_data.a, input_data.b, lambda a, b: a / b)


@router.post("/divide/submit")
async def divide_submit(
    request: Request,
    a: Annotated[float, Form(...)],
    b: Annotated[float, Depends(_divisor_not_zero_form)],
    *,
    turstile_valid: bool = Depends(is_turnstile_valid),  # noqa: ARG001
) -> CalculationOutput:
    """
    Divides two numbers.
    Requires a valid turnsile token.
    """

    return _do_calculation("divide", request, a, b, lambda a, b: a / b)


@router.post("/multiply")
async def multiply(
    request: Request,
    input_data: CalculationInput,
    api_key: APIKey = Depends(get_api_key),  # noqa: ARG001
) -> CalculationOutput:
    """
    Multiplies two numbers.
    Requires a valid api key
    """

    return _do_calculation("multiply", request, input_data.a, input_data.b, lambda a, b: a * b)


@router.post("/multiply/submit")
async def multiply_submit(
    request: Request,
    a: float = Form(...),
    b: float = Form(...),
    *,
    turstile_valid: bool = Depends(is_turnstile_valid),  # noqa: ARG001
) -> CalculationOutput:
    """
    Multiplies two numbers.
    Requires a valid turnsile token.
    """

    return _do_calculation("multiply", request, a, b, lambda a, b: a * b)


@router.post("/subtract")
async def subtract(
    request: Request,
    input_data: CalculationInput,
    api_key: APIKey = Depends(get_api_key),  # noqa: ARG001
) -> CalculationOutput:
    """
    Subtracts two numbers.
    Requires a valid api key
    """

    return _do_calculation("subtract", request, input_data.a, input_data.b, lambda a, b: a - b)


@router.post("/subtract/submit")
async def subtract_submit(
    request: Request,
    a: float = Form(...),
    b: float = Form(...),
    *,
    turstile_valid: bool = Depends(is_turnstile_valid),  # noqa: ARG001
) -> CalculationOutput:
    """
    Subtracts two numbers.
    Requires a valid turnsile token.
    """

    return _do_calculation("subtract", request, a, b, lambda a, b: a - b)


@router.post("/add")
async def add(
    request: Request,
    input_data: CalculationInput,
    api_key: APIKey = Depends(get_api_key),  # noqa: ARG001
) -> CalculationOutput:
    """
    Adds two numbers.
    Requires a valid api key.
    """
    return _do_calculation("add", request, input_data.a, input_data.b, lambda a, b: a + b)


@router.post("/add/submit")
async def add_submit(
    request: Request,
    a: float = Form(...),
    b: float = Form(...),
    *,
    turstile_valid: bool = Depends(is_turnstile_valid),  # noqa: ARG001
) -> CalculationOutput:
    """
    Adds two numbers.
    Requires a valid turnsile token.
    """

    return _do_calculation("add", request, a, b, lambda a, b: a + b)


# endregion
