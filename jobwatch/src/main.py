import sys
import time
import yaml
import os

sys.path.insert(0, os.path.dirname(__file__))

from ats_clients import fetch_greenhouse, fetch_lever, fetch_workday
from custom_sites import HANDLERS
from filters import filter_jobs
from notifier import send_telegram_message, format_job_message
from state import load_seen_ids, save_seen_ids

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "companies.yaml")
MAX_YEARS = 5


def load_companies():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)["companies"]


def fetch_company_jobs(entry):
    name = entry["name"]
    ats = entry["ats"]
    try:
        if ats == "greenhouse":
            return fetch_greenhouse(name, entry["board_token"])
        elif ats == "lever":
            return fetch_lever(name, entry["company_slug"])
        elif ats == "workday":
            return fetch_workday(name, entry["tenant"], entry["site"])
        elif ats == "custom":
            handler = HANDLERS.get(entry["handler"])
            if not handler:
                print(f"[WARN] No handler registered for {name} ({entry['handler']})")
                return []
            return handler(name)
        else:
            print(f"[WARN] Unknown ats type '{ats}' for {name}")
            return []
    except Exception as e:
        print(f"[ERROR] Failed to fetch jobs for {name}: {e}")
        return []


def check_config():
    """Dry run: hit every company's API and report which ones fail, without sending Telegram messages."""
    companies = load_companies()
    for entry in companies:
        name = entry["name"]
        try:
            jobs = fetch_company_jobs(entry)
            print(f"[OK]   {name:<25} -> {len(jobs)} jobs fetched")
        except Exception as e:
            print(f"[FAIL] {name:<25} -> {e}")
        time.sleep(0.5)  # be polite to APIs


def run(dry_run=False):
    companies = load_companies()
    seen_ids = load_seen_ids()
    all_new_matches = []

    for entry in companies:
        jobs = fetch_company_jobs(entry)
        matches = filter_jobs(jobs, max_years=MAX_YEARS)
        new_matches = [j for j in matches if j["id"] not in seen_ids]
        all_new_matches.extend(new_matches)
        time.sleep(0.5)  # be polite to APIs

    print(f"Found {len(all_new_matches)} new matching jobs.")

    if dry_run:
        print("\n[DRY RUN] No Telegram messages will be sent. Matches found:\n")
        if not all_new_matches:
            print("  (none)")
        for job in all_new_matches:
            print(f"  - {job['company']} | {job['title']} | {job.get('location')}")
            print(f"    {job['url']}")
        print("\n[DRY RUN] Nothing was marked as 'seen' - re-running normally later")
        print("will still notify you about all of these.")
        return

    for job in all_new_matches:
        try:
            send_telegram_message(format_job_message(job))
            seen_ids.add(job["id"])
            time.sleep(1)  # avoid Telegram rate limits
        except Exception as e:
            print(f"[ERROR] Failed to send Telegram message for {job['title']} @ {job['company']}: {e}")

    save_seen_ids(seen_ids)


if __name__ == "__main__":
    if "--check-config" in sys.argv:
        check_config()
    elif "--dry-run" in sys.argv:
        run(dry_run=True)
    else:
        run()
