[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![status workflow test](https://github.com/cirebon-dev/TelegramSDK/actions/workflows/python-app.yml/badge.svg)](https://github.com/cirebon-dev/TelegramSDK/actions) 
[![status workflow build](https://github.com/cirebon-dev/TelegramSDK/actions/workflows/release_to_pypi.yml/badge.svg)](https://github.com/cirebon-dev/TelegramSDK/actions)
[![Downloads](https://static.pepy.tech/badge/TelSDK)](https://pepy.tech/project/TelSDK)

# TelegramSDK

There are already many telegram bot libraries for Python, but I wrote my own version according to my expectations

- Compatible with any python version (2 & 3).

- Allow multiprocessing.

- Easy to use.

- etc

Not all telegram bot api methods are implemented yet and you are welcome to contribute :)

## Installation

> Note: If you are running an older version of Python, you must first install a version of the requests library that is compatible with your current Python version.


with pip:
```
pip install TelSDK
```
with poetry:
```
poetry add TelSDK
```
from source:
```
python setup.py install
```

## Example Usage

Example with poll method:

```python
# -*-coding:utf8;-*-
from TelegramSDK import telegram as bot


# telegram token is automatic loaded from environment variable TELEGRAM_BOT_TOKEN but you can also set it manually
bot.set_token("your token")

# call this function if you run on old device
# bot.disable_ssl()


def handler(data):
    bot.update(data)
    download_photo = bot.download_file("/tmp", filter=(".jpeg", ".jpg", ".png"))
    if len(download_photo):
        bot.reply_message("Photo downloaded: {}".format(download_photo))
    else:
        try:
            # user not send any file
            bot.reply_message("OK: " + bot.data.message.text)
            """
            or  reply with file bot.reply_file("path/to/file/example.pdf", caption="example file!")
            """
        except BaseException as e:
            # handle user send file but not photo
            bot.reply_message("file not supported!")


bot.poll(handler, worker=5, debug=True)
```

Example with webhook (flask, bottle etc)

```python
@post("/webhook")
def handler():
    bot.update(request.json)
    bot.reply_message("OK: " + bot.data.message.text)
```

TelegramSDK has built-in session function based [zcache](https://pypi.org/project/zcache), for example:

```python
if bot.get_session():
    count = bot.get_session() + 1
    bot.set_session(count, ttl=3600)
    bot.reply_message("count: %d" % count)
else:
    bot.set_session(1, ttl=3600)
    bot.reply_message("count: 1")
```

for more doc please read the source code.

## License

MIT