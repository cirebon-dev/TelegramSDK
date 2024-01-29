# -*-coding:utf8;-*-
from datetime import datetime
import os


class util:
    """Class utility."""

    def parse_response(data):
        """
        Function to make telegram response accessible through dot "." like an object.
        The key "from" renamed to "_from" to avoid conflict with Python keyword "from".
        This function used in telegram.update()
        Args:
            - data (dict): json decoded from telegram response.
        Returns:
            - dict: dict that can be accessed like an object.
        """

        def format_dict_nested(dictionary):
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    format_dict_nested(value)
                    dictionary[key] = objectify(value)
            return dictionary

        class objectify(dict):
            __slots__ = ()
            __getattr__ = dict.__getitem__
            __setattr__ = dict.__setitem__

        def parse(array):
            if "message" in array and "from" in array["message"]:
                array["message"]["_from"] = array["message"]["from"]
                del array["message"]["from"]
            u = format_dict_nested(array)
            return objectify(u)

        ret = parse(data)
        return ret

    def get_command(msg):
        """
        Use this method to parse command.
        Args:
            - msg (str): Text message.
        Returns:
            - str: if command found.
            - None: if command not found.
        """
        if msg.startswith("/"):
            command = msg.split(" ")[0]
            command = command.split("@")[0]
            return command.strip()
        else:
            return None

    def get_text(msg):
        """
        Use this method to parse text.
        Args:
            - msg (str): Text message.
        Returns:
            - str: if text found.
            - None: if text not found.
        """
        if msg.startswith("/"):
            text = msg.split(" ")
            if len(text) > 1:
                del text[0]
                text = " ".join(text)
                return text.strip()
            else:
                return None
        else:
            return msg.strip()

    def save_file(content, local_path):
        """
        This function used in telegram.download_file().
        Args:
            - content (str or binary): File Content.
            - path (str): File name or path
        """
        if type(content) == str:
            with open(local_path, "w") as f:
                f.write(content)
        else:
            with open(local_path, "wb") as f:
                f.write(content)

    def find(data, search):
        """
        Function to recursive search value of a dict key.
        This function used in telegram.download_file().
        """

        def _inner(obj, search):
            # Check if current object contains search directly at root level
            if isinstance(obj, dict) and search in obj:
                yield obj[search]

            # Iterate over dictionary items excluding special case above which has already been handled
            elif isinstance(obj, dict):
                for _, value in obj.items():
                    yield from _inner(value, search)

            # Process individual elements when iterable object is given such as a list
            elif isinstance(obj, (list, tuple)):
                for item in obj:
                    yield from _inner(item, search)

        return tuple(_inner(data, search))

    def uniq_file(path, filename):
        """
        Function to generate unique file name.
        This function used in telegram.download_file().
        """
        basename, ext = os.path.splitext(filename)
        now = datetime.now().strftime("%Y%m%d_%H%M%S_")
        new_basename = now + basename

        return os.path.join(path, new_basename + ext)
