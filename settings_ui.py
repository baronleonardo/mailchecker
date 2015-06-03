from gi.repository import Gtk
import sys
import os
import encrypt

current_path = os.path.abspath(os.path.dirname(sys.argv[0])) + "/"
glade_file = "settings_ui.glade"
credentials_file = "credentials"

# Signals
class Handler:

    def on_delete_window(self, *args):
        # Close the dialog
        Gtk.main_quit(*args)

    def on_save(self, *args):
        # Get Data from text entries from the settings dialog
        email = builder.get_object('email_entry').get_text()
        password = builder.get_object('password_entry').get_text()
        imap = builder.get_object('imap_entry').get_text()
        mailbox = builder.get_object('mailbox_entry').get_text()

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
        Gtk.main_quit(*args)

# Encrypt password


def encrypt_password(password):
    password = encrypt.dencrypt("encrypt", password)
    return password


builder = Gtk.Builder()
# Load the Glade file
builder.add_from_file(current_path + glade_file)
# Attach Signals
builder.connect_signals(Handler())
# Get the dialog window
dialog = builder.get_object('dialog1')


def show_dialog():
    # Show the dialog window
    dialog.show()
