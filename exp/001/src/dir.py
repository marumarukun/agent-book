import os


def create_dir(path: str):
    if os.path.isdir(path):
        print(f"Directory already exists: {path}")
    else:
        os.makedirs(path, exist_ok=True)
        print(f"Directory created: {path}")
