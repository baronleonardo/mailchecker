import os, sys
import webbrowser
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtCore import pyqtSignal, pyqtSlot

class UIAccountSettings(QDialog):
    # mailBox name
    # email
    # password
    # imap
    # timer
    newEmailAdded = pyqtSignal(str, str, str, str, str, int)

    CURR_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))

    def __init__(self, parent=None):
        super(UIAccountSettings, self).__init__(parent)
        self.ui_settings = uic.loadUi("%s/%s" % (self.CURR_PATH, 'email_settings.ui'), self)

        # hint button
        self.ui_settings.hintBtn.clicked.connect(self.__open_link)
        self.ui_settings.hintBtn.setToolTip("If you fail to load your gmail account,\n"
                                            "Check this link out:\n"
                                            "https://support.google.com/mail/answer/78754")
        self.ui_settings.buttonBox.accepted.connect(self.__on_acceptedBtn_clicked)

    def __open_link(self):
        url = "https://support.google.com/mail/answer/78754"
        webbrowser.open(url, new=0, autoraise=True)

    def update_data(self,
                    mailBox_name: str = "",
                    email: str = "",
                    password: str = "",
                    imap: str = "",
                    timer_value: int = 15):
        self.ui_settings.mailBoxName_lineEdit.setText(mailBox_name)
        self.ui_settings.email_lineEdit.setText(email)
        self.ui_settings.password_lineEdit.setText(password)
        self.ui_settings.imap_lineEdit.setText(imap)
        self.ui_settings.timer_spinBox.setValue(timer_value)


    @pyqtSlot()
    def __on_acceptedBtn_clicked(self):
        # mailBox name
        # email
        # password
        # imap
        # timer
        self.ui_settings.newEmailAdded.emit(self.ui_settings.mailBoxName_lineEdit.text(),
                                            self.ui_settings.email_lineEdit.text(),
                                            self.ui_settings.password_lineEdit.text(),
                                            self.ui_settings.imap_lineEdit.text(),
                                            'inbox',
                                            self.ui_settings.timer_spinBox.value())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UIAccountSettings()
    window.show()
    sys.exit(app.exec())
