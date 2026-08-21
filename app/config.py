from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MUSIC_DIR = BASE_DIR / "music"
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "music.db"

MUSIC_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

BG = "#0B0D10"
SIDEBAR = "#000000"
SURFACE = "#121212"
CARD = "#181818"
CARD_HOVER = "#282828"
TEXT = "#FFFFFF"
MUTED = "#A7A7A7"
GREEN = "#1DB954"
BORDER = "#303030"

SUPPORTED = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"}
