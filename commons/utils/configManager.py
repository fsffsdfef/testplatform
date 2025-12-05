import os
import threading
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._config = {}
            self._load_config()
            self._initialized = True

    def _load_config(self):
        self._config_update()

    def _config_update(self):
        pass
