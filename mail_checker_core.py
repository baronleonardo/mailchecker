
# !/usr/bin/env python2

from gi.repository import Gtk
from gi.repository import Notify
from gi.repository import GObject
import imaplib
import sys
import os.path
import threading


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

    from_milliseconds_to_minutes = 60 * 1000

    def __init__(self, mail_account_data, settings_data, tray_icon):

        self.mail_account_data = mail_account_data
        self.settings_data = settings_data
        self.tray_icon = tray_icon

        # Tray icon tooltip
        tray_icon.set_tooltip_text(
            "You have " + str(self.unread_msgs_num) + " new messages.")

    def timer(self, button=None, state=None):
        if state == "initiate":
            # timer for checking for new mails
            GObject.timeout_add(self.mail_account_data["checker_timer_in_minutes"] * self.from_milliseconds_to_minutes,
                                self.check_new_mails, "main_counter")

            # check mail upon startup
            # "initial" is used to make sure that this timer will work
            # only once and will not interfere with the main timer
            self.current_timer_id = GObject.timeout_add( 1 * 1000, self.check_new_mails, "initial")
            print("timer id=" + str(self.current_timer_id) + " added")

        elif state == "re-initiate":
            GObject.source_remove(self.current_timer_id)
            print("timer id=" + str(self.current_timer_id) + " removed")
            # initiate a new timer
            self.timer("initiate")

    def send_notification(self, number_of_mails):
        str_number_of_mails = str(number_of_mails)

        # to display "mail" if only one mail is there, and "mails" if there's
        # more than one mail.
        if number_of_mails == 1:
            new_mail = " new mail."
        else:
            new_mail = " new mails."

        notify = Notify.Notification.new(
            "You've Got Mail!", str_number_of_mails + new_mail,
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

        try:
            connection = imaplib.IMAP4_SSL(self.mail_account_data["mailIMAP"])

            if connection.login(self.mail_account_data["email"], self.mail_account_data["password"])[0] != 'OK':
                exit("no conn")

            print(self.mail_account_data["email"])

            connection.select(self.mail_account_data["mailbox"])

            # Number of unread mails
            self.unread_msgs_num = len(
                connection.search(None, 'UnSeen')[1][0].split())

            if self.unread_msgs_num == 0:
                self.tray_icon.set_from_file(
                    self.current_path + self.settings_data["zero_messages_tray_icon"])
                print("Zero new mails")
            else:
                self.on_new_mail()

            # Close the connection
            connection.shutdown()

        except:
            self.invalid_mail_data()
            print("Invalid mail account data")

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
        self.tray_icon.set_tooltip_text(
            "You have " + str(self.unread_msgs_num) + " new messages.")

    def invalid_mail_data(self):
        # Change tray icon to red to indicate an error
        self.tray_icon.set_from_file(
            self.current_path + self.settings_data["error_tray_icon"])
        # Send notification - Invalid Mail account data
        icon = Gtk.STOCK_DIALOG_ERROR
        notify = Notify.Notification.new(
            "Error!", "Invalid Mail account data", icon)
        notify.show()

# if __name__ == '__main__':
#     mail_checker = MailChecker()
#     Gtk.main()
#     mail_checker.main()
