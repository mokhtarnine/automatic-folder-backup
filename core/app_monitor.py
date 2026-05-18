import time
import psutil

class AppMonitor:
    def __init__(self,app_name: str,check_interval:int):
        self.app_name = app_name
        self.check_interval = check_interval
        self.is_running = False

    def is_app_running(self) -> bool :
        for process in psutil.process_iter(["name"]):
            try:
                if process.info["name"] == self.app_name:
                    self.is_running = True
                    return True
            except(psutil.NoSuchProcess, psutil.AccessDenied ):
                continue
        self.is_running = False
        return False
    
    def start(self):
        print(f"Monitoring {self.app_name}...")

        self.is_running = self.is_app_running()

        if self.is_running:
            print(f"{self.app_name} is running.")
        else:
            print(f"{self.app_name} is not running.")
            
    def wait_for_close(self):
        while self.is_app_running():
            print(f"{self.app_name} is still running")
            time.sleep(self.check_interval)

        print(f"{self.app_name} is closed.")
        return
    
