from gi.repository import Gtk
import sys
import os

current_path = os.path.abspath(os.path.dirname(sys.argv[0])) + "/"
glade_file = "settings_ui.glade"
credentials_file = "credentials"


class Handler:

    """Signals"""

    dialog_builder = None

    def __init__(self, dialog_builder):
        self.dialog_builder = dialog_builder

    @staticmethod
    def on_close_window(*args):
        # Close the dialog
        print("the settings dialog closed")
        # self.dialog_builder.get_dialog().hide()

    @staticmethod
    def on_click_add_button(*args):
        # Show Settings dialog
        print("Under Construction")

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

    @staticmethod
    def on_click_edit_button():
        print("Under Construction")
        # get Tree View contains list of mails
        # tree_view = self.dialog_builder.get_tree_view()
        # get selected mail
        # selection = tree_view.get_selection()
        # selected_mail, itr = selection.get_selected()


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
        # set mail list
        self.mail_list = self.builder.get_object('email_list')

    def load_mails(self, mails):
        self.mail_list.append(mails)

    def load_icons(self, zero_messages_tray_icon, new_messages_tray_icon, error_tray_icon):
        normal = self.builder.get_object("normal_tray_icon")
        normal.set_from_file(zero_messages_tray_icon)

        new_messages = self.builder.get_object("new_tray_icon")
        new_messages.set_from_file(new_messages_tray_icon)

        error = self.builder.get_object("error_tray_icon")
        error.set_from_file(error_tray_icon)

    def load_actions(self, action_on_left_click_tray_icon, action_on_new_mail):
        on_left_click_label = self.builder.get_object("action_on_left_click_tray_icon")
        on_left_click_label.set_text(action_on_left_click_tray_icon)

        on_new_mail_label = self.builder.get_object("action_on_new_mail")
        on_new_mail_label.set_text(action_on_new_mail)

    def get_tree_view(self):
        return self.builder.get_object("treeview1")

    def get_close_button(self):
        return self.builder.get_object("close_button")

    def get_mail_list(self):
        return self.mail_list

    def get_builder(self):
        return self.builder

    def get_dialog(self):
        return self.dialog

    def show_dialog(self, *args):
        # Show the dialog window
        self.dialog.show()