
# !/usr/bin/env python2

import gtk
import imaplib


class MailChecker:

    mail = "example@mail.com"
    password = "PASSWORD"
    mailIMAP = "imap.mail.com"
    mailbox = "INBOX"

    timeoutInSecs = 900

    zeroMsgsIcons = "indicator-messages"
    newMsgs = "indicator-messages-new"

    def __init__(self):
        self.icon = gtk.StatusIcon()
        # add a tray icon
        self.icon.set_from_icon_name(self.zeroMsgsIcons)
        # right click signal and slot
        self.icon.connect('popup-menu', self.on_right_click)
        # timer for checking for new mails
        gtk.timeout_add(self.timeoutInSecs * 1000, self.checkMail)
        # icon.connect('activate', on_left_click)

    def message(self, data=None):
        """Function to display messages to the user."""

        msg = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                                gtk.MESSAGE_INFO, gtk.BUTTONS_OK, data)
        msg.run()
        msg.destroy()

    def checkMail(self, data=None):
        connection = imaplib.IMAP4_SSL(self.mailIMAP)
        if connection.login(self.mail, self.password)[0] != 'OK':
            exit("no conn")

        connection.select(self.mailbox)
        # print the mailboxes in the mail
        # print connection.list()
        unread_msgs_num = len(connection.search(None, 'UnSeen')[1][0].split())

        # to help in debugging
        print(unread_msgs_num)

        if unread_msgs_num != 0:
            self.icon.set_from_icon_name(self.newMsgs)
        # self.icon.status_icon_new_from_icon_name('indicator-messages-new')
        # this show double tray icons
        connection.shutdown()
        # this return used, to make sure that the timer will be in
        #  infinite loop
        return True

    def close_app(self, data=None):
        gtk.main_quit()

    def make_menu(self, event_button, event_time, data=None):
        menu = gtk.Menu()
        check_mail_item = gtk.MenuItem("Check Mail")
        close_item = gtk.MenuItem("Close App")

        # Append the menu items
        menu.append(check_mail_item)
        menu.append(close_item)
        # add callbacks
        check_mail_item.connect_object(
            "activate", self.checkMail, "Check Mail")
        close_item.connect_object("activate", self.close_app, "Close App")
        # Show the menu items
        check_mail_item.show()
        close_item.show()

        # Popup the menu
        menu.popup(None, None, None, event_button, event_time)

    def on_right_click(self, data, event_button, event_time):
        self.make_menu(event_button, event_time)

    def main(self):
        gtk.main()


# def on_left_click(event):
#     message("Status Icon Left Clicked")

if __name__ == '__main__':
    mail_checker = MailChecker()
    mail_checker.main()
