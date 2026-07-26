"""
Filters jobs down to: Software Engineer 1/2 equivalent, <=5 years experience,
India location, excluding internships/co-ops.

This is heuristic - titles and leveling conventions vary a LOT by company
(Amazon: SDE1/SDE2, Google: L3/L4, Meta: E3/E4, most others: "Software
Engineer" with no number, or "Software Engineer I/II"). Tune the keyword
lists below as you see false positives/negatives come through.
"""
import re

# Titles that qualify as junior/mid-level SWE roles
# (?=\s|-|\d|$) after swe/sde allows "SDE1", "SDE-1", "SDE 1", "SDE" with no
# trailing space to all match, instead of requiring a word boundary that
# digits don't create.
TITLE_INCLUDE = re.compile(
    r"\b(software engineer|swe(?=\s|-|\d|$)|sde(?=\s|-|\d|$)|"
    r"full[\s-]?stack (developer|engineer)|"
    r"backend (developer|engineer)|frontend (developer|engineer)|"
    r"platform engineer|systems? engineer|application engineer)",
    re.IGNORECASE,
)

# Level markers indicating junior/mid (I, II, 1, 2, L3, L4, E3, E4) - optional signal
LEVEL_JUNIOR = re.compile(
    r"\b(i{1,2}|1|2|l3|l4|e3|e4|junior|associate)\b", re.IGNORECASE
)

# Anything with these terms gets excluded outright
TITLE_EXCLUDE = re.compile(
    r"\b(intern|internship|co-?op|senior|staff|principal|lead|architect|"
    r"manager|director|vp|head of|iii|iv|v\b|sde\s*3|sde\s*4|l5|l6|l7|e5|e6|"
    r"sde-3|sde-4)\b",
    re.IGNORECASE,
)

# "up to 5 years" experience patterns in job descriptions
EXPERIENCE_PATTERN = re.compile(
    r"(\d+)\s*(?:\+|-|to)?\s*(?:\d+)?\s*years?", re.IGNORECASE
)

INDIA_LOCATION = re.compile(
    r"\b(india|bangalore|bengaluru|hyderabad|pune|gurgaon|gurugram|noida|"
    r"delhi|mumbai|chennai|kolkata|remote[\s-]?india)\b",
    re.IGNORECASE,
)


def max_experience_mentioned(text):
    """Return the highest number-of-years figure mentioned, or None if none found."""
    years = []
    for m in re.finditer(r"(\d+)\s*(?:\+|-|to|–)\s*(\d+)\s*years?", text, re.IGNORECASE):
        years.append(int(m.group(2)))
    for m in re.finditer(r"(\d+)\+?\s*years?", text, re.IGNORECASE):
        years.append(int(m.group(1)))
    return max(years) if years else None


def is_relevant_job(job, max_years=5):
    title = job.get("title", "")
    description = job.get("description", "") or ""
    location = job.get("location", "") or ""

    if TITLE_EXCLUDE.search(title):
        return False, "excluded keyword in title"

    if not TITLE_INCLUDE.search(title):
        return False, "not a matching engineering title"

    # Location check - only apply if location field is populated (some ATS's give empty strings)
    combined_location_text = f"{location} {description[:300]}"
    if location and not INDIA_LOCATION.search(combined_location_text):
        return False, "not India-based"

    # Experience check - only enforce if a number of years is actually mentioned
    exp = max_experience_mentioned(description)
    if exp is not None and exp > max_years:
        return False, f"requires {exp} years (> {max_years})"

    return True, "match"


def filter_jobs(jobs, max_years=5):
    matches = []
    for job in jobs:
        ok, _reason = is_relevant_job(job, max_years=max_years)
        if ok:
            matches.append(job)
    return matches
