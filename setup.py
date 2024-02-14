#!/usr/bin/env python
import sys
from setuptools import setup
from os import path


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md")) as f:
    long_description = f.read()
setup(
    name="TelSDK",
    version="v0.1.1",
    description="Synchronous Telegram bot SDK for python 2 & 3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="guangrei",
    author_email="myawn@pm.me",
    url="https://github.com/cirebon-dev/TelegramSDK",
    packages=["TelegramSDK"],
    license="MIT",
    platforms="any",
    install_requires=["requests", "zcache"],
)
