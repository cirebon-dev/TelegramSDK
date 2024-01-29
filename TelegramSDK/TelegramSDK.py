# -*-coding:utf8;-*-
from .util import util
import os
import json
import requests


class TelegramSDK:
    """
    Python Telegram bot SDK that can be run on every Python 3.
    this is class low level, for high level section see telegram.py
    author: guangrei
    """

    token = "xxx"
    ssl_verify = True
    data = None
    method = "webhook"
    worker = 1
    headers = {
        "accept": "application/json",
        "User-Agent": "Telegram Bot SDK - (https://github.com/cirebon-dev/TelegramSDK",
    }

    def set_webhook(url, certificate=None):
        """
        Use this method to specify a url and receive incoming updates via an outgoing webhook.
        Args:
            - url (str): HTTPS url to send updates to. Use an empty string to remove webhook integration.
            - certificate (str, optional): Path to certificate file. Default to None.
        Returns:
            - dict: dict that can be accessed like an object.
        """
        api = TelegramSDK.get_endpoints() + "setWebHook"
        data = {"url": url}
        if certificate is not None:
            files = {"certificate": (os.path.basename(certificate), open(certificate))}
            ret = requests.post(
                api, data=data, files=files, verify=TelegramSDK.ssl_verify
            ).json()
        else:
            ret = requests.post(
                api,
                data=data,
                headers=TelegramSDK.headers,
                verify=TelegramSDK.ssl_verify,
            ).json()
        return util.parse_response(ret)

    def remove_webhook():
        """
        Use this method to remove a previously set outgoing webhook.
        Returns:
            - dict: dict that can be accessed like an object.
        """
        api = TelegramSDK.get_endpoints() + "setWebhook?remove"
        data = {"url": "Empty"}
        ret = requests.post(
            api,
            data=data,
            headers=TelegramSDK.headers,
            verify=TelegramSDK.ssl_verify,
        ).json()
        return util.parse_response(ret)

    def get_updates(offset=None, limit=100, timeout=0):
        """
        Use this method to receive incoming updates using long polling.
        Args:
            - offset (int, optional): Identifier of the first update to be returned. Must be greater by one than the highest among the identifiers of previously received updates. By default, updates starting with the earliest unconfirmed update are returned. An update is considered confirmed as soon as getUpdates is called with an offset higher than its update_id. The negative offset can be specified to retrieve updates starting from -offset update from the end of the updates queue. All previous updates will forgotten. Defaults to None.
            - limit (int, optional): Limits the number of updates to be retrieved. Values between 1—100 are accepted. Defaults to 100.
            - timeout (int, optional): Timeout in seconds for long polling. Defaults to 0.
        Returns:
            - dict: dict that can be accessed like an object.
        """
        data = {"offset": offset, "limit": limit, "timeout": timeout}
        api = TelegramSDK.get_endpoints() + "getUpdates"
        ret = requests.post(
            api,
            data=data,
            headers=TelegramSDK.headers,
            verify=TelegramSDK.ssl_verify,
        ).json()
        return ret

    def send_message(
        text,
        chat_id,
        parse_mode=None,
        disable_web_page_preview=False,
        disable_notification=False,
        reply_to_message_id=None,
        reply_markup=None,
    ):
        """
        Use this method to send text messages.
        Args:
            - text (str): Text of the message to be sent.
            - chat_id (str): Unique identifier for the target chat or username of the target channel (in the format @channelusername).
            - parse_mode (str, optional): Send Markdown or HTML, if you want Telegram apps to show bold, italic, fixed-width text or inline URLs in your bot's message. Defaults to None.
            - disable_web_page_preview (bool, optional): Disables link previews for links in this message. Defaults to False.
            - disable_notification (bool, optional): Sends the message silently. iOS users will not receive a notification, Android users will receive a notification with no sound. Other apps coming soon. Defaults to False.
            - reply_to_message_id (int, optional): If the message is a reply, ID of the original message. Defaults to None.
            reply_markup (str, optional): reply markup. Defaults to None.
        Returns:
            - dict: dict that can be accessed like an object.
        """
        api = TelegramSDK.get_endpoints() + "sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": disable_web_page_preview,
            "disable_notification": disable_notification,
        }
        if parse_mode:
            data["parse_mode"] = parse_mode
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        if reply_markup:
            data["reply_markup"] = reply_markup
        ret = requests.post(
            api,
            data=data,
            headers=TelegramSDK.headers,
            verify=TelegramSDK.ssl_verify,
        ).json()
        return util.parse_response(ret)

    def send_document(
        chat_id,
        document,
        caption=None,
        disable_notification=False,
        reply_to_message_id=None,
    ):
        """
        Use this method to send general files.
        Args:
            - document (str): File to send. You can either pass a file_id as String to resend a file that is already on the Telegram servers, or upload a new file by just passing the path to the file as String and the SDK will take care of uploading it for you.
            - chat_id (str): Unique identifier for the target chat or username of the target channel (in the format @channelusername)
            - caption (str, optional): Document caption (may also be used when resending documents by file_id), 0-200 characters. Default to None.
            - disable_notification (bool, optional): Sends the message silently. iOS users will not receive a notification, Android users will receive a notification with no sound. Other apps coming soon. Defaults to False.
            - reply_to_message_id (int, optional): If the message is a reply, ID of the original message. Defaults to None.
        Returns:
            - dict: dict that can be accessed like an object.
        """

        api = TelegramSDK.get_endpoints() + "sendDocument"
        try:
            data = {
                "chat_id": chat_id,
                "reply_to_message_id": reply_to_message_id,
                "caption": caption,
                "disable_notification": disable_notification,
            }
            files = {"document": (os.path.basename(document), open(document, 'rb'))}
            ret = requests.post(
                api, data=data, files=files, verify=TelegramSDK.ssl_verify
                ).json()
        except BaseException as e:
            data["document"] = document
            ret = requests.post(
                api,
                data=data,
                headers=TelegramSDK.headers,
                verify=TelegramSDK.ssl_verify,
            ).json()
        return util.parse_response(ret)

    def send_chat_action(chat_id, action="typing"):
        """
        Args:
            - chat_id (str): Unique identifier for the target chat or username of the target channel (in the format @channelusername)
            - action (str, optional): Type of action to broadcast. Choose one, depending on what the user is about to receive: typing for text messages, upload_photo for photos, record_video or upload_video for videos, record_audio or upload_audio for audio files, upload_document for general files, find_location for location data. Defaults to "typing".
        Returns:
            - dict: dict that can be accessed like an object.
        """
        api = TelegramSDK.get_endpoints() + "sendChatAction"
        data = {"action": action}
        ret = requests.post(
            api,
            data=data,
            headers=TelegramSDK.headers,
            verify=TelegramSDK.ssl_verify,
        )
        return util.parse_response(ret)

    def get_endpoints():
        """
        Function to get telegram bot endpoints dynamically.
        Returns:
            - str: telegram bot endpoints.
        """
        token = os.environ.get("TELEGRAM_BOT_TOKEN", TelegramSDK.token)
        return "https://api.telegram.org/bot" + token + "/"

    def get_file(file_id):
        """
        Use this method to get basic info about a file and prepare it for downloading.
        Args:
            - file_id (int): File identifier to get info about
        Returns:
            - dict: dict that can be accessed like an object.
        """

        api = TelegramSDK.get_endpoints() + "getFile?file_id=" + file_id
        ret = requests.get(api, verify=TelegramSDK.ssl_verify).json()
        return util.parse_response(ret)
