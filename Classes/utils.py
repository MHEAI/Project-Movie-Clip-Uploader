import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Utilities:
    def __init__(self):
        pass

    def cleanup_files(self, file_paths):
        for path in file_paths:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    logging.info(f"Deleted file: {path}")
                except Exception as e:
                    logging.error(f"Error deleting {path}: {e}")
            else:
                logging.info(f"File not found, skipping: {path}")
