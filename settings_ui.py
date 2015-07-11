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
        print("the settings dialog closed")

    @staticmethod
    def on_click_add_button(*args):
        print("Add new mail data")

    @staticmethod
    def on_click_delete_button(*args):
        # TODO: confirm first before delete the credentials file
        print("remove an mail account")

    @staticmethod
    def on_click_edit_button(*args):
        print("edit button clicked")

    @staticmethod
    def on_error_button_click(self):
        print("Error button clicked")

    @staticmethod
    def on_new_mail_button_click(self):
        print("new mail button clicked")

    @staticmethod
    def on_normal_button_click(self):
        print("normal button clicked")


class DialogBuilder:
    builder = Gtk.Builder()
    dialog = None
    mailbox_list = None

    is_edit_button_clicked = False
    is_add_button_clicked = False

    def __init__(self):
        # Load the Glade file
        self.builder.add_from_file(current_path + glade_file)
        # Attach Signals
        self.builder.connect_signals(Handler(self))
        # Get the dialog window
        self.dialog = self.builder.get_object('dialog1')

    def load_mailboxes(self, mailboxes):
        self.mailbox_list = mailboxes
        mailbox_list = self.get_mailbox_list_store()

        # Load email to the tree view
        for iii in range(0, mailboxes.__len__()):
            mailbox_list.append([mailboxes[iii]])

    def update_mailboxes_list(self, new_mailbox):
        self.mailbox_list.append(new_mailbox)
        mail_list = self.get_mailbox_list_store()

        mail_list.append([new_mailbox])

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

    def get_selected_mailbox(self):
        # get Tree View contains list of mails
        tree_view = self.get_tree_view()
        # get selected mail
        selection = tree_view.get_selection()
        selected_mailbox, itr = selection.get_selected()

        return selected_mailbox, itr

    def get_tree_view(self):
        return self.builder.get_object("treeview1")

    def get_close_button(self):
        return self.builder.get_object("close_button")

    def get_add_button(self):
        return self.builder.get_object("add_email_button")

    def get_edit_button(self):
        return self.builder.get_object("edit_email_button")

    def get_remove_button(self):
        return self.builder.get_object("remove_email_button")

    def get_new_button(self):
        return self.builder.get_object("new_button")

    def get_normal_button(self):
        return self.builder.get_object("normal_button")

    def get_normal_tray_icon(self):
        return self.builder.get_object("normal_tray_icon")

    def get_error_button(self):
        return self.builder.get_object("error_button")

    def get_new_tray_icon(self):
        return self.builder.get_object("new_tray_icon")

    def get_mailbox_list_store(self):
        return self.builder.get_object("mailbox_list")

    def get_error_tray_icon(self):
        return self.builder.get_object("error_tray_icon")

    def get_builder(self):
        return self.builder

    def get_dialog(self):
        return self.dialog

    def show_dialog(self, *args):
        # Show the dialog window
        self.dialog.show()