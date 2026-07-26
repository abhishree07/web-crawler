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


def fetch_ashby(company, job_board_name):
    """
    Ashby's public job board API. Confirmed pattern used by Notion,
    Confluent, and many other companies that migrated off Greenhouse.
    """
    url = f"https://api.ashbyhq.com/posting-api/job-board/{job_board_name}"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    jobs = []
    for j in data.get("jobs", []):
        jobs.append({
            "id": f"ashby:{job_board_name}:{j.get('id')}",
            "title": j.get("title", ""),
            "location": j.get("location", ""),
            "url": j.get("jobUrl", ""),
            "description": j.get("descriptionPlain", "") or "",
            "company": company,
        })
    return jobs


def fetch_workday(company, tenant, site, wd_num=None, search_text="software engineer"):
    """
    Workday's public jobs API. The numbered subdomain (wd1, wd3, wd5, etc.)
    varies per company and isn't guessable from the company name, so if
    wd_num isn't given we auto-try the common ones and use whichever
    responds successfully.
    """
    payload = {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": search_text}
    wd_candidates = [wd_num] if wd_num else [1, 2, 3, 5, 10, 4, 6, 7, 8, 9, 11, 12]

    last_error = None
    for n in wd_candidates:
        base = f"https://{tenant}.wd{n}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
        try:
            resp = requests.post(base, json=payload, headers=HEADERS, timeout=TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                jobs = []
                for j in data.get("jobPostings", []):
                    path = j.get("externalPath", "")
                    jobs.append({
                        "id": f"workday:{tenant}:{path}",
                        "title": j.get("title", ""),
                        "location": j.get("locationsText", ""),
                        "url": f"https://{tenant}.wd{n}.myworkdayjobs.com/{site}{path}",
                        "description": "",  # Workday search results don't include full JD; title+location filtering only
                        "company": company,
                    })
                return jobs
            else:
                last_error = requests.HTTPError(f"{resp.status_code} Client Error for wd{n}: {base}")
        except requests.RequestException as e:
            last_error = e

    # None of the wd_num candidates worked - the "site" segment is probably
    # wrong too (this varies per company, e.g. "Visa" vs "Visa_Careers").
    # Re-raise the last error so it shows up in the check-config / run logs.
    raise last_error or Exception(f"Could not resolve Workday endpoint for {company}")
