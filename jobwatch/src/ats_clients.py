"""
Generic fetchers for the big 3 ATS platforms. Each returns a list of
normalized job dicts: {id, title, location, url, description, company}
"""
import requests

TIMEOUT = 20
HEADERS = {"User-Agent": "Mozilla/5.0 (job-alert-bot)"}


def fetch_greenhouse(company, board_token):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    jobs = []
    for j in data.get("jobs", []):
        jobs.append({
            "id": f"greenhouse:{board_token}:{j['id']}",
            "title": j.get("title", ""),
            "location": (j.get("location") or {}).get("name", ""),
            "url": j.get("absolute_url", ""),
            "description": j.get("content", "") or "",
            "company": company,
        })
    return jobs


def fetch_lever(company, company_slug):
    url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    jobs = []
    for j in data:
        cats = j.get("categories", {})
        jobs.append({
            "id": f"lever:{company_slug}:{j['id']}",
            "title": j.get("text", ""),
            "location": cats.get("location", ""),
            "url": j.get("hostedUrl", ""),
            "description": j.get("descriptionPlain", "") or j.get("description", "") or "",
            "company": company,
        })
    return jobs


def fetch_workday(company, tenant, site, wd_num=1, search_text="software engineer"):
    """
    Workday's public jobs API. wd_num is the numbered subdomain (wd1, wd5,
    etc.) which varies by company - if this 404s, try wd_num 1 through 12.
    """
    base = f"https://{tenant}.wd{wd_num}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
    payload = {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": search_text}
    resp = requests.post(base, json=payload, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    jobs = []
    for j in data.get("jobPostings", []):
        path = j.get("externalPath", "")
        jobs.append({
            "id": f"workday:{tenant}:{path}",
            "title": j.get("title", ""),
            "location": j.get("locationsText", ""),
            "url": f"https://{tenant}.wd{wd_num}.myworkdayjobs.com/{site}{path}",
            "description": "",  # Workday search results don't include full JD; title+location filtering only
            "company": company,
        })
    return jobs
