from pathlib import Path
import zipfile

from utils.logger import get_logger


logger = get_logger(__name__)


class BackupManager:
    """
    Creates a zip backup from a file or a folder.
    """

    def __init__(self, source_path: str, backup_dir: str, backup_name: str):
        self.source_path = Path(source_path).expanduser()
        self.backup_dir = Path(backup_dir).expanduser()
        self.backup_name = backup_name

    def get_backup_path(self) -> Path:
        return self.backup_dir / self.backup_name

    def create_backup(self) -> str | None:
        try:
            source_path = self.source_path.resolve()
            if not source_path.exists():
                raise FileNotFoundError(f"Source path does not exist: {source_path}")

            self.backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = self.get_backup_path().resolve()

            if backup_path.exists():
                backup_path.unlink()
                logger.info("Removed old backup: %s", backup_path)

            file_count = 0
            skipped_count = 0
            with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
                if source_path.is_dir():
                    for file_path in source_path.rglob("*"):
                        if not file_path.is_file():
                            continue

                        try:
                            zip_file.write(file_path, arcname=file_path.relative_to(source_path))
                            file_count += 1
                        except OSError as e:
                            skipped_count += 1
                            logger.warning("Skipped unreadable file %s: %s", file_path, e)
                else:
                    zip_file.write(source_path, arcname=source_path.name)
                    file_count = 1

            if file_count == 0:
                raise ValueError(f"No files were added to backup from: {source_path}")

            if skipped_count:
                logger.warning("Backup completed with %s skipped files", skipped_count)

            logger.info("Backup created with %s files: %s", file_count, backup_path)
            return str(backup_path)
        except Exception as e:
            logger.exception("Error creating backup: %s", e)
            return None