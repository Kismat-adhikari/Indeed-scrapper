# 🚀 How to Use the Indeed Job Scraper

## 📋 Prerequisites

Before running the scraper, make sure you have everything set up:

### 1. Required Files
- ✅ `scraper_selenium.py` - Main scraper
- ✅ `proxies.txt` - **ESSENTIAL** - Proxy servers for avoiding detection
- ✅ `.env` - Database credentials 
- ✅ `view_jobs.py` - To view saved jobs

### 2. Required Software
- **Chrome Browser** - Must be installed on your system
- **Python 3.7+** - With pip package manager

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `selenium` - For browser automation
- `webdriver-manager` - Auto-manages Chrome driver
- `supabase` - Database connection
- `python-dotenv` - Environment variables

## 🔧 Setup Instructions

### Step 1: Verify Proxies File
Check that `proxies.txt` exists and has proxy servers in this format:
```
ip:port:username:password
ip:port:username:password
```

**⚠️ IMPORTANT:** Without valid proxies, Indeed may block your requests!

### Step 2: Configure Database
Make sure `.env` file contains:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Step 3: Test Chrome Installation
Chrome browser must be installed for Selenium to work.

## 🎯 Running the Scraper

### Command:
```bash
python scraper_selenium.py
```

### Follow the Prompts:

1. **What jobs?** 
   - Enter keywords separated by commas
   - Example: `python developer, software engineer, data analyst`

2. **Where?**
   - Enter locations separated by commas  
   - Example: `remote, new york, san francisco`

3. **How many pages?**
   - Enter 1-5 (recommended: 2-3)
   - Each page = ~10-15 jobs

4. **Ready?**
   - Type `yes` to start scraping

## 📊 What Happens Next

1. **Browser Initialization**: Chrome opens in background (headless mode)
2. **Proxy Usage**: Rotates through proxies to avoid detection
3. **Job Scraping**: Visits Indeed search pages and extracts job data
4. **Detailed Extraction**: Visits individual job pages for complete salary information
5. **Data Saving**: Saves to both:
   - Text file: `scraped_jobs_TIMESTAMP.txt`
   - Database: Supabase (for querying later)

## 📁 Output Files

### Text File Format:
```
================================================================================
TITLE: Senior Python Developer
COMPANY: Tech Corp
LOCATION: Remote
SALARY: $120,000 - $150,000 a year
POSTED: 2 days ago
LINK: https://indeed.com/viewjob?jk=abc123
SUMMARY: We are looking for a skilled Python developer...
================================================================================
```

**Note**: The scraper now visits individual job pages to get accurate salary data, so it takes a bit longer but provides complete information!

### View Database Results:
```bash
python view_jobs.py
```

## ⚠️ Troubleshooting

### Common Issues:

**1. "Selenium not installed" Error:**
```bash
pip install selenium webdriver-manager
```

**2. "Chrome not found" Error:**
- Install Chrome browser from google.com/chrome

**3. "No jobs found" Error:**
- Check your keywords/locations are valid
- Verify proxies.txt has working proxies
- Try different search terms

**4. Database Connection Error:**
- Check .env file has correct Supabase credentials
- Verify internet connection

### Success Indicators:
- ✅ Browser initializes successfully
- ✅ Found X job elements on each page
- ✅ Saved X new jobs from page Y
- ✅ Results saved to scraped_jobs_TIMESTAMP.txt

## 🔄 Best Practices

1. **Start Small**: Test with 1-2 pages first
2. **Valid Proxies**: Ensure proxies.txt has working proxies
3. **Reasonable Delays**: Don't change the built-in delays
4. **Monitor Logs**: Watch console output for errors
5. **Check Results**: Verify jobs are being saved correctly

## 💡 Pro Tips

- Use specific job titles for better results
- "Remote" location often has most jobs
- Run during business hours for fresh postings
- Check generated text files after each run
- Use `view_jobs.py` to query saved data instead of re-scraping