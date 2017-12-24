from PyQt5.QtCore import QObject
import imaplib
import socket

class EMail(QObject):
    """
    email handler
    """

    def __init__(self, email: str, password: str, imap: str, mailbox: str, parent=None):
        super().__init__(parent)

        self.__connection = None
        self.__email = email
        self.__password = password
        self.__imap = imap
        self.__mailbox = mailbox

    def connect(self) -> bool:
        try:
            self.__connection = imaplib.IMAP4_SSL(self.__imap)

            if self.__connection.login(self.__email, self.__password)[0] != 'OK':
                exit("Authentication Failed!")
            print("Connected.")
            return True
        except socket.gaierror as error:
            print(error)
            return False

    def disconnect(self):
        if self.__connection != None:
            self.__connection.logout()
            self.__connection = None

    def __mailbox_open(self, is_read_only=True):
        print("mailbox name: %s" % self.__mailbox)
        status,_ = self.__connection.select(self.__mailbox, is_read_only)

        if status != 'OK':
            return False
        else:
            return True

    def __mailbox_close(self):
        self.__connection.close()

    def get_mail_count(self, auto_open_mailbox=False, auto_close_mailbox=False):
        """
        check for new mails and return their length
        """

        if self.__connection is None:
            print("Error: No connection")
            return -1

        if auto_open_mailbox is True:
            if self.__mailbox_open() is False:
                print("Error: bad mailbox name %s" % self.__mailbox)
                return -1

        # get the uinque IDs for the unread messages
        status, unseen_emails = self.__connection.search(None, 'UNSEEN')
        # data = data[0].decode().split()

        if status != 'OK':
            print("Error getting new emails.")
            return -1

        # Number of unread mails
        unread_msgs_num = len(unseen_emails[0].split())

        # if self.MAX_UNREAD_MSG_LEN <= unread_msgs_num:
            # max_msgs_to_read = self.MAX_UNREAD_MSG_LEN

        # messages = [unread_msgs_num]
        # get the sender and the subject from the unread messages
        # for iii in range(0, max_msgs_to_read):
        #     _, m_data = connection.uid('fetch', data[iii], "(RFC822)")
        #     email_message = email.message_from_string(m_data[0][1].decode())
        #     messages.append(
        #         [email_message['From'][:email_message['From'].index('<')],
        #          email_message['Subject']]
        #     )

        if auto_close_mailbox is True:
            self.__mailbox_close()

        print("Unread emails: %d" % unread_msgs_num)

        return unread_msgs_num
