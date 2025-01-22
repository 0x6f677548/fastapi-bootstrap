import logging
from fastapi_bootstrap.api_server.middleware.base import BaseHTTPMiddleware
from time import perf_counter


class LogCallMiddleware(BaseHTTPMiddleware):
    log_level: int = logging.INFO
    log_request: bool = True
    log_response: bool = True

    def __init__(self, app, config: dict):
        self._logger = logging.getLogger(__name__)
        super().__init__(app, config)

    async def dispatch(self, request, call_next):
        if not self.middleware_enabled or not self._logger.isEnabledFor(self.log_level):
            return await call_next(request)

        _start = perf_counter()
        if self.log_request:
            self._logger.log(
                self.log_level,
                f"Request id {self._getrequest_id(request)}: "
                f"Received request for '{request.url}' from '{request.client.host}' "
                f"with origin {request.headers.get('origin')} and "
                f"user agent {request.headers.get('user-agent')}",
            )

        _response = await call_next(request)

        if self.log_response:
            _duration = perf_counter() - _start
            self._logger.log(
                self.log_level,
                f"Request id {self._getrequest_id(request)}: "
                f"Response status code {_response.status_code} for '{request.url}' "
                f"processed in {_duration} seconds",
            )
        return _response
