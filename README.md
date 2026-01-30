# PS PKG Scraper CLI

A simple command-line tool to search and retrieve PS4/PS5 game download links.

## Setup

1.  **Install Python 3.8+**
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Interactive mode (default):
```bash
python app.py
```
Direct search (non-interactive prompt + selection):
```bash
python app.py -s "Grand Theft Auto"
# or
python app.py --search "Grand Theft Auto"
```

Workflow:
- Search for a game name.
- Select a result to view game info and download links.
- Copy links as needed.

## Configuration

Settings are read from `settings.json` (defaults are used if missing). You can customize:
- scraper.base_url
- scraper.timeout
- scraper.ignore_domains
- database.cache_file
- database.cache_ttl

Default cache file: `games_cache.json`. Default cache TTL: 31536000 seconds (configurable via `settings.json`).

## Notes

- The tool caches scraped results to speed up subsequent lookups; update or clear the cache file to refresh entries.
- Use responsibly and respect site terms of service.
