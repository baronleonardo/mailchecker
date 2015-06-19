from gi.repository import Gtk
from gi.repository import GObject
import sys
import os
import encrypt

current_path = os.path.abspath(os.path.dirname(sys.argv[0])) + "/"
glade_file = "mail_settings_ui.glade"
credentials_file = "credentials"

# Signals


class Handler:

    dialog_builder = None

    def __init__(self, dialog_builder):
        self.dialog_builder = dialog_builder

    def on_close_window(self, *args):
        # Close the dialog
        self.dialog_builder.get_dialog().destroy()

    def on_save(self, *args):
        print("Save new mail data")

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

    def load_mail_data(self, email, password, mailIMAP, checker_timer_in_minutes):
        """set Data to text entries in the mail settings dialog"""
        email = self.builder.get_object('email_entry').set_text(email)
        password = self.builder.get_object('password_entry').set_text(password)
        imap = self.builder.get_object('imap_entry').set_text(mailIMAP)
        timer = self.builder.get_object('timer_spin').set_value(checker_timer_in_minutes)


    def change_cancel_button_to_close(self):
        cancel_button = self.builder.get_object("cancel_button")
        cancel_button.set_label("Close")

# if __name__ == "__main__":
#     dialog = DialogBuilder()
#     dialog.show_dialog()
#     Gtk.main()
