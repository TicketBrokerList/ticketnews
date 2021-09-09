import json

import requests
from decouple import config


class SlackMessage:
    def __init__(self) -> None:
        self.mods_webhook = config("SLACK_CHANNEL_WEBHOOK")

    def post(self, message: str) -> None:
        title, link = message.values()
        link = link.split("?utm_source")[0]
        slack_msg = {
            "blocks": [
                {"type": "divider"},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"{title}\n{link}"}},
            ],
        }
        requests.post(self.mods_webhook, data=json.dumps(slack_msg))
