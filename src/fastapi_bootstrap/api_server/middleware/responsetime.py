import logging
from fastapi_bootstrap.api_server.middleware.base import BaseHTTPMiddleware


# this is a middleware that will add a X-Response-Time header to the response
class ResponseTimeMiddleware(BaseHTTPMiddleware):
    header = "X-Response-Time"

    def __init__(self, app, config: dict):
        self._logger = logging.getLogger(__name__)
        super().__init__(app, config)

    async def dispatch(self, request, call_next):
        if not self.middleware_enabled:
            return await call_next(request)

        from time import perf_counter

        _start = perf_counter()

        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                "Request id %s: Processing request for %s. Start time: %s",
                self._getrequest_id(request),
                request.url,
                _start,
            )

        _response = await call_next(request)
        _duration = perf_counter() - _start
        _response.headers[self.header] = str(_duration)

        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                "Request id %s processed in %s seconds",
                self._getrequest_id(request),
                _duration,
            )

        return _response
