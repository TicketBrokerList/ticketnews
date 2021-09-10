import json
from typing import Union

import requests
from decouple import config


class SlackMessage:
    def __init__(self) -> None:
        self.WEBHOOK_URI = config("GENERAL_CHANNEL_WEBHOOK")

    def post(self, message: Union[str, dict], site: Union[str, None] = None) -> None:
        if site == "TicketNews":
            title, link = message.values()
            link = link.split("?utm_source")[0]
            slack_msg = {
                "blocks": [
                    {"type": "divider"},
                    {"type": "section", "text": {"type": "mrkdwn", "text": f"{title}\n{link}"}},
                ],
            }
        elif site == "MetaCritic":
            [[date, releases]] = message.items()
            formatted_date = date.strftime("%B %d, %Y").upper()
            formatted_releases = "\n".join(f"{r['artist_name']} - {r['album_title']}" for r in releases)
            slack_msg = {
                "blocks": [
                    {"type": "divider"},
                    {"type": "section", "text": {"type": "mrkdwn", "text": f"*UPCOMING ALBUM RELEASES - {formatted_date}*"}},
                    {"type": "divider"},
                    {"type": "section", "text": {"type": "mrkdwn", "text": f"{formatted_releases}"}},
                ],
            }
        if site:
            requests.post(self.WEBHOOK_URI, data=json.dumps(slack_msg))
