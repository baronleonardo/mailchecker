import sys
import threading
from email import EMail
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot
from ui_trayicon import MailChecker_UI_TrayIcon
from ui_settings import UISettings, UISettingsData
from account import MailChecker_AccountsManager
from settings import MailChecker_Settings
from settings import MailChecker_Settings_Options

class MailChecker(QObject):
    """
    TODO: put them in database or so
    TODO: encrypt data
    """
    APP_NAME = "mailchecker"

    def __init__(self, parent=None):
        super(MailChecker, self).__init__(parent)

        self.account_manager = MailChecker_AccountsManager(self.APP_NAME)
        self.settings = MailChecker_Settings()

        if self.settings.check_existance() is False:
            self.settings.create()

        self.ui_settings = None
        # this will be a list of dictionary
        # it will hold email_name and timer object for that email
        self.accounts = []

        self.__tray_icon = None

    @pyqtSlot(int)
    def __on_timeout(self, account_index: int):

        # if there troubles in connection, then change the state to `ERROR`
        if self.accounts[account_index]['email_obj'].connect() is False:
            self.__tray_icon.change_state(self.__tray_icon.States.ERROR)

        print("checking %s..." % self.accounts[account_index]['email_name'])
        new_emails_count = self.accounts[account_index]['email_obj'].get_mail_count(True)
        self.accounts[account_index]['unread_emails'] = new_emails_count

        # disconnect
        self.accounts[account_index]['email_obj'].disconnect()

        if new_emails_count >= self.__tray_icon.States.NEW.value:
            self.__tray_icon.change_state(self.__tray_icon.States.NEW)
        elif new_emails_count == -1:
            self.__tray_icon.change_state(self.__tray_icon.States.ERROR)
        else:
            accounts_has_new_emails = False
            for account in self.accounts:
                if account['unread_emails'] != 0:
                    accounts_has_new_emails = True

            if accounts_has_new_emails is False:
                self.__tray_icon.change_state(self.__tray_icon.States.NORMAL)

        self.__config_tooltip()

    def __config_tooltip(self):
        tooltip = ""
        for account in self.accounts:
            tooltip += "%5s: %i emails\r\n" % (account['email_name'], account['unread_emails'])
        self.__tray_icon.setToolTip(tooltip)

    @pyqtSlot()
    def __show_settings_dialog(self):
        ui_settings_data = UISettingsData(self.account_manager.get_all_accounts_nicknames(),
                                          self.settings.read(
                                              MailChecker_Settings_Options.on_click),
                                          self.settings.read(
                                              MailChecker_Settings_Options.on_new_email),
                                          self.settings.read(
                                              MailChecker_Settings_Options.icon_normal),
                                          self.settings.read(
                                              MailChecker_Settings_Options.icon_new_email),
                                          self.settings.read(
                                              MailChecker_Settings_Options.icon_error))
        self.ui_settings = UISettings(ui_settings_data)

        # signals
        self.__signals_control(True)

        self.ui_settings.show()

    def __signals_control(self, connect_signals: bool):
        if connect_signals:
            self.ui_settings.runOnClickOptionChanged.connect(
                lambda newVal: self.settings.update(MailChecker_Settings_Options.on_click,
                                                    newVal))
            self.ui_settings.runOnNewEmailOptionChanged.connect(
                lambda newVal: self.settings.update(MailChecker_Settings_Options.on_new_email,
                                                    newVal))
            self.ui_settings.normalIconChanged.connect(
                lambda newVal: self.settings.update(MailChecker_Settings_Options.icon_normal,
                                                    newVal))
            self.ui_settings.newEmailIconChanged.connect(
                lambda newVal: self.settings.update(MailChecker_Settings_Options.icon_new_email,
                                                    newVal))
            self.ui_settings.errorIconChanged.connect(
                lambda newVal: self.settings.update(MailChecker_Settings_Options.icon_error,
                                                    newVal))
            self.ui_settings.newEmailAdded.connect(self.__onNewEmailAdded)
            self.ui_settings.emailRemoved.connect(self.__onEmailRemoved)
            self.ui_settings.signalDialogClosed.connect(self.__on_settings_dialog_closed)
        else:
            self.ui_settings.runOnClickOptionChanged.disconnect()
            self.ui_settings.runOnNewEmailOptionChanged.disconnect()
            self.ui_settings.normalIconChanged.disconnect()
            self.ui_settings.newEmailIconChanged.disconnect()
            self.ui_settings.errorIconChanged.disconnect()
            self.ui_settings.newEmailAdded.disconnect()
            self.ui_settings.emailRemoved.disconnect()
            self.ui_settings.signalDialogClosed.disconnect()

    def __activate_account(self,
                           email_name: str,
                           email_address: str,
                           password: str,
                           imap: str,
                           mailbox: str,
                           timer_value: int):
        self.accounts.append({'email_name': email_name,
                              'unread_emails': 0,
                              'email_obj': EMail(email_address, password, imap, mailbox),
                              'timer': QTimer(self)})
        account_index = len(self.accounts) - 1

        # configure the timer
        timer = self.accounts[account_index]['timer']
        # the slot will create a new thread for each account
        # This help in increasing responsiveness for the program
        timer.timeout.connect(lambda: threading.Thread(target=self.__on_timeout,
                                                       args=[account_index],
                                                       daemon=True).start())
        timer.start(timer_value * 60 * 1000)

    def __check_all_accounts_for_new_emails(self):
        for iii in range(len(self.accounts)):
            self.__on_timeout(iii)

    @pyqtSlot(str, str, str, str, str, int)
    def __onNewEmailAdded(self,
                          email_name: str,
                          email: str,
                          password: str,
                          imap: str,
                          mailbox: str,
                          timer_value: int):
        self.account_manager.add_account(email_name,
                                         email,
                                         password,
                                         imap,
                                         mailbox,
                                         timer_value)

        self.__activate_account(email_name, email, password, imap, mailbox, timer_value)

    @pyqtSlot(str)
    def __onEmailRemoved(self, email_name):
        self.account_manager.delete_account(email_name)
        account = next(account for account in self.accounts if account['email_name'])
        timer = account['timer']
        # disconnect the timer
        timer.timeout.disconnect()

    @pyqtSlot()
    def __on_settings_dialog_closed(self):
        self.__signals_control(False)

    def exec(self):
        """
        start the mailchecker
        """
        app = QApplication(sys.argv)

        self.__tray_icon = MailChecker_UI_TrayIcon(app.quit,
                                                   self.__check_all_accounts_for_new_emails,
                                                   self. __show_settings_dialog)
        # TODO: find a better way
        self.__tray_icon.set_onLeftClick_action(
            self.settings.read(MailChecker_Settings_Options.on_click))

        accounts_data = self.account_manager.get_all_accounts_data()

        if accounts_data:
            for account_data in accounts_data:
                # email_address: str, password: str, imap: str, mailbox: str
                self.__activate_account(account_data['nickname'],
                                        account_data['email_address'],
                                        account_data['password'],
                                        account_data['imap'],
                                        account_data['mailbox'],
                                        account_data['timeout'])

        self.__tray_icon.show()

        app.exec_()


if __name__ == '__main__':
    mail_checker = MailChecker()
    mail_checker.exec()
