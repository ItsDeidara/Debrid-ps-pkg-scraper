# PS PKG Scraper CLI

A simple command-line tool to search and retrieve PS4/PS5 game download links.

## Setup

1.  **Install Python 3.8+**
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the tool:
```bash
python app.py
```

1.  **Search:** Enter a game name (e.g., "Grand Theft Auto").
2.  **Select:** Type the number of the game you want.
3.  **Download:** Copy the scraped links.

**Note:** Search results are cached locally in `games_cache.json` for 4 hours to speed up subsequent requests.
