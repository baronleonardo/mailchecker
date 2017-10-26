import configparser
import os, sys
from enum import Enum

class MailChecker_Settings_Options(Enum):
    icon_normal = 'icon_normal'
    icon_new_email = 'icon_new_email'
    icon_error = 'icon_error'
    on_click = 'on_click'
    on_new_email = 'on_new_email'

class MailChecker_Settings():

    __SETTINGS_FILENAME = "mail_checker.ini"
    __CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    __SETTINGS_FILE = os.path.join(__CURRENT_PATH, __SETTINGS_FILENAME)

    __SETTINGS_SECTION = 'Settings'
    __SETTINGS_TEMPLATE = {'icon_normal': 'icons/Dark_Theme/indicator-messages.svg',
                           'icon_new_email': 'icons/Dark_Theme/indicator-messages-new.svg',
                           'icon_error': 'icons/Dark_Theme/indicator-messages-error.svg',
                           'on_click': '',
                           'on_new_email': ''}

    def __init__(self):
        self.__settings = configparser.ConfigParser()

    def create(self) -> bool:
        self.__settings.read(self.__SETTINGS_FILE)

        if self.__settings.has_section(self.__SETTINGS_SECTION) is False:
            print("create a `settings` file")
            self. __settings[self.__SETTINGS_SECTION] = self.__SETTINGS_TEMPLATE

            with open(self.__SETTINGS_FILE, 'w') as __settings_file:
                self.__settings.write(__settings_file)
            return True
        else:
            return False

    def update(self, option: MailChecker_Settings_Options, value: str) -> bool:
        self.__settings.read(self.__SETTINGS_FILE)

        if type(option) != MailChecker_Settings_Options:
            print("`option` parameter has wrong type", file=sys.stderr)
            return False

        if self.__settings.has_section(self.__SETTINGS_SECTION) is False:
            print("No section `%s` found. you may be need to create it first." %
                  self.__SETTINGS_SECTION, file=sys.stderr)
            return False

        self.__settings.set(self.__SETTINGS_SECTION, option.value, value)
        with open(self.__SETTINGS_FILE, 'w') as __settings_file:
            self.__settings.write(__settings_file)

        return True

    def read(self, option: MailChecker_Settings_Options) -> str:
        self.__settings.read(self.__SETTINGS_FILE)

        if self.__settings.has_section(self.__SETTINGS_SECTION) is False:
            print("No section `%s` found. you may be need to create it first." %
                  self.__SETTINGS_SECTION, file=sys.stderr)
            return ""

        return self.__settings[self.__SETTINGS_SECTION][option.value]

    def check_existance(self) -> bool:
        if os.path.isfile(self.__SETTINGS_FILE) is False:
            return False


class MailChecker_AccountSettings_Options(Enum):
    nickname = 'nickname'
    email_address = 'email_address'
    imap = 'imap'
    mailbox = 'mailbox'
    timeout = 'timeout'

class MailChecker_AccountSettings():

    __EMAIL_SETTINGS_FILENAME = "accounts.ini"
    __CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    __EMAIL_SETTINGS_FILE = os.path.join(__CURRENT_PATH, __EMAIL_SETTINGS_FILENAME)

    __EMAIL_SETTINGS_TEMPLATE = {'nickname': '',
                                 'email_address': '',
                                 'imap': '',
                                 'mailbox': '',
                                 'timeout': ''}

    def __init__(self):
        self.__email_settings = configparser.ConfigParser()

    def create(self,
               nickname: str,
               email_address: str,
               imap: str,
               mailbox: str = 'inbox',
               timeout: int = 10):
        self.__email_settings.read(self.__EMAIL_SETTINGS_FILE)

        if self.__email_settings.has_section(nickname) is False:
            print("create a new account")

            new_email_settings = self.__EMAIL_SETTINGS_TEMPLATE
            new_email_settings['nickname'] = nickname
            new_email_settings['email_address'] = email_address
            new_email_settings['imap'] = imap
            new_email_settings['mailbox'] = mailbox
            new_email_settings['timeout'] = str(timeout)
            self. __email_settings[nickname] = new_email_settings

            with open(self.__EMAIL_SETTINGS_FILE, 'w+') as __email_settings_file:
                self.__email_settings.write(__email_settings_file)

        else:
            self.update(nickname, email_address, imap, mailbox, timeout)

    def exits(self, nickname: str) -> bool:
        if self.__email_settings.has_section(nickname) is False:
            return False
        else:
            return True

    def update(self,
               nickname: str,
               email_address: str = "",
               imap: str = "",
               mailbox: str = "",
               timeout: int = -1) -> bool:
        self.__email_settings.read(self.__EMAIL_SETTINGS_FILE)

        if self.__email_settings.has_section(nickname) is False:
            return False

        if email_address != "":
            self.__email_settings.set(nickname, 'email_address', email_address)

        if imap != "":
            self.__email_settings.set(nickname, 'imap', imap)

        if mailbox != "":
            self.__email_settings.set(nickname, 'mailbox', mailbox)

        if timeout != -1:
            self.__email_settings.set(nickname, 'timeout', str(timeout))

        with open(self.__EMAIL_SETTINGS_FILE, 'w+') as __email_settings_file:
            self.__email_settings.write(__email_settings_file)

        return True

    def remove(self, nickname: str) -> bool:
        self.__email_settings.read(self.__EMAIL_SETTINGS_FILE)

        if self.__email_settings.has_section(nickname) is False:
            return False

        self.__email_settings.remove_section(nickname)

        with open(self.__EMAIL_SETTINGS_FILE, 'w+') as __email_settings_file:
            self.__email_settings.write(__email_settings_file)

        return True

    def read(self, nickname, option: MailChecker_AccountSettings_Options) -> str:
        self.__email_settings.read(self.__EMAIL_SETTINGS_FILE)

        if self.__email_settings.has_section(nickname) is False:
            return ''

        if type(option) != MailChecker_AccountSettings_Options:
            print("`option` parameter has wrong type", file=sys.stderr)
            return ''

        return self.__email_settings[nickname][option.value]

    def read_email_data(self, nickname) -> dict:
        self.__email_settings.read(self.__EMAIL_SETTINGS_FILE)

        if self.__email_settings.has_section(nickname) is False:
            return ''

        return dict(self.__email_settings.items(nickname))

    def list_nicknames(self):
        self.__email_settings.read(self.__EMAIL_SETTINGS_FILE)
        return self.__email_settings.sections()

if __name__ == "__main__":
    config = MailChecker_AccountSettings()
    config.create('test', 'mohamedayman.fcis@zoho.com', 'imap.zoho.com', 'inbox', 10)
    config.create('test2', 'mohamedayman.fcis@zoho.com', 'imap.zoho.com', 'inbox', 100)
    print(config.read_email_data(config.list_nicknames())[0])
