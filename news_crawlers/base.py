from abc import ABC, abstractmethod
from typing import List
from .slack import SlackMessage


class BaseCrawler(ABC):
    slack = SlackMessage()

    @abstractmethod
    def _get_articles(self):
        pass

    @abstractmethod
    def _filter_new_posts(self):
        pass

    def _notify(self, new_posts: List[str] = []) -> None:
        for post in new_posts:
            self.slack.post(post)

    @abstractmethod
    def crawl(self):
        pass
