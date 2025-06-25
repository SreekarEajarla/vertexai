import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from google.cloud import storage

# Set these variables according to your environment
WATCH_DIRECTORY = '/path/to/watch'  # Directory to monitor
GCS_BUCKET_NAME = 'your-gcs-bucket'
GCS_DESTINATION_PREFIX = ''  # Optional: path prefix in the bucket ('' = root)

# Initialize GCS client (make sure GOOGLE_APPLICATION_CREDENTIALS is set)
storage_client = storage.Client()

def upload_to_gcs(source_file, bucket_name, destination_blob_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file)
    print(f"Uploaded {source_file} to gs://{bucket_name}/{destination_blob_name}")

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            # Wait a bit to ensure file is closed/written
            time.sleep(2)
            filename = os.path.basename(event.src_path)
            gcs_path = os.path.join(GCS_DESTINATION_PREFIX, filename)
            upload_to_gcs(event.src_path, GCS_BUCKET_NAME, gcs_path)

    def on_modified(self, event):
        if not event.is_directory:
            # Wait a bit to ensure file is closed/written
            time.sleep(2)
            filename = os.path.basename(event.src_path)
            gcs_path = os.path.join(GCS_DESTINATION_PREFIX, filename)
            upload_to_gcs(event.src_path, GCS_BUCKET_NAME, gcs_path)

if __name__ == "__main__":
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIRECTORY, recursive=True)
    observer.start()
    print(f"Watching directory: {WATCH_DIRECTORY}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
