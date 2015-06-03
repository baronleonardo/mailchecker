from gi.repository import Gtk
import sys
import os
import encrypt

current_path = os.path.abspath(os.path.dirname(sys.argv[0])) + "/"
glade_file = "settings_ui.glade"
credentials_file = "credentials"

# Signals
class Handler:

    dialog = None

    def __init__(self, dialog):
        self.dialog = dialog

    def on_delete_window(self, *args):
        # Close the dialog
        self.dialog.get_dialog().destroy()

    def on_save(self, *args):
        # Get Data from text entries from the settings dialog
        email = self.builder.get_object('email_entry').get_text()
        password = self.builder.get_object('password_entry').get_text()
        imap = self.builder.get_object('imap_entry').get_text()
        mailbox = self.builder.get_object('mailbox_entry').get_text()

        # Encrypt the password
        password = encrypt_password(password)

        # Save Email Data
        credentials = open(current_path + credentials_file, 'w')
        credentials.write(email + "\n")
        credentials.write(password + "\n")
        credentials.write(imap + "\n")
        credentials.write(mailbox)
        credentials.close()

        # Close the dialog
        self.dialog.get_dialog().destroy()

# Encrypt password


def encrypt_password(password):
    password = encrypt.dencrypt("encrypt", password)
    return password


class DialogBuilder:
    builder = Gtk.Builder()
    dialog = None

    def __init__(self):
        # Load the Glade file
        self.builder.add_from_file(current_path + glade_file)
        # Attach Signals
        self.builder.connect_signals(Handler(self))
        # Get the dialog window
        self.dialog = self.builder.get_object('dialog1')

    def get_builder(self):
        return self.builder

    def get_dialog(self):
        return self.dialog

    def show_dialog(self):
        # Show the dialog window
        self.dialog.show()
