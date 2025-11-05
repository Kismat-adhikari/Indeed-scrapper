"""
Test Session-Based Scraper
==========================
"""

from scraper_v3 import IndeedScraperV3
from proxy_manager import ProxyManager

def test_session_scraper():
    """Test the session-based scraper."""
    print("🧪 Testing session-based Indeed scraper...")
    
    # Load a few proxies for testing
    pm = ProxyManager('proxies.txt')
    proxies = pm.load_proxies()[:3]  # Use only 3 proxies for testing
    
    print(f"📡 Loaded {len(proxies)} proxies for testing")
    
    # Create scraper instance
    url = "https://www.indeed.com/jobs?q=python+developer&l=Minnesota"
    scraper = IndeedScraperV3(url, 6, proxies)  # Test with 6 pages to trigger session rotation
    
    # Run scraper
    jobs = scraper.scrape_all_pages()
    
    print(f"\n✅ Test completed!")
    print(f"📊 Total jobs scraped: {len(jobs)}")
    
    if jobs:
        print(f"📝 Sample job: {jobs[0].get('title', 'N/A')} at {jobs[0].get('company', 'N/A')}")

if __name__ == "__main__":
    test_session_scraper()