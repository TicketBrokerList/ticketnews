from collections import defaultdict
from datetime import datetime

import dateparser
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers

from .base import BaseCrawler


class MetaCriticCrawler(BaseCrawler):
    site = "MetaCritic"
    url = "https://www.metacritic.com/browse/albums/release-date/coming-soon"

    @staticmethod
    def _get_headers():
        header = Headers(
            browser="chrome", os="win", headers=True  # Generate only Chrome UA  # Generate ony Windows platform  # generate misc headers
        )
        return header.generate()

    def _get_articles(self) -> list[dict]:
        response = requests.get(self.url, headers=self._get_headers())
        response.raise_for_status()
        return response.text

    @staticmethod
    def _clean_text(text: str | None) -> str:
        return text.strip() if text else ""

    def _parse_articles(self, html_body: str) -> list[dict]:
        soup = BeautifulSoup(html_body, "lxml")
        table = soup.find("table", {"class": "musicTable"})
        rows = table.find_all("tr")
        album_releases = defaultdict(list)
        release_date = ""

        for i, row in enumerate(rows):
            if len(row.get("class", [])) and row["class"][0] == "module":
                release_date = dateparser.parse(row.text.strip())
            else:
                artist_name = self._clean_text(row.find("td", {"class", "artistName"}).text)
                album_title = self._clean_text(row.find("td", {"class", "albumTitle"}).text)
                data = {"artist_name": artist_name, "album_title": album_title}
                album_releases[release_date].append(data)
        return album_releases

    def _filter_new_posts(self, entries: str) -> list[str]:
        dates = sorted(entries.keys())
        new_posts = []
        for date in dates:
            post = {date: entries[date]}
            new_posts.append(post)

        return new_posts[:3]

    def crawl(self) -> None:
        body = self._get_articles()
        articles = self._parse_articles(body)
        new_posts = self._filter_new_posts(articles)
        print(f"{len(new_posts)} {self.site} articles found.")
        self.notify(new_posts, site=self.site)
