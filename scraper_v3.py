"""
Indeed Scraper v3.0 - Anti-Bot Protection Bypass
================================================
Uses undetected-chromedriver to bypass Cloudflare protection with session-based proxy rotation.
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

from chrome_driver_manager import get_driver
from session_manager import SessionManager, ProxySession
from human_behavior import HumanBehaviorSimulator


class IndeedScraperV3:
    """
    Scraper using undetected-chromedriver with session-based proxy rotation.
    """
    
    def __init__(self, base_url: str, page_count: int, proxy_file: str = "proxies.txt"):
        self.base_url = base_url
        self.page_count = page_count
        self.session_manager = SessionManager(proxy_file)
        self.current_session: Optional[ProxySession] = None
        self.driver = None
        self.human_behavior: Optional[HumanBehaviorSimulator] = None
        
        # Load existing proxy statistics
        if self.session_manager:
            self.session_manager.load_proxy_stats("proxy_stats.json")
    
    def _get_next_proxy(self) -> Optional[Dict]:
        """Get proxy from current session."""
        if self.current_session:
            return self.current_session.proxy
        return None
    
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
    
    def _init_driver(self, session: Optional[ProxySession] = None) -> uc.Chrome:
        """Initialize Chrome driver with session-based proxy authentication."""
        if session and session.proxy:
            # Use ProxyAuthManager for automatic authentication
            proxy_auth_manager = self.session_manager.proxy_auth_manager if self.session_manager else None
            driver = get_driver(
                use_proxy=True, 
                proxy_config=session.proxy,
                proxy_auth_manager=proxy_auth_manager
            )
        else:
            # No proxy or session
            driver = get_driver(use_proxy=False)
        
        # Set session-specific user agent if available
        if session and session.user_agent:
            try:
                driver.execute_script(f"Object.defineProperty(navigator, 'userAgent', {{get: function() {{ return '{session.user_agent}'; }}}});")
            except:
                pass  # Ignore if script fails
        
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
            captcha_indicators = [
                'just a moment' in page_lower and 'cloudflare' in page_lower,
                'challenge-platform' in page_lower,
                'captcha' in page_lower,
                'please verify you are a human' in page_lower,
                'access denied' in page_lower,
                'blocked' in page_lower and 'request' in page_lower
            ]
            return any(captcha_indicators)
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
        """Simulate human-like behavior using dedicated simulator."""
        if self.human_behavior:
            self.human_behavior.simulate_page_arrival()
        else:
            # Fallback to basic behavior
            scroll_amount = random.randint(300, 800)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.5, 1.5))
            
            self.driver.execute_script(f"window.scrollBy(0, -{scroll_amount // 2});")
            time.sleep(random.uniform(0.3, 0.8))
    
    def _scrape_page(self, page_number: int) -> List[Dict]:
        """Scrape a single page with session-based approach."""
        url = self._build_page_url(page_number)
        jobs = []
        
        print(f"  📄 Scraping page {page_number}... ", end='', flush=True)
        
        try:
            # Navigate to page
            self.driver.get(url)
            
            # Initial wait for page load
            time.sleep(random.uniform(3, 5))
            
            # Check for CAPTCHA immediately
            if self._check_for_captcha():
                print("🛡️ CAPTCHA detected!")
                if self.session_manager:
                    self.session_manager.record_failure(is_captcha=True)
                
                if not self._wait_for_captcha_solve():
                    print("❌ Failed - CAPTCHA not solved")
                    return []
            
            # Check page title
            page_title = self.driver.title
            print(f"(title: {page_title[:30]}...) ", end='', flush=True)
            
            # Enhanced human behavior simulation
            if self.human_behavior:
                self.human_behavior.simulate_page_arrival()
            else:
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
                    WebDriverWait(self.driver, 8).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    element_found = True
                    print(f"(found: {selector_value}) ", end='', flush=True)
                    break
                except TimeoutException:
                    continue
            
            if not element_found:
                print("(no job elements found) ", end='', flush=True)
                if self.session_manager:
                    self.session_manager.record_failure()
                return []
            
            # Get page HTML
            html = self.driver.page_source
            
            # Extract jobs from JSON data embedded in the page
            extracted_jobs = self._extract_jobs_from_json(html)
            
            if extracted_jobs:
                print(f"Found {len(extracted_jobs)} jobs from JSON")
                
                # Simulate human browsing behavior for the found jobs
                if self.human_behavior:
                    browse_time = self.human_behavior.simulate_job_browsing(len(extracted_jobs))
                    print(f"   ⏱️ Browsed jobs for {browse_time:.1f} seconds")
                
                for job in extracted_jobs:
                    job['scraped_from_page'] = page_number
                    jobs.append(job)
                
                # Record success with session manager
                if self.session_manager:
                    self.session_manager.record_success()
            else:
                print("⚠️ No jobs found in JSON data")
                if self.session_manager:
                    self.session_manager.record_failure()
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            if self.session_manager:
                self.session_manager.record_failure()
        
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
                    title = job.get('title', 'Not mentioned')
                    company = job.get('company', 'Not mentioned')
                    
                    # Extract location
                    location = 'Not mentioned'
                    if 'formattedLocation' in job:
                        location = job['formattedLocation']
                    elif 'location' in job:
                        location = job['location']
                    
                    # ===== EXTRACT SALARY WITH PERIOD DETECTION =====
                    # Handles: $55 - $75 an hour, $95k–$125k, $95,000/year, $140,000 - $150,000 a year
                    salary = 'Not mentioned'
                    salary_period = 'Not mentioned'
                    
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
                    # Check BOTH jobTypes field AND taxonomyAttributes
                    job_type = 'Not mentioned'
                    
                    # Method 1: Check jobTypes field (most reliable)
                    if 'jobTypes' in job and job['jobTypes']:
                        job_type = ', '.join(job['jobTypes'])
                    
                    # Method 2: Check taxonomyAttributes if jobTypes is empty
                    elif 'taxonomyAttributes' in job:
                        for attr in job['taxonomyAttributes']:
                            if attr.get('label') == 'job-types' and attr.get('attributes'):
                                # Extract job type labels from attributes
                                types = [a['label'] for a in attr['attributes'] if 'label' in a]
                                if types:
                                    job_type = ', '.join(types)
                                    break
                    
                    # ===== EXTRACT POSTED DATE =====
                    # This is separate from job type! (e.g., "30+ days ago", "2 days ago")
                    posted_date = 'Not mentioned'
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
                    job_url = f"https://www.indeed.com/viewjob?jk={job_id}" if job_id else 'Not mentioned'
                    
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
        """Scrape all pages using session-based proxy rotation."""
        all_jobs = []
        pages_scraped = 0
        
        try:
            print("🚀 Starting session-based scraping...")
            
            # Display proxy pool status
            if self.session_manager:
                pool_status = self.session_manager.get_proxy_pool_status()
                print(f"� Proxy pool: {pool_status['healthy_proxies']}/{pool_status['total_proxies']} healthy proxies")
            
            while pages_scraped < self.page_count:
                # Check if we need a new session
                if not self.current_session or self.session_manager.should_rotate_session():
                    self._start_new_session()
                    
                    if not self.current_session:
                        print("❌ No healthy proxies available. Stopping.")
                        break
                
                # Calculate pages remaining in this session
                pages_remaining_in_session = min(
                    self.current_session.max_pages - self.current_session.pages_scraped,
                    self.page_count - pages_scraped
                )
                
                print(f"\n🔄 Session: {self.current_session.session_id}")
                print(f"   Proxy: {self.current_session.proxy.get('server', 'unknown')}")
                print(f"   Pages in session: {self.current_session.pages_scraped}/{self.current_session.max_pages}")
                print(f"   Will scrape {pages_remaining_in_session} more pages")
                
                # Scrape pages in this session
                for session_page in range(pages_remaining_in_session):
                    page_num = pages_scraped + 1
                    
                    # Add session break between pages (except first page of session)
                    if session_page > 0 and self.human_behavior:
                        self.human_behavior.simulate_session_break()
                    
                    jobs = self._scrape_page(page_num)
                    all_jobs.extend(jobs)
                    pages_scraped += 1
                    
                    print(f"  ✓ Page {page_num} complete: {len(jobs)} jobs scraped")
                    
                    # Check if session was terminated due to CAPTCHA
                    if self.current_session and not self.current_session.is_active:
                        print("   🛡️ Session terminated due to CAPTCHA")
                        break
                    
                    # Inter-page delay within session
                    if session_page < pages_remaining_in_session - 1:
                        delay = random.uniform(2, 5)
                        time.sleep(delay)
                
                # End session
                if self.current_session:
                    successful = not self.current_session.captcha_triggered
                    self.current_session.end_session(successful=successful)
            
            # Save proxy statistics
            if self.session_manager:
                self.session_manager.save_proxy_stats("proxy_stats.json")
                
                # Display final stats
                final_status = self.session_manager.get_proxy_pool_status()
                print(f"\n📊 Final proxy pool status:")
                print(f"   Sessions completed: {final_status['sessions_completed']}")
                print(f"   Healthy proxies: {final_status['healthy_proxies']}/{final_status['total_proxies']}")
                
                for health, count in final_status['health_distribution'].items():
                    if count > 0:
                        print(f"   {health}: {count}")
        
        except Exception as e:
            print(f"\n❌ Error during scraping: {str(e)}")
        finally:
            if self.driver:
                print("\n🔒 Closing browser...")
                try:
                    self.driver.quit()
                except:
                    pass
        
        print(f"\n  📊 Total jobs scraped: {len(all_jobs)}")
        return all_jobs
    
    def _start_new_session(self):
        """Start a new scraping session with fresh proxy."""
        # Clean up previous session
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self.human_behavior = None
        
        # Start new session
        if self.session_manager:
            self.current_session = self.session_manager.start_new_session()
        
        if self.current_session:
            # Initialize driver with session proxy
            print("� Initializing browser for new session...")
            self.driver = self._init_driver(self.current_session)
            
            # Initialize human behavior simulator
            self.human_behavior = HumanBehaviorSimulator(self.driver)
        else:
            # Fallback: no session manager or no proxies
            print("🚀 Starting browser without proxy session...")
            self.driver = self._init_driver()
            self.human_behavior = HumanBehaviorSimulator(self.driver) if self.driver else None
