from collections import defaultdict
from datetime import datetime
from typing import Dict, List

import dateparser
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers

from .base import BaseCrawler
from .db import Post, Session


class MetaCriticCrawler(BaseCrawler):
    site = "MetaCritic"
    url = "https://www.metacritic.com/browse/albums/release-date/coming-soon"

    def __init__(self) -> None:
        super().__init__()
        self.db_session = Session()

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

    def _is_date_posted(self, check_date: datetime) -> bool:
        """Check if this date has been posted before"""
        return bool(self.db_session.query(Post).filter(Post.album_release_date == check_date).first())

    def _save_date(self, post_date: datetime) -> None:
        """Save the date record to database"""
        post = Post(album_release_date=post_date)
        self.db_session.add(post)
        self.db_session.commit()

    def _filter_new_posts(self, entries: Dict) -> List[Dict]:
        dates = sorted(entries.keys())
        new_posts = []

        for date in dates[:3]:  # Look at latest 3 dates
            if not self._is_date_posted(date):  # Check date before appending
                post = {date: entries[date]}
                new_posts.append(post)
                self._save_date(date)  # Save the date right after we decide to use it

        return new_posts

    def crawl(self) -> None:
        body = self._get_articles()
        articles = self._parse_articles(body)
        new_posts = self._filter_new_posts(articles)
        print(f"{len(new_posts)} {self.site} articles found.")
        self.notify(new_posts, site=self.site)
