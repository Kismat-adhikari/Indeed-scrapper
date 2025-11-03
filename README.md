# 🎯 Indeed Job Scraper (Selenium Version)

A working Indeed job scraper that bypasses anti-bot detection using Selenium.

## ✅ Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the scraper:**
```bash
python scraper_selenium.py
```

3. **Follow the prompts:**
- Jobs: `python developer, software engineer`
- Location: `remote, new york`  
- Pages: `2`
- Ready: `yes`

4. **View results:**
- Check the generated `scraped_jobs_TIMESTAMP.txt` file
- Run `python view_jobs.py` to query the database

## 📁 Files

| File | Purpose |
|------|---------|
| `scraper_selenium.py` | Main working scraper (uses real browser) |
| `view_jobs.py` | Query and analyze saved jobs |
| `.env` | Database credentials |
| `requirements.txt` | Dependencies |

## 🔧 Why This Works

- Uses **real Chrome browser** (Selenium) 
- Looks like human browsing to Indeed
- Can't be detected as a bot
- Successfully finds and saves jobs

## 📊 Output

Jobs are saved to:
1. **Text file** - `scraped_jobs_TIMESTAMP.txt` (human readable)
2. **Database** - Supabase (for querying/analysis)

---

*Previous scrapers that used `requests` library were blocked by Indeed with 403 errors. This Selenium version works!*