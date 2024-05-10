import configparser
import logging
import time
from pathlib import Path

import pyperclip
import requests

# .riddlesolver in the user's home directory
CONFIG_FILE = Path.joinpath(Path.home(), ".riddlesolver")
DEFAULT_CONFIG = {
    "openai": {
        "api_key": "insert_your_api_key_here",
        "model": "gpt-3.5-turbo",
        "base_url": "https://api.openai.com/v1"
    },
    "general": {
        "cache_dir": "",
        "cache_duration": "7"
    },
    "github": {
        "access_token": ""
    }
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_config():
    """
    Retrieves the configuration from the config file.

    Returns:
        configparser.ConfigParser: The loaded configuration.
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    logger.info("Configuration loaded from file.")
    return config


def set_config(config):
    """
    Saves the configuration to the config file.

    Args:
        config (configparser.ConfigParser): The configuration to save.
    """
    with open(CONFIG_FILE, "w") as config_file:
        config.write(config_file)
    logger.info("Configuration saved to file.")


def load_config_from_file():
    """
    Loads the configuration from the config file. If the file doesn't exist, creates a new config file with default values.

    Returns:
        configparser.ConfigParser: The loaded configuration.
    """
    config = configparser.ConfigParser()
    if not Path(CONFIG_FILE).exists():
        config.read_dict(DEFAULT_CONFIG)
        save_config_to_file(config)
        logger.info("Default configuration created and saved to file.")
    else:
        config.read(CONFIG_FILE)
        logger.info("Configuration loaded from file.")
    return config


def save_config_to_file(config):
    """
    Saves the configuration to the config file.

    Args:
        config (configparser.ConfigParser): The configuration to save.
    """
    with open(CONFIG_FILE, "w") as config_file:
        config.write(config_file)
    logger.info("Configuration saved to file.")


def get_default_config():
    """
    Returns the default configuration.

    Returns:
        configparser.ConfigParser: The default configuration.
    """
    config = configparser.ConfigParser()
    config.read_dict(DEFAULT_CONFIG)
    logger.info("Default configuration loaded.")
    return config


def get_config_value(section, key):
    """
    Retrieves the value of a specific configuration option.

    Args:
        section (str): The section of the configuration option.
        key (str): The key of the configuration option.

    Returns:
        str: The value of the configuration option.
    """
    config = load_config_from_file()
    value = config.get(section, key, fallback=None)
    logger.info(f"Retrieved configuration value: [{section}] {key} = {value}")
    return value


def set_config_value(section, key, value):
    """
    Sets the value of a specific configuration option.

    Args:
        section (str): The section of the configuration option.
        key (str): The key of the configuration option.
        value (str): The value to set for the configuration option.
    """
    config = load_config_from_file()
    if section not in config:
        config.add_section(section)
    config.set(section, key, value)
    logger.info(f"Configuration value set: [{section}] {key} = {value}")


def grant_github_auth():
    """
    Grants GitHub access to the application by setting the GitHub access token in the configuration.
    """
    config = load_config_from_file()
    code_response = request_device_code()

    verification_uri = code_response.get("verification_uri")
    user_code = code_response.get("user_code")
    device_code = code_response.get("device_code")
    interval = code_response.get("interval")

    # save the user_code to the clipboard
    pyperclip.copy(user_code)
    logger.info(f'User code copied to clipboard: {user_code}')
    logger.info(f"Please go to {verification_uri} and enter the code {user_code} to authenticate.")

    access_token = poll_for_token(device_code, interval)
    if access_token:
        set_config_value(section="github", key="access_token", value=access_token)
        save_config_to_file(config)
        logger.info("GitHub authentication successful.")
    else:
        logger.error("GitHub authentication failed.")


def request_device_code():
    """
    Requests a device code from GitHub for authentication.

    Returns:
        dict: The device code response.
    """
    url = f'https://github.com/login/device/code'
    parameters = {'client_id': 'Iv1.6ca45792fc03e432'}
    headers = {'Accept': 'application/json'}

    response = requests.post(url, data=parameters, headers=headers)
    response.raise_for_status()
    logger.info("Device code requested from GitHub.")
    return response.json()


def request_token(device_code):
    uri = f"https://github.com/login/oauth/access_token"
    parameters = {
        "client_id": "Iv1.6ca45792fc03e432",
        "device_code": device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
    }

    headers = {"Accept": "application/json"}

    response = requests.post(uri, data=parameters, headers=headers)
    response.raise_for_status()
    logger.info("Access token requested from GitHub.")
    return response.json()


def poll_for_token(device_code, interval):
    """
    Polls GitHub for the access token using the device code.

    Args:
        device_code (str): The device code.
        interval (int): The polling interval in seconds.
    """
    while True:
        response = request_token(device_code)
        error = response.get("error")
        access_token = response.get("access_token")

        if error:
            if error == "authorization_pending":
                time.sleep(interval)
                logger.info("Authorization pending. Waiting before polling again.")
                continue
            elif error == "slow_down":
                time.sleep(interval + 5)
                logger.warning("Polling too fast. Waiting for an extended interval before polling again.")
                continue
            elif error == "expired_token":
                logger.error("The device code has expired. Please run `login` again.")
                return None
            elif error == "access_denied":
                logger.info("Login cancelled by user.")
                return None
            else:
                logger.error(f"Error occurred during polling: {response}")
                return None
        else:
            logger.info("Access token obtained from GitHub.")
            return access_token