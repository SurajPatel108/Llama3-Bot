import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CSVChangeHandler(FileSystemEventHandler):
    def __init__(self, file_path):
        self.file_path = file_path

    def on_modified(self, event):
        if event.src_path == self.file_path:
            print(f"{self.file_path} has been updated.")
            self.run_main_script()

    def run_main_script(self):
        print("Running main.py...")
        subprocess.run(['python3', 'main.py'], check=True)

if __name__ == "__main__":
    # Define the file to watch
    csv_file_path = os.path.join('data', 'liveData.csv')
    
    # Check if the file exists
    if not os.path.exists(csv_file_path):
        print(f"Error: {csv_file_path} does not exist.")
        exit(1)

    # Create an event handler
    event_handler = CSVChangeHandler(file_path=csv_file_path)

    # Set up the observer
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(csv_file_path), recursive=False)

    # Start observing
    observer.start()
    print(f"Watching {csv_file_path} for changes...")

    try:
        while True:
            time.sleep(1)  # Polling interval
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
