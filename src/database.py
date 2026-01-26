import json
import os
import time

CACHE_FILE = "games_cache.json"
CACHE_TTL = 14400  # 4 hours
_cache = {}


def init_db():
    global _cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                _cache = json.load(f)
            print(f"Local cache loaded ({len(_cache)} items).")
        except Exception as e:
            print(f"Error loading cache file: {e}")
            _cache = {}
    else:
        print("No cache file found. Created new local cache.")
        _cache = {}


def get_cached_game(url):
    data = _cache.get(url)

    if data:
        age = time.time() - data.get("timestamp", 0)

        if age < CACHE_TTL:
            return {
                "title": data["title"],
                "size": data["size"],
                "links": data["links"],
                "downloads": data.get("downloads", "N/A"),
            }

    return None


def save_to_cache(game_data, links):
    global _cache

    record = {
        "url": game_data["url"],
        "title": game_data["title"],
        "size": game_data["size"],
        "downloads": game_data.get("downloads", "N/A"),
        "links": links,
        "timestamp": time.time(),
    }

    _cache[game_data["url"]] = record

    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_cache, f, indent=4)
    except Exception as e:
        print(f"Failed to save cache to disk: {e}")
