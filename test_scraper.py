"""
Quick Test Script - Indeed Scraper v2.0
=========================================
Use this to quickly test the improved scraper functionality.
"""

import asyncio
import json
from pathlib import Path
from scraper import IndeedScraper
from proxy_manager import ProxyManager


async def quick_test():
    """
    Quick test of the scraper with a single page.
    """
    print("🧪 Running Quick Test...\n")
    
    # Test URL - Software Engineer jobs (usually has salaries listed)
    test_url = "https://www.indeed.com/jobs?q=software+engineer&l=San+Francisco"
    
    # Load proxies
    proxy_manager = ProxyManager("proxies.txt")
    proxies = proxy_manager.load_proxies()
    
    print(f"✓ Loaded {len(proxies)} proxies\n")
    
    # Create scraper for just 1 page
    scraper = IndeedScraper(test_url, 1, proxies)
    
    print("📄 Scraping 1 test page...\n")
    jobs = await scraper.scrape_all_pages()
    
    print(f"\n✅ Test complete!")
    print(f"📊 Jobs scraped: {len(jobs)}\n")
    
    if jobs:
        print("📋 Sample job data:\n")
        sample = jobs[0]
        
        print(f"Title:       {sample['title']}")
        print(f"Company:     {sample['company']}")
        print(f"Location:    {sample['location']}")
        print(f"Salary:      {sample['salary']}")
        print(f"Job Type:    {sample['job_type']}")
        print(f"Posted:      {sample['posted_date']}")
        print(f"URL:         {sample['url']}")
        print(f"\nSummary:     {sample['summary'][:100]}...")
        
        # Check data quality
        print("\n🔍 Data Quality Check:")
        
        salaries_found = sum(1 for job in jobs if job['salary'] != 'Not specified')
        valid_urls = sum(1 for job in jobs if job['url'].startswith('https://'))
        
        print(f"  Salaries extracted: {salaries_found}/{len(jobs)} ({salaries_found/len(jobs)*100:.0f}%)")
        print(f"  Valid URLs:         {valid_urls}/{len(jobs)} ({valid_urls/len(jobs)*100:.0f}%)")
        
        # Save test results
        test_output = Path("output") / "test_results.json"
        test_output.parent.mkdir(exist_ok=True)
        
        with open(test_output, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Test results saved to: {test_output}")
    else:
        print("❌ No jobs scraped - check your connection or proxies")


if __name__ == "__main__":
    asyncio.run(quick_test())
