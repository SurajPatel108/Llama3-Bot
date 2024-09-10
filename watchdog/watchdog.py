from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, script_to_run):
        self.script_to_run = script_to_run

    def on_modified(self, event):
        if event.src_path.endswith('livedata.csv'):
            print(f"{event.src_path} has been modified")
            subprocess.run(['python', self.script_to_run])

if __name__ == "__main__":
    path = 'data/liveData.csv'
    script_to_run = 'main.py'
    event_handler = FileChangeHandler(script_to_run)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()