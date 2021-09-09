from typing import List

import feedparser

from .base import BaseCrawler
from .db import Post, Session
from .slack import SlackMessage


class TicketNewsCrawler(BaseCrawler):
    site = "ticketnews"
    url = "https://www.ticketnews.com/feed/"

    def _get_articles(self) -> List[dict]:
        response = feedparser.parse("https://www.ticketnews.com/feed/")
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
        self._notify(new_posts)
