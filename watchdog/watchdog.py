import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, script_to_run, file_to_watch):
        self.script_to_run = script_to_run
        self.file_to_watch = file_to_watch
        self.last_modified = time.time()

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(self.file_to_watch):
            current_time = time.time()
            if current_time - self.last_modified > 1:  # Debounce mechanism
                self.last_modified = current_time
                print(f"{event.src_path} has been modified")
                self.run_script()

    def run_script(self):
        try:
            result = subprocess.run(['python', self.script_to_run],
                                    check=True,
                                    capture_output=True,
                                    text=True)
            print(f"Script output:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"Error running {self.script_to_run}: {e}")
            print(f"Error output:\n{e.stderr}")

def watch_file(file_path, script_to_run):
    directory = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)

    event_handler = FileChangeHandler(script_to_run, file_name)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()

    print(f"Watching for changes to {file_path}...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping file watch...")
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    file_to_watch = os.path.join('data', 'liveData.csv')
    script_to_run = 'main.py'
    watch_file(file_to_watch, script_to_run)
