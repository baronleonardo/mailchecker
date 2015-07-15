from gi.repository import Gtk
from gi.repository import Notify
import os
import sys
import encrypt
import db_controller
import mail_checker_core
import mail_settings_ui
import settings_ui
import triggers
import file_chooser


class MailChecker:
    # transforms relative path into absolute path
    # because libnotify needs absolute paths for some reason
    current_path = os.path.abspath(os.path.dirname(sys.argv[0])) + "/"
    settings_file = "settings"
    default_settings_file = "settings_defaults"

    database = None

    list_of_mails = []
    list_of_mails_cores = []

    tray_icon = None
    tray_icon_tooltip = None
    right_clicked_menu = None
    settings_builder = None
    mail_settings_builder = None

    # mail_account_data = None
    settings_data = None

    notification_icon = "mailIcon.png"

    def __init__(self):

        self.database = db_controller.DatabaseController(self.current_path)

        if self.settings_file_exists():
            self.load_settings()
        else:
            self.on_settings_file_not_found()

        if self.database.db_exists():
            self.load_mail_accounts()
        else:
            self.database.on_db_not_found()

        if (self.list_of_mails_cores and self.settings_data) is not None:
            self.construct()

            # Initiate the timer
            for mail_core in self.list_of_mails_cores:
                mail_core.timer(None, "initiate")

    def construct(self):
        self.tray_icon = self.create_tray_icon()
        self.tray_icon_tooltip = self.create_tray_icon_tooltip()

        for iii in range(0, self.list_of_mails.__len__()):
            core = mail_checker_core.Core(self.list_of_mails[iii], self.settings_data["notification_icon"])
            self.list_of_mails_cores.append(core)

        # Create a trigger when receiving new email
        mail_triggers = triggers.Triggers(self.settings_data, self.list_of_mails_cores.__len__(),
                                          self.tray_icon, self.current_path)
        mail_triggers.initiate(self.list_of_mails_cores)

        self.right_clicked_menu = self.create_right_clicked_menu()
        self.initialize_notification_system()
        self.notification_icon = self.current_path + self.notification_icon

    @staticmethod
    def initialize_notification_system():
        # initialize pynotify... "Basics" can be changed to whatever... it
        # doesn't matter.
        if not Notify.init("Basics"):
            sys.exit(1)

    def settings_file_exists(self):
        # Check if settings file exists
        f = os.path.exists(self.current_path + self.settings_file)
        if f is False:
            print("settings file not found!")
            return False
        else:
            return True

    def on_settings_file_not_found(self):
        """Load default settings"""
        os.system("touch '" + self.current_path + self.settings_file + "'")
        settings = open(self.current_path + self.settings_file, 'w')
        default = open(self.current_path + self.default_settings_file, 'r')

        settings.write(default.read())

    def load_settings(self):
        print("load settings")

        settings = open(self.current_path + self.settings_file, 'r')
        str_settings = settings.read()

        zero_messages_tray_icon   = str_settings.splitlines()[0]
        new_messages_tray_icon    = str_settings.splitlines()[1]
        error_tray_icon           = str_settings.splitlines()[2]
        action_on_left_click_tray = str_settings.splitlines()[3]
        action_on_new_mail        = str_settings.splitlines()[4]

        self.settings_data = {
            "zero_messages_tray_icon": zero_messages_tray_icon,
            "new_messages_tray_icon": new_messages_tray_icon,
            "error_tray_icon": error_tray_icon,
            "action_on_left_click_tray_icon": action_on_left_click_tray,
            "action_on_new_mail": action_on_new_mail,
            "notification_icon": self.current_path + self.notification_icon
        }

        settings.close()

    def load_mail_accounts(self, type_of_load=None, mail_data=None):

        if type_of_load == "dialog":
            self.mail_settings_builder.load_mail_data(mail_data)
        elif type_of_load is None:
            # Load mail accounts from the database
            self.load_mail_accounts_from_db()

    def load_mail_accounts_from_db(self):
        # Get the list of mail accounts
        list_of_mails = self.database.load()

        # Create a dictionary for this list
        for mail_account in list_of_mails:
            mail_account_data = {
                "mailbox_name": mail_account[0],
                "email": mail_account[1],
                "password": encrypt.dencrypt("decrypt", mail_account[2]),
                "mailIMAP": mail_account[3],
                "mailbox": mail_account[4],
                "checker_timer_in_minutes": mail_account[5],
            }

            self.list_of_mails.append(mail_account_data)

    def on_edit_current_mail_data(self, button=None, type_of_load=None):
        selected_mail, itr = self.settings_builder.get_selected_mailbox()

        mail_data = None
        for mail in self.list_of_mails:
            if mail["mailbox_name"] == selected_mail.get_value(itr, 0):
                mail_data = mail
        self.show_mail_settings("update")
        self.load_mail_accounts(type_of_load, mail_data)

    def on_remove_current_mail_data(self, *args):
        selected_mail, itr = self.settings_builder.get_selected_mailbox()
        row_id = selected_mail.get_path(itr)[0]

        # Remove from the TreeView
        selected_mail.remove(itr)
        # Remove mail core from mail cores
        self.list_of_mails_cores.__delitem__(row_id)
        # Remove mail from mails list
        self.list_of_mails.__delitem__(row_id)
        # Remove from the database
        self.database.remove(row_id + 1)

    def on_add_new_mail_data(self, *args):
        self.show_mail_settings("new")

    def create_tray_icon(self):
        """Create tray icon"""
        tray_icon = Gtk.StatusIcon()
        # has tooltip
        tray_icon.set_has_tooltip(True)
        # add a tray icon
        tray_icon.set_from_file(
            self.current_path + self.settings_data["zero_messages_tray_icon"])

        # right click signal and slot
        tray_icon.connect('popup-menu', self.on_right_click_tray_icon)
        # left click signal and slot
        tray_icon.connect('activate', self.on_left_click_tray_icon)

        return tray_icon

    def create_tray_icon_tooltip(self):
        tooltip = Gtk.Tooltip()
        # update unread msgs if mouse hover on the tray icon
        self.tray_icon.connect("query-tooltip", self.set_tooltip)
        return tooltip

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
        for mail_core in self.list_of_mails_cores:
            check_mail_item.connect_object("activate", mail_core.check_new_mails, "Check Mail")
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
            os.system(self.settings_data["action_on_left_click_tray_icon"] + " 2> /dev/null &")

    def set_tooltip(self, widget=None, x=0, y=0, keyboard_mode=None,
                    tooltip=None):

        message = ""
        unread_msgs = 0
        has_new_msgs = True

        states = []

        for core in self.list_of_mails_cores:
            if core.is_checking_for_new_mails:
                message = "Checking ..."
                break
            elif core.is_there_internet_connection is False:
                message = "No Internet connection!"
                break
            elif core.is_invalid_mail_account:
                states.append(core.mail_account_data["mailbox_name"] + ": Invalid mail Account")
            else:
                states.append(str(core.unread_msgs_num) + " in " + core.mail_account_data["mailbox_name"])
                unread_msgs += core.unread_msgs_num

        if states.__len__() == 0:
            self.tray_icon.set_tooltip_text(message)

        else:
            message = "You have " + str(unread_msgs) + " new message(s):\n"

            for iii in range(0, states.__len__()):
                message += "\t" + states[iii]
                if iii != states.__len__() - 1:
                    message += "\n"

            self.tray_icon.set_tooltip_text(message)

    def show_mail_settings(self, type_of_update):
        self.mail_settings_builder = mail_settings_ui.DialogBuilder()
        # Construct additional signals
        self.mail_settings_dialog_additional_signals(type_of_update)
        # Show Mail Settings Dialog
        self.mail_settings_builder.show_dialog()

    def show_settings(self, *args):
        self.settings_builder = settings_ui.DialogBuilder()
        # Construct additional signals
        self.settings_dialog_additional_signals()
        # Show Settings Dialog
        self.settings_builder.show_dialog()
        # load emails account
        self.settings_builder.load_mailboxes(self.get_list_of_mailboxes())
        self.settings_builder.load_icons(self.settings_data["zero_messages_tray_icon"],
                                         self.settings_data["new_messages_tray_icon"],
                                         self.settings_data["error_tray_icon"])
        self.settings_builder.load_actions(self.settings_data["action_on_left_click_tray_icon"],
                                           self.settings_data["action_on_new_mail"])

    def mail_settings_dialog_additional_signals(self, type_of_update):
        # Get save Button from Settings dialog
        save_button = self.mail_settings_builder.get_save_button()

        # Reinitialize the timer if save-button is clicked
        if (self.list_of_mails_cores and self.settings_data) is not None:
            for mail_core in self.list_of_mails_cores:
                save_button.connect('clicked', mail_core.timer, 're-initiate')

        if type_of_update == "new":
            save_button.connect('clicked', self.save_new_mail_data, "new")
        elif type_of_update == "update":
            save_button.connect('clicked', self.save_new_mail_data, "update")

    def settings_dialog_additional_signals(self):
        # TODO: slots methods need to be transferred into their corresponding file
        close_button = self.settings_builder.get_close_button()
        close_button.connect('clicked', self.save_new_settings)

        edit_button = self.settings_builder.get_edit_button()
        edit_button.connect('clicked', self.on_edit_current_mail_data, "dialog")

        remove_button = self.settings_builder.get_remove_button()
        remove_button.connect('clicked', self.on_remove_current_mail_data)

        add_button = self.settings_builder.get_add_button()
        add_button.connect('clicked', self.on_add_new_mail_data)

        normal_button = self.settings_builder.get_normal_button()
        normal_button.connect('clicked', self.choose_tray_icon, 'normal_button')

        new_button = self.settings_builder.get_new_button()
        new_button.connect('clicked', self.choose_tray_icon, 'new_button')

        error_button = self.settings_builder.get_error_button()
        error_button.connect('clicked', self.choose_tray_icon, 'error_button')

    def choose_tray_icon(self, button=None, button_type=None):
        chooser = file_chooser.FileChooserWindow()
        chosen_file = chooser.run()

        if button_type == "normal_button":
            # Update settings data
            self.settings_data["zero_messages_tray_icon"] = chosen_file
            # Change the icon and update the button
            icon_image = self.settings_builder.get_normal_tray_icon()
            button.set_image(icon_image.new_from_file(chosen_file))

        elif button_type == "new_button":
            # Update settings data
            self.settings_data["new_messages_tray_icon"] = chosen_file
            # Change the icon and update the button
            icon_image = self.settings_builder.get_new_tray_icon()
            button.set_image(icon_image.new_from_file(chosen_file))

        elif button_type == "error_button":
            # Update settings data
            self.settings_data["error_tray_icon"] = chosen_file
            # Change the icon and update the button
            icon_image = self.settings_builder.get_error_tray_icon()
            button.set_image(icon_image.new_from_file(chosen_file))

    @staticmethod
    def encrypt_password(password):
        """"Encrypt Password"""
        password = encrypt.dencrypt("encrypt", password)
        return password

    def save_new_mail_data(self, button=None, type_of_update=None):
        # TODO: need to be changed - One mail updated per time, why update all the list
        # Get Data from text entries from the mail settings dialog
        mailbox_name = self.mail_settings_builder.get_builder().get_object('mailbox_name_entry').get_text()
        email = self.mail_settings_builder.get_builder().get_object('email_entry').get_text()
        password = self.mail_settings_builder.get_builder().get_object('password_entry').get_text()
        imap = self.mail_settings_builder.get_builder().get_object('imap_entry').get_text()
        timer = self.mail_settings_builder.get_builder().get_object('timer_spin').get_value()

        # Encrypt the password
        password = self.encrypt_password(password)

        # Convert timer into string type
        timer = str(timer)

        mail_data = {
            "mailbox_name": mailbox_name,
            "email": email,
            "password": password,
            "mailIMAP": imap,
            "checker_timer_in_minutes": timer
        }

        # Save mail Data
        if type_of_update == "new":
            # Insert row of data into the database
            self.database.insert(mail_data)
            # Add the new mail to the TreeView list
            list_of_mailboxes = self.get_list_of_mailboxes()
            if list_of_mailboxes.__len__() == 0:
                self.settings_builder.update_mailboxes_list(mail_data.get("mailbox_name"))
            else:
                self.settings_builder.update_mailboxes_list(list_of_mailboxes[list_of_mailboxes.__len__()-1])
        elif type_of_update == "update":
            # Get row_id
            selected_mailbox, itr = self.settings_builder.get_selected_mailbox()
            row_id = selected_mailbox.get_path(itr)[0] + 1
            # Update database
            self.database.update(row_id, mail_data)
            # Update TreeView
            mailbox_name = self.mail_settings_builder.get_mailbox_name().get_text()
            selected_mailbox.set_value(itr, 0, mailbox_name)

        # Close the mail settings dialog
        self.mail_settings_builder.close_mail_settings_dialog()

        # Re-load mail data
        del self.list_of_mails[:]
        self.load_mail_accounts()

        # load settings if this is the first executing time
        if self.settings_data is None:
            self.load_settings()

        # delete and re-Construct the mail checker core
        del self.list_of_mails_cores[:]
        for iii in range(0, self.list_of_mails.__len__()):
            core = mail_checker_core.Core(self.list_of_mails[iii], self.settings_data["notification_icon"])
            self.list_of_mails_cores.append(core)

            # Check for new emails
            core.timer(None, "initiate")

    def save_new_settings(self, *args):
        action_on_left_click_tray_icon = \
            self.settings_builder.get_builder().get_object('action_on_left_click_tray_icon').get_text()
        action_on_new_mail = \
            self.settings_builder.get_builder().get_object('action_on_new_mail').get_text()

        with open(self.current_path + self.settings_file, 'w'):
            pass

        settings = open(self.current_path + self.settings_file, 'w')

        # TODO: Save icon path too

        # Temporary save the same icons
        settings.write(self.settings_data["zero_messages_tray_icon"] + "\n")
        settings.write(self.settings_data["new_messages_tray_icon"] + "\n")
        settings.write(self.settings_data["error_tray_icon"] + "\n")
        settings.write(action_on_left_click_tray_icon + "\n")
        settings.write(action_on_new_mail + "\n")

        settings.flush()
        settings.close()

        # load settings data
        self.load_settings()

        # Destroy
        self.settings_builder.get_dialog().destroy()

    def get_list_of_mailboxes(self):
        mailbox_list = []

        for mail_account in self.list_of_mails:
            mailbox_list.append(mail_account["mailbox_name"])

        return mailbox_list

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


if __name__ == '__main__':
    mail_checker = MailChecker()
    mail_checker.run()
