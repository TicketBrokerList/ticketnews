import json
import os

import requests
from dotenv import load_dotenv


class SlackMessage:
    def __init__(self) -> None:
        load_dotenv()
        self.WEBHOOK_URI = os.environ.get("SLACK_CHANNEL_WEBHOOK")
        if not self.WEBHOOK_URI:
            raise ValueError("SLACK_CHANNEL_WEBHOOK environment variable is not set")

    def post(self, message: str | dict, site: str | None = None) -> None:
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
        else:
            raise ValueError("No site provided!")
        requests.post(self.WEBHOOK_URI, data=json.dumps(slack_msg))
