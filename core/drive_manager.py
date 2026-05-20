import os
import subprocess

from utils.logger import get_logger


logger = get_logger(__name__)


class DriveManager:
    """
    Responsible for uploading backups to Google Drive with rclone.
    """

    def __init__(self, rclone_path: str, remote_path: str):
        self.rclone_path = rclone_path
        self.remote_path = remote_path

    def upload_backup(self, file_path: str) -> bool:
        try:
            if not os.path.exists(self.rclone_path):
                logger.error("rclone executable not found: %s", self.rclone_path)
                return False

            if not os.path.exists(file_path):
                logger.error("Backup file not found: %s", file_path)
                return False

            command = [
                self.rclone_path,
                "copy",
                file_path,
                self.remote_path,
            ]

            startupinfo = None
            creationflags = 0
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW

            logger.info("Uploading backup %s to %s", file_path, self.remote_path)
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300,
                startupinfo=startupinfo,
                creationflags=creationflags,
            )
            if result.returncode == 0:
                logger.info("Backup uploaded successfully")
                return True

            logger.error("Upload failed with exit code %s", result.returncode)
            if result.stderr:
                logger.error("rclone error: %s", result.stderr.strip())
            return False

        except subprocess.TimeoutExpired:
            logger.exception("Upload timed out")
            return False
        except PermissionError as e:
            logger.exception("Permission error during upload: %s", e)
            return False
        except Exception as e:
            logger.exception("Error uploading backup: %s", e)
            return False