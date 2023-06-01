import requests
import json


class DiscordHandler:
    def __init__(self) -> None:
        self.WEBHOOK_URI = "https://discord.com/api/webhooks/1113638203216363591/FWeqeoy47Hwyxw0xYge63pTgPPt7PZKEEQs9-ObjyKKNQP7z8RVBdWlyT8oRvl3Bdjf5"

    def post(self, message, site=None) -> None:
        if site == "TicketNews":
            title, link = message.values()
            link = link.split("?utm_source")[0]
            discord_msg = {"content": f"{title}\n{link}"}
        elif site == "MetaCritic":
            [[date, releases]] = message.items()
            formatted_date = date.strftime("%B %d, %Y").upper()
            formatted_releases = "\n".join(f"{r['artist_name']} - {r['album_title']}" for r in releases)
            discord_msg = {"content": f"**UPCOMING ALBUM RELEASES - {formatted_date}**\n\n{formatted_releases}"}
        else:
            raise ValueError("No site provided!")

        headers = {"Content-Type": "application/json"}
        requests.post(self.WEBHOOK_URI, data=json.dumps(discord_msg), headers=headers)
