# YouTube → Discord Upload Notifier

Checks 4 YouTube channels every 15 minutes and posts a message to a Discord
channel whenever one of them uploads a new video. No YouTube API key needed —
uses YouTube's public RSS feeds. Runs entirely on GitHub Actions, for free.

## Setup

1. Create a Discord webhook (Channel Settings → Integrations → Webhooks → New Webhook)
2. Get your 4 YouTube channel IDs (channel page → Share → Copy channel ID)
3. Edit check_uploads.py and replace the CHANNELS dict with your 4 channels
4. Push this folder to a GitHub repo
5. Add DISCORD_WEBHOOK_URL as a repo secret (Settings → Secrets and variables → Actions)

The workflow runs automatically every 15 minutes once pushed.