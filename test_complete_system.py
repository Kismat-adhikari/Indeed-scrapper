"""
Test Complete Session-Based Scraper with Proxy Authentication
=============================================================
"""

from scraper_v3 import IndeedScraperV3

def test_complete_system():
    """Test the complete session-based scraper with automatic proxy authentication."""
    print("🧪 Testing complete session-based scraper with proxy authentication...")
    
    # Test with Indeed search
    url = "https://www.indeed.com/jobs?q=python+developer&l=Minnesota"
    pages = 12  # Test with 12 pages to trigger multiple sessions
    
    print(f"🎯 Target: {pages} pages from {url}")
    
    # Create scraper - it will automatically load and authenticate proxies
    scraper = IndeedScraperV3(url, pages)
    
    # Run scraper
    jobs = scraper.scrape_all_pages()
    
    print(f"\n✅ Scraping completed!")
    print(f"📊 Total jobs scraped: {len(jobs)}")
    
    if jobs:
        print(f"📝 Sample jobs:")
        for i, job in enumerate(jobs[:3]):
            print(f"   {i+1}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
            print(f"      Location: {job.get('location', 'N/A')}")
            print(f"      Salary: {job.get('salary', 'N/A')}")
            print()

if __name__ == "__main__":
    test_complete_system()