from typing import Any

import yaml


class ConfigLoader:
    """
    Config loader is responsible for loading configuration.
    """

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: dict[str, Any] = {}

    def load(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as file:
                self.config = yaml.safe_load(file) or {}
                return self.config
        except Exception as e:
            print(f"Error loading config file: {e}")
            return None