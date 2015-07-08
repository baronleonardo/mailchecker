import os
import threading

class Triggers:
    settings_data = None
    number_of_mail_cores = 0
    length_of_core_list = 0
    tray_icon = None
    current_path = None

    semaphore = None

    # is_invalid_mail_account = False
    # is_there_internet_connection = True

    def __init__(self, settings_data, length_of_core_list, tray_icon, current_path):
        self.settings_data = settings_data
        self.length_of_core_list = length_of_core_list
        self.tray_icon = tray_icon
        self.current_path = current_path

        self.semaphore = threading.Semaphore()

    def initiate(self, list_of_mail_cores):
        for core in list_of_mail_cores:
            threading.Thread(target=self.on_new_mail, args=(core,)).start()
            threading.Thread(target=self.on_no_internet, args=(core,)).start()
            threading.Thread(target=self.on_invalid_mail_account, args=(core,)).start()

    def on_new_mail(self, core):
        while True:
            core.new_mail_trigger.wait()
            self.semaphore.acquire()

            self.tray_icon.set_from_file(
                self.current_path + self.settings_data["new_messages_tray_icon"])

            self.semaphore.release()

            if self.settings_data["action_on_new_mail"] != "":
                # TODO: on new mails
                os.system(self.settings_data["action_on_new_mail"] + " 2> /dev/null &")

            core.new_mail_trigger.clear()

    def on_no_internet(self, core):
        while True:
            core.no_internet_connection_trigger.wait()

            self.semaphore.acquire()

            self.tray_icon.set_from_file(
                self.current_path + self.settings_data["error_tray_icon"])

            self.semaphore.release()

            core.no_internet_connection_trigger.clear()

    def on_invalid_mail_account(self, core):
        while True:
            core.invalid_mail_trigger.wait()

            self.semaphore.acquire()

            self.tray_icon.set_from_file(
                self.current_path + self.settings_data["error_tray_icon"])

            self.semaphore.release()

            core.invalid_mail_trigger.clear()