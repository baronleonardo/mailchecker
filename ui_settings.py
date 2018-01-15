from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QTableWidgetItem, QTableWidget, QMessageBox
from PyQt5.QtGui import QIcon
import os, sys
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from ui_account_settings import UIAccountSettings


class UISettingsData():
    emails_name_list = []
    runOnClickOption = ""
    runOnNewEmailOption = ""
    normalIconPath = ""
    newEmailIconPath = ""
    errorIconPath = ""

    def __init__(self,
                 emails_name_list: list,
                 runOnClickOption: str,
                 runOnNewEmailOption: str,
                 normalIconPath: str,
                 newEmailIconPath: str,
                 errorIconPath: str):
        self.emails_name_list = emails_name_list
        self.runOnClickOption = runOnClickOption
        self.runOnNewEmailOption = runOnNewEmailOption
        self.normalIconPath = normalIconPath
        self.newEmailIconPath = newEmailIconPath
        self.errorIconPath = errorIconPath


class UISettings(QDialog):
    # These signals fired after the `close` button clicked
    runOnClickOptionChanged = pyqtSignal(str)
    runOnNewEmailOptionChanged = pyqtSignal(str)
    normalIconChanged = pyqtSignal(str)
    newEmailIconChanged = pyqtSignal(str)
    errorIconChanged = pyqtSignal(str)

    # this signal is like the one inside `UIAccountSettings` class
    newEmailAdded = pyqtSignal(str, str, str, str, str, int)
    emailRemoved = pyqtSignal(str)

    # fire a signal after settings dialog closed
    signalDialogClosed = pyqtSignal()

    CURR_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

    def __init__(self, ui_data: UISettingsData, parent=None):
        # check for `ui_data` type
        if isinstance(ui_data, UISettingsData) is False:
            print("`ui_data` does not has `UISettingsData` type.", file=sys.stderr)
            sys.exit(1)

        super(UISettings, self).__init__(parent)
        self.ui_settings = uic.loadUi("%s/%s" % (self.CURR_PATH, 'settings.ui'), self)
        self.__prepare_signals_and_slots()

        # prepare a dictionary to hold settings
        self.__options = {
            "runOnClickOption_Changed": {"signal": self.runOnClickOptionChanged,
                                         "value": ui_data.runOnClickOption,
                                         "get_value": self.ui_settings.runOnClick.text,
                                         "state": False},
            "runOnNewEmailOption_Changed": {"signal": self.runOnNewEmailOptionChanged,
                                            "value": ui_data.runOnNewEmailOption,
                                            "get_value": self.ui_settings.runOnNewEmails.text,
                                            "state": False},
            "normalIcon_Changed": {"signal": self.normalIconChanged,
                                   "value": ui_data.normalIconPath,
                                   "set_value": self.ui_settings.normalIcon.setIcon,
                                   "state": False},
            "newEmailIcon_Changed": {"signal": self.newEmailIconChanged,
                                     "value": ui_data.newEmailIconPath,
                                     "set_value": self.ui_settings.newEmailIcon.setIcon,
                                     "state": False},
            "errorIcon_Changed": {"signal": self.errorIconChanged,
                                  "value": ui_data.errorIconPath,
                                  "set_value": self.ui_settings.errorIcon.setIcon,
                                  "state": False},
        }

        # set data to the ui
        if ui_data.emails_name_list:
            for emails_name in ui_data.emails_name_list:
                self.ui_settings.emailsTable.append(emails_name)
        self.ui_settings.runOnClick.setText(ui_data.runOnClickOption)
        self.ui_settings.runOnNewEmails.setText(ui_data.runOnNewEmailOption)
        self.ui_settings.normalIcon.setIcon(QIcon(ui_data.normalIconPath))
        self.ui_settings.newEmailIcon.setIcon(QIcon(ui_data.newEmailIconPath))
        self.ui_settings.errorIcon.setIcon(QIcon(ui_data.errorIconPath))

        # set the first email as the selected one
        self.ui_settings.emailsTable.setCurrentCell(0, 0)

    @pyqtSlot(str)
    def __updateOption(self, option: str):
        """
        This change state of an option in `__options`
        """
        # update the `value` content if 'get_value' exists
        try:
            self.__options[option]['value'] = self.__options[option]['get_value']()
        except KeyError:
            pass

        self.__options[option]['state'] = True

    @pyqtSlot(str)
    def __choose_new_icon_dialog(self, option: str):
        icon_name, _ = QFileDialog.getOpenFileName(self,
                                                   "choose new icon",
                                                   "%s/%s" % (self.CURR_PATH, "icons"),
                                                   "Image Files (*.png *.jpg *.bmp *.svg)")
        if icon_name != "":
            self.__options[option]['set_value'](QIcon(icon_name))
            self.__options[option]['value'] = icon_name
            self.__updateOption(option)

    def __prepare_signals_and_slots(self):
        # signal for options changed
        self.ui_settings.runOnClick.textChanged.connect(
            lambda: self.__updateOption("runOnClickOption_Changed"))
        self.ui_settings.runOnNewEmails.textChanged.connect(
            lambda: self.__updateOption("runOnNewEmailOption_Changed"))
        self.ui_settings.normalIcon.clicked.connect(
            lambda: self.__choose_new_icon_dialog("normalIcon_Changed"))
        self.ui_settings.newEmailIcon.clicked.connect(
            lambda: self.__choose_new_icon_dialog("newEmailIcon_Changed"))
        self.ui_settings.errorIcon.clicked.connect(
            lambda: self.__choose_new_icon_dialog("errorIcon_Changed"))
        # on close button clicked
        self.ui_settings.closeBtn.clicked.connect(self.__on_closeBtn_clicked)
        # on add button clicked
        self.ui_settings.addEmailBtn.clicked.connect(self.__on_addEmailBtn_clicked)
        # on remove button clicked
        self.ui_settings.removeEmailBtn.clicked.connect(self.__on_removeEmailBtn_clicked)
        # on settings dialog closed
        self.ui_settings.finished.connect(self.signalDialogClosed.emit)

    @pyqtSlot()
    def __on_closeBtn_clicked(self):
        for value in self.__options.values():
            if value['state'] is True:
                value['signal']['QString'].emit(value['value'])
                value['state'] = False

    @pyqtSlot()
    def __on_addEmailBtn_clicked(self):
        # add new email dialog
        account_settings = UIAccountSettings(self)
        account_settings.newEmailAdded.connect(self.__on_newEmailAdded)
        account_settings.show()

    @pyqtSlot()
    def __on_removeEmailBtn_clicked(self):
        emailToBeRemoved_index = self.ui_settings.emailsTable.currentRow()
        emailToBeRemoved = self.ui_settings.emailsTable.currentItem().text()
        result = QMessageBox.warning(self,
                                     "Removing an email",
                                     "Are you sure about removing this email ?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if result == QMessageBox.Yes:
            self.ui_settings.emailsTable.removeRow(emailToBeRemoved_index)
            self.emailRemoved.emit(emailToBeRemoved)

    @pyqtSlot(str, str, str, str, str, int)
    def __on_newEmailAdded(self,
                           email_name: str,
                           email_address: str,
                           password: str,
                           imap: str,
                           mailbox: str,
                           timer_value: int):
        self.newEmailAdded.emit(email_name, email_address, password, imap, mailbox, timer_value)
        # add the email name to the table
        self.ui_settings.emailsTable.append(email_name)


class QEmailsNameTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super(QEmailsNameTableWidget, self).__init__(parent)

    def append(self, email_name: str):
        """
        append a new item (new email_name) into the list
        """
        # increment rows by 1
        self.setRowCount(self.rowCount() + 1)
        # There is only one column, column 0
        self.setItem(self.rowCount() - 1, 0, QTableWidgetItem(email_name))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    data = UISettingsData(['Gmail', 'Zoho', 'Yahoo'],
                          "geary",
                          "",
                          "/run/media/leo-0/LEO/Projects/mailchecker/indicator-messages-red.png",
                          "/run/media/leo-0/LEO/Projects/mailchecker/indicator-messages-red.png",
                          "/run/media/leo-0/LEO/Projects/mailchecker/indicator-messages-red.png")
    window = UISettings(data)
    window.show()
    sys.exit(app.exec())
