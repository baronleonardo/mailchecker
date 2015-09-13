import os
import sqlite3
import sys


class DatabaseController:
    db_file = "db"
    table_name = "mail_accounts_data"
    current_path = ""

    def __init__(self, current_path):
        self.current_path = current_path
    
    def db_exists(self):
        # Check if mail account file exists
        f = os.path.exists(self.current_path + self.db_file)
        if f is False:
            return False
        else:
            return True

    def on_db_not_found(self):
        # create a db file
        os.system("touch '" + self.current_path + self.db_file + "'")

        # Connect to the database
        db_conn = sqlite3.connect(self.db_file)
        # Create a cursor
        db_cursor = db_conn.cursor()

        # create table
        list_of_mails = db_cursor.execute('''CREATE TABLE %s (
                                          mailbox_name,
                                          email	TEXT,
                                          password	TEXT,
                                          mailIMAP	TEXT,
                                          mailbox	TEXT DEFAULT 'INBOX',
                                          checker_timer_in_minutes	INTEGER );'''
                                          % self.table_name)
        # Close the Database
        db_conn.close()

    def load(self):
        # Connect to the database
        db_conn = sqlite3.connect(self.db_file)
        # Create a cursor
        db_cursor = db_conn.cursor()

        # Get the list of mail accounts
        list_of_mails = db_cursor.execute("SELECT * FROM %s" % self.table_name)

        # Close the database
        # db_conn.close()

        return list_of_mails

    def insert(self, mail_data):
        # Connect to the database
        db_conn = sqlite3.connect(self.db_file)
        # Create a cursor
        db_cursor = db_conn.cursor()

        data = (mail_data["mailbox_name"], mail_data["email"], mail_data["password"], mail_data["mailIMAP"],
                mail_data["checker_timer_in_minutes"])

        # Insert row of data into the database
        db_cursor.execute("INSERT INTO " +
                          self.table_name +
                          " (`mailbox_name`, `email`,`password`,`mailIMAP`,`checker_timer_in_minutes`)" +
                          " VALUES (?,?,?,?,?);", data)
        db_conn.commit()
        # Close the database
        db_conn.close()

    def remove(self, row_id):
        # Connect to the database
        db_conn = sqlite3.connect(self.db_file)
        # Create a cursor
        db_cursor = db_conn.cursor()

        row_id = (str(row_id),)

        # Insert row of data into the database
        db_cursor.execute("DELETE FROM " + self.table_name + " WHERE `_rowid_`=?;", row_id)
        db_conn.commit()

        db_conn.close()

    def update(self, row_id, mail_data):
        # Connect to the database
        db_conn = sqlite3.connect(self.db_file)
        # Create a cursor
        db_cursor = db_conn.cursor()

        data = (mail_data["mailbox_name"], str(mail_data["email"]), str(mail_data["password"]),
                str(mail_data["mailIMAP"]), str(mail_data["checker_timer_in_minutes"]), str(row_id))

        # create table
        list_of_mails = db_cursor.execute("UPDATE " + self.table_name +
                                          ''' SET `mailbox_name`=?, `email`=?, `password`=?, `mailIMAP`=?,
                                           `checker_timer_in_minutes`=? WHERE
                                           `_rowid_`=?;''', data)
        db_conn.commit()
        # Close the Database
        db_conn.close()
