import keyboard
import json
import configparser

from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 

from pathlib import Path

from core.models.git_account import GitAccount


class GitConfigSwitcherApp:

    def _on_systray_unavailable(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "Systray", "System tray is not available.")
            exit(1)

    def _gitaccounts_load(self) -> list:
        with open(f"{Path.home()}/.gitswitcher", "r", encoding="utf-8") as f:
            return [GitAccount(**element) for element in json.load(f)]

    def _read_gitconfig(self):
        config = configparser.ConfigParser()
        config.read(f"{Path.home()}/.gitconfig")

        gitconfig_data = {}
        for section in config.sections():
            gitconfig_data[section] = {}
            for key, value in config.items(section):
                gitconfig_data[section][key] = value

        return gitconfig_data

    def _write_gitconfig(self, gitconfig_data):
        config = configparser.ConfigParser()

        for section, values in gitconfig_data.items():
            config[section] = values

        with open(f"{Path.home()}/.gitconfig", "w") as configfile:
            config.write(configfile)   

    def _raise_notification(self, title, message):
        self.tray.showMessage(title, message, QIcon("core/images/default.png"), 1000)

    def _menu_settings_action(self):
        self._raise_notification("Error", "Under development!")

    def _gitaccount_switch(self, index=None):
        # TODO: Refactor this shit
        if index == None:
            index = self.global_index + 1
        self.global_index = index
        if self.global_index >= len(self.accounts):
            self.global_index = 0

        for action in self.menu.actions():
            if action.objectName() == self.accounts[self.global_index].name:
                action.setChecked(True)

        gconfig = self._read_gitconfig()
        gconfig['user']['email'] = self.accounts[self.global_index].email
        gconfig['user']['name'] = self.accounts[self.global_index].gitname
        self._write_gitconfig(gconfig)

        self._raise_notification("Git Switch", f"Account swithced to {self.accounts[self.global_index].name}")

    def _menu_init(self) -> QMenu:
        menu = QMenu("Menu")

        ag = QActionGroup(self.app)
        ag.setExclusive(True)

        for idx, account in enumerate(self.accounts):
            account.qAction = QAction(account.name)
            account.qAction.setObjectName(account.name)
            account.qAction.setCheckable(True)
            account.qAction.triggered.connect(lambda checked, index=idx: self._gitaccount_switch(index))
            menu.addAction(ag.addAction(account.qAction))

        menu.addSeparator()
        menu.settings_option = QAction("Settings")
        menu.settings_option.triggered.connect(self._menu_settings_action)
        menu.addAction(menu.settings_option)

        menu.addSeparator()
        menu.quit_option = QAction("Quit")
        menu.quit_option.triggered.connect(self.app.quit)
        menu.addAction(menu.quit_option)

        return menu

    def _tray_init(self) -> QSystemTrayIcon:
        tray = QSystemTrayIcon() 
        tray.setIcon(QIcon("core/images/default.png")) 
        tray.setVisible(True)

        return tray

    def __init__(self) -> None:
        self.app = QApplication([])
        self.app.setQuitOnLastWindowClosed(False)

        self.global_index = 0

        self._on_systray_unavailable()
        self.tray = self._tray_init()

        self.accounts = self._gitaccounts_load()
        self.menu = self._menu_init()
        self.tray.setContextMenu(self.menu)

        self.hotkey = keyboard.add_hotkey("alt+h", self._gitaccount_switch, suppress=True)
        
    def run(self):
        # Enter Qt application main loop
        self.app.exec_()
        exit()     

app = GitConfigSwitcherApp()
app.run()   