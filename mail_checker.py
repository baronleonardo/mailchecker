
# !/usr/bin/env python2

from gi.repository import Gtk
from gi.repository import Notify
from gi.repository import GObject
import imaplib
import sys
import os.path
import encrypt
import settings_ui
import threading


class MailChecker:

    # transforms relative path into absolute path
    # because libnotify needs absolute paths for some reason
    current_path = os.path.abspath(os.path.dirname(sys.argv[0])) + "/"

    mail = "example@mail.com"
    password = "PASSWORD"
    mailIMAP = "imap.mail.com"
    mailbox = "INBOX"

    # timer for repeatly cheaking new mails
    timeoutInSecs = 900

    # if you have a light-colored panel ..
    # change zeroMsgsIcons to "indicator-messages-dark.svg"
    zero_messages_tray_icon = "indicator-messages.svg"
    new_messgaes_tray_icon = "indicator-messages-new.svg"
    error_tray_icon = "indicator-messages-error.svg"

    notification_icon = "mailIcon.png"

    # used to compare current unread messages with those
    # from last time we checked so that we would only send notifications
    # when number of unread mails has changed
    oldNumberOfMails = 0
    unread_msgs_num = 0

    # A right-clicked menu
    menu = Gtk.Menu()

    def __init__(self):
        # print(self.current_path)

        self.notification_icon = self.current_path \
            + self.notification_icon

        self.tray_icon = Gtk.StatusIcon()
        # add a tray icon
        self.tray_icon.set_from_file(
            self.current_path + self.zero_messages_tray_icon)
        # right click signal and slot
        self.tray_icon.connect('popup-menu', self.on_right_click)

        # Tray icon tooltip
        self.tray_icon.set_tooltip_text(
            "You have " + str(self.unread_msgs_num) + " new messeges.")

        # icon.connect('activate', on_left_click)

        # initialize pynotify... "Basics" can be changed to whatever... it
        # doesn't matter.
        if not Notify.init("Basics"):
            sys.exit(1)

        # Create a right-clicked menu
        self.create_menu()

        # check if mail data exist
        self.check_credentials()

    def check_credentials(self):
        # Check if mail account file exists
        f = os.path.exists(self.current_path + "credentials")
        if f is True:
            self.initiate(None, 'initiate')
        else:
            os.system("touch '" + self.current_path + "credentials'")
            self.show_settings()

    # obj parameter used because signals pushed from save-button
    # return save-button object as first argument
    def initiate(self, obj=None, state=None):
        # reads credentials from a file called 'credentials'
        # because it's never a good idea to have your credentials
        # hardwired to the code.
        credentials = open(self.current_path + "credentials", 'r')
        str_credentials = credentials.read()

        print(str_credentials)

        self.mail = str_credentials.splitlines()[0]
        self.password = str_credentials.splitlines()[1]
        self.mailIMAP = str_credentials.splitlines()[2]

        self.password = encrypt.dencrypt("decrypt", self.password)

        if state == 'initiate':
            self.timer('initiate')

        elif state == 'reinitiate':
            self.timer('reinitiate')

    def timer(self, state=None):
        self.timer_id = 0

        if state == "initiate":
            # timer for checking for new mails
            GObject.timeout_add(self.timeoutInSecs * 1000, self.checkMail)

            # checkmail upon startup
            # "initial" is used to make sure that this timer will work
            # only once and will not interfere with the main timer
            self.timer_id = GObject.timeout_add(
                1 * 1000, self.checkMail, "initial")
            print("timer id=" + str(self.timer_id) + " added")

        elif state == "reinitiate":
            GObject.source_remove(self.timer_id)
            print("timer id=" + str(self.timer_id) + " removed")
            # initiate a new timer
            self.timer("initiate")

    def send_notification(self, mailNumber):
        str_mailNumber = str(mailNumber)

        # to display "mail" if only one mail is there, and "mails" if there's
        # more than one mail.
        if mailNumber == 1:
            newMail = " new mail."
        else:
            newMail = " new mails."

        notify = Notify.Notification.new(
            "You've Got Mail!", str_mailNumber + newMail,
            self.notification_icon)

        if not notify.show():
            print("Failed to send notification")
            sys.exit(1)

    def checkMail(self, state=None):
        print("state = " + state)
        # Run check mail in a thread
        check_mail = threading.Thread(target=self.thread_check_mail)
        # Make the thread, daemon to solve the hang problem when we want
        # to close the app and it is still checking
        check_mail.setDaemon(True)
        check_mail.start()

        # this return used, to make sure that the timer will be in
        #  infinite loop
        if state == "initial":
            return False
        else:
            return True

    def thread_check_mail(self):
        """Don't call this method call checkMail() instead"""

        try:
            connection = imaplib.IMAP4_SSL(self.mailIMAP)

            if connection.login(self.mail, self.password)[0] != 'OK':
                exit("no conn")

            connection.select(self.mailbox)

            # Number of unread mails
            self.unread_msgs_num = len(
                connection.search(None, 'UnSeen')[1][0].split())

            if self.unread_msgs_num == 0:
                self.tray_icon.set_from_file(
                    self.current_path + self.zero_messages_tray_icon)
                print("Zero new mails")
            else:
                self.on_new_mail()

            # Close the connection
            connection.shutdown()

        except:
            self.invaild_mail_data()
            print("Invaild mail account data")

    def on_new_mail(self):

        if self.unread_msgs_num != self.oldNumberOfMails:
            is_numberOfmailsChanged = True
        else:
            is_numberOfmailsChanged = False

        self.oldNumberOfMails = self.unread_msgs_num

        # to help in debugging
        print("Mails # = " + str(self.unread_msgs_num))

        # change tray icon for new messages
        self.tray_icon.set_from_file(
            self.current_path + self.new_messgaes_tray_icon)
        # if number of messages changed from last check
        if is_numberOfmailsChanged:
            self.send_notification(self.unread_msgs_num)
        else:
            print("Unchanged number of new mails")

        # Tray icon tooltip
        self.tray_icon.set_tooltip_text(
            "You have " + str(self.unread_msgs_num) + " new messeges.")

    def invaild_mail_data(self):
        # Chnage tray icon to red to indicate an error
        self.tray_icon.set_from_file(
            self.current_path + self.error_tray_icon)
        # Send notification - Invaild Mail account data
        icon = Gtk.STOCK_DIALOG_ERROR
        notify = Notify.Notification.new(
            "Error!", "Invaild Mail account data", icon)
        notify.show()

    def close_app(self, data=None):
        Gtk.main_quit()

    def create_menu(self):
        check_mail_item = Gtk.MenuItem("Check Mail")
        seprator_item = Gtk.SeparatorMenuItem()
        settings_item = Gtk.MenuItem("Settings")
        close_item = Gtk.MenuItem("Close")

        # Append the menu items
        self.menu.append(check_mail_item)
        self.menu.append(seprator_item)
        self.menu.append(settings_item)
        self.menu.append(close_item)

        # add callbacks
        check_mail_item.connect_object(
            "activate", self.checkMail, "Check Mail")
        settings_item.connect_object(
            "activate", self.show_settings, "Settings")
        close_item.connect_object("activate", self.close_app, "Close")
        # Show the menu items
        self.menu.show_all()

    def show_menu(self, event_button, event_time):
        # Popup the menu
        self.menu.popup(None, None, None, None, event_button, event_time)

    def show_settings(self, data=None):
        # Show Settings dialog
        dialog_builder = settings_ui.DialogBuilder()
        # Construct signals
        self.settings_dialog_signals(dialog_builder)
        # Show Settings Dialog
        dialog_builder.show_dialog()

    def settings_dialog_signals(self, dialog_builder):
        # Get save Button from Settings dialog
        save_button = dialog_builder.get_save_button()

        save_button.connect('clicked', self.initiate, 'reinitiate')

    def on_right_click(self, data, event_button, event_time):
        self.show_menu(event_button, event_time)

    def main(self):
        Gtk.main()

if __name__ == '__main__':
    mail_checker = MailChecker()
    mail_checker.main()
