import os


class Config(object):
    SECRET_KEY = os.urandom(24).hex()
    ENABLE_LOG = 1
