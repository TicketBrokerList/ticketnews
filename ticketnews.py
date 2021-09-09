import json
from datetime import datetime

import feedparser
import requests
from decouple import config


class SlackMessage:
    def __init__(self):
        self.mods_webhook = config("SLACK_CHANNEL_WEBHOOK")

    def post(self, message):
        title, link = message.values()
        link = link.split("?utm_source")[0]
        slack_msg = {
            "blocks": [
                {"type": "divider"},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"{title}\n{link}"}},
            ],
        }
        requests.post(self.mods_webhook, data=json.dumps(slack_msg))


def main():
    # check latest post sent to Slack
    filename = "/root/ticketnews/last_ticketnews_rss.txt"
    with open(filename, "r") as f:
        latest_rss_link = f.read()

    # parse rss
    response = feedparser.parse("https://www.ticketnews.com/feed/")
    entries = response["entries"]

    new_posts = []
    for entry in entries:
        title = entry["title"]
        link = entry["link"]
        if link != latest_rss_link:
            post_obj = {"title": title, "link": link}
            new_posts.append(post_obj)
        else:
            break

    # check if post was already sent
    if len(new_posts):
        with open(filename, "w") as f:
            f.write(new_posts[0]["link"])

        slack = SlackMessage()
        for post in new_posts:
            slack.post(post)

    # cronjob logs
    print(f"[{datetime.utcnow()}] {len(new_posts)} new posts found: {new_posts}")


if __name__ == "__main__":
    main()
