from pathlib import Path

in_test = False

BASE_DIR = Path(__file__).resolve().parent
def get_database():
    if in_test:
        return BASE_DIR / "test.db"
    else:
        return BASE_DIR / "music_app.db"
