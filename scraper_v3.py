"""
Indeed Scraper v3.0 - Anti-Bot Protection Bypass
================================================
Uses undetected-chromedriver to bypass Cloudflare protection.
"""

import asyncio
import time
import random
import os
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class IndeedScraperV3:
    """
    Scraper using undetected-chromedriver to bypass bot detection.
    """
    
    def __init__(self, base_url: str, page_count: int, proxies: List[Dict]):
        self.base_url = base_url
        self.page_count = page_count
        self.proxies = proxies
        self.current_proxy_index = 0
        self.driver = None
    
    def _get_next_proxy(self) -> Optional[Dict]:
        """Get next proxy from rotation."""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy
    
    def _build_page_url(self, page_number: int) -> str:
        """Build URL for specific page."""
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        parsed = urlparse(self.base_url)
        params = parse_qs(parsed.query)
        
        start_value = (page_number - 1) * 10
        params['start'] = [str(start_value)]
        
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
    
    def _init_driver(self, use_proxy: bool = True) -> uc.Chrome:
        """Initialize undetected Chrome driver."""
        options = uc.ChromeOptions()
        
        # Stealth options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Add proxy if available
        if use_proxy and self.proxies:
            proxy = self._get_next_proxy()
            if proxy:
                proxy_str = proxy['server'].replace('http://', '')
                options.add_argument(f'--proxy-server={proxy_str}')
        
        # Create driver with undetected-chromedriver
        driver = uc.Chrome(options=options, version_main=None)
        driver.set_window_size(1920, 1080)
        
        return driver
    
    def _check_for_captcha(self) -> bool:
        """Check if Cloudflare CAPTCHA is present."""
        try:
            page_source = self.driver.page_source
            # First check if we have job data - if yes, no CAPTCHA
            if 'window.mosaic.providerData' in page_source:
                return False
            # Only flag as CAPTCHA if it's actually blocking
            page_lower = page_source.lower()
            if 'just a moment' in page_lower and 'cloudflare' in page_lower:
                return True
            if 'challenge-platform' in page_lower:
                return True
            return False
        except:
            return False
    
    def _wait_for_captcha_solve(self, timeout: int = 60):
        """Wait for user to solve CAPTCHA manually."""
        print(f"\n⚠️  CAPTCHA detected! Please solve it in the browser...")
        print(f"    Waiting up to {timeout} seconds...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self._check_for_captcha():
                print("    ✓ CAPTCHA solved!")
                time.sleep(2)
                return True
            time.sleep(2)
        
        print("    ❌ Timeout waiting for CAPTCHA solve")
        return False
    
    def _simulate_human_behavior(self):
        """Simulate human-like behavior."""
        # Random scroll
        scroll_amount = random.randint(300, 800)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 1.5))
        
        # Scroll back a bit
        self.driver.execute_script(f"window.scrollBy(0, -{scroll_amount // 2});")
        time.sleep(random.uniform(0.3, 0.8))
        
        # Move mouse (using JavaScript)
        self.driver.execute_script("""
            var event = new MouseEvent('mousemove', {
                'view': window,
                'bubbles': true,
                'cancelable': true,
                'clientX': Math.random() * window.innerWidth,
                'clientY': Math.random() * window.innerHeight
            });
            document.dispatchEvent(event);
        """)
    
    def _scrape_page(self, page_number: int) -> List[Dict]:
        """Scrape a single page."""
        url = self._build_page_url(page_number)
        jobs = []
        
        print(f"  📄 Scraping page {page_number}... ", end='', flush=True)
        
        try:
            # Navigate to page
            self.driver.get(url)
            time.sleep(random.uniform(4, 6))
            
            # Save HTML for debugging
            debug_file = f"output/debug_v3_page_{page_number}.html"
            try:
                os.makedirs('output', exist_ok=True)
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                print(f"(saved HTML to {debug_file}) ", end='', flush=True)
            except:
                pass
            
            # Check for CAPTCHA
            if self._check_for_captcha():
                print("\n⚠️  CAPTCHA detected!")
                if not self._wait_for_captcha_solve():
                    print("❌ Failed - CAPTCHA not solved")
                    return []
            
            # Check page title
            page_title = self.driver.title
            print(f"(title: {page_title[:30]}...) ", end='', flush=True)
            
            # Simulate human behavior
            self._simulate_human_behavior()
            
            # Wait for job cards with multiple strategies
            selectors_to_try = [
                (By.CLASS_NAME, "job_seen_beacon"),
                (By.CSS_SELECTOR, "[data-jk]"),
                (By.CSS_SELECTOR, "td.resultContent"),
                (By.CSS_SELECTOR, "h2.jobTitle"),
                (By.ID, "mosaic-provider-jobcards"),
            ]
            
            element_found = False
            for selector_type, selector_value in selectors_to_try:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    element_found = True
                    print(f"(found: {selector_value}) ", end='', flush=True)
                    break
                except TimeoutException:
                    continue
            
            if not element_found:
                print("(no job elements found) ", end='', flush=True)
            
            # Get page HTML
            html = self.driver.page_source
            
            # Extract jobs from JSON data embedded in the page
            extracted_jobs = self._extract_jobs_from_json(html)
            
            if extracted_jobs:
                print(f"Found {len(extracted_jobs)} jobs from JSON")
                for job in extracted_jobs:
                    job['scraped_from_page'] = page_number
                    jobs.append(job)
            else:
                print("⚠️ No jobs found in JSON data")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        return jobs
    
    def _extract_jobs_from_json(self, html_content: str) -> List[Dict]:
        """Extract job data from the JSON embedded in the page with proper field normalization"""
        try:
            import json
            import re
            from html import unescape
            
            # Find the JSON data in the script tag
            pattern = r'window\.mosaic\.providerData\["mosaic-provider-jobcards"\]\s*=\s*({.*?});'
            match = re.search(pattern, html_content, re.DOTALL)
            
            if not match:
                return []
            
            json_str = match.group(1)
            data = json.loads(json_str)
            
            # Navigate to the jobs array
            jobs_data = []
            if 'metaData' in data and 'mosaicProviderJobCardsModel' in data['metaData']:
                model = data['metaData']['mosaicProviderJobCardsModel']
                if 'results' in model:
                    jobs_data = model['results']
            
            # Extract data from each job
            extracted_jobs = []
            for job in jobs_data:
                try:
                    job_id = job.get('jobkey', '')
                    title = job.get('title', 'Not specified')
                    company = job.get('company', 'Not specified')
                    
                    # Extract location
                    location = 'Not specified'
                    if 'formattedLocation' in job:
                        location = job['formattedLocation']
                    elif 'location' in job:
                        location = job['location']
                    
                    # ===== EXTRACT SALARY WITH PERIOD DETECTION =====
                    # Handles: $55 - $75 an hour, $95k–$125k, $95,000/year, $140,000 - $150,000 a year
                    salary = None
                    salary_period = None
                    
                    if 'extractedSalary' in job:
                        sal_data = job['extractedSalary']
                        # Get salary type (hourly, yearly, etc.)
                        if 'type' in sal_data:
                            sal_type = sal_data['type'].lower()
                            if 'hour' in sal_type:
                                salary_period = 'hour'
                            elif 'year' in sal_type or 'annual' in sal_type:
                                salary_period = 'year'
                            elif 'month' in sal_type:
                                salary_period = 'month'
                            elif 'week' in sal_type:
                                salary_period = 'week'
                        
                        # Build salary string
                        if 'max' in sal_data and sal_data.get('max'):
                            salary = f"${sal_data.get('min', 0):,.0f} - ${sal_data['max']:,.0f}"
                        elif 'min' in sal_data and sal_data.get('min'):
                            salary = f"${sal_data['min']:,.0f}"
                    
                    # Fallback to salarySnippet text
                    if not salary and 'salarySnippet' in job:
                        snippet = job['salarySnippet']
                        if 'text' in snippet:
                            salary_text = snippet['text']
                            salary = salary_text
                            
                            # Detect period from salary text
                            salary_lower = salary_text.lower()
                            if 'hour' in salary_lower or '/hr' in salary_lower:
                                salary_period = 'hour'
                            elif 'year' in salary_lower or '/yr' in salary_lower or 'annual' in salary_lower:
                                salary_period = 'year'
                            elif 'month' in salary_lower or '/mo' in salary_lower:
                                salary_period = 'month'
                            elif 'week' in salary_lower or '/wk' in salary_lower:
                                salary_period = 'week'
                    
                    # ===== EXTRACT JOB TYPE (NOT POSTED DATE!) =====
                    # Job types: Full-time, Part-time, Contract, Internship, Temporary
                    job_type = None
                    
                    if 'jobTypes' in job and job['jobTypes']:
                        # This is the CORRECT field for job types
                        job_type = ', '.join(job['jobTypes'])
                    
                    # ===== EXTRACT POSTED DATE =====
                    # This is separate from job type! (e.g., "30+ days ago", "2 days ago")
                    posted_date = None
                    if 'formattedRelativeTime' in job:
                        posted_date = job['formattedRelativeTime']
                    
                    # ===== EXTRACT AND CLEAN SUMMARY =====
                    # Remove HTML tags and get clean text
                    summary = job.get('snippet', 'No description')
                    
                    if summary and summary != 'No description':
                        # Remove HTML tags
                        summary = re.sub(r'<[^>]+>', '', summary)
                        # Decode HTML entities (e.g., &amp; -> &)
                        summary = unescape(summary)
                        # Clean up whitespace
                        summary = re.sub(r'\s+', ' ', summary).strip()
                        # Remove bullet point markers
                        summary = summary.replace('•', '').replace('◦', '')
                        summary = summary.strip()
                    
                    # Build URL
                    job_url = f"https://www.indeed.com/viewjob?jk={job_id}" if job_id else None
                    
                    extracted_jobs.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'salary': salary,
                        'salary_period': salary_period,
                        'job_type': job_type,
                        'posted_date': posted_date,
                        'summary': summary,
                        'url': job_url
                    })
                    
                except Exception as e:
                    continue
            
            return extracted_jobs
            
        except Exception as e:
            return []
    
    def _extract_job_data(self, card, page_number: int) -> Optional[Dict]:
        """Extract job information from card."""
        try:
            # Title
            title_elem = card.find('h2', class_='jobTitle') or card.find('a', class_='jcs-JobTitle')
            title = title_elem.get_text(separator=' ', strip=True).replace('new', '').strip() if title_elem else 'N/A'
            
            # Company
            company_elem = (card.find('span', attrs={'data-testid': 'company-name'}) or 
                          card.find('span', class_='companyName'))
            company = company_elem.get_text(strip=True) if company_elem else 'N/A'
            
            # Location
            location_elem = (card.find('div', attrs={'data-testid': 'text-location'}) or 
                           card.find('div', class_='companyLocation'))
            location = location_elem.get_text(strip=True) if location_elem else 'N/A'
            
            # Salary
            salary = 'Not specified'
            salary_selectors = [
                card.find('div', class_='salary-snippet'),
                card.find('span', class_='salary-snippet'),
                card.find('div', class_='metadata'),
            ]
            
            for elem in salary_selectors:
                if elem:
                    text = elem.get_text(strip=True)
                    if '$' in text:
                        salary = text
                        break
            
            # Job type
            job_type = 'Not specified'
            metadata = card.find('div', class_='metadata')
            if metadata:
                job_type = metadata.get_text(strip=True)
            
            # Posted date
            date_elem = card.find('span', class_='date')
            posted_date = date_elem.get_text(strip=True) if date_elem else 'Not specified'
            
            # Summary
            summary_elem = card.find('div', class_='job-snippet')
            summary = summary_elem.get_text(strip=True) if summary_elem else 'No description'
            
            # URL
            link_elem = card.find('a', class_='jcs-JobTitle') or card.find('a', attrs={'data-jk': True})
            job_url = 'N/A'
            
            if link_elem:
                href = link_elem.get('href', '')
                if href:
                    job_url = f'https://www.indeed.com{href}' if href.startswith('/') else href
            
            if job_url == 'N/A':
                job_id = card.get('data-jk')
                if job_id:
                    job_url = f'https://www.indeed.com/viewjob?jk={job_id}'
            
            return {
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
            
        except Exception as e:
            return None
    
    def scrape_all_pages(self) -> List[Dict]:
        """Scrape all pages."""
        all_jobs = []
        
        try:
            # Initialize driver
            print("🚀 Starting Chrome browser...")
            self.driver = self._init_driver(use_proxy=False)  # Start without proxy first
            
            for page_num in range(1, self.page_count + 1):
                jobs = self._scrape_page(page_num)
                all_jobs.extend(jobs)
                print(f"  ✓ Page {page_num} complete: {len(jobs)} jobs scraped")
                
                if page_num < self.page_count:
                    time.sleep(random.uniform(3, 6))
            
        except Exception as e:
            print(f"\n❌ Error during scraping: {str(e)}")
        finally:
            if self.driver:
                print("\n🔒 Closing browser...")
                try:
                    self.driver.quit()
                except:
                    pass  # Ignore cleanup errors
        
        print(f"\n  📊 Total jobs scraped: {len(all_jobs)}")
        return all_jobs
