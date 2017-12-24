import keyring
import sys

class MailChecker_Keyring():
    def __init__(self, section_name):
        self.__keyring = None
        self.__section_name = section_name
        self.__identify_keyring()

    def __identify_keyring(self):
        # identify the system
        if sys.platform == 'linux':
            kwallet = None
            gnome_keyring = None
            for __keyring in keyring.backend.get_all_keyring():
                if __keyring.name.find('kwallet') != -1:
                    kwallet = __keyring
                # This is gnome keyring
                elif __keyring.name.find('SecretService') != -1:
                    gnome_keyring = __keyring

            if kwallet != None:
                keyring.set_keyring(kwallet)
                self.__keyring = kwallet
            elif gnome_keyring != None:
                keyring.set_keyring(gnome_keyring)
                self.__keyring = gnome_keyring
            else:
                print("Unsupported keyring", file=sys.stderr)
        else:
            print("Unsupported keyring", file=sys.stderr)

    def __check_availability(self, account_name=None):
        if self.__keyring is False:
            print("Can not find a keyring. You may need to open one.", file=sys.stderr)
            return False

        if account_name != None:
            if keyring.get_password(self.__section_name, account_name) is None:
                print("wrong account_name or the keyring is close. you may need to open it first",
                      file=sys.stderr)
                return False

    def add_account(self, account_name, password) -> bool:
        if self.__check_availability() is False:
            return False

        if self.__keyring.set_password(self.__section_name, account_name, password) is False:
            print("Can not write into keyring. You may need to open it.", file=sys.stderr)
            return False

        return True

    def update_account(self, account_name, new_password) -> bool:
        if self.__check_availability(account_name) is False:
            return False

        self.add_account(account_name, new_password)

        return True

    def delete_account(self, account_name) -> bool:
        if self.__check_availability(account_name) is False:
            return False

        keyring.delete_password(self.__section_name, account_name)
        return True

    def get_account_password(self, account_name) -> str:
        if self.__check_availability() is False:
            return False

        password = keyring.get_password(self.__section_name, account_name)

        if password is None:
            print("wrong account_name or the keyring is close. you may need to open it first",
                  file=sys.stderr)
            return ''

        return password

if __name__ == "__main__":
    __keyring = MailChecker_Keyring("mailchecker")
    __keyring.add_account("mohamedayman.fcis@gmail.com", "KFC")
    __keyring.update_account("mohamedayman.fcis@gmail.com", "Adel")
    print(__keyring.get_account_password("mohamedayman.fcis@gmail.com"))
    __keyring.delete_account("mohamedayman.fcis@gmail.com")
