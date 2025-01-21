from abc import ABC, abstractmethod

from .slack import SlackMessage


class BaseCrawler(ABC):
    slack = SlackMessage()

    @abstractmethod
    def _get_articles(self) -> list[dict]:
        pass

    @abstractmethod
    def _filter_new_posts(self, *args, **kwargs) -> list[str]:
        pass

    def notify(self, new_posts: dict, site: str | None = None) -> None:
        for post in new_posts:
            self.slack.post(post, site=site)

    @abstractmethod
    def crawl(self) -> None:
        pass
