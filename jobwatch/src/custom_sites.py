"""
Dedicated fetchers for companies that don't use Greenhouse/Lever/Workday.

IMPORTANT: I built and wrote this code without live internet access, so
these endpoints/params are my best-effort based on how these APIs have
worked historically. Run `python src/main.py --check-config` after you
deploy (GitHub Actions has internet) - it'll tell you exactly which of
these return errors so you can fix the URL/params quickly. These are the
ones most likely to need a small tweak.
"""
import requests

TIMEOUT = 20
HEADERS = {"User-Agent": "Mozilla/5.0 (job-alert-bot)"}


def fetch_google(company="Google"):
    url = "https://careers.google.com/api/v3/search/"
    params = {"q": "software engineer", "location": "India", "page_size": 20}
    resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    jobs = []
    for j in data.get("jobs", []):
        jobs.append({
            "id": f"google:{j.get('id')}",
            "title": j.get("title", ""),
            "location": ", ".join(l.get("display", "") for l in j.get("locations", [])),
            "url": f"https://careers.google.com/jobs/results/{j.get('id')}/",
            "description": j.get("description", "") or "",
            "company": company,
        })
    return jobs


def fetch_amazon(company="Amazon"):
    url = "https://www.amazon.jobs/en/search.json"
    params = {"query": "software engineer", "country": "IN", "result_limit": 20}
    resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    jobs = []
    for j in data.get("jobs", []):
        jobs.append({
            "id": f"amazon:{j.get('id_icims') or j.get('job_path')}",
            "title": j.get("title", ""),
            "location": j.get("location", ""),
            "url": f"https://www.amazon.jobs{j.get('job_path', '')}",
            "description": j.get("description_short", "") or "",
            "company": company,
        })
    return jobs


def fetch_microsoft(company="Microsoft"):
    url = "https://gcsservices.careers.microsoft.com/search/api/v1/search"
    params = {"q": "software engineer", "l": "en_us", "lc": "India", "p": "1", "rt": "professional", "pgSz": 20}
    resp = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    jobs = []
    for j in data.get("operationResult", {}).get("result", {}).get("jobs", []):
        jid = j.get("jobId")
        jobs.append({
            "id": f"microsoft:{jid}",
            "title": j.get("title", ""),
            "location": j.get("properties", {}).get("primaryLocation", ""),
            "url": f"https://jobs.careers.microsoft.com/global/en/job/{jid}",
            "description": "",
            "company": company,
        })
    return jobs


def fetch_meta(company="Meta"):
    # Meta's careers site is heavily JS-rendered with no stable public JSON API.
    # Marking as unsupported for now - will need a headless-browser approach
    # (e.g. Playwright) if you want Meta included; flag this to me and I'll add it.
    return []


def fetch_uber(company="Uber"):
    url = "https://www.uber.com/api/loadSearchJobsResults"
    payload = {"limit": 20, "page": 0, "params": {"location": ["India"], "team": [], "query": "software engineer"}}
    resp = requests.post(url, json=payload, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    jobs = []
    for j in data.get("data", {}).get("results", []):
        jobs.append({
            "id": f"uber:{j.get('id')}",
            "title": j.get("title", ""),
            "location": ", ".join(loc.get("city", "") for loc in j.get("allLocations", [])),
            "url": f"https://www.uber.com/global/en/careers/list/{j.get('id')}/",
            "description": j.get("description", "") or "",
            "company": company,
        })
    return jobs


def fetch_flipkart(company="Flipkart"):
    # Flipkart's careers site does not expose a stable public JSON API as of
    # my training data. Placeholder - returns nothing until verified/fixed.
    return []


def fetch_zomato(company="Zomato"):
    return []  # same as Flipkart - needs verification once you have internet access


def fetch_phonepe(company="PhonePe"):
    return []  # same - needs verification


def fetch_myntra(company="Myntra"):
    return []  # same - needs verification


def fetch_rippling(company="Rippling"):
    # Rippling uses its own ATS at ats.rippling.com with no documented public
    # JSON API (confirmed via search - individual job postings are at
    # ats.rippling.com/rippling/jobs/<id> but no board-level JSON endpoint
    # was found). Placeholder until verified/fixed.
    return []


HANDLERS = {
    "google": fetch_google,
    "amazon": fetch_amazon,
    "microsoft": fetch_microsoft,
    "meta": fetch_meta,
    "uber": fetch_uber,
    "flipkart": fetch_flipkart,
    "zomato": fetch_zomato,
    "phonepe": fetch_phonepe,
    "myntra": fetch_myntra,
    "rippling": fetch_rippling,
}
