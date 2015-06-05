from gi.repository import Gtk
import sys
import os
import encrypt

current_path = os.path.abspath(os.path.dirname(sys.argv[0])) + "/"
glade_file = "settings_ui.glade"
credentials_file = "credentials"

# Signals


class Handler:

    dialog_builder = None

    def __init__(self, dialog_builder):
        self.dialog_builder = dialog_builder

    def on_delete_window(self, *args):
        # Close the dialog
        self.dialog_builder.get_dialog().destroy()

    def on_save(self, *args):
        builder = self.dialog_builder.get_builder()
        # Get Data from text entries from the settings dialog
        email = builder.get_object('email_entry').get_text()
        password = builder.get_object('password_entry').get_text()
        imap = builder.get_object('imap_entry').get_text()

        # Encrypt the password
        password = encrypt_password(password)

        # Save Email Data
        credentials = open(current_path + credentials_file, 'w')
        credentials.write(email + "\n")
        credentials.write(password + "\n")
        credentials.write(imap + "\n")

        cancel_button = self.dialog_builder.get_builder().get_object(
            "cancel_button")
        cancel_button.set_label("Close")

        # Close the dialog
        # self.dialog.get_dialog().destroy()
        # save = dialog.get_object('save_button')


def encrypt_password(password):
    """"Encrypt Password"""
    password = encrypt.dencrypt("encrypt", password)
    return password


class DialogBuilder:
    builder = Gtk.Builder()
    dialog = None
    save_button = None

    def __init__(self):
        # Load the Glade file
        self.builder.add_from_file(current_path + glade_file)
        # Attach Signals
        self.builder.connect_signals(Handler(self))
        # Get the dialog window
        self.dialog = self.builder.get_object('dialog1')
        self.save_button = self.builder.get_object('save_button')

    def get_builder(self):
        return self.builder

    def get_dialog(self):
        return self.dialog

    def get_save_button(self):
        return self.save_button

    def show_dialog(self):
        # Show the dialog window
        self.dialog.show()
