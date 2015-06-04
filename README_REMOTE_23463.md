# mailchecker
This is an attempt to create a simple mail checker
until now it has been tested on GNU/Linux only and uses IMAP only   

Requirements:
--------------
gtk2  
python2     
pygtk

How To Use:
------------
~~1. Create a file called 'credentials' in the same folder containing the script~~  
~~2. in the first line of that file type in your email~~  
~~3. in the second line type in your password~~   
~~4. in the third line type in your imap mail domain~~  
5. open a terminal and run `python2 mail_checker.py`

Example for how the credentials file may look like:
---------------------------------------------------

example@mail.com  
ENCRYPTED PASSWORD!   
imap.mail.com   
INBOX   

- Gmail -> "imap.gmail.com"   
- Yahoo -> "imap.yahoo.com"   

TO-DO list:
------------
- [ ] solve hang problem when the mail is checking
- [ ] restart timer on new mail account
- [ ] create new method - on_new_mail() - for a more tide organisation
- [ ] can add more than one mail account
- [ ] can change applet icons from the settings dialog
- [ ] user can run a command or a script if he recieves a new mail
- [ ] user can run a command or a script if he left-click on the tray icon
- [ ] save user data in default configuration folder
- [ ] edit existing mail account
