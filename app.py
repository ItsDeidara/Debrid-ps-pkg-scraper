"""
Main application entry point. Handles user interaction,
CLI interface for searching, and orchestration of scraping and storage.
"""

import sys
from urllib.parse import urlparse

from src.database import get_cached_game, init_db, save_to_cache
from src.scraper import get_game_links, search_games


def get_host_name(url):
    try:
        domain = urlparse(url).netloc
        domain = domain.replace("www.", "").split(".")[0]
        return domain.capitalize()
    except Exception:
        return "Link"


def process_selection(game):
    print(f"\n--- {game['title']} ---")

    cached_data = get_cached_game(game["url"])

    if cached_data:
        print("[*] Loaded from cache")
        links = cached_data["links"]
        size = cached_data["size"]
    else:
        print("[*] Scraping live data (this may take a moment)...")
        links, size = get_game_links(game["url"], game["size"])
        if links:
            game["size"] = size
            save_to_cache(game, links)

    print(f"Size: {size}")

    if links:
        print("\nDownload Links:")
        for link in links:
            host = get_host_name(link)
            print(f"- [{host}] {link}")
    else:
        print("No download links found.")
    print("-" * 30)


def handle_selection_loop(games):
    while True:
        choice = input(
            "\nEnter number to download (or 'back' to search again): "
        ).strip()
        if choice.lower() in ["back", "b"]:
            break

        try:
            selection_idx = int(choice) - 1
            if 0 <= selection_idx < len(games):
                process_selection(games[selection_idx])
                continue_choice = input(
                    "\nSelect another from this list? (y/n): "
                ).lower()
                if continue_choice != "y":
                    break
            else:
                print("Invalid number.")
        except ValueError:
            print("Please enter a valid number.")


def main():
    print("=== PS PKG Scraper  ===")
    init_db()

    while True:
        try:
            query = input("\nSearch Game (or 'exit' to quit): ").strip()

            if query.lower() in ["exit", "quit", "q"]:
                print("Goodbye!")
                break

            if not query:
                continue

            print(f"Searching for '{query}'...")
            games = search_games(query)

            if not games:
                print("No games found.")
                continue

            print(f"\nFound {len(games)} results:")
            for idx, game in enumerate(games):
                print(f"{idx + 1}. {game['title']}")

            handle_selection_loop(games)

        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
