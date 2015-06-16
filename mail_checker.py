from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Notify
from tendo.singleton import SingleInstance
import os
import sys
import encrypt
import mail_checker_core
import mail_settings_ui
import settings_ui


class MailChecker:

    # transforms relative path into absolute path
    # because libnotify needs absolute paths for some reason
    current_path = os.path.abspath(os.path.dirname(sys.argv[0])) + "/"
    credentials_file = "credentials"
    settings_file = "settings"
    default_settings_file = "settings_defaults"

    tray_icon = None
    right_clicked_menu = None
    settings_builder = None
    mail_settings_builder = None
    mail_checker_core = None

    mail_account_data = None
    settings_data = None

    notification_icon = "mailIcon.png"

    def __init__(self):
        # Start only one instance from the mail checker
        SingleInstance()
        self.mail_settings_builder = mail_settings_ui.DialogBuilder()

        if self.check_settings_file_existence():
            self.load_settings()
        else:
            self.on_settings_file_not_found()

        if self.check_credentials_file_existence():
            self.load_mail_account()

        else:
            self.on_credentials_file_not_found()

        if (self.mail_account_data and self.settings_data) is not None:
            self.construct()
            # Initiate the timer
            self.mail_checker_core.timer(None, "initiate")

    def construct(self):
        self.tray_icon = self.create_tray_icon()

        self.mail_checker_core = mail_checker_core.Core(self.mail_account_data, self.settings_data, self.tray_icon)
        self.settings_builder = settings_ui.DialogBuilder()

        self.right_clicked_menu = self.create_right_clicked_menu()
        self.initialize_notification_system()
        self.notification_icon = self.current_path + self.notification_icon

    @staticmethod
    def initialize_notification_system():
        # initialize pynotify... "Basics" can be changed to whatever... it
        # doesn't matter.
        if not Notify.init("Basics"):
            sys.exit(1)

    def check_settings_file_existence(self):
        # Check if settings file exists
        f = os.path.exists(self.current_path + self.settings_file)
        if f is False:
            os.system("touch '" + self.current_path + self.settings_file + "'")
            print("settings file not found!")
            return False
        else:
            return True

    def on_settings_file_not_found(self):
        """Load default settings"""
        settings = open(self.current_path + self.settings_file, 'w')
        default = open(self.current_path + self.default_settings_file, 'r')

        settings.write(default.read())

    def load_settings(self):
        print("load settings")

        settings = open(self.current_path + self.settings_file, 'r')
        str_settings = settings.read()

        zero_messages_tray_icon = str_settings.splitlines()[0]
        new_messages_tray_icon = str_settings.splitlines()[1]
        error_tray_icon = str_settings.splitlines()[2]
        action_on_left_click_tray = str_settings.splitlines()[3]
        action_on_new_mail = str_settings.splitlines()[4]

        self.settings_data = dict({"zero_messages_tray_icon": zero_messages_tray_icon,
                                   "new_messages_tray_icon": new_messages_tray_icon,
                                   "error_tray_icon": error_tray_icon,
                                   "action_on_left_click_tray_icon": action_on_left_click_tray,
                                   "action_on_new_mail": action_on_new_mail,
                                   "notification_icon": self.current_path + self.notification_icon})

        settings.close()

    def check_credentials_file_existence(self):
        # Check if mail account file exists
        f = os.path.exists(self.current_path + self.credentials_file)
        if f is False:
            os.system("touch '" + self.current_path + self.credentials_file + "'")
            return False
        else:
            return True

    def on_credentials_file_not_found(self):
        """Show mail settings dialog"""
        self.show_mail_settings()

    def load_mail_account(self):
        credentials = open(self.current_path + "credentials", 'r')
        str_credentials = credentials.read()

        print(str_credentials)

        email = str_credentials.splitlines()[0]
        password = str_credentials.splitlines()[1]
        mailIMAP = str_credentials.splitlines()[2]
        checker_timer = int(str_credentials.splitlines()[3])

        password = encrypt.dencrypt("decrypt", password)

        self.mail_account_data = \
            dict({"email": email, "password": password,
                  "mailIMAP": mailIMAP, "mailbox": "INBOX", "checker_timer_in_minutes": checker_timer})

        credentials.close()

    def create_tray_icon(self):
        """Create tray icon"""
        tray_icon = Gtk.StatusIcon()
        # add a tray icon
        tray_icon.set_from_file(
            self.current_path + self.settings_data["zero_messages_tray_icon"])

        # right click signal and slot
        tray_icon.connect('popup-menu', self.on_right_click_tray_icon)
        # left click signal and slot
        tray_icon.connect('activate', self.on_left_click_tray_icon)

        # TODO: create action when the tray-icon clicked

        return tray_icon

    def create_right_clicked_menu(self):
        """Create right clicked menu"""
        menu = Gtk.Menu()

        check_mail_item = Gtk.MenuItem("Check Mail")
        separator_item = Gtk.SeparatorMenuItem()
        settings_item = Gtk.MenuItem("Settings")
        close_item = Gtk.MenuItem("Close")

        # Append the menu items
        menu.append(check_mail_item)
        menu.append(separator_item)
        menu.append(settings_item)
        menu.append(close_item)

        # add callbacks
        check_mail_item.connect_object("activate", self.mail_checker_core.check_new_mails, "Check Mail")
        settings_item.connect_object("activate", self.show_settings, "Settings")
        close_item.connect_object("activate", self.close_app, "Close")

        # Show the menu items
        menu.show_all()

        return menu

    def on_right_click_tray_icon(self, status_icon, event_button, event_time):
        print("right click")
        # Popup the menu
        self.right_clicked_menu.popup(None, None, None, None, event_button, event_time)

    def on_left_click_tray_icon(self, *args):
        print("left click")
        if self.settings_data["action_on_left_click_tray_icon"] != "":
            # run the command in background and direct the errors to /dev/null black hole
            os.system(self.settings_data["action_on_left_click_tray_icon"]+" 2> /dev/null &")

    def show_mail_settings(self, *args):
        # Construct additional signals
        self.mail_settings_dialog_additional_signals()
        # Show Mail Settings Dialog
        self.mail_settings_builder.show_dialog()

    def show_settings(self, *args):
        # Construct additional signals
        self.settings_dialog_additional_signals()
        # Show Settings Dialog
        self.settings_builder.show_dialog()
        # load emails account
        self.settings_builder.load_mails(self.get_list_of_mails())
        self.settings_builder.load_icons(self.settings_data["zero_messages_tray_icon"],
                                         self.settings_data["new_messages_tray_icon"],
                                         self.settings_data["error_tray_icon"])
        self.settings_builder.load_actions(self.settings_data["action_on_left_click_tray_icon"],
                                           self.settings_data["action_on_new_mail"])

    def mail_settings_dialog_additional_signals(self):
        # Get save Button from Settings dialog
        save_button = self.mail_settings_builder.get_save_button()

        # Reinitialize the timer if save-button is clicked
        if (self.mail_account_data and self.settings_data) is not None:
            save_button.connect('clicked', self.mail_checker_core.timer, 're-initiate')
        save_button.connect('clicked', self.save_new_mail_data)

    def settings_dialog_additional_signals(self):
        close_button = self.settings_builder.get_close_button()
        close_button.connect('clicked', self.save_new_settings)

    @staticmethod
    def encrypt_password(password):
        """"Encrypt Password"""
        password = encrypt.dencrypt("encrypt", password)
        return password

    def save_new_mail_data(self, *args):
        # Get Data from text entries from the mail settings dialog
        email = self.mail_settings_builder.get_builder().get_object('email_entry').get_text()
        password = self.mail_settings_builder.get_builder().get_object('password_entry').get_text()
        imap = self.mail_settings_builder.get_builder().get_object('imap_entry').get_text()
        timer = self.mail_settings_builder.get_builder().get_object('timer_spin').get_value()

        # Encrypt the password
        password = self.encrypt_password(password)

        # Save Email Data
        credentials = open(self.current_path + self.credentials_file, 'w')
        credentials.write(email + "\n")
        credentials.write(password + "\n")
        credentials.write(imap + "\n")
        credentials.write(str(int(timer)) + "\n")
        # Close the credentials file
        credentials.close()

        # Change the label of cancel button into "Close"
        self.mail_settings_builder.change_cancel_button_to_close()

        # Load mail data from credentials file
        self.load_mail_account()

        # load settings if there this is the first execute time
        if self.settings_data is None:
            self.load_settings()

        # Construct the mail checker
        self.construct()
        # Check for new emails
        self.mail_checker_core.timer(None, "initiate")

    def save_new_settings(self, *args):
        action_on_left_click_tray_icon =\
            self.settings_builder.get_builder().get_object('action_on_left_click_tray_icon').get_text()
        action_on_new_mail = \
            self.settings_builder.get_builder().get_object('action_on_new_mail').get_text()

        settings = open(self.current_path + self.settings_file, 'w')

        with open(self.current_path + self.settings_file, 'w'):
            pass

        # TODO: Save icon path too

        # Temporary save the same icons
        settings.write(self.settings_data["zero_messages_tray_icon"] + "\n")
        settings.write(self.settings_data["new_messages_tray_icon"] + "\n")
        settings.write(self.settings_data["error_tray_icon"] + "\n")
        settings.write(action_on_left_click_tray_icon + "\n")
        settings.write(action_on_new_mail + "\n")

        # Destroy and re-create
        self.settings_builder.get_dialog().destroy()
        self.settings_builder = settings_ui.DialogBuilder()

    def get_list_of_mails(self):
        mail_list = []
        mail_list.append(self.mail_account_data["email"])

        return mail_list

    def get_tray_icon(self):
        if self.tray_icon is not None:
            return self.tray_icon

    def get_right_clicked_menu(self):
        return self.right_clicked_menu

    @staticmethod
    def run():
        Gtk.main()

    @staticmethod
    def close_app(*args):
        Gtk.main_quit()


class SignalSender(GObject.GObject):
    """This a signal sender"""

    def __init__(self):
        GObject.GObject.__init__(self)
        GObject.type_register(SignalSender)
        GObject.signal_new("on_click_save_button", SignalSender, GObject.SIGNAL_RUN_FIRST,
                   GObject.TYPE_NONE, ())

if __name__ == '__main__':
    mail_checker = MailChecker()
    mail_checker.run()