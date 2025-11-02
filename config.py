"""
Configuration file for Indeed Job Scraper
Modify these settings to customize your scraping behavior
"""

# Search keywords to look for
KEYWORDS = [
    "software engineer",
    "python developer",
    "data analyst",
    "web developer",
    "machine learning engineer",
    "devops engineer"
]

# Locations to search in
LOCATIONS = [
    "New York, NY",
    "San Francisco, CA",
    "Los Angeles, CA",
    "Chicago, IL",
    "Seattle, WA",
    "Remote",
    "Austin, TX",
    "Boston, MA"
]

# Scraping settings
MAX_PAGES_PER_SEARCH = 5  # Number of pages to scrape per keyword/location combo
DELAY_MIN = 3  # Minimum delay between requests (seconds)
DELAY_MAX = 8  # Maximum delay between requests (seconds)

# Database settings (loaded from .env)
# SUPABASE_URL - set in .env file
# SUPABASE_KEY - set in .env file

# Proxy settings
PROXY_FILE = "proxies.txt"  # Path to proxy file
USE_PROXIES = True  # Set to False to disable proxy usage
