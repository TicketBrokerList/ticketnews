import json

import feedparser
import requests
from decouple import config


class SlackMessage:
    def __init__(self):
        self.mods_webhook = config("MODS_SLACK_WEBHOOK")

    def post(self, message):
        slack_msg = {
            "blocks": [
                {"type": "divider"},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"{message}"}},
            ],
        }
        requests.post(self.mods_webhook, data=json.dumps(slack_msg))


def main():
    filename = "last_ticketsnews_rss.txt"
    with open(filename, "r") as f:
        latest_rss_link = f.read()

    response = feedparser.parse("https://www.ticketnews.com/feed/")

    entries = response["entries"]
    links = [entry["links"][0]["href"] for entry in entries]
    new_posts = []
    for link in links:
        if link != latest_rss_link:
            new_posts.append(link)
        else:
            break

    if len(new_posts):
        with open(filename, "w") as f:
            f.write(new_posts[0])

        slack = SlackMessage()
        for post in new_posts:
            slack.post(post)


if __name__ == "__main__":
    main()
