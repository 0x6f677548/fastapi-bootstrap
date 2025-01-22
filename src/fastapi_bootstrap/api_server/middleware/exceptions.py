import logging
from fastapi_bootstrap.api_server.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi_bootstrap.api_server.monitoring.instrumentation import current_span_set_error


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """
    This is a middleware that handles exceptions and returns a JSON response with status code 500
    It should be the last middleware in the pipeline and it handles all exceptions that were not
    explicitly handled by other middlewares or routers.
    If the exception reaches this middleware, it means it is not an expected exception and it
    should be logged.
    If the exception is not handled here, it will be handled by the default exception handler of
    FastAPI. This may happen if the exception happens inside this middleware itself.
    """

    def __init__(self, app, config: dict):
        self._logger = logging.getLogger(__name__)
        super().__init__(app, config)

    async def dispatch(self, request, call_next):
        if not self.middleware_enabled:
            return await call_next(request)

        try:
            if self._logger.isEnabledFor(logging.DEBUG):
                self._logger.debug(
                    f"ExceptionHandlerMiddleware: Request id {self._getrequest_id(request)}: "
                    f"Received request for {request.url}"
                )
            return await call_next(request)
        except Exception as exc:  # pylint: disable=broad-except
            # set the status of the current span to error
            current_span_set_error(exc)

            self._logger.exception(
                f"ExceptionHandlerMiddleware: Request id {self._getrequest_id(request)}: "
                f"Exception '{exc}' occurred while processing request for {request.url}"
            )

            return JSONResponse(
                status_code=500,
                content={
                    "message": "Internal server error."
                    "If the problem persists, please contact the administrator"
                },
            )
