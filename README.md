# 🔍 Indeed Job Scraper

A powerful, fully local Python scraper for Indeed.com job listings. No API keys required!

## ✨ Features

- 🚀 **100% Local** - Runs entirely on your machine
- 🔄 **Proxy Rotation** - Automatically rotates through your proxy list
- ⚡ **Async Scraping** - Fast concurrent scraping with Playwright
- 📊 **Rich Output** - Clean JSON results with detailed job information
- 🎨 **Beautiful CLI** - Progress tracking with Rich library
- 🛡️ **Error Handling** - Graceful fallbacks and retry logic

## 📁 Project Structure

```
indeed_scraper/
│
├─ main.py              # CLI entry point
├─ scraper.py           # Core scraping logic (async, Playwright)
├─ proxy_manager.py     # Proxy rotation and error handling
├─ proxies.txt          # Your proxy list (already included)
├─ requirements.txt     # Required libraries
├─ README.md            # This file
└─ output/
   └─ results.json      # Generated JSON output (created after first run)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

```bash
playwright install
```

### 3. Run the Scraper

```bash
python main.py
```

### 4. Follow the Prompts

- Enter an Indeed search URL (e.g., `https://www.indeed.com/jobs?q=software+engineer&l=Remote`)
- Enter the number of pages to scrape (e.g., `3`)

### 5. View Results

Results are saved to `output/results.json`

## 📝 Proxy Format

Your `proxies.txt` file should contain one proxy per line in this format:

```
host:port:username:password
```

Example:
```
72.46.139.137:6697:tnfqnyqb:bsjia1uasdxr
45.196.40.119:6197:tnfqnyqb:bsjia1uasdxr
```

Alternative formats supported:
- `host:port` (no authentication)
- `host:port:username` (no password)

## 📊 Output Format

Each job in the uniquely-named JSON file (e.g., `results_20251105_143022.json`) contains:

```json
{
  "title": "Software Engineer",
  "company": "Tech Corp",
  "location": "Remote",
  "salary": "$120,000 - $150,000 a year",
  "job_type": "Full-time",
  "posted_date": "Just posted",
  "summary": "We are looking for...",
  "url": "https://www.indeed.com/viewjob?jk=abc123",
  "scraped_from_page": 1
}
```

**Note:** Each scrape creates a new JSON file with a timestamp to preserve historical data.

## 🔧 Troubleshooting

### Timeout Errors

The scraper now includes:
- Extended timeouts (45s for navigation, 15s for selectors)
- Multiple retry attempts per page (up to 2 retries)
- Automatic fallback from proxy to direct connection
- Multiple selector strategies for resilience

### Salary Not Extracting

Fixed with:
- Multiple salary selector strategies
- Checks for $ symbols and numeric values
- Proper separation of salary from job_type metadata
- Handles ranges, hourly, and annual formats

### Invalid Job URLs

Fixed by:
- Multiple URL extraction methods
- Direct job ID (`data-jk`) extraction
- Proper URL construction for Indeed's format
- Fallback URL building from multiple sources

## 🎯 Usage Examples

### Example 1: Software Engineer Jobs
```
URL: https://www.indeed.com/jobs?q=software+engineer&l=Remote
Pages: 3
Expected Results: ~45 jobs
```

### Example 2: Data Analyst Jobs
```
URL: https://www.indeed.com/jobs?q=data+analyst&l=New+York
Pages: 5
Expected Results: ~75 jobs
```

## 🔮 Future Enhancements (Roadmap)

Planned features (commented in code):

- **AI-Based Selector Repair** - Auto-detect when Indeed changes HTML structure
- **Database Integration** - Save to Supabase/MongoDB
- **CLI Flags** - `--url`, `--pages`, `--output` for automation
- **Email Notifications** - Get notified when scraping completes
- **Scheduler** - Run automatically on a schedule
- **Advanced Filters** - Filter by salary, date, job type
- **Multiple Export Formats** - CSV, Excel support

## ⚙️ Technical Details

- **Python Version**: 3.10+
- **Browser**: Chromium (via Playwright)
- **Async Runtime**: asyncio
- **Parsing**: BeautifulSoup4
- **UI**: Rich library

## 🤝 Contributing

Feel free to fork and submit pull requests!

## 📄 License

MIT License - Use freely!

## ⚠️ Disclaimer

This tool is for educational purposes. Always respect Indeed's Terms of Service and robots.txt. Use responsibly and don't overload their servers.

---

**Happy Scraping! 🎉**
