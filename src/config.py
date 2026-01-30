import json
import os

# Default fallback values in case settings.json is missing or corrupt
DEFAULTS = {
    "scraper": {
        "base_url": "https://www.superpsx.com/",
        "timeout": 15,
        "ignore_domains": []
    },
    "database": {
        "cache_file": "games_cache.json",
        "cache_ttl": 31536000
    }
}

class Config:
    def __init__(self, config_path="settings.json"):
        self.settings = self._load_settings(config_path)

    def _load_settings(self, path):
        if not os.path.exists(path):
            print(f"[WARNING] {path} not found. Using defaults.")
            return DEFAULTS
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[ERROR] Could not load {path}: {e}. Using defaults.")
            return DEFAULTS

    @property
    def scraper(self):
        return self.settings.get("scraper", DEFAULTS["scraper"])

    @property
    def database(self):
        return self.settings.get("database", DEFAULTS["database"])

# Create a singleton instance to be imported elsewhere
cfg = Config()
