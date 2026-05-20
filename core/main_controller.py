from core.config_loader import ConfigLoader
from core.app_monitor import AppMonitor
from core.folder_watcher import FolderWatcher
from core.backup_manager import BackupManager
from core.drive_manager import DriveManager
from utils.logger import get_logger


logger = get_logger(__name__)


class MainController:
    REQUIRED_CONFIG_KEYS = (
        "app_name",
        "folder_to_watch",
        "backup_dir",
        "backup_name",
        "rclone_path",
        "remote_path",
        "check_interval",
    )

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = None

        self.app_monitor = None
        self.folder_watcher = None
        self.backup_manager = None
        self.drive_manager = None

    def setup(self) -> bool:
        try:
            loader = ConfigLoader(self.config_path)
            self.config = loader.load()

            if self.config is None:
                logger.error("Failed to load config")
                return False

            missing_keys = [key for key in self.REQUIRED_CONFIG_KEYS if key not in self.config]
            if missing_keys:
                logger.error("Missing config keys: %s", ", ".join(missing_keys))
                return False

            self.app_monitor = AppMonitor(
                app_name=self.config["app_name"],
                check_interval=int(self.config["check_interval"]),
            )

            self.folder_watcher = FolderWatcher(
                path=self.config["folder_to_watch"],
            )

            self.backup_manager = BackupManager(
                source_path=self.config["folder_to_watch"],
                backup_dir=self.config["backup_dir"],
                backup_name=self.config["backup_name"],
            )

            self.drive_manager = DriveManager(
                rclone_path=self.config["rclone_path"],
                remote_path=self.config["remote_path"],
            )

            return True
        except Exception as e:
            logger.exception("Setup failed: %s", e)
            return False

    def run(self):
        if not self.setup():
            return

        logger.info("Automatic backup controller started")

        try:
            while True:
                watcher_started = False

                self.app_monitor.wait_for_open()

                if not self.folder_watcher.start():
                    logger.error("Could not start folder watcher")
                    continue
                watcher_started = True

                try:
                    self.app_monitor.wait_for_close()
                finally:
                    if watcher_started:
                        self.folder_watcher.stop()

                self.backup_if_changed()
                self.folder_watcher.reset()
        except KeyboardInterrupt:
            logger.info("Application stopped by user")
        except Exception as e:
            logger.exception("Unexpected application error: %s", e)

    def backup_if_changed(self):
        if not self.folder_watcher.has_changes():
            logger.info("No changes detected. Waiting for next app open")
            return

        logger.info("Changes detected. Creating backup")
        backup_path = self.backup_manager.create_backup()

        if not backup_path:
            logger.error("Backup creation failed")
            return

        logger.info("Uploading backup to Google Drive")
        if not self.drive_manager.upload_backup(backup_path):
            logger.error("Backup upload failed")