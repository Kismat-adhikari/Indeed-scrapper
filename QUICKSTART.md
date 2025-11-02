# 🚀 Quick Start Guide

## Setup Complete! ✅

Your Indeed Job Scraper is ready to use. Here's how to get started:

---

## 📋 What You Have

- ✅ `indeed_scraper.py` - Main scraper module
- ✅ `run_scraper.py` - Simple runner script
- ✅ `config.py` - Configuration settings
- ✅ `test_setup.py` - Setup verification
- ✅ `view_jobs.py` - Database viewer utility
- ✅ `requirements.txt` - Python dependencies
- ✅ `.env` - Supabase credentials (configured)
- ✅ `proxies.txt` - Proxy list (configured)

---

## 🎯 Quick Commands

### 1. Test Your Setup
```bash
python test_setup.py
```
This verifies all dependencies and connections are working.

### 2. Customize Your Search
Edit `config.py` and modify:
```python
KEYWORDS = ["software engineer", "python developer"]
LOCATIONS = ["New York, NY", "Remote"]
MAX_PAGES_PER_SEARCH = 3
```

### 3. Run the Scraper
```bash
python run_scraper.py
```
This starts scraping with your configured settings.

### 4. View Your Data
```bash
python view_jobs.py
```
Interactive menu to view, search, and export scraped jobs.

---

## 🔧 Configuration Options

### In `config.py`:

```python
# What jobs to search for
KEYWORDS = ["software engineer", "data scientist", "devops"]

# Where to search
LOCATIONS = ["New York", "San Francisco", "Remote"]

# How many pages per search (each page ≈ 10-15 jobs)
MAX_PAGES_PER_SEARCH = 5

# Delays between requests (seconds)
DELAY_MIN = 3
DELAY_MAX = 8
```

---

## 📊 Example Usage

### Basic Scraping
```bash
# Use default settings from config.py
python run_scraper.py
```

### Custom Scraping (in Python)
```python
from indeed_scraper import IndeedScraper

scraper = IndeedScraper()
scraper.scrape_jobs(
    keywords=["remote python developer"],
    locations=["United States"],
    max_pages=10,
    delay_range=(5, 12)
)
```

---

## 🎨 Expected Output

When you run the scraper, you'll see:
```
============================================================
Starting Indeed Job Scraper
============================================================

2024-11-02 10:30:45 - INFO - Loaded 10 proxies
2024-11-02 10:30:46 - INFO - Loaded 0 existing job links from database

============================================================
Scraping: 'software engineer' in 'New York, NY'
============================================================

2024-11-02 10:30:47 - INFO - Processing page 1/3 (start=0)
2024-11-02 10:30:48 - INFO - Found 15 job cards on page
2024-11-02 10:30:48 - INFO - Parsed 15 valid jobs from page
2024-11-02 10:30:49 - INFO - Saved: Senior Software Engineer at Google
2024-11-02 10:30:49 - INFO - Saved: Python Developer at Microsoft
...
2024-11-02 10:30:55 - INFO - Saved 15 new jobs from this page

============================================================
✓ Scraping completed successfully!
✓ Total new jobs saved: 45
============================================================
```

---

## 💡 Tips for Success

### 1. Start Small
- Begin with 1-2 keywords and 1-2 locations
- Use `MAX_PAGES_PER_SEARCH = 2` for testing

### 2. Use Good Delays
- Keep `DELAY_MIN` at least 3 seconds
- Higher delays = less likely to get blocked

### 3. Proxy Management
- If proxies fail, the scraper will retry
- Monitor the logs for proxy errors
- Consider rotating proxy providers if needed

### 4. Run Periodically
- Daily scraping: capture new postings
- Weekly scraping: avoid rate limits
- Don't run continuously

### 5. Monitor Your Data
```bash
python view_jobs.py
```
Use option 2 to see statistics about your scraped data.

---

## 🐛 Troubleshooting

### No Jobs Found?
- Check if Indeed changed their HTML structure
- Try different keywords/locations
- Verify proxies are working

### Database Errors?
- Verify `.env` credentials
- Check Supabase dashboard
- Ensure table exists with correct schema

### Rate Limited?
- Increase delays in `config.py`
- Use more/better proxies
- Reduce `MAX_PAGES_PER_SEARCH`

---

## 📝 Logging

Logs are saved to:
- **Console**: Real-time progress
- **scraper.log**: Detailed operation logs

Check logs if something goes wrong:
```bash
# Windows PowerShell
Get-Content scraper.log -Tail 50

# Or open in text editor
notepad scraper.log
```

---

## 🔄 Regular Maintenance

### Weekly Tasks:
1. Check `scraper.log` for errors
2. Verify proxies still work
3. Update keywords if needed
4. Export data: `python view_jobs.py` → option 4

### Monthly Tasks:
1. Review statistics in `view_jobs.py`
2. Clean up old/duplicate entries
3. Update requirements: `pip install -r requirements.txt --upgrade`

---

## 🎓 Next Steps

1. **Run your first scrape:**
   ```bash
   python run_scraper.py
   ```

2. **View your results:**
   ```bash
   python view_jobs.py
   ```

3. **Customize for your needs:**
   - Edit `config.py` with your target jobs
   - Adjust delays and page limits
   - Add more keywords/locations

4. **Schedule regular scraping:**
   - Windows Task Scheduler
   - Cron jobs (Linux/Mac)
   - Cloud functions (for automation)

---

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `indeed_scraper.py` | Core scraping logic |
| `run_scraper.py` | Simple runner |
| `config.py` | Search settings |
| `test_setup.py` | Verify setup |
| `view_jobs.py` | View/analyze data |
| `.env` | Credentials |
| `proxies.txt` | Proxy list |
| `scraper.log` | Operation logs |

---

## ⚠️ Legal Reminder

- This is for educational/personal use
- Respect Indeed's Terms of Service
- Don't overload their servers
- Use reasonable delays
- Consider Indeed's official API for commercial use

---

## 🆘 Need Help?

1. Run: `python test_setup.py`
2. Check: `scraper.log`
3. Verify: credentials in `.env`
4. Test: proxies in `proxies.txt`

---

**Happy Scraping! 🎉**
