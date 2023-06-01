from abc import ABC, abstractmethod
from typing import List

from .slack import SlackMessage
from .discord import DiscordHandler


class BaseCrawler(ABC):
    slack = SlackMessage()
    discord = DiscordHandler()

    @abstractmethod
    def _get_articles(self):
        pass

    @abstractmethod
    def _filter_new_posts(self):
        pass

    def notify(self, new_posts: List[str] = [], site: str = None) -> None:
        for post in new_posts:
            self.slack.post(post, site=site)
            self.discord.post(post, site=site)

    @abstractmethod
    def crawl(self):
        pass
