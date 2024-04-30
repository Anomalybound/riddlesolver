import configparser
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
    else:
        config.read(CONFIG_FILE)
    return config


def save_config_to_file(config):
    """
    Saves the configuration to the config file.

    Args:
        config (configparser.ConfigParser): The configuration to save.
    """
    with open(CONFIG_FILE, "w") as config_file:
        config.write(config_file)


def get_default_config():
    """
    Returns the default configuration.

    Returns:
        configparser.ConfigParser: The default configuration.
    """
    config = configparser.ConfigParser()
    config.read_dict(DEFAULT_CONFIG)
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
    return config.get(section, key, fallback=None)


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
    print(f'User code copied to clipboard: {user_code}')
    print(f"Please go to {verification_uri} and enter the code {user_code} to authenticate.")

    access_token = poll_for_token(device_code, interval)
    if access_token:
        set_config_value(section="github", key="access_token", value=access_token)
        save_config_to_file(config)
        print("GitHub authentication successful.")


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
                # The user has not yet entered the code.
                # Wait, then poll again.
                continue
            elif error == "slow_down":
                time.sleep(interval + 5)
                # The app polled too fast.
                # Wait for the interval plus 5 seconds, then poll again.
                continue
            elif error == "expired_token":
                # The `device_code` expired, and the process needs to restart.
                print("The device code has expired. Please run `login` again.")
            elif error == "access_denied":
                # The user cancelled the process. Stop polling.
                print("Login cancelled by user.")
                return
            else:
                print(response)
                return
        else:
            return access_token
