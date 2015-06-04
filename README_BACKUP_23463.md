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

<<<<<<< HEAD
### as for the IMAP field, here's an example of what you should type in:
- Gmail -> `imap.gmail.com`
- Yahoo -> `imap.yahoo.com`
=======
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
>>>>>>> 57d1118813d5606c0d6bfcd2c952b62232794b78
