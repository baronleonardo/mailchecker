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
1. Simply open a terminal and run `python2 mail_checker.py`
2. In the settings dialog place you email and your password.

Example for what you might type into the settings dialog:
---------------------------------------------------
```
example@mail.com  
PASSWORD 
imap.mail.com
```
### as for the IMAP field, here's an example of what you should type in:
- Gmail -> `imap.gmail.com`	
- Yahoo -> `imap.yahoo.com` 

TO-DO list:
------------
- [ ] App freezes when checking for mails, that needs to be fixed (maybe use threads?).
- [ ] Restart timer on new mail account.
- [ ] Create new method - on_new_mail() - for better code readiblity and organization.
- [ ] Support for multiple accounts.
- [ ] User can change applet icons from the settings dialog.
- [ ] User can run a command or a script if he recieves a new mail.
- [ ] User can run a command or a script if he left-click on the tray icon.
- [ ] Save user data in default configuration folder (in the ~/.config/ or something). 
- [ ] Edit existing mail account.
