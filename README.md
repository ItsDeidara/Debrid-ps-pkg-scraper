# Debrid PS PKG Scraper GUI

A dark-mode Tkinter application for searching and retrieving PS4/PS5 game download links, with integrated Real Debrid and inital FTP support.
<img width="2076" height="1441" alt="image" src="https://github.com/user-attachments/assets/6e705f57-0879-4170-83a3-deaf0b598019" />

## Setup

1.  **Install Python 3.8+**
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the application:
```bash
python app.py
```

Workflow:
- Enter a game name in the search box and click "Search".
- Select a game from the results list to view details and download links.
- Select a download link to enable buttons for Real Debrid download or FTP transfer.
- Use the "Settings" button to configure API keys and FTP server details.
- View download history with the "Download History" button.

## Features

- **Game Search**: Search PS4/PS5 games with caching for fast lookups.
- **Real-Debrid Integration**: [Direct download via Real Debrid API for privacy and faster downloads.](http://real-debrid.com/?id=2672286)
- **FTP Transfer**: Upload files to configured FTP servers.
- **Download History**: Track and view past downloads.
- **Settings Management**: Configure APIs and FTP in a dedicated window.

## Configuration

Settings are stored in `settings.json` (defaults are used if missing). You can customize:
- scraper.base_url
- scraper.timeout
- scraper.ignore_domains
- database.cache_file
- database.cache_ttl
- apis.real_debrid_api_key
- ftp.host, ftp.port, ftp.username, ftp.password

Use the Settings window in the GUI to configure API keys and FTP details.

## Notes

- The tool caches scraped results to speed up subsequent lookups; update or clear the cache file (`games_cache.json`) to refresh entries.
- Download history is saved in `download_history.json`.
- Ensure Real Debrid API key is configured for unrestricted downloads.
- FTP transfer requires server configuration in settings.
- Use responsibly and respect site terms of service.
