import json
import os
import threading

PATH = (
    '/etc/DTunnelManager/' if os.geteuid() == 0 else os.path.expanduser('~/.config/DTunnelManager/')
)

CONFIG_FILE = 'config.json'
CONFIG_FILE_PATH = os.path.join(PATH, CONFIG_FILE)

DEFAULT_CONFIG = {'bot_token': '', 'admin_id': -1}

if not os.path.exists(PATH):
    os.makedirs(PATH)

if not os.path.exists(CONFIG_FILE_PATH):
    with open(CONFIG_FILE_PATH, 'w') as f:
        json.dump(DEFAULT_CONFIG, f)


class ConfigParser:
    __lock = threading.Lock()

    def __init__(self):
        self.config = {}
        self.load()

    def load(self):
        with self.__lock:
            with open(CONFIG_FILE_PATH, 'r') as f:
                self.config = json.load(f)

    def save(self):
        with self.__lock:
            with open(CONFIG_FILE_PATH, 'w') as f:
                json.dump(self.config, f)

    def get(self, key):
        with self.__lock:
            return self.config[key]

    def set(self, key, value):
        with self.__lock:
            self.config[key] = value

        self.save()

    def delete(self, key):
        with self.__lock:
            del self.config[key]
            self.save()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()
