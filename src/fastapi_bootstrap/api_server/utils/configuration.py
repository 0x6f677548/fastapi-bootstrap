import json
import os
import re
import logging


class ConfigDict(dict):
    """
    A dictionary that encapsulates another dictionary and
    replaces environment variables in the values.
    If a value contains an environment variable in the format ${ENV_VAR_NAME}
    it is replaced with the value of the environment variable.
    If the environment variable is not defined, the value is not replaced.
    It uses expandvars from os.path to replace the environment variables.

    It also provides a get method that will return the default value if the key is not found and
    will convert the value to the type of the default value if the value is not of the same type.
    """

    _env_var_regex = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)|\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
    _logger = logging.getLogger(__name__)

    # pylint: disable=redefined-builtin
    def __init__(self, dictionary, *, expand_env_vars=True):
        if expand_env_vars:
            super().__init__(self._replace_env_vars(dictionary))
        else:
            super().__init__(dictionary)

    def _replace_env_vars(self, data):
        if isinstance(data, str):
            _expanded = os.path.expandvars(data)

            _matches = self._env_var_regex.findall(_expanded)
            for _match in _matches:
                self._logger.warning(
                    "Environment variable %s is not defined. It will not be replaced. "
                    "This may cause the application to not work as expected. "
                    "Falling back to default values if they are defined.",
                    _match,
                )

            return _expanded
        elif isinstance(data, list):
            return [self._replace_env_vars(item) for item in data]
        elif isinstance(data, dict):
            return ConfigDict(
                {key: self._replace_env_vars(value) for key, value in data.items()},
                expand_env_vars=False,
            )
        elif isinstance(data, tuple):
            return tuple(self._replace_env_vars(item) for item in data)
        else:
            return data

    def _ensure_type(self, value, default_value):
        if isinstance(default_value, bool) and isinstance(value, str):
            value = value.lower() == "true"
        elif isinstance(default_value, bool) and not isinstance(value, bool):
            value = default_value
        elif isinstance(default_value, int) and not isinstance(value, int):
            value = default_value
        elif isinstance(default_value, float) and not isinstance(value, float):
            value = default_value
        elif isinstance(default_value, str) and not isinstance(value, str):
            value = default_value
        return value

    def get(self, key, default_value=None):
        _value = super().get(key, default_value)

        # check if the value is actually a environment variable and
        # if it is, use the default value (if it is defined)
        if (
            default_value is not None
            and isinstance(_value, str)
            and self._env_var_regex.match(_value)
        ):
            self._logger.warning(
                "Environment variable %s is not defined. Falling back to default value: %s",
                _value,
                default_value,
            )
            return default_value
        else:
            return self._ensure_type(_value, default_value)

    @classmethod
    def from_json_file(cls, file_path: str):
        """
        Creates a ConfigDict from a json file.
        """
        # pylint: disable=unspecified-encoding
        with open(file_path) as _f:
            _config_dict = json.load(_f)
        return cls(_config_dict)
