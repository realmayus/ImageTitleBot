# ImageTitleBot
A reddit bot that puts posts' titles above their image.


# How to use
Just mention the bot's username in a comment below a post with an image.

# How to run
Ideally, create a virtual environment at first.
Then install all requirements using `python3 -m pip install -r requirements.txt`.
Now create a config file called `config.ini` and populate it with these values:

```ini
[reddit]
user_agent =    ; bot_username (by /u/your_username)
client_id =   ; Obtain this by creating a reddit script application
client_secret = ; Obtain this by creating a reddit script application
username = ; The username of the bot's reddit account
password = ; The password of the bot's reddit account

[imgur]
client_id =  ; Obtain this by creating an anonymous imgur application.
```

After that just start the script using python: `python3 main.py`
