from typing import Any

import yaml

from utils.logger import get_logger


logger = get_logger(__name__)


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
                logger.info("Config loaded from %s", self.config_path)
                return self.config
        except Exception as e:
            logger.exception("Error loading config file: %s", e)
            return None