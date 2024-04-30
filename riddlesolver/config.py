import configparser
from pathlib import Path

# .riddlesolver in the user's home directory
CONFIG_FILE = f"{Path.home()}/.riddlesolver"
DEFAULT_CONFIG = {
    "openai": {
        "api_key": "",
        "model": "gpt-3.5-turbo",
        "base_url": "https://api.openai.com/v1"
    },
    "general": {
        "cache_dir": "~/.cache/repo_cache",
        "cache_duration": "7"
    },
    "github": {
        "access_token": ""
    }
}


def get_config():
    """
    Retrieves the configuration from the config file.

    Returns:
        configparser.ConfigParser: The loaded configuration.
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config


def set_config(config):
    """
    Saves the configuration to the config file.

    Args:
        config (configparser.ConfigParser): The configuration to save.
    """
    with open(CONFIG_FILE, "w") as config_file:
        config.write(config_file)


def load_config_from_file():
    """
    Loads the configuration from the config file. If the file doesn't exist, creates a new config file with default values.

    Returns:
        configparser.ConfigParser: The loaded configuration.
    """
    config = configparser.ConfigParser()
    if not Path(CONFIG_FILE).exists():
        config.read_dict(DEFAULT_CONFIG)
        set_config(config)
    else:
        config.read(CONFIG_FILE)
    return config


def save_config_to_file(config):
    """
    Saves the configuration to the config file.

    Args:
        config (configparser.ConfigParser): The configuration to save.
    """
    set_config(config)


def get_default_config():
    """
    Returns the default configuration.

    Returns:
        configparser.ConfigParser: The default configuration.
    """
    config = configparser.ConfigParser()
    config.read_dict(DEFAULT_CONFIG)
    return config


def get_config_value(config, section, key):
    """
    Retrieves the value of a specific configuration option.

    Args:
        config (configparser.ConfigParser): The configuration.
        section (str): The section of the configuration option.
        key (str): The key of the configuration option.

    Returns:
        str: The value of the configuration option.
    """
    return config.get(section, key, fallback=None)


def set_config_value(config, section, key, value):
    """
    Sets the value of a specific configuration option.

    Args:
        config (configparser.ConfigParser): The configuration.
        section (str): The section of the configuration option.
        key (str): The key of the configuration option.
        value (str): The value to set for the configuration option.
    """
    if section not in config:
        config.add_section(section)
    config.set(section, key, value)
