from gi.repository import Gtk
import sys
import os
import mail_settings_ui

current_path = os.path.abspath(os.path.dirname(sys.argv[0])) + "/"
glade_file = "settings_ui.glade"
credentials_file = "credentials"


class Handler:

    """Signals"""

    dialog_builder = None

    def __init__(self, dialog_builder):
        self.dialog_builder = dialog_builder

    def on_delete_window(self, *args):
        # Close the dialog
        self.dialog_builder.get_dialog().destroy()

    def on_click_add_button(self, *args):
        # Show Settings dialog
        dialog_builder = mail_settings_ui.DialogBuilder()
        # Show Settings Dialog
        dialog_builder.show_dialog()

    def on_click_delete_button(self, *args):
        # get Tree View contains list of mails
        tree_view = self.dialog_builder.get_tree_view()
        # get selected mail
        selection = tree_view.get_selection()
        selected_mail, itr = selection.get_selected()
        # remove selected mail
        selected_mail.remove(itr)

        # delete mail account from credentials file
        # This a temporary workaround as it is one mail data
        # TODO: confirm first before delete the credentials file
        os.remove(current_path + credentials_file)

    def on_click_edit_button(self):
        # get Tree View contains list of mails
        tree_view = self.dialog_builder.get_tree_view()
        # get selected mail
        selection = tree_view.get_selection()
        selected_mail, itr = selection.get_selected()


class DialogBuilder:
    builder = Gtk.Builder()
    dialog = None
    mail_list = None

    def __init__(self):
        # Load the Glade file
        self.builder.add_from_file(current_path + glade_file)
        # Attach Signals
        self.builder.connect_signals(Handler(self))
        # Get the dialog window
        self.dialog = self.builder.get_object('dialog1')
        # mail list
        self.mail_list = self.builder.get_object('email_list')

    def load_mails(self):
        credentials = open(current_path + credentials_file, 'r')
        str_credentials = credentials.read()
        mail = str_credentials.splitlines()[0]
        self.mail_list.append([mail])

    def get_tree_view(self):
        return self.builder.get_object("treeview1")

    def get_mail_list(self):
        return self.mail_list

    def get_builder(self):
        return self.builder

    def get_dialog(self):
        return self.dialog

    def show_dialog(self):
        # Show the dialog window
        self.dialog.show()