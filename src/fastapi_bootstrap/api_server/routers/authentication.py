import logging
import aiohttp
from fastapi.security.api_key import APIKeyQuery, APIKeyHeader
from fastapi import Form, Header, Security, HTTPException, status
from fastapi_bootstrap.api_server.monitoring.instrumentation import (
    current_span_set_attribute,
    current_span_add_warning_event,
)
from opentelemetry.trace import Tracer
from opentelemetry import trace


_logger: logging.Logger = logging.getLogger(__name__)


class AuthConfig:
    _API_KEY_NAME = "api-key"  # the name of the api key header(suffixed by x-) and query parameter

    _turnstile_secret_key: str  # the secret key used to validate the captcha token
    _turnstile_enabled: bool = False  # whether or not to use the turnstile captcha
    # the turnstile validation endpoint
    _turnstile_siteverify_url: str = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    _valid_api_keys: list[str]  # the list of valid api keys

    # the name of query parameter to use for the api key
    _api_key_query = APIKeyQuery(name=_API_KEY_NAME, auto_error=False)
    # the name of the header to use for the api key
    _api_key_header = APIKeyHeader(name=f"x-{_API_KEY_NAME}", auto_error=False)

    def init_from_config(self, config):
        """
        This function is used to initialize the authentication module.
        It will read the configuration and set the global variables accordingly.
        """

        def _mask_sensitive_values(config: dict) -> dict:
            import copy

            sensitive_keys = {"secret_key", "valid_api_keys"}
            masked_config = copy.deepcopy(config)

            def recursive_mask(d):
                for k, v in d.items():
                    if isinstance(v, dict):
                        recursive_mask(v)
                    elif k.lower() in sensitive_keys:
                        d[k] = "****"

            recursive_mask(masked_config)
            return masked_config

        self._authentication_config = config.get("authentication", {}) if config else {}
        _logger.info(
            "Configuration for authentication: %s",
            _mask_sensitive_values(self._authentication_config),
        )

        # turstile configuration
        _turnstile_config = self._authentication_config.get("turnstile", {})
        self._turnstile_enabled = _turnstile_config.get("enabled", self._turnstile_enabled)
        self._turnstile_secret_key = _turnstile_config.get("secret_key", None)
        self._turnstile_siteverify_url = _turnstile_config.get(
            "siteverify_url", self._turnstile_siteverify_url
        )

        # api key management configuration
        _api_key_management_config = self._authentication_config.get("api_key_management", {})
        self._valid_api_keys = _api_key_management_config.get("valid_api_keys", [])
        _logger.info("Authentication configuration initialized")


authconfig = AuthConfig()


# ------------------ security ------------------

# Creates a tracer from the global tracer provider
_tracer: Tracer = trace.get_tracer(__name__)


async def _validate_turnstile_token(
    secret_key, token: str | None = None, ip: str | None = None
) -> bool:
    with _tracer.start_as_current_span("_validate_turnstile_token"):
        if not token:
            return False

        # Validate the token by calling the "/siteverify" API endpoint.
        form_data = aiohttp.FormData()
        form_data.add_field("secret", secret_key)
        form_data.add_field("response", token)
        if ip:
            form_data.add_field("remoteip", ip)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                authconfig._turnstile_siteverify_url, data=form_data
            ) as response:
                outcome = await response.json()
                _success = outcome.get("success")
                if not _success:
                    # cloudflare returns a list of error codes.
                    # keep them as a list in the span for troubleshooting
                    current_span_set_attribute("error-codes", outcome.get("error-codes", []))

                return outcome.get("success")


async def is_turnstile_valid(
    cf_turnstile_response=Form(alias="cf-turnstile-response", default=None),
    cf_connecting_ip=Header(alias="cf-connecting-ip", default=None),
) -> bool:
    _authorized = not authconfig._turnstile_enabled or await _validate_turnstile_token(
        authconfig._turnstile_secret_key, cf_turnstile_response, cf_connecting_ip
    )
    _logger.debug("Authorized by turnstile token: %s", _authorized)

    if cf_connecting_ip:
        current_span_set_attribute("cf_connecting_ip", cf_connecting_ip)

    if not _authorized:
        _message = f"Invalid or missing turnstile token: {cf_turnstile_response}"

        # adds a warning event to the current span and sets the warning attribute to true
        current_span_add_warning_event(
            "authorization_failed",
            f"{_message}; cf_turnstile_response: {cf_turnstile_response}",
        )

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_message)

    return _authorized


async def get_api_key(
    api_key_query_value: str = Security(authconfig._api_key_query),
    api_key_header_value: str = Security(authconfig._api_key_header),
):
    """
    This function is used to get the api key from the request.
    It will check for the api key in the following order:
    1. api key query parameter
    2. api key header

    if the api key is not found, or is invalid, it will raise an HTTPException
    """

    # TODO: refactor to use a key management service # pylint: disable=fixme
    _authorized: bool = (
        api_key_header_value is not None and api_key_header_value in authconfig._valid_api_keys
    ) or (api_key_query_value is not None and api_key_query_value in authconfig._valid_api_keys)

    if _authorized:
        _api_key = api_key_query_value if api_key_query_value else api_key_header_value
        # add the api key to the request state so it can be used by the request hook
        # request.state.api_key = api_key_query if api_key_query else api_key_header

        # add the api key to the current span
        current_span_set_attribute(authconfig._API_KEY_NAME, _api_key)

        return _api_key
    else:
        _message = (
            f"Invalid or missing API key. "
            f"api_key_query: {api_key_query_value}, "
            f"api_key_header: {api_key_header_value}"
        )
        # adds a warning event to the current span and sets the warning attribute to true
        current_span_add_warning_event("authorization_failed", _message)

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_message)
