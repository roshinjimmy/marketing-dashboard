CHANNEL_COLORS = {
    "Facebook": "#4267B2",
    "Google": "#DB4437",
    "TikTok": "#25F4EE",
}


def color_for_channel(name: str) -> str:
    return CHANNEL_COLORS.get(name, "#888888")
