
# !/usr/bin/env python2

from gi.repository import Gtk
from gi.repository import Notify
from gi.repository import GObject
import imaplib
import sys
import os.path
import encrypt
import settings_ui


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
    zeroMsgsIcons = "indicator-messages.svg"
    newMsgs = "indicator-messages-new.svg"

    notification_icon = "mailIcon.png"

    # used to compare current unread messages with those
    # from last time we checked so that we would only send notifications
    # when number of unread mails has changed
    oldNumberOfMails = 0

    # A right-clicked menu
    menu = Gtk.Menu()

    def __init__(self):
        print(self.current_path)

        # reads credentials from a file called 'credentials'
        # because it's never a good idea to have your crendentials
        # hardwired to the code.
        credentials = open(self.current_path + "credentials", 'r')
        str_credentials = credentials.read()

        self.mail = str_credentials.splitlines()[0]
        self.password = str_credentials.splitlines()[1]
        self.mailIMAP = str_credentials.splitlines()[2]

        self.password = encrypt.dencrypt("decrypt", self.password)

        self.notification_icon = self.current_path \
            + self.notification_icon

        self.icon = Gtk.StatusIcon()
        # add a tray icon
        self.icon.set_from_file(self.current_path + self.zeroMsgsIcons)
        # right click signal and slot
        self.icon.connect('popup-menu', self.on_right_click)
        # timer for checking for new mails
        GObject.timeout_add(self.timeoutInSecs * 1000, self.checkMail)
        # icon.connect('activate', on_left_click)

        # initialize pynotify... "Basics" can be changed to whatever... it
        # doesn't matter.
        if not Notify.init("Basics"):
            sys.exit(1)

        # checkmail upon startup
        # "initial" is used to make sure that this timer will work
        # only once and will not interfere with the main timer
        GObject.timeout_add(1 * 1000, self.checkMail, "initial")

        # Create a right-clicked menu
        self.create_menu()

    def send_notification(self, mailNumber):
        str_mailNumber = str(mailNumber)

        # to display "mail" if only one mail is there, and "mails" if there's
        # more than one mail.
        if mailNumber == 1:
            newMail = " new mail."
        else:
            newMail = " new mails."

        self.notify = Notify.Notification.new(
            "You've Got Mail!", str_mailNumber + newMail,
            self.notification_icon)

        if not self.notify.show():
            print("Failed to send notification")
            sys.exit(1)

    def checkMail(self, data=None):
        connection = imaplib.IMAP4_SSL(self.mailIMAP)
        if connection.login(self.mail, self.password)[0] != 'OK':
            exit("no conn")

        connection.select(self.mailbox)
        # print the mailboxes in the mail
        # print connection.list()
        unread_msgs_num = len(connection.search(None, 'UnSeen')[1][0].split())

        if unread_msgs_num != self.oldNumberOfMails:
            numberOfmailsChanged = True
        else:
            numberOfmailsChanged = False

        self.oldNumberOfMails = unread_msgs_num

        # to help in debugging
        print(unread_msgs_num)

        if unread_msgs_num != 0:
            # change tray icon for new messages
            self.icon.set_from_file(self.current_path + self.newMsgs)
            # if number of messages changed from last check
            if numberOfmailsChanged:
                self.send_notification(unread_msgs_num)
        else:
            self.icon.set_from_file(self.current_path + self.zeroMsgsIcons)

        connection.shutdown()
        # this return used, to make sure that the timer will be in
        #  infinite loop
        if data == "initial":
            return False
        else:
            return True

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
        settings_ui.show_dialog()

    def on_right_click(self, data, event_button, event_time):
        self.show_menu(event_button, event_time)

    def main(self):
        Gtk.main()

if __name__ == '__main__':
    mail_checker = MailChecker()
    mail_checker.main()
