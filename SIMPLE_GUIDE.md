# ✨ SIMPLE GUIDE - Indeed Job Scraper

## 🚀 Quick Start (3 Steps)

### Step 1: Open Terminal
Open PowerShell or Command Prompt in this folder

### Step 2: Run This Command
```bash
python scraper_interactive.py
```

### Step 3: Answer the Questions
```
What jobs? → Type: python developer, data analyst
Where? → Type: New York, Remote  
How many pages? → Type: 3
Ready? → Type: yes
```

**That's it!** Wait a few minutes and you'll get a text file with all the jobs!

---

## 📁 What You Get

After it finishes, you'll have a file like:
```
scraped_jobs_20251102_145830.txt
```

Open it with Notepad to see all your jobs!

Each job shows:
- ✅ Job title
- ✅ Company name
- ✅ Location
- ✅ Salary (if listed)
- ✅ Description
- ✅ Link to apply

---

## ⏱️ How Long Does It Take?

**Quick search** (2 keywords, 2 locations, 2 pages): ~5 minutes
**Medium search** (3 keywords, 3 locations, 3 pages): ~10 minutes
**Big search** (5 keywords, 5 locations, 5 pages): ~25 minutes

You can stop it anytime by pressing `Ctrl+C`

---

## 💾 Where Is Everything Saved?

1. **Text File** → `scraped_jobs_TIMESTAMP.txt` (easy to read)
2. **Database** → Supabase (for searching later)
3. **Log File** → `scraper.log` (if you need to debug)

---

## 🎯 Tips for Best Results

### Good Keywords:
- ✅ "python developer"
- ✅ "data analyst remote"
- ✅ "software engineer"
- ✅ "machine learning"

### Bad Keywords:
- ❌ "job" (too broad)
- ❌ "work" (too broad)
- ❌ Single letters or numbers

### Good Locations:
- ✅ "New York, NY"
- ✅ "Remote"
- ✅ "San Francisco, CA"
- ✅ "United States"

### Pages:
- Start with 2-3 pages
- Each page = ~10-15 jobs
- More pages = more time

---

## 🐛 Problems?

### It's stuck?
- **Wait**: Each page takes ~10 seconds (this is normal!)
- **Stop it**: Press `Ctrl+C` if you want to cancel
- **Check**: Look at `scraper.log` to see what's happening

### No jobs found?
- Try different keywords
- Try "Remote" as location
- Check if Indeed.com is working

### Errors?
1. Check `scraper.log` file
2. Make sure your `.env` file has Supabase credentials
3. Make sure `proxies.txt` has proxies

---

## 📖 Want More Details?

- **How does it work?** → Read `HOW_IT_WORKS.md`
- **Full documentation** → Read `README.md`
- **Quick reference** → Read `QUICKSTART.md`

---

## 🎉 Example Session

```
> python scraper_interactive.py

============================================================
           INDEED JOB SCRAPER
============================================================

What job titles are you looking for?
   Enter keywords: python developer, data scientist

✓ Searching for: python developer, data scientist

Where should I search?
   Enter locations: Remote, New York

✓ Searching in: Remote, New York

How many pages should I scrape per search?
   Enter number of pages: 3

✓ Scraping 3 pages per search

============================================================
SEARCH SUMMARY
============================================================
Keywords: 2
Locations: 2
Total searches: 4
Total pages: 12
Estimated jobs: 144
Estimated time: 2.0 minutes
============================================================

Ready to start? yes

============================================================
STARTING SCRAPER...
============================================================

[... scraping happens here ...]

============================================================
✓ SCRAPING COMPLETED!
============================================================
✓ Total new jobs saved to database: 127
✓ Results also saved to: scraped_jobs_20251102_145830.txt
✓ Detailed logs saved to: scraper.log
============================================================

View your results:
  1. Open 'scraped_jobs_20251102_145830.txt' to see all jobs
  2. Run 'python view_jobs.py' to query database
  3. Check 'scraper.log' for detailed logs
```

---

## 🎓 Summary

**What it does:**
Searches Indeed for jobs and saves them to a text file

**How to use it:**
Run `python scraper_interactive.py` and answer questions

**What you get:**
A text file with all the jobs you can open in Notepad

**How long:**
5-20 minutes depending on how much you search

**Problems?**
Check `scraper.log` or read `HOW_IT_WORKS.md`

---

**That's it! Start searching for jobs now! 🚀**
