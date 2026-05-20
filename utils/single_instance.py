import msvcrt
from pathlib import Path

from utils.logger import LOG_DIR, get_logger


logger = get_logger(__name__)


class SingleInstance:
    def __init__(self, lock_name: str = "app.lock"):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.lock_path = LOG_DIR / lock_name
        self.lock_file = None
        self.acquired = False

    def __enter__(self):
        self.lock_file = open(self.lock_path, "a+")
        try:
            msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
            self.acquired = True
            logger.info("Application lock acquired: %s", self.lock_path)
        except OSError:
            self.acquired = False
            logger.warning("Another backup app instance is already running")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.lock_file:
            if self.acquired:
                try:
                    self.lock_file.seek(0)
                    msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                    logger.info("Application lock released")
                except OSError as e:
                    logger.warning("Could not release application lock: %s", e)
            self.lock_file.close()