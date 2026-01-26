import re
import urllib.parse

import cloudscraper
from bs4 import BeautifulSoup

BASE_URL = "https://www.superpsx.com/"
IGNORE_DOMAINS = ["superpsx", "facebook", "twitter", "discord"]


def get_scraper():
    return cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )


def search_games(search_query):
    params = {"s": search_query}
    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"

    try:
        scraper = get_scraper()
        response = scraper.get(url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        results = []

        items = soup.select("li.grid-style article.item")

        for item in items:
            title_node = item.select_one("h2.penci-entry-title a")
            if not title_node:
                continue

            img_node = item.select_one("div.thumbnail a")
            image = img_node.get("data-bgset") if img_node else None

            results.append(
                {
                    "title": title_node.get_text(strip=True),
                    "url": title_node["href"],
                    "image": image,
                    "downloads": "N/A",
                    "size": "N/A",
                }
            )

        return results

    except Exception as e:
        print(f"Search failed: {e}")
        return []


def get_game_links(game_url, current_size="N/A"):
    scraper = get_scraper()
    final_links = []
    new_size = current_size

    try:
        resp = scraper.get(game_url, timeout=15)
        soup = BeautifulSoup(resp.content, "html.parser")

        rows = soup.select("table.has-fixed-layout tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2 and "size" in cols[0].get_text(strip=True).lower():
                new_size = cols[1].get_text(strip=True)
                break

        dl_node = soup.select_one("a:has(img[alt='Download'])") or soup.find(
            "a", href=re.compile(r"dll-")
        )

        if dl_node:
            dl_page_url = dl_node["href"]
            try:
                dl_resp = scraper.get(dl_page_url, timeout=15)
                dl_soup = BeautifulSoup(dl_resp.content, "html.parser")

                tables = dl_soup.select("table")
                for table in tables:
                    for link in table.select("a[href]"):
                        href = link["href"]
                        if not any(domain in href for domain in IGNORE_DOMAINS):
                            final_links.append(href)

            except Exception as e:
                print(f"DL page scraping failed: {e}")

        return list(set(final_links)), new_size

    except Exception as e:
        print(f"Link extraction failed: {e}")
        return [], new_size
