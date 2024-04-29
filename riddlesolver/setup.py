import os
import winreg


def update_path_mac():
    # Get the installation directory
    install_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Update the PATH environment variable
    path = os.environ.get('PATH', '')
    if install_dir not in path:
        os.environ['PATH'] = f"{install_dir}:{path}"


def update_path_windows():
    # Get the installation directory
    install_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Update the PATH environment variable
    path_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
    path = winreg.QueryValueEx(path_key, 'PATH')[0]
    if install_dir not in path:
        winreg.SetValueEx(path_key, 'PATH', 0, winreg.REG_EXPAND_SZ, f"{install_dir};{path}")
    winreg.CloseKey(path_key)
