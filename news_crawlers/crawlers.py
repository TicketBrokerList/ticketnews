from collections import defaultdict
from datetime import datetime
from typing import List, Union

import dateparser
import feedparser
import requests
from bs4 import BeautifulSoup
from fake_headers import Headers

from .base import BaseCrawler
from .db import Post, Session


class TicketNewsCrawler(BaseCrawler):
    site = "TicketNews"
    url = "https://www.ticketnews.com/feed/"

    def _get_articles(self) -> List[dict]:
        response = feedparser.parse(self.url)
        return response["entries"]

    def _filter_new_posts(self, entries: str) -> List[str]:
        with Session() as session:
            past_posts = [r for r, in session.query(Post.url).all()]

            new_posts = []
            for entry in entries:
                title = entry["title"]
                url = entry["link"].split("?")[0]
                if url not in past_posts:
                    post_obj = {"title": title, "link": url}
                    new_posts.append(post_obj)

                    # record new post
                    post = Post(site=self.site, url=url)
                    session.add(post)
                    session.commit()
                else:
                    break

            return new_posts[:3]

    def crawl(self) -> None:
        articles = self._get_articles()
        new_posts = self._filter_new_posts(articles)
        print(f"{len(new_posts)} {self.site} articles found.")
        self.notify(new_posts, site=self.site)


class MetaCriticCrawler(BaseCrawler):
    site = "MetaCritic"
    url = "https://www.metacritic.com/browse/albums/release-date/coming-soon"

    @staticmethod
    def _get_headers():
        header = Headers(
            browser="chrome", os="win", headers=True  # Generate only Chrome UA  # Generate ony Windows platform  # generate misc headers
        )
        return header.generate()

    def _get_articles(self) -> List[dict]:
        response = requests.get(self.url, headers=self._get_headers())
        if response.status_code != 200:
            raise ValueError("Something went wrong!")
        return response.text

    @staticmethod
    def _clean_text(text: Union[str, None]) -> str:
        return text.strip() if text else ""

    def _parse_articles(self, html_body: str) -> List[dict]:
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

    def _filter_new_posts(self, entries: str) -> List[str]:
        dates = sorted(entries.keys())
        d = datetime.utcnow()
        new_posts = []
        for date in dates:
            time_to_release = (date - datetime(d.year, d.month, d.day)).days
            if time_to_release == 0 or time_to_release == 7:
                post = {date: entries[date]}
                new_posts.append(post)

        return new_posts[:3]

    def crawl(self) -> None:
        body = self._get_articles()
        articles = self._parse_articles(body)
        new_posts = self._filter_new_posts(articles)
        print(f"{len(new_posts)} {self.site} articles found.")
        self.notify(new_posts, site=self.site)
