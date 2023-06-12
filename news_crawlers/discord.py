import requests
import json


class DiscordHandler:
    def __init__(self) -> None:
        self.WEBHOOK_URI = "https://discord.com/api/webhooks/1117859469683073165/v3Y8RIbd5n3i6eT-ScAR_wqX_cYb69BwQwoh8ygXqs1vHorgKJ4BkzHgc8w-2pQb7adH"

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
