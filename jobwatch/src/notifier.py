import os
import requests

TIMEOUT = 15


def send_telegram_message(text, bot_token=None, chat_id=None):
    bot_token = bot_token or os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = chat_id or os.environ["TELEGRAM_CHAT_ID"]
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    resp = requests.post(url, json=payload, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def format_job_message(job):
    return (
        f"🟢 <b>{job['company']}</b> — {job['title']}\n"
        f"📍 {job.get('location') or 'Location not specified'}\n"
        f"🔗 {job['url']}"
    )
