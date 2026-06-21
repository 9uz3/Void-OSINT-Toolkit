"""Void OSINT Toolkit — settings.json load/save."""
import json
import os
from . import constants as C

DEFAULTS = {
    "language": "en",
    "theme": "white",
    "username": "Operator",
    "skip_boot": False,
    "setup_complete": True,
    "last_setup_config_rev": "0",
    "last_seen_config_rev": "0",
}


class Settings:
    def __init__(self):
        self.data = dict(DEFAULTS)
        self.load()

    def load(self):
        os.makedirs(C.CONFIG_DIR, exist_ok=True)
        if os.path.isfile(C.SETTINGS_PATH):
            try:
                with open(C.SETTINGS_PATH, encoding="utf-8") as f:
                    merged = {**DEFAULTS, **json.load(f)}
                self.data = merged
            except Exception:
                pass
        C.apply_theme(C._THEME_ALIASES.get(self.data.get("theme", "white"), self.data.get("theme", "white")))

    def save(self):
        os.makedirs(C.CONFIG_DIR, exist_ok=True)
        with open(C.SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        return self.data.get(key, default if default is not None else DEFAULTS.get(key))

    def set(self, key, value):
        self.data[key] = value
        if key == "theme":
            C.apply_theme(C._THEME_ALIASES.get(value, value))

    @property
    def lang(self):
        return self.data.get("language", "en")

    @property
    def username(self):
        return self.data.get("username", "Operator")


_settings = None


def get_settings():
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
