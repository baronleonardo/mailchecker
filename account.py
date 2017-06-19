import sys
from sys_keyring import MailChecker_Keyring
from settings import MailChecker_AccountSettings

class MailChecker_AccountsManagerData():
    nickname = ""
    email_address = ""
    password = ""
    imap = ""
    mailbox = "",
    timeout = -1

    def __init__(self,
                 nickname: str,
                 email_address: str,
                 password: str,
                 imap: str,
                 mailbox: str = 'index',
                 timeout: int = 10):
        self.nickname = nickname
        self.email_address = email_address
        self.password = password
        self.imap = imap
        self.mailbox = mailbox
        self.timeout = timeout


class MailChecker_AccountsManager():
    def __init__(self, app_name: str):
        self.__account_settings = MailChecker_AccountSettings()
        self.__keyring = MailChecker_Keyring(app_name)

    def add_account(self,
                    nickname: str,
                    email_address: str,
                    password: str,
                    imap: str,
                    mailbox: str = 'index',
                    timeout: int = 10):

        if self.__account_settings.exits(nickname):
            print("An account already exists with the same `nickname` %s" % nickname,
                  file=sys.stderr)
            return False

        # create first in `accounts.ini`
        self.__account_settings.create(nickname, email_address, imap, mailbox, timeout)
        # create the password in the keyring
        self.__keyring.add_account(nickname, password)

    def delete_account(self, nickname: str) -> bool:
        if self.__account_settings.remove(nickname):
            if self.__keyring.delete_account(nickname):
                return True

        return False

    def update_account(self,
                       nickname: str,
                       new_email: str = "",
                       new_password: str = "",
                       new_imap: str = "",
                       new_mailbox: str = "",
                       new_timeout: int = -1):
        if self.__account_settings.update(nickname, new_email, new_imap, new_mailbox, new_timeout):
            if new_password != "":
                if self.__keyring.update_account(nickname, new_password):
                    return True
                else:
                    return False
        else:
            return False

    def get_account_data(self, nickname) -> dict:
        account = self.__account_settings.read_email_data(nickname)
        # convert timeout into integer
        account['timeout'] = int(account['timeout'])
        account['password'] = self.__keyring.get_account_password(nickname)

        return account

    def get_all_accounts_data(self) -> list:
        data = []
        for nickname in self.__account_settings.list_nicknames():
            data.append(self.get_account_data(nickname))

        return data

    def get_all_accounts_nicknames(self) -> list:
        return self.__account_settings.list_nicknames()

    def check_account_existance(self, nickname) -> bool:
        if self.__account_settings.exits(nickname):
            return True

        return False


if __name__ == "__main__":
    manager = MailChecker_AccountsManager("mailchecker")
    manager.add_account("test", "mohamedayman.fcis@zoho.com", "0121314", "imap.zoho.com")
    manager.update_account("test", new_password="meandme")
    print(manager.get_account_data("test"))
    print(manager.check_account_existance("test"))
    print(manager.get_all_accounts_data())
    # manager.delete_account("test")
