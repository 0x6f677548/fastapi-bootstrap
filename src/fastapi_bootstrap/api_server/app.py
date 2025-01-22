import logging
import os

from fastapi import FastAPI, Request
from fastapi_bootstrap.api_server.middleware.cors import CORSMiddleware
from fastapi_bootstrap.api_server.middleware.exceptions import ExceptionHandlerMiddleware
from fastapi_bootstrap.api_server.middleware.logcall import LogCallMiddleware
from fastapi_bootstrap.api_server.middleware.requestid import RequestIdMiddleware
from fastapi_bootstrap.api_server.middleware.responsetime import ResponseTimeMiddleware
from fastapi_bootstrap.api_server.middleware.opentelemetry import OtelSpanAttributesMiddleware
from fastapi_bootstrap.api_server.monitoring.instrumentation import (
    current_span_set_error,
)
from fastapi_bootstrap.api_server.monitoring.logutils import (
    init_logging_from_file,
    init_logging_from_config,
)
from fastapi_bootstrap.api_server.routers.authentication import authconfig
from fastapi_bootstrap.api_server.routers.calculator import router as calculator_router
from fastapi_bootstrap.api_server.utils.configuration import ConfigDict


def _load_server_config() -> ConfigDict:
    server_config = {}
    # load the config file from environment variable CONFIG_FILE.
    # if the environment variable is not set, use the default config file
    # which is located in ./config/api_server.config.json
    cfg_file = os.environ.get("CONFIG_FILE", "./config/api_server.config.json")

    # check if we have a relative path and if so, make it absolute
    if not os.path.isabs(cfg_file):
        cfg_file = os.path.abspath(os.path.join(os.path.dirname(__file__), cfg_file))

    if os.path.exists(cfg_file):
        server_config = ConfigDict.from_json_file(cfg_file)
    return server_config


_server_config = _load_server_config()
if "logging" in _server_config:
    init_logging_from_config(_server_config, "logging")
else:
    init_logging_from_file()


_logger = logging.getLogger(__name__)
_logger.info("Starting server")


authconfig.init_from_config(_server_config)
app: FastAPI = FastAPI()
app.include_router(calculator_router)


# region adding middleware to the pipeline.
# order is important: the first middleware added will be the last one to be executed

# OpenTelemetry middleware
app.add_middleware(OtelSpanAttributesMiddleware)

# CORS configuration and middleware
app.add_middleware(CORSMiddleware, config=_server_config)

# Response time middleware
app.add_middleware(ResponseTimeMiddleware, config=_server_config)

# Logging middleware
app.add_middleware(LogCallMiddleware, config=_server_config)

# Request id middleware
app.add_middleware(RequestIdMiddleware, config=_server_config)

# Exception handler middleware
app.add_middleware(ExceptionHandlerMiddleware, config=_server_config)

# endregion

_logger.info("Server configured, routers and middleware added. Starting server...")


@app.exception_handler(Exception)
async def exception_callback(request: Request, exc: Exception):
    """
    This is the default exception handler for FastAPI.
    It is called when an exception is raised in the server
    and it is not handled by any other exception handler.
    If ExceptionHandlerMiddleware is the last middleware in the pipeline,
    this handler will be called only if the exception
    happens inside the middleware itself. Otherwise, the exception
    will be handled by ExceptionHandlerMiddleware.
    Otherwise, the exception will be handled by the default exception
    handler of FastAPI (which is the same as this one)
    """
    # try to get the request id from the request state
    request_id = request.state.request_id if hasattr(request.state, "request_id") else None
    _logger.exception(
        "Request id %s: Critical exception '%s' \
                      occurred while processing request for %s",
        request_id,
        exc,
        request.url,
    )

    # set the status of the current span to error

    current_span_set_error(exc)
