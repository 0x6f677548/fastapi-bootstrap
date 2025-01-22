import logging
import logging.config


def init_default_logging():
    """Inits default logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d %(name)-20s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d,%H:%M:%S",
    )

    # set the root logger level to INFO
    logging.getLogger().setLevel(logging.INFO)


def init_logging_from_file(filename: str = "logging.conf"):
    """Configures logging from a configuration file. If the file does not exist,
    it configures logging to the console.
    filename: the name of the configuration file
    """

    # check if the config file exists
    import os

    if not os.path.exists(filename):
        init_default_logging()
    else:
        # read the logging configuration from the config file
        logging.config.fileConfig(filename)


def init_logging_from_config(config: dict, section: str = "logging"):
    """Initializes logging from a configuration dictionary.
    config: a dictionary containing the logging configuration.
    """

    if config is None or section not in config:
        init_default_logging()
    else:
        _logging_settings = config[section]
        logging.config.dictConfig(_logging_settings)
