import time

import psutil

from utils.logger import get_logger


logger = get_logger(__name__)


class AppMonitor:
    """
    Watches whether the target app is open, then waits for open/close changes.
    """

    def __init__(self, app_name: str, check_interval: int):
        self.app_name = app_name
        self.check_interval = check_interval
        self.is_running = False

    def is_app_running(self) -> bool:
        try:
            for process in psutil.process_iter(["name"]):
                try:
                    if process.info["name"] == self.app_name:
                        self.is_running = True
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.exception("Error checking app process: %s", e)
            self.is_running = False
            return False

        self.is_running = False
        return False

    def start(self):
        logger.info("Monitoring %s", self.app_name)
        self.is_running = self.is_app_running()

        if self.is_running:
            logger.info("%s is running", self.app_name)
        else:
            logger.info("%s is not running", self.app_name)

    def wait_for_open(self):
        try:
            logger.info("Waiting for %s to open", self.app_name)
            while not self.is_app_running():
                time.sleep(self.check_interval)

            logger.info("%s is open", self.app_name)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.exception("Error while waiting for app to open: %s", e)

    def wait_for_close(self):
        try:
            logger.info("Waiting for %s to close", self.app_name)
            while self.is_app_running():
                time.sleep(self.check_interval)

            logger.info("%s is closed", self.app_name)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.exception("Error while waiting for app to close: %s", e)