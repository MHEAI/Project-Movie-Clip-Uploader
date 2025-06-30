import os
class Utilities:
    def __init__(self):
         pass
    def cleanup_files(self, file_paths):
            for path in file_paths:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                        print(f"Deleted file: {path}")
                    except Exception as e:
                        print(f"Error deleting {path}: {e}")
                else:
                    print(f"File not found, skipping: {path}")