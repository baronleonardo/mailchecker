import sys
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, pyqtSignal
import subprocess
from enum import Enum

class MailChecker_UI_TrayIcon(QSystemTrayIcon):
    """
    `on_quit_action`, `on_update_action` both are like pointer of functions
    to be used on the right click menu
    """

    States = Enum('States', {'NORMAL': 0, 'NEW': 1, 'ERROR': 3})

    __activated = pyqtSignal(QSystemTrayIcon.ActivationReason, str)

    def __init__(self, on_quit_action, on_update_action, on_settings_action, parent=None):
        super(MailChecker_UI_TrayIcon, self).__init__(parent)

        # Icons
        self.normal_icon = QIcon.fromTheme("indicator-messages")
        self.new_emails_icon = QIcon.fromTheme("indicator-messages-red")
        self.error_icon = QIcon.fromTheme("indicator-messages-red")

        # set icon for the initial state
        self.setIcon(self.normal_icon)
        self.current_state = self.States.NORMAL

        menu = MailChecker_RightClickMenu(on_quit_action, on_update_action, on_settings_action)

        self.setContextMenu(menu)

    def set_onLeftClick_action(self, on_click):
        if on_click:
            # try to disconnect if it's already connected
            try:
                self.__activated.disconnect()
            except TypeError:
                pass

            super(MailChecker_UI_TrayIcon, self).activated.connect(
                lambda activationReason: self.__activated.emit(activationReason, on_click))
            self.__activated.connect(self.__on_click)

    @pyqtSlot(QSystemTrayIcon.ActivationReason, str)
    def __on_click(self, activation_reason, action: str):
        """
        on trayicon clicked
        """
        # left click
        if activation_reason == QSystemTrayIcon.Trigger:
            # run a program on click as a daemon process
            subprocess.Popen([action])

    def change_icon(self, state: States, new_icon: str):
        if isinstance(state, self.States) is False:
            print("Wrong state type", file=sys.stderr)
            return

        if state == self.States.NORMAL:
            self.normal_icon = new_icon
        elif state == self.States.NEW:
            self.new_emails_icon = new_icon
        elif state == self.States.ERROR:
            self.error_icon = new_icon

        # change current icon if `state` is the current state
        if self.current_state == state:
            self.setIcon(new_icon)

    def change_state(self, state: States):
        if state == self.States.NORMAL:
            self.setIcon(self.normal_icon)
            # self.setToolTip("0 emails")
        elif state == self.States.NEW:
            self.setIcon(self.new_emails_icon)
            # self.setToolTip("%s emails" % str(new_emails))
        elif state == self.States.ERROR:
            self.setIcon(self.error_icon)
            # self.setToolTip("Error!")


class MailChecker_RightClickMenu(QMenu):
    """
    right click menu for the mail checker
    """

    def __init__(self, on_quit_action, on_update_action, on_settings_action, parent=None):
        super(MailChecker_RightClickMenu, self).__init__(parent)

        update_action = QAction("Update", self)
        update_action.triggered.connect(lambda isTriggered: on_update_action())

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(lambda isTriggered: on_settings_action())

        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(lambda isTriggered: on_quit_action())

        self.addAction(update_action)
        self.addAction(settings_action)
        self.addSeparator()
        self.addAction(quit_action)


if __name__ == "__main__":
    def on_quit():
        print("quit")
        sys.exit(0)

    def on_update():
        print("update")

    def on_settings():
        print("settings")

    app = QApplication(sys.argv)
    mail_checker = MailChecker_UI_TrayIcon(on_quit, on_update, on_settings)
    mail_checker.set_onLeftClick_action('kate')
    mail_checker.show()

    sys.exit(app.exec())