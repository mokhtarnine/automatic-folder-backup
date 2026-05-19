from pathlib import Path
import shutil
import zipfile


class BackupManager:
    def __init__(self, source_path: str, backup_dir: str, backup_name: str):
        self.source_path = Path(source_path)
        self.backup_dir = Path(backup_dir)
        self.backup_name = backup_name

    def get_backup_path(self) -> Path:
        return self.backup_dir / self.backup_name

    def create_backup(self) -> str | None:
        try:
            if not self.source_path.exists():
                raise FileNotFoundError(f"Source path does not exist: {self.source_path}")

            self.backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = self.get_backup_path()

            if backup_path.exists():
                backup_path.unlink()

            if self.source_path.is_dir():
                base_name = str(backup_path.with_suffix(""))
                shutil.make_archive(base_name, "zip", root_dir=str(self.source_path))
            else:
                with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    zip_file.write(self.source_path, arcname=self.source_path.name)

            return str(backup_path)
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None