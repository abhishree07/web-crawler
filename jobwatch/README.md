# Job Alert Bot

Watches career pages for SDE1/SDE2-equivalent roles (≤5 years experience,
excludes internships), based in India, and sends a Telegram message for
each new matching posting. Runs for free on GitHub Actions every 3 hours —
no server needed.

## 1. Push this to your GitHub repo

Copy all these files into your existing repo, then commit and push.

## 2. Add your Telegram credentials as GitHub Secrets

In your repo: **Settings → Secrets and variables → Actions → New repository secret**

Add two secrets:
- `TELEGRAM_BOT_TOKEN` — your bot's API token (from BotFather)
- `TELEGRAM_CHAT_ID` — your Telegram chat ID

Never commit these directly into the code or config files.

## 3. Enable GitHub Actions

Go to the **Actions** tab in your repo and enable workflows if prompted.
The workflow (`.github/workflows/job_alert.yml`) will run automatically
every 3 hours. You can also trigger it manually anytime from the Actions
tab ("Run workflow" button) to test it immediately.

## 4. Verify the company configs work (important first step)

Some entries in `config/companies.yaml` and `src/custom_sites.py` are
marked `# VERIFY` — I wrote these without live internet access, based on
known API patterns, but some board tokens / endpoints may need a small
correction. To check them all at once:

1. Go to the Actions tab → run the workflow manually once, OR
2. Run locally: `pip install -r requirements.txt && python src/main.py --check-config`

This prints `[OK]` or `[FAIL]` for every company without sending any
Telegram messages, so you can quickly see which entries need fixing.

### Fixing a failed entry
- **Greenhouse**: visit `https://boards.greenhouse.io/<guess>` — if it 404s,
  google "`<company> careers greenhouse`" to find the real board token.
- **Lever**: visit `https://jobs.lever.co/<guess>` similarly.
- **Workday**: open the company's actual careers page, check the URL —
  it'll look like `https://COMPANY.wdN.myworkdayjobs.com/SITE`. Update
  `tenant`, `site`, and the `wd_num` (wd1, wd3, wd5, etc.) accordingly.

## 5. Add more companies

Copy a block in `config/companies.yaml` and fill in the token. For a
company with no ATS API at all, add a small function to
`src/custom_sites.py` (there are several examples already) and register
it in the `HANDLERS` dict.

## 6. Tune the filtering

`src/filters.py` controls what counts as a "match":
- `TITLE_INCLUDE` — engineering title keywords
- `TITLE_EXCLUDE` — seniority/internship terms that disqualify a posting
- `INDIA_LOCATION` — Indian cities/keywords
- `max_experience_mentioned()` — parses "X-Y years" out of the job description

If you start getting too many/few notifications, tweak these regexes.

## How it avoids duplicate alerts

`data/seen_jobs.json` stores the IDs of every job already notified about.
The GitHub Action commits this file back to the repo after each run, so
state persists across scheduled runs.

## Interview difficulty note

Per your request, the config is deliberately **not** loading up on quant/HFT
firms (Jane Street, Two Sigma, HRT, Citadel, DRW, Optiver, IMC, SIG, etc.) —
those typically have the hardest, most specialized interview loops (advanced
algo/probability/latency-focused rounds) and aren't the fastest path to an
offer in 2-3 months. The current list leans toward companies known for
solid pay with a more standard DSA + system design bar: Databricks, Airbnb,
Coinbase, Figma, Confluent, Razorpay, CRED, Meesho, PhonePe, Zeta, Groww,
Abnormal Security, Rubrik, Cohesity, etc. Tell me if you want more of a
specific flavor (fintech, e-commerce, SaaS) and I'll expand the config
further in that direction.

## Notes / limitations

- Meta's careers site has no stable public API (JS-rendered) — left
  unimplemented for now; flag it if you want it added via a headless
  browser approach.
- Some Indian startups (Flipkart, Zomato, PhonePe, Myntra) don't have a
  documented public jobs API either — placeholders are in
  `custom_sites.py` returning no jobs until filled in.
- Quant/prop-trading firms from your list (Jane Street, Two Sigma, HRT,
  Citadel, DRW, etc.) are intentionally left out of v1 since they rarely
  post numbered SDE1/SDE2 India roles — easy to add the same way as
  others if you want them included.
