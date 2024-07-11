import pystray
import requests
import hashlib
import json
import configparser
from PIL import Image
from io import BytesIO
from pathlib import Path


class GitAccount:
    name: str
    email: str
    friendly_name: str

    def __init__(self, name: str, email: str, friendly_name: str):
        self.name = name
        self.email = email
        self.friendly_name = friendly_name


with open("config.json", "r", encoding="utf-8") as f:
    gitAccounts = [GitAccount(**account) for account in json.load(f)]

icon = pystray.Icon("GitConfig Switcher")
checked_items = set()


def load_image_from_url(email):
    email_encoded = email.lower().encode("utf-8")
    email_hash = hashlib.sha256(email_encoded).hexdigest()

    response = requests.get(f"https://www.gravatar.com/avatar/{email_hash}?s=64")
    image_data = BytesIO(response.content)
    return Image.open(image_data)


def read_gitconfig():
    config = configparser.ConfigParser()
    config.read(f"{Path.home()}/.gitconfig")

    gitconfig_data = {}
    for section in config.sections():
        gitconfig_data[section] = {}
        for key, value in config.items(section):
            gitconfig_data[section][key] = value

    return gitconfig_data


def write_gitconfig(gitconfig_data):
    config = configparser.ConfigParser()

    for section, values in gitconfig_data.items():
        config[section] = values

    with open(f"{Path.home()}/.gitconfig", "w") as configfile:
        config.write(configfile)


def on_action(icon, item):
    if item not in checked_items:
        checked_items.clear()
        checked_items.add(item)

    gitConfig = read_gitconfig()

    for account in gitAccounts:
        if account.friendly_name == item.text:
            gitConfig["user"]["email"] = account.email
            gitConfig["user"]["name"] = account.name

    icon.icon = load_image_from_url(gitConfig["user"]["email"])

    write_gitconfig(gitConfig)


def on_exit(icon, item):
    icon.stop()


def main():
    gitConfig = read_gitconfig()
    menu = []

    for account in gitAccounts:
        item = pystray.MenuItem(
            f"{account.friendly_name}", on_action, lambda item: item in checked_items
        )
        if account.email == gitConfig["user"]["email"]:
            checked_items.add(item)
        menu.append(item)

    icon.icon = load_image_from_url(gitConfig["user"]["email"])
    icon.menu = pystray.Menu(*tuple(menu), pystray.MenuItem("Exit", on_exit))

    icon.run()


main()
