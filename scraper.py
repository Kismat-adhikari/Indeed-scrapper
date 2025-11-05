"""
Indeed Scraper Module
=====================
Handles the core scraping logic using Playwright for dynamic content.
Extracts job listings from Indeed search results pages.
"""

import asyncio
import json
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup


class IndeedScraper:
    """
    Asynchronous scraper for Indeed job listings.
    """
    
    def __init__(self, base_url: str, page_count: int, proxies: List[Dict]):
        """
        Initialize the scraper.
        
        Args:
            base_url: Indeed search URL
            page_count: Number of pages to scrape
            proxies: List of proxy configurations
        """
        self.base_url = base_url
        self.page_count = page_count
        self.proxies = proxies
        self.current_proxy_index = 0
        self.all_jobs = []
    
    def _get_next_proxy(self) -> Optional[Dict]:
        """
        Get the next proxy from the rotation.
        
        Returns:
            Proxy configuration dict or None if no proxies available
        """
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy
    
    def _build_page_url(self, page_number: int) -> str:
        """
        Build URL for a specific page number.
        Indeed uses 'start' parameter: page 1=0, page 2=10, page 3=20, etc.
        
        Args:
            page_number: Page number (1-indexed)
            
        Returns:
            URL string for that page
        """
        parsed = urlparse(self.base_url)
        params = parse_qs(parsed.query)
        
        # Calculate start parameter (0-indexed, increments by 10)
        start_value = (page_number - 1) * 10
        params['start'] = [str(start_value)]
        
        # Rebuild URL
        new_query = urlencode(params, doseq=True)
        new_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        return new_url
    
    async def _create_browser(self, proxy: Optional[Dict] = None) -> Browser:
        """
        Create a Playwright browser instance with optional proxy.
        
        Args:
            proxy: Proxy configuration
            
        Returns:
            Browser instance
        """
        playwright = await async_playwright().start()
        
        browser_args = {
            'headless': True,  # Run in background
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        }
        
        if proxy:
            browser_args['proxy'] = proxy
        
        browser = await playwright.chromium.launch(**browser_args)
        return browser
    
    async def _scrape_page(self, page_number: int) -> List[Dict]:
        """
        Scrape a single page of Indeed results.
        
        Args:
            page_number: Page number to scrape (1-indexed)
            
        Returns:
            List of job dictionaries
        """
        url = self._build_page_url(page_number)
        proxy = self._get_next_proxy()
        jobs = []
        max_retries = 2
        
        print(f"  📄 Scraping page {page_number}... ", end='', flush=True)
        
        for attempt in range(max_retries):
            playwright = None
            browser = None
            
            try:
                # Create browser with proxy
                playwright = await async_playwright().start()
                
                browser_args = {
                    'headless': True,
                    'args': [
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                }
                
                if proxy and attempt == 0:
                    browser_args['proxy'] = proxy
                
                browser = await playwright.chromium.launch(**browser_args)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()
                
                # Navigate to page with simpler wait strategy
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                
                # Wait a bit for dynamic content
                await asyncio.sleep(4)
                
                # Try to wait for job cards with multiple selectors (don't fail if not found)
                selector_found = False
                for selector in ['.job_seen_beacon', '[data-jk]', '.jobsearch-ResultsList', '#mosaic-provider-jobcards', 'td.resultContent']:
                    try:
                        await page.wait_for_selector(selector, timeout=5000)
                        selector_found = True
                        break
                    except PlaywrightTimeout:
                        continue
                
                if not selector_found:
                    print(f"⚠️  Warning: No expected selectors found, trying to scrape anyway...")
                
                # Scroll to load lazy content
                try:
                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    await asyncio.sleep(2)
                    await page.evaluate('window.scrollTo(0, 0)')
                    await asyncio.sleep(1)
                except:
                    pass
                
                # Get page content
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Debug: Save HTML to file for inspection
                debug_file = f"output/debug_page_{page_number}.html"
                try:
                    import os
                    os.makedirs('output', exist_ok=True)
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"(Debug: saved to {debug_file})")
                except:
                    pass
                
                # Try multiple approaches to find job cards
                job_cards = []
                
                # Method 1: job_seen_beacon
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                # Method 2: data-jk attribute
                if not job_cards:
                    job_cards = soup.find_all('div', attrs={'data-jk': True})
                
                # Method 3: resultContent (table-based layout)
                if not job_cards:
                    job_cards = soup.find_all('td', class_='resultContent')
                
                # Method 4: Look for any div with jobsearch in class name
                if not job_cards:
                    job_cards = soup.find_all('div', class_=lambda x: x and 'jobsearch' in str(x).lower())
                
                # Method 5: Look for slider_container
                if not job_cards:
                    job_cards = soup.find_all('div', class_='slider_container')
                
                # Method 6: Find by structure - look for job titles
                if not job_cards:
                    job_titles = soup.find_all('h2', class_='jobTitle')
                    if job_titles:
                        # Get parent containers
                        job_cards = [title.find_parent('div', class_=lambda x: x and 'job' in str(x).lower()) or title.find_parent('td') or title.find_parent('li') for title in job_titles]
                        job_cards = [card for card in job_cards if card]
                
                print(f"Found {len(job_cards)} jobs")
                
                # Extract data from each job card
                for card in job_cards:
                    try:
                        job = self._extract_job_data(card, page_number)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        print(f"    ⚠️  Error extracting job: {str(e)}")
                        continue
                
                # Clean up
                await context.close()
                await browser.close()
                await playwright.stop()
                
                # Success - break retry loop
                break
                
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
                
                # Clean up on error
                try:
                    if browser:
                        await browser.close()
                    if playwright:
                        await playwright.stop()
                except:
                    pass
                
                # If not last attempt, retry
                if attempt < max_retries - 1:
                    print(f"    🔄 Retrying (attempt {attempt + 2}/{max_retries})...")
                    await asyncio.sleep(2)
                else:
                    print(f"    ❌ All attempts failed for page {page_number}")
        
        return jobs
    

    
    def _extract_job_data(self, card, page_number: int) -> Optional[Dict]:
        """
        Extract job information from a job card element.
        
        Args:
            card: BeautifulSoup job card element
            page_number: Current page number
            
        Returns:
            Dictionary with job data or None
        """
        try:
            # Job title
            title_elem = card.find('h2', class_='jobTitle')
            if not title_elem:
                title_elem = card.find('a', class_='jcs-JobTitle')
            if not title_elem:
                title_elem = card.find('h2', attrs={'class': lambda x: x and 'jobTitle' in x})
            
            # Extract title text, removing any "new" badges
            title = 'N/A'
            if title_elem:
                # Get all text but filter out "new" labels
                title_text = title_elem.get_text(separator=' ', strip=True)
                title = title_text.replace('new', '').strip()
            
            # Company name
            company_elem = card.find('span', attrs={'data-testid': 'company-name'})
            if not company_elem:
                company_elem = card.find('span', class_='companyName')
            if not company_elem:
                company_elem = card.find('span', attrs={'class': lambda x: x and 'company' in str(x).lower()})
            company = company_elem.get_text(strip=True) if company_elem else 'N/A'
            
            # Location
            location_elem = card.find('div', attrs={'data-testid': 'text-location'})
            if not location_elem:
                location_elem = card.find('div', class_='companyLocation')
            if not location_elem:
                location_elem = card.find('div', attrs={'class': lambda x: x and 'location' in str(x).lower()})
            location = location_elem.get_text(strip=True) if location_elem else 'N/A'
            
            # Salary - improved extraction with multiple selectors
            salary = 'Not specified'
            
            # Try multiple salary selectors
            salary_selectors = [
                ('div', {'class': 'salary-snippet'}),
                ('span', {'class': 'salary-snippet'}),
                ('div', {'class': 'metadata'}),
                ('div', {'class': 'salary-snippet-container'}),
                ('span', {'data-testid': 'attribute_snippet_testid'}),
                ('div', {'class': lambda x: x and 'salary' in str(x).lower()}),
            ]
            
            for tag, attrs in salary_selectors:
                salary_elem = card.find(tag, attrs)
                if salary_elem:
                    salary_text = salary_elem.get_text(strip=True)
                    # Check if this actually contains salary info (has $ or numbers)
                    if '$' in salary_text or any(char.isdigit() for char in salary_text):
                        if 'hour' in salary_text.lower() or 'year' in salary_text.lower() or 'month' in salary_text.lower():
                            salary = salary_text
                            break
            
            # Also check in metadata divs for salary info
            if salary == 'Not specified':
                metadata_divs = card.find_all('div', class_='metadata')
                for meta in metadata_divs:
                    meta_text = meta.get_text(strip=True)
                    if '$' in meta_text:
                        salary = meta_text
                        break
            
            # Job type (full-time, part-time, etc.) - extract separately from salary
            job_type = 'Not specified'
            metadata_elem = card.find('div', class_='metadata')
            
            if metadata_elem:
                metadata_text = metadata_elem.get_text(strip=True)
                # Look for job type keywords
                job_type_keywords = ['full-time', 'part-time', 'contract', 'temporary', 'internship', 'remote']
                for keyword in job_type_keywords:
                    if keyword.lower() in metadata_text.lower():
                        job_type = metadata_text
                        break
            
            # If job_type contains salary info, try to separate them
            if '$' in job_type and salary == 'Not specified':
                salary = job_type
                job_type = 'Not specified'
            
            # Posted date
            date_elem = card.find('span', class_='date')
            if not date_elem:
                date_elem = card.find('span', attrs={'data-testid': 'myJobsStateDate'})
            if not date_elem:
                date_elem = card.find('span', attrs={'class': lambda x: x and 'date' in str(x).lower()})
            posted_date = date_elem.get_text(strip=True) if date_elem else 'Not specified'
            
            # Job summary/snippet
            summary_elem = card.find('div', class_='job-snippet')
            if not summary_elem:
                summary_elem = card.find('div', attrs={'data-testid': 'job-snippet'})
            if not summary_elem:
                summary_elem = card.find('div', class_='jobCardShelfContainer')
            if not summary_elem:
                summary_elem = card.find('ul')
            summary = summary_elem.get_text(strip=True) if summary_elem else 'No description available'
            
            # Job URL - improved extraction
            job_url = 'N/A'
            
            # Try multiple link selectors
            link_elem = card.find('a', class_='jcs-JobTitle')
            if not link_elem:
                link_elem = card.find('a', attrs={'data-jk': True})
            if not link_elem:
                link_elem = card.find('h2', class_='jobTitle')
                if link_elem:
                    link_elem = link_elem.find('a')
            if not link_elem:
                link_elem = card.find('a', href=True)
            
            if link_elem:
                href = link_elem.get('href', '')
                if href:
                    # Handle different URL formats
                    if href.startswith('http'):
                        job_url = href
                    elif href.startswith('/'):
                        job_url = 'https://www.indeed.com' + href
                    else:
                        job_url = 'https://www.indeed.com/' + href
                    
                    # Extract job ID and build clean URL
                    if 'jk=' in job_url or '/viewjob?' in job_url:
                        # URL is already in correct format
                        pass
                    elif 'data-jk' in str(link_elem):
                        job_id = link_elem.get('data-jk')
                        if job_id:
                            job_url = f'https://www.indeed.com/viewjob?jk={job_id}'
            
            # If still no URL, try to extract from data-jk attribute
            if job_url == 'N/A':
                job_id = card.get('data-jk')
                if not job_id:
                    jk_elem = card.find(attrs={'data-jk': True})
                    if jk_elem:
                        job_id = jk_elem.get('data-jk')
                
                if job_id:
                    job_url = f'https://www.indeed.com/viewjob?jk={job_id}'
            
            # Build job dictionary
            job = {
                'title': title,
                'company': company,
                'location': location,
                'salary': salary,
                'job_type': job_type,
                'posted_date': posted_date,
                'summary': summary,
                'url': job_url,
                'scraped_from_page': page_number
            }
            
            return job
            
        except Exception as e:
            print(f"    ⚠️  Failed to extract job data: {str(e)}")
            return None
    
    async def scrape_all_pages(self) -> List[Dict]:
        """
        Scrape all specified pages.
        
        Returns:
            List of all job dictionaries
        """
        all_jobs = []
        
        for page_num in range(1, self.page_count + 1):
            jobs = await self._scrape_page(page_num)
            all_jobs.extend(jobs)
            print(f"  ✓ Page {page_num} complete: {len(jobs)} jobs scraped")
            
            # Be polite - small delay between pages
            if page_num < self.page_count:
                await asyncio.sleep(3)
        
        print(f"\n  📊 Total jobs scraped: {len(all_jobs)}")
        return all_jobs


# FUTURE EXPANSION (commented):
# - Add AI-based selector repair:
#   When Indeed changes HTML structure, use LLM to identify new selectors
#   from page source and auto-update extraction logic
#
# - Concurrent page scraping:
#   Use asyncio.gather() to scrape multiple pages simultaneously
#   (Be careful with rate limiting)
#
# - Screenshot capture:
#   Save screenshots of each page for debugging selector issues
#
# - Job detail page scraping:
#   Click into each job to get full description, benefits, etc.
