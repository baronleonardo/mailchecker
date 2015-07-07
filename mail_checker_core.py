
# !/usr/bin/env python2

from gi.repository import Gtk
from gi.repository import Notify
from gi.repository import GObject
import imaplib
import sys
import os.path
import threading
import urllib2


class Core:

    # transforms relative path into absolute path
    # because libnotify needs absolute paths for some reason
    current_path = os.path.abspath(os.path.dirname(sys.argv[0])) + "/"

    mail_account_data = None
    settings_data = None
    tray_icon = None

    # used to compare current unread messages with those
    # from last time we checked so that we would only send notifications
    # when number of unread mails has changed
    oldNumberOfMails = 0
    unread_msgs_num = 0

    current_timer_id = 0

    is_invalid_mail_account = False
    is_there_internet_connection = True
    is_checking_for_new_mails = False
    has_new_message = False

    from_milliseconds_to_minutes = 60 * 1000

    def __init__(self, mail_account_data, settings_data, tray_icon):

        self.mail_account_data = mail_account_data
        self.settings_data = settings_data
        self.tray_icon = tray_icon

        # Tray icon tooltip
        # tray_icon.set_tooltip_text(
        #     "You have " + str(self.unread_msgs_num) + " new messages.")

    def timer(self, button=None, state=None):
        if state == "initiate":
            # timer for checking for new mails
            GObject.timeout_add(self.mail_account_data["checker_timer_in_minutes"] * self.from_milliseconds_to_minutes,
                                self.check_new_mails, "main_counter")

            # check mail upon startup
            # "initial" is used to make sure that this timer will work
            # only once and will not interfere with the main timer
            self.current_timer_id = GObject.timeout_add(1 * 1000, self.check_new_mails, "initial")
            print("timer id=" + str(self.current_timer_id) + " added")

        elif state == "re-initiate":
            GObject.source_remove(self.current_timer_id)
            print("timer id=" + str(self.current_timer_id) + " removed")
            # initiate a new timer
            self.timer("initiate")

    def send_notification(self, number_of_mails):

        # to display "mail" if only one mail is there, and "mails" if there's
        # more than one mail.
        if number_of_mails == 1:
            new_mail = " new mail."
        else:
            new_mail = " new mails."

        notify = Notify.Notification.new(
            "You've Got Mail!", str(number_of_mails) + new_mail,
            self.settings_data["notification_icon"])

        if not notify.show():
            print("Failed to send notification")
            sys.exit(1)

    def check_new_mails(self, state=None):
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

        self.is_checking_for_new_mails = True

        try:
            connection = imaplib.IMAP4_SSL(self.mail_account_data["mailIMAP"])

            self.is_there_internet_connection = True

            if connection.login(self.mail_account_data["email"], self.mail_account_data["password"])[0] != 'OK':
                exit("no conn")

            self.is_invalid_mail_account = False

            print(self.mail_account_data["email"])

            connection.select(self.mail_account_data["mailbox"])

            # Number of unread mails
            self.unread_msgs_num = len(
                connection.search(None, 'UnSeen')[1][0].split())

            if self.unread_msgs_num == 0:
                self.tray_icon.set_from_file(
                    self.current_path + self.settings_data["zero_messages_tray_icon"])
                print("Zero new mails")

                # Tray icon tooltip
                # self.tray_icon.set_tooltip_text(
                #     "You have " + str(self.unread_msgs_num) + " new messages.")
            else:
                self.on_new_mail()

            # Close the connection
            connection.shutdown()
        except:
            if self.check_internet_availability() is False:
                self.on_no_internet_connection()
                self.is_there_internet_connection = False
                print("No internet connection")
            else:
                self.invalid_mail_data()
                self.is_invalid_mail_account = True
                print("Invalid mail account data")

        self.is_checking_for_new_mails = False

    def on_new_mail(self):

        if self.unread_msgs_num != self.oldNumberOfMails:
            is_number_of_mails_changed = True
        else:
            is_number_of_mails_changed = False

        self.oldNumberOfMails = self.unread_msgs_num

        # to help in debugging
        print("Mails # = " + str(self.unread_msgs_num))

        # change tray icon for new messages
        self.tray_icon.set_from_file(
            self.current_path + self.settings_data["new_messages_tray_icon"])
        # if number of messages changed from last check
        if is_number_of_mails_changed:
            self.send_notification(self.unread_msgs_num)
        else:
            print("Unchanged number of new mails")

        # Tray icon tooltip
        # self.tray_icon.set_tooltip_text(
        #     "You have " + str(self.unread_msgs_num) + " new messages.")

    @staticmethod
    def check_internet_availability():
        try:
            url_available = urllib2.urlopen('http://google.com', timeout=1)
            return True
        except urllib2.URLError as e:
            pass
        return False

    def on_no_internet_connection(self):
        if self.is_there_internet_connection is True:
            # Change tray icon to red to indicate an error
            self.tray_icon.set_from_file(
                self.current_path + self.settings_data["error_tray_icon"])

        self.is_there_internet_connection = False

    def invalid_mail_data(self):
        if self.is_invalid_mail_account is False:
            if self.mail_account_data is None:
                print("data is None")
            # Change tray icon to red to indicate an error
            self.tray_icon.set_from_file(
                self.current_path + self.settings_data["error_tray_icon"])
            # Send notification - Invalid Mail account data
            icon = Gtk.STOCK_DIALOG_ERROR
            notify = Notify.Notification.new(
                "Error!", "Invalid Mail account data", icon)
            notify.show()

        self.is_invalid_mail_account = True

# if __name__ == '__main__':
#     mail_checker = MailChecker()
#     Gtk.main()
#     mail_checker.main()
