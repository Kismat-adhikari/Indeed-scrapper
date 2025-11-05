# 🚀 Quick Start Guide - Indeed Scraper v2.0

## ⚡ Fastest Way to Get Started

### 1️⃣ Install Dependencies (First Time Only)
```powershell
pip install -r requirements.txt
playwright install
```

### 2️⃣ Run the Scraper
```powershell
python main.py
```

### 3️⃣ Enter Your Search Details
```
Enter Indeed search URL: https://www.indeed.com/jobs?q=python+developer&l=Remote
Enter number of pages to scrape: 3
```

### 4️⃣ Wait for Results
The scraper will:
- ✅ Load your proxies from `proxies.txt`
- ✅ Scrape each page (showing progress)
- ✅ Save results to `output/results_TIMESTAMP.json`

### 5️⃣ View Your Data
```powershell
# Open the most recent results file
code output\results_*.json
```

---

## 🧪 Quick Test (1 Page Only)

Test the scraper with a single page:
```powershell
python test_scraper.py
```

This will:
- Scrape just 1 page
- Show data quality metrics
- Save to `output/test_results.json`

---

## 📊 What You Get

Each JSON file contains job data:
```json
{
  "title": "Python Developer",
  "company": "Tech Company",
  "location": "Remote",
  "salary": "$100,000 - $130,000 a year",
  "job_type": "Full-time",
  "posted_date": "Just posted",
  "summary": "Job description here...",
  "url": "https://www.indeed.com/viewjob?jk=abc123",
  "scraped_from_page": 1
}
```

---

## 🎯 Best Practices

### ✅ DO:
- Start with 1-3 pages for testing
- Check `output/` folder for results
- Use specific search queries (job title + location)
- Wait 3-5 seconds between large scrapes

### ❌ DON'T:
- Scrape 50+ pages in one run (be respectful)
- Run multiple instances simultaneously
- Use broken/invalid proxies

---

## 🔍 Popular Search URLs

### Software Engineering:
```
https://www.indeed.com/jobs?q=software+engineer&l=Remote
https://www.indeed.com/jobs?q=python+developer&l=San+Francisco
https://www.indeed.com/jobs?q=full+stack+developer&l=New+York
```

### Data Science:
```
https://www.indeed.com/jobs?q=data+scientist&l=Remote
https://www.indeed.com/jobs?q=data+analyst&l=Austin
https://www.indeed.com/jobs?q=machine+learning+engineer&l=Seattle
```

### Design:
```
https://www.indeed.com/jobs?q=UI+designer&l=Remote
https://www.indeed.com/jobs?q=UX+designer&l=Los+Angeles
```

---

## 🆘 Common Issues

### "No module named 'playwright'"
```powershell
pip install playwright
playwright install
```

### "Timeout errors"
- Check your internet connection
- Try without proxies first
- Increase delay between pages

### "No jobs found"
- Verify your URL is correct
- Make sure Indeed is accessible in your region
- Try a different search query

---

## 📈 Expected Results

| Pages | Jobs Expected | Time Estimate |
|-------|---------------|---------------|
| 1     | ~15 jobs      | 15-20 seconds |
| 3     | ~45 jobs      | 50-60 seconds |
| 5     | ~75 jobs      | 90-120 seconds|

*Times vary based on proxies and connection speed*

---

## 💡 Pro Tips

1. **Test First**: Run `python test_scraper.py` before large scrapes
2. **Check URLs**: Validate a few job URLs are working
3. **Monitor Output**: Watch terminal for any errors
4. **Unique Files**: Each scrape creates a new file - no overwrites!
5. **Data Quality**: Expect 85%+ salary extraction rate

---

## 🎉 You're Ready!

Run this now:
```powershell
python main.py
```

Happy scraping! 🚀

---

**Need help?** Check these files:
- `README.md` - Full documentation
- `CHANGELOG.md` - What changed in v2.0
- `UPDATE_SUMMARY.md` - Detailed improvements
- `CODE_COMPARISON.py` - Before/after code examples
