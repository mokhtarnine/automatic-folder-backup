# Automatic Folder Backup

Automatic Folder Backup is a small Windows background tool that watches a folder only while a target application is open. When the app closes, the tool creates a zip backup if files changed, then uploads that backup to Google Drive using rclone.

This project was built for backing up an Obsidian vault, but it can be used with any app and folder.

## What It Does

The program follows this flow:

```text
Start program
Run quietly in background
Wait until target app opens
When target app opens -> watch folder
When target app closes -> stop watcher
If folder changed -> create zip backup
Upload backup to Google Drive with rclone
Wait for target app to open again
Repeat forever
```

## Features

- Runs quietly in the background with `pythonw.exe`
- Watches a folder only while the target app is open
- Creates a zip backup only when changes are detected
- Uploads backups to Google Drive using rclone
- Writes logs to `logs/app.log`
- Prevents duplicate background instances with a lock file
- Handles common errors such as missing config keys, missing rclone, upload failures, and unreadable files

## Project Structure

```text
folder_Backup/
|-- main.py
|-- requirements.txt
|-- README.md
|-- start_backup.vbs
|-- config/
|   `-- config.yaml
|-- core/
|   |-- app_monitor.py
|   |-- backup_manager.py
|   |-- config_loader.py
|   |-- drive_manager.py
|   |-- folder_watcher.py
|   `-- main_controller.py
|-- utils/
|   |-- __init__.py
|   |-- logger.py
|   `-- single_instance.py
|-- backups/
|   `-- latest_backup.zip
`-- logs/
    |-- app.log
    `-- app.lock
```

`backups/`, `logs/`, and `__pycache__/` are runtime/generated folders and should usually not be committed to GitHub.

## Requirements

- Windows 10 or Windows 11
- Python 3.10+
- rclone configured with a Google Drive remote
- A target application to monitor, for example `Obsidian.exe`

Python packages:

```text
watchdog
psutil
pyyaml
```

They are listed in `requirements.txt`.

## Installation

Clone the project:

```powershell
git clone <your-repo-url>
cd folder_Backup
```

Create a virtual environment:

```powershell
python -m venv venvback
```

Activate it:

```powershell
.\venvback\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

If your virtual environment is outside the repo, adjust the paths in the startup section.

## rclone Setup

Install or download rclone from:

```text
https://rclone.org/downloads/
```

Configure Google Drive:

```powershell
rclone config
```

Create a remote name. Example:

```text
Obsidian:
```

Test the remote:

```powershell
rclone lsd Obsidian:
```

Example upload test:

```powershell
rclone copy .\backups\latest_backup.zip Obsidian:Backups
```

## Configuration

Edit `config/config.yaml`:

```yaml
app_name: "Obsidian.exe"
folder_to_watch: 'C:\Users\YourName\OneDrive\Documents\Obsidian Vault'
backup_dir: "./backups"
backup_name: "latest_backup.zip"
rclone_path: 'C:\path\to\rclone.exe'
remote_path: 'Obsidian:Backups'
check_interval: 5
```

### Config Values

`app_name`:
The executable name of the app to monitor. For Obsidian, use:

```yaml
app_name: "Obsidian.exe"
```

`folder_to_watch`:
The folder that should be backed up.

`backup_dir`:
Where the zip backup will be created.

`backup_name`:
The backup zip file name.

`rclone_path`:
Full path to `rclone.exe`.

`remote_path`:
rclone remote destination. Example:

```yaml
remote_path: 'Obsidian:Backups'
```

`check_interval`:
How often the program checks if the target app opened or closed, in seconds.

## Run Manually

From the project folder:

```powershell
python main.py
```

For quiet background mode:

```powershell
pythonw main.py
```

If using a virtual environment:

```powershell
.\venvback\Scripts\python.exe main.py
```

or quietly:

```powershell
.\venvback\Scripts\pythonw.exe main.py
```

## Run At Windows Startup

The project includes `start_backup.vbs`, a small Windows launcher script.

It runs the program quietly and sets the working directory correctly.

Example `start_backup.vbs`:

```vbscript
Set shell = CreateObject("WScript.Shell")
shell.CurrentDirectory = "C:\path\to\folder_Backup"
shell.Run """C:\path\to\venvback\Scripts\pythonw.exe"" ""C:\path\to\folder_Backup\main.py""", 0, False
```

### Add To Startup Folder

Open the Startup folder:

```text
Win + R
shell:startup
```

Create a shortcut that points to:

```text
C:\path\to\folder_Backup\start_backup.vbs
```

After restart, Windows will run the backup watcher automatically.

## Logs

Logs are written here:

```text
logs/app.log
```

Check logs with:

```powershell
Get-Content .\logs\app.log -Tail 50
```

Useful messages include:

```text
Automatic backup controller started
Waiting for Obsidian.exe to open
Started watching folder
Changes detected. Creating backup
Backup created with X files
Backup uploaded successfully
```

## Duplicate Instance Protection

The app uses:

```text
logs/app.lock
```

This prevents multiple background copies from running at the same time. If another copy starts, it exits and logs:

```text
Another backup app instance is already running
```

## Troubleshooting

### rclone Window Appears

The project hides rclone with `CREATE_NO_WINDOW` in `core/drive_manager.py`. If a window still appears, check that the app is running the latest code and restart the background process.

### Upload Sometimes Fails

Check logs:

```powershell
Get-Content .\logs\app.log -Tail 100
```

Common causes:

- rclone path is wrong
- Google Drive remote is not configured
- Internet connection is unavailable
- More than one old copy of the app is still running

### Backup Zip Is Empty

Check the backup size:

```powershell
Get-Item .\backups\latest_backup.zip
```

Check zip contents:

```powershell
tar -tf .\backups\latest_backup.zip
```

If empty, verify `folder_to_watch` in `config/config.yaml`.

### Python Not Found

Check Python:

```powershell
python --version
```

If using a virtual environment:

```powershell
.\venvback\Scripts\python.exe --version
```

### App Does Not Start At Boot

Check the Startup folder:

```text
Win + R
shell:startup
```

Make sure the shortcut points to `start_backup.vbs`.

## GitHub Notes

Before pushing to GitHub, do not commit runtime files such as:

```text
__pycache__/
logs/
backups/
*.pyc
```

Also avoid committing personal machine-specific paths if you want other people to use the project. Keep `config/config.yaml` as an example or document that users must edit it for their own machine.

## License

Add a license file if you plan to publish this project publicly.