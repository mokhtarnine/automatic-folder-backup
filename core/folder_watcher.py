from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

"""
This file is responsible for watching a folder and recording file changes.
"""


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, watcher):
        self.watcher = watcher

    def _record(self, message: str):
        self.watcher.changed = True
        self.watcher.events.append(message)

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

    def start(self):
        watch_path = Path(self.path).expanduser()
        if not watch_path.exists():
            raise FileNotFoundError(f"Folder to watch does not exist: {watch_path}")

        handler = ChangeHandler(self)
        self.observer = Observer()
        self.observer.schedule(handler, str(watch_path), recursive=True)
        self.observer.start()

        print(f"Started watching folder: {watch_path}")

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None

    def has_changes(self) -> bool:
        return self.changed

    def get_changes(self) -> list:
        return self.events