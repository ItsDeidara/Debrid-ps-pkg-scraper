import json
import os
import time

try:
    from src.config import cfg  # type: ignore
except Exception:
    cfg = None

DEFAULT_CACHE_FILE = "games_cache.json"
DEFAULT_CACHE_TTL = 31536000

if cfg and getattr(cfg, "database", None) is not None:
    try:
        CACHE_FILE = cfg.database.get("cache_file", DEFAULT_CACHE_FILE)
        CACHE_TTL = cfg.database.get("cache_ttl", DEFAULT_CACHE_TTL)
    except Exception:
        CACHE_FILE = DEFAULT_CACHE_FILE
        CACHE_TTL = DEFAULT_CACHE_TTL
else:
    CACHE_FILE = DEFAULT_CACHE_FILE
    CACHE_TTL = DEFAULT_CACHE_TTL

class GameCache:
    def __init__(self):
        self._cache = {}

    def load(self):
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except (OSError, json.JSONDecodeError):
                self._cache = {}
        else:
            self._cache = {}

    def get(self, url):
        data = self._cache.get(url)
        if not data:
            return None

        if "metadata" not in data:
            return None

        meta = data["metadata"]
        if meta.get("version", "N/A") == "N/A" and meta.get("cusa", "N/A") == "N/A":
            return None
            
        if not data.get("links"):
            return None

        timestamp = data.get("timestamp", 0)
        if (time.time() - timestamp) > CACHE_TTL:
            return None

        return data

    def save(self, game_data, links, metadata):
        self._cache[game_data["url"]] = {
            "url": game_data["url"],
            "title": game_data["title"],
            "size": metadata.get("size", "N/A"),
            "downloads": game_data.get("downloads", "N/A"),
            "links": links,
            "metadata": metadata,
            "timestamp": time.time(),
        }

        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=4)
        except OSError:
            pass