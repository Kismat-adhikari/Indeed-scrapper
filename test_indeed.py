"""
Test script to diagnose Indeed scraping issues
"""

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random

# Test basic connectivity
print("="*60)
print("TESTING INDEED SCRAPER")
print("="*60 + "\n")

# Test 1: Can we reach Indeed?
print("Test 1: Checking if we can reach Indeed.com...")
try:
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    response = requests.get('https://www.indeed.com', headers=headers, timeout=10)
    print(f"✓ Status code: {response.status_code}")
    if response.status_code == 200:
        print("✓ Can reach Indeed.com\n")
    else:
        print(f"⚠ Got status code {response.status_code}\n")
except Exception as e:
    print(f"✗ Error: {e}\n")

# Test 2: Can we search for jobs?
print("Test 2: Trying a simple search...")
try:
    search_url = "https://www.indeed.com/jobs?q=software+engineer&l=New+York"
    print(f"URL: {search_url}")
    
    response = requests.get(search_url, headers=headers, timeout=15)
    print(f"✓ Status code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Try different selectors to find job cards
        print("\nTrying different job card selectors...")
        
        selectors = [
            ('div.job_seen_beacon', 'job_seen_beacon'),
            ('div[data-testid="slider_item"]', 'slider_item'),
            ('a.jcs-JobTitle', 'jcs-JobTitle'),
            ('div.jobsearch-SerpJobCard', 'jobsearch-SerpJobCard'),
            ('div[class*="job"]', 'any div with "job" class'),
            ('a[data-jk]', 'links with data-jk'),
        ]
        
        for selector, name in selectors:
            elements = soup.select(selector)
            print(f"  {name}: Found {len(elements)} elements")
        
        # Check page title
        title = soup.find('title')
        if title:
            print(f"\nPage title: {title.get_text()}")
        
        # Print first 500 chars of HTML to inspect
        print("\nFirst 500 characters of response:")
        print(response.text[:500])
        print("\n" + "="*60)
        
        # Look for any text mentioning jobs
        if 'job' in response.text.lower():
            print("✓ Page contains job-related content")
        else:
            print("⚠ Page doesn't seem to contain jobs")
            
        # Check if we're being blocked
        if 'captcha' in response.text.lower() or 'robot' in response.text.lower():
            print("⚠ WARNING: Site may be detecting us as a bot!")
        
    else:
        print(f"⚠ Bad response: {response.status_code}")
        print(f"Response text: {response.text[:500]}")
        
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Try with a proxy
print("\n" + "="*60)
print("Test 3: Testing with proxy...")
try:
    with open('proxies.txt', 'r') as f:
        proxy_line = f.readline().strip()
    
    if proxy_line:
        parts = proxy_line.split(':')
        if len(parts) == 4:
            ip, port, username, password = parts
            proxy_url = f"http://{username}:{password}@{ip}:{port}"
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            print(f"Testing proxy: {ip}:{port}")
            
            response = requests.get(search_url, headers=headers, proxies=proxies, timeout=20)
            print(f"✓ Status code with proxy: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ Proxy works!")
            else:
                print(f"⚠ Proxy returned: {response.status_code}")
        else:
            print("✗ Invalid proxy format")
    else:
        print("✗ No proxies found")
        
except Exception as e:
    print(f"✗ Proxy error: {e}")

print("\n" + "="*60)
print("DIAGNOSIS COMPLETE")
print("="*60)
