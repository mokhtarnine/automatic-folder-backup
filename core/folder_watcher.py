from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from utils.logger import get_logger


logger = get_logger(__name__)

"""
This file is responsible for watching a folder and recording file changes.
"""


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, watcher):
        self.watcher = watcher

    def _record(self, message: str):
        self.watcher.changed = True
        self.watcher.events.append(message)
        logger.info(message)

    def on_created(self, event):
        self._record(f"created: {event.src_path}")

    def on_modified(self, event):
        self._record(f"modified: {event.src_path}")

    def on_deleted(self, event):
        self._record(f"deleted: {event.src_path}")

    def on_moved(self, event):
        self._record(f"moved: {event.src_path} -> {event.dest_path}")


class FolderWatcher:
    def __init__(self, path: str):
        self.path = path
        self.observer = None
        self.changed = False
        self.events = []

    def start(self) -> bool:
        try:
            watch_path = Path(self.path).expanduser().resolve()
            if not watch_path.exists():
                raise FileNotFoundError(f"Folder to watch does not exist: {watch_path}")
            if not watch_path.is_dir():
                raise NotADirectoryError(f"Path to watch is not a folder: {watch_path}")

            self.reset()
            handler = ChangeHandler(self)
            self.observer = Observer()
            self.observer.schedule(handler, str(watch_path), recursive=True)
            self.observer.start()

            logger.info("Started watching folder: %s", watch_path)
            return True
        except Exception as e:
            logger.exception("Error starting folder watcher: %s", e)
            self.observer = None
            return False

    def stop(self):
        if not self.observer:
            return

        try:
            self.observer.stop()
            self.observer.join()
            logger.info("Stopped watching folder: %s", self.path)
        except Exception as e:
            logger.exception("Error stopping folder watcher: %s", e)
        finally:
            self.observer = None

    def reset(self):
        self.changed = False
        self.events = []

    def has_changes(self) -> bool:
        return self.changed

    def get_changes(self) -> list:
        return self.events