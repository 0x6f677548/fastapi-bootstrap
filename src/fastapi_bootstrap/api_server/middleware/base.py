""" Base http middleware class """

import logging
from starlette.middleware.base import BaseHTTPMiddleware as starlette_BaseHTTPMiddleware


class BaseHTTPMiddleware(starlette_BaseHTTPMiddleware):
    """Base http middleware class"""

    _logger: logging.Logger = logging.getLogger(__name__)
    middleware_config = None
    middleware_enabled = True

    async def dispatch(self, request, call_next):
        raise NotImplementedError()  # pragma: no cover

    def set_fields(self, **kwargs):
        """Set fields from kwargs"""
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    def __init__(self, app, config: dict):
        super().__init__(app)
        self.middleware_name = self.__class__.__name__

        if config is None:
            config = {}
        _middleware_section_configuration = config.get("middleware", {})
        self.middleware_config = _middleware_section_configuration.get(self.middleware_name, {})

        self.middleware_enabled = self.middleware_config.get("enabled", True)

        if self.middleware_enabled:
            if self.middleware_config:
                self._logger.info(
                    "Enabling %s middleware with the following configuration: %s",
                    self.middleware_name,
                    self.middleware_config,
                )
            else:
                self._logger.info(
                    "Enabling %s middleware with default configuration",
                    self.middleware_name,
                )

            self.set_fields(**self.middleware_config.get("kwargs", {}))

        else:
            self._logger.info("%s middleware is disabled", self.middleware_name)

    def _getrequest_id(self, request) -> str:
        if hasattr(request.state, "request_id"):
            return request.state.request_id
        return ""
