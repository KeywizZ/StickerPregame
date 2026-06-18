import json
import os
import sys

from stickergoblin.config import CONFIG_FILENAME


def project_root() -> str:
    if getattr(sys, "frozen", False):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(rel_path: str) -> str:
    return os.path.join(project_root(), rel_path)


def user_config_path() -> str:
    appdata = os.environ.get("APPDATA")
    if appdata:
        config_dir = os.path.join(appdata, "StickerGoblin")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, CONFIG_FILENAME)
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = project_root()
    return os.path.join(base, CONFIG_FILENAME)


def load_config() -> dict:
    path = user_config_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def save_config(data: dict) -> None:
    path = user_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass
