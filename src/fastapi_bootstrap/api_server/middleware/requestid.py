from uuid import uuid4
import logging
from fastapi_bootstrap.api_server.middleware.base import BaseHTTPMiddleware


# This is a middleware that adds a request id to the request state
class RequestIdMiddleware(BaseHTTPMiddleware):
    header = "X-Request-Id"

    def __init__(self, app, config: dict):
        self._logger = logging.getLogger(__name__)
        super().__init__(app, config)

    async def dispatch(self, request, call_next):
        if not self.middleware_enabled:
            return await call_next(request)

        _request_id = str(uuid4())
        request.state.request_id = _request_id
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug("Request id %s: Received request for %s", _request_id, request.url)

        _response = await call_next(request)
        _response.headers[self.header] = _request_id

        return _response
