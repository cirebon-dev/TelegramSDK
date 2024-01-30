# -*-coding:utf8;-*-
from zcache import Cache
from .TelegramSDK import TelegramSDK
from .util import util
import time
import os
import requests
import logging
import json


logging.basicConfig(format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S")


class telegram(TelegramSDK):
    """
    Python Telegram bot SDK that can be run on every Python 3.
    this is class high level, for low level section see TelegramSDK.py
    author: guangrei.
    """

    def update(data):
        """
        Function to update TelegramSDK.data
        Args:
            - data (str or dict): data telegram webhook json.
        """
        if type(data) == str:
            data = json.loads(data)
        TelegramSDK.data = util.parse_response(data)

    def set_token(token):
        """
        Use this method to set telegram.token manually.
        Args:
            - token (str): Telegram bot Api token.
        """
        TelegramSDK.token = token

    def disable_ssl():
        """
        Use this method to disable ssl verification.
        """
        TelegramSDK.ssl_verify = False

    def download_file(path, max_size=0, filter=()):
        """
        Use this method to auto download file.
        Args:
            - path (str): Directory for downloaded files.
            - max_fize (int, optional): Limit file size to be downloaded. Default to 0 (no limit).
            - filter (list or tuple): Filter file extension to be downloaded. Default to ()
        Returns:
            - list: List of path downloaded files.
        """
        result = util.find(telegram.data, "file_id")
        output = []
        for file_id in result:
            p = telegram.get_file(file_id)
            file_name = os.path.basename(p.result.file_path)
            file_ext = os.path.splitext(file_name)[1]
            if max_size > 0 and p.result.file_size > max_size:
                continue
            if len(filter) and file_ext.lower() not in filter:
                continue
            api = (
                "https://api.telegram.org/file/bot"
                + telegram.token
                + "/"
                + p.result.file_path
            )
            r = requests.get(api, verify=telegram.ssl_verify)
            save = util.uniq_file(path, file_name)
            util.save_file(r.content, save)
            output.append(save)
        if TelegramSDK.method == "poll" and TelegramSDK.worker == 1:
            telegram.get_updates(offset=telegram.data.update_id + 1, limit=1)
        return output

    def reply_message(*args, **kwargs):
        """
        Use this method to quick reply with text message.
        """
        kwargs["chat_id"] = telegram.data.message.chat.id
        kwargs["reply_to_message_id"] = telegram.data.message.message_id
        ret = telegram.send_message(*args, **kwargs)
        if TelegramSDK.method == "poll" and TelegramSDK.worker == 1:
            telegram.get_updates(
                offset=telegram.data.update_id + 1, limit=1
            )  # remove from queue
        return ret

    def reply_file(path, **kwargs):
        """
        Use this method to quick reply with file.
        """
        kwargs["chat_id"] = telegram.data.message.chat.id
        kwargs["document"] = path
        kwargs["reply_to_message_id"] = telegram.data.message.message_id
        ret = telegram.send_document(**kwargs)
        if TelegramSDK.method == "poll" and TelegramSDK.worker == 1:
            telegram.get_updates(
                offset=telegram.data.update_id + 1, limit=1
            )  # remove from queue
        return ret

    def _feeder(interval, queue, debug):
        """
        This is private function, to be used as feeder in multiprocessing poll.
        """
        if debug:
            logging.warning("feeder started!")
        try:
            while True:
                data = telegram.get_updates()
                if data["ok"]:
                    for i in data["result"]:
                        if "message" in i:
                            if debug:
                                logging.warning("feeder: enqueue %d.", i["update_id"])
                            queue.put_nowait(i)
                            telegram.get_updates(offset=i["update_id"] + 1, limit=1)
                else:
                    raise ValueError(data)
                if interval:
                    time.sleep(interval)
        except BaseException as e:
            logging.error(str(e))
            exit(1)

    def _worker(name, callback, queue, debug=False):
        """
        This is private function, to be used as worker in multiprocessing poll.
        """
        if debug:
            logging.warning("worker %d start!", name)
        try:
            while True:
                if not queue.empty():
                    data = queue.get()
                    if debug:
                        logging.warning(
                            "worker %d: dequeue %d.", name, data["update_id"]
                        )
                    try:
                        callback(data)
                    except BaseException as e:
                        logging.exception("Exception occurred!")
        except BaseException as e:
            logging.error(str(e))
            exit(1)

    def poll(callback, interval=1, worker=1, debug=False):
        """
        Use this method to poll the bot.
        Args:
            - callback (callable): Function to handle user data.
            - interval (int): Interval number for request looping, set 0 to no interval. Default to 1.
            - worker (int): Number of worker. Default to 1 (without multiprocessing).
            - debug (bool, optional): Show more verbose in multiprocessing mode. Default to False.
        """
        TelegramSDK.method = "poll"
        TelegramSDK.remove_webhook()
        logging.warning(
            "Running telegram.poll() with %d interval and %d worker.", interval, worker
        )
        if worker > 1:
            import multiprocessing

            q = multiprocessing.Queue()
            processes = []
            TelegramSDK.worker = worker
            process = multiprocessing.Process(
                target=telegram._feeder, args=(interval, q, debug)
            )
            process.start()
            processes.append(process)
            for i in range(worker):
                process = multiprocessing.Process(
                    target=telegram._worker, args=(i + 1, callback, q, debug)
                )
                process.start()
                processes.append(process)
            for process in processes:
                process.join()
        else:
            while True:
                data = telegram.get_updates()
                if data["ok"]:
                    for i in data["result"]:
                        if "message" in i:
                            try:
                                callback(i)
                            except BaseException as e:
                                logging.exception("Exception occurred!")
                else:
                    raise ValueError(data)
                if interval:
                    time.sleep(interval)

    def set_session(value, ttl=0, database="database.json"):
        """
        Function set_session based user id and chat id.
        Args:
            - value (Any): Json serialize able object (str, int, dict, bool etc)
            - ttl (int, optional): Limit time to life. Default to 0 (no limit).
            - database (str, optional): Zcache database path. Default to database.json.
        """

        data = telegram.data
        id = str(data.message._from.id)
        chat_id = str(data.message.chat.id)
        c = Cache(path=database)
        if not c.has(id):
            data = data.message._from
            data["session_" + chat_id] = value
            c.set(id, data, ttl=ttl)
        else:
            data = c.get(id)
            data["session_" + chat_id] = value
            c.set(id, data, ttl=ttl)

    def get_session(database="database.json"):
        """
        Function get_session based user id and chat id.
        Args:
            database (str, optional): Zcache database path. Default to database.json.
        Returns:
            - Any: session value if exists.
            - None: if session not exists.
        """

        data = telegram.data
        id = str(data.message._from.id)
        chat_id = str(data.message.chat.id)
        c = Cache(path=database)
        if not c.has(id):
            return None
        else:
            data = c.get(id)
            return data["session_" + chat_id]
