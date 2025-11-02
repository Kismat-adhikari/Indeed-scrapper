# Indeed Job Scraper

A robust Python-based web scraper that collects job listings from Indeed and stores them in a Supabase database with proxy rotation support.

## Features

- ✅ **Multi-keyword & Multi-location Search**: Search for multiple job types across different locations
- ✅ **Proxy Rotation**: Automatic proxy rotation from `proxies.txt` to avoid detection
- ✅ **Duplicate Prevention**: Checks existing database entries to avoid duplicate job listings
- ✅ **Random Delays**: Uses random delays between requests to mimic human behavior
- ✅ **Pagination Support**: Automatically follows multiple pages of search results
- ✅ **Comprehensive Data Extraction**: Extracts job title, company, location, salary, description, link, and posted date
- ✅ **Error Handling**: Robust retry logic with exponential backoff
- ✅ **Logging**: Detailed logging to both console and log file

## Prerequisites

- Python 3.8 or higher
- Supabase account with a database table
- Proxy list (optional but recommended)

## Installation

1. **Clone or download this repository**

2. **Install required packages:**
```bash
pip install -r requirements.txt
```

3. **Set up your environment variables:**
   - Make sure your `.env` file contains:
   ```
   SUPABASE_URL=your_supabase_url_here
   SUPABASE_KEY=your_supabase_anon_key_here
   ```

4. **Add proxies to `proxies.txt`** (one per line in format: `ip:port:username:password`)

## Database Schema

Make sure your Supabase database has this table:

```sql
CREATE TABLE indeed_jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT,
    company TEXT,
    location TEXT,
    salary TEXT,
    summary TEXT,
    link TEXT,
    posted_date TEXT,
    scraped_at TIMESTAMP DEFAULT NOW()
);
```

## Usage

### Method 1: Using the Simple Runner (Recommended)

1. **Edit `config.py`** to customize your search parameters:
   ```python
   KEYWORDS = ["software engineer", "data analyst"]
   LOCATIONS = ["New York", "Remote"]
   MAX_PAGES_PER_SEARCH = 3
   ```

2. **Run the scraper:**
   ```bash
   python run_scraper.py
   ```

### Method 2: Using the Main Script Directly

Run with default settings:
```bash
python indeed_scraper.py
```

Or customize in the script's `main()` function.

### Method 3: Import as a Module

```python
from indeed_scraper import IndeedScraper

scraper = IndeedScraper()

# Scrape jobs
scraper.scrape_jobs(
    keywords=["python developer", "data scientist"],
    locations=["San Francisco", "Remote"],
    max_pages=5,
    delay_range=(3, 8)
)
```

## Configuration Options

### In `config.py`:

- **KEYWORDS**: List of job search terms
- **LOCATIONS**: List of locations to search (use "Remote" for remote jobs)
- **MAX_PAGES_PER_SEARCH**: Number of pages to scrape per keyword/location combo
- **DELAY_MIN / DELAY_MAX**: Random delay range between requests (seconds)

### Search Tips:

- **Keywords**: Be specific (e.g., "senior python developer" vs "developer")
- **Locations**: Use city, state format (e.g., "New York, NY") or "Remote"
- **Pages**: Each page contains ~10-15 jobs, don't set too high to avoid bans

## How It Works

1. **Initialization**: Loads proxies, connects to Supabase, fetches existing job links
2. **URL Building**: Creates Indeed search URLs with specified keywords and locations
3. **Request Making**: Makes HTTP requests with rotating proxies and random user agents
4. **HTML Parsing**: Extracts job data using BeautifulSoup
5. **Duplicate Check**: Compares job links against existing database entries
6. **Data Storage**: Saves new jobs to Supabase database
7. **Pagination**: Continues to next pages until max_pages reached or no more results

## Output

- **Console Logging**: Real-time progress updates
- **Log File**: `scraper.log` contains detailed operation logs
- **Database**: Jobs stored in Supabase `indeed_jobs` table

## Error Handling

The scraper includes:
- Retry logic for failed requests (3 attempts by default)
- Exponential backoff on failures
- Proxy rotation on errors
- Graceful handling of missing elements
- Rate limit detection and handling

## Best Practices

1. **Use Proxies**: Essential for avoiding IP bans
2. **Random Delays**: Keep delays between 3-10 seconds
3. **Limit Pages**: Don't scrape too many pages in one session
4. **Monitor Logs**: Check `scraper.log` for issues
5. **Run Periodically**: Schedule daily or weekly runs instead of continuous scraping

## Troubleshooting

### No jobs found:
- Check if Indeed has changed their HTML structure
- Verify your proxies are working
- Try different keywords or locations

### Database connection errors:
- Verify your Supabase credentials in `.env`
- Check your internet connection
- Ensure the table exists with correct schema

### Proxy errors:
- Validate proxy format in `proxies.txt`
- Test proxies manually
- Try running without proxies temporarily

### Rate limiting:
- Increase delay range in config
- Reduce MAX_PAGES_PER_SEARCH
- Use more proxies

## Legal Disclaimer

This scraper is for educational purposes only. Always:
- Review Indeed's Terms of Service
- Respect robots.txt
- Don't overload their servers
- Use reasonable delays between requests
- Consider using Indeed's official API if available

## License

MIT License - feel free to modify and use as needed.

## Support

For issues or questions:
1. Check the logs in `scraper.log`
2. Verify your configuration settings
3. Ensure all dependencies are installed correctly
