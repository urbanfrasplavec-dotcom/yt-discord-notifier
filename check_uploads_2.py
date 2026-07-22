#!/usr/bin/env python3
"""
Checks a second list of YouTube channels' RSS feeds for new uploads and posts
a notification to a (different) Discord webhook when a new video is found.

This is a sibling to check_uploads.py — same logic, separate channel list,
separate state file, and separate Discord webhook secret, so the two run
completely independently of each other.
"""

import json
import os
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

STATE_FILE = "seen_2.json"

CHANNELS = {
    "UCWsslCoN3b_wBaFVWK_ye_A": "Hamza",
    "UCHW4DMIaBmTGGGPmbmr-Dsg": "Hamza Unfiltered",
    "UCYuy-3wvWzFN639UdgIQbFg": "Hamza Ahmed | Influencer School",
    "UC6oapb1Vl2GAtYfrKRFZ55w": "Hamza Advanced",
}

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL_2")

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}


def fetch_latest_video(channel_id):
    """Returns (video_id, title, url, author) for the most recent video, or None."""
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    req = urllib.request.Request(feed_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()

    root = ET.fromstring(data)
    entry = root.find("atom:entry", NS)
    if entry is None:
        return None

    video_id = entry.find("yt:videoId", NS).text
    title = entry.find("atom:title", NS).text
    link = entry.find("atom:link", NS).attrib["href"]
    author = entry.find("atom:author/atom:name", NS).text

    return {"video_id": video_id, "title": title, "url": link, "author": author}


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def notify_discord(video, friendly_name):
    if not DISCORD_WEBHOOK_URL:
        print("WARNING: DISCORD_WEBHOOK_URL_2 not set, skipping notification.")
        return

    content = f"📺 **{friendly_name}** just uploaded a new video!\n**{video['title']}**\n{video['url']}"
    payload = json.dumps({"content": content}).encode("utf-8")

    req = urllib.request.Request(
        DISCORD_WEBHOOK_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; yt-discord-notifier/1.0)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"Discord response: {resp.status}")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        webhook_len = len(DISCORD_WEBHOOK_URL) if DISCORD_WEBHOOK_URL else 0
        print(f"Discord HTTPError {e.code}: {error_body}")
        print(f"(Webhook URL length as seen by script: {webhook_len} chars — sanity check this matches your actual webhook URL length)")
        raise


def main():
    state = load_state()
    changed = False

    for channel_id, friendly_name in CHANNELS.items():
        try:
            video = fetch_latest_video(channel_id)
        except Exception as e:
            print(f"ERROR fetching {friendly_name} ({channel_id}): {e}", file=sys.stderr)
            continue

        if video is None:
            print(f"No videos found for {friendly_name}")
            continue

        last_seen_id = state.get(channel_id)

        if video["video_id"] != last_seen_id:
            print(f"New upload detected for {friendly_name}: {video['title']}")
            notify_discord(video, friendly_name)
            state[channel_id] = video["video_id"]
            changed = True
        else:
            print(f"No new upload for {friendly_name}")

    if changed:
        save_state(state)


if __name__ == "__main__":
    main()
