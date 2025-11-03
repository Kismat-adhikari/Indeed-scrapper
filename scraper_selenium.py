"""
Alternative Indeed Job Scraper using requests-html for better JavaScript handling
This version is more resilient to Indeed's anti-bot measures
"""

import os
import time
import random
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import List, Dict
from datetime import datetime
import logging
import json

# Try to import selenium - we'll need it for Indeed
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IndeedScraperV2:
    """Improved scraper using Selenium for better success rate"""
    
    def __init__(self):
        if not SELENIUM_AVAILABLE:
            logger.error("Selenium not installed. Install with: pip install selenium")
            raise ImportError("selenium package required")
        
        load_dotenv()
        
        # Initialize Supabase
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Load existing links
        self.existing_links = set()
        self.load_existing_links()
        
        # Will initialize browser on first use
        self.driver = None
    
    def load_existing_links(self):
        """Load existing job links from database"""
        try:
            response = self.supabase.table('indeed_jobs').select('link').execute()
            self.existing_links = {job['link'] for job in response.data if job.get('link')}
            logger.info(f"Loaded {len(self.existing_links)} existing job links")
        except Exception as e:
            logger.error(f"Error loading existing links: {e}")
    
    def init_browser(self):
        """Initialize Chrome browser with options"""
        if self.driver:
            return
        
        try:
            logger.info("Initializing browser...")
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Use webdriver-manager to auto-install chromedriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("✓ Browser initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize browser: {e}")
            logger.info("Make sure Chrome browser is installed")
            raise
    
    def scrape_jobs(self, keywords: List[str], locations: List[str], max_pages: int = 3):
        """Main scraping function"""
        try:
            self.init_browser()
            
            all_jobs = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"scraped_jobs_{timestamp}.txt"
            
            # Write header to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"INDEED JOB SCRAPER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
            
            total_saved = 0
            
            for keyword in keywords:
                for location in locations:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"Searching: '{keyword}' in '{location}'")
                    logger.info(f"{'='*60}\n")
                    
                    for page in range(max_pages):
                        start = page * 10
                        jobs = self.scrape_page(keyword, location, start)
                        
                        if not jobs:
                            logger.info("No jobs found on this page")
                            break
                        
                        # Save jobs
                        saved = self.save_jobs(jobs, output_file)
                        total_saved += saved
                        all_jobs.extend(jobs)
                        
                        logger.info(f"Saved {saved} new jobs from page {page + 1}")
                        
                        # Random delay
                        if page < max_pages - 1:
                            delay = random.uniform(3, 7)
                            logger.info(f"Waiting {delay:.1f}s...")
                            time.sleep(delay)
                    
                    # Delay between searches
                    time.sleep(random.uniform(2, 5))
            
            # Write summary
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write(f"TOTAL JOBS FOUND: {total_saved}\n")
                f.write("=" * 80 + "\n")
            
            logger.info(f"\n✓ Scraping complete! Found {total_saved} new jobs")
            logger.info(f"✓ Results saved to: {output_file}")
            
            return total_saved
            
        finally:
            if self.driver:
                self.driver.quit()
    
    def scrape_page(self, keyword: str, location: str, start: int = 0):
        """Scrape a single page"""
        try:
            # Build URL
            url = f"https://www.indeed.com/jobs?q={keyword.replace(' ', '+')}&l={location.replace(' ', '+')}&start={start}"
            logger.info(f"Fetching: {url[:80]}...")
            
            self.driver.get(url)
            time.sleep(random.uniform(2, 4))  # Wait for page load
            
            jobs = []
            
            # Try to find job cards
            try:
                # Wait for job listings to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.job_seen_beacon, a[data-jk], div.jobsearch-SerpJobCard"))
                )
                
                # Find all job cards - try multiple selectors
                job_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon")
                if not job_elements:
                    job_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[data-jk]")
                if not job_elements:
                    job_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.jobsearch-SerpJobCard")
                
                logger.info(f"Found {len(job_elements)} job elements")
                
                for element in job_elements:
                    job = self.extract_job_data(element)
                    if job and job.get('link') and job['link'] not in self.existing_links:
                        jobs.append(job)
                
            except Exception as e:
                logger.error(f"Error finding jobs: {e}")
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping page: {e}")
            return []
    
    def extract_job_data(self, element):
        """Extract job data from search results element"""
        try:
            job = {}
            
            # Try to extract job ID and link
            try:
                job_id = element.get_attribute('data-jk')
                if not job_id:
                    # Try finding it in child elements
                    link_elem = element.find_element(By.CSS_SELECTOR, "a[data-jk]")
                    job_id = link_elem.get_attribute('data-jk') if link_elem else None
                
                if job_id:
                    job['link'] = f"https://www.indeed.com/viewjob?jk={job_id}"
            except:
                pass
            
            if not job.get('link'):
                return None
            
            # Extract basic info from search results
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, "h2.jobTitle, a.jcs-JobTitle, span[title]")
                job['title'] = title_elem.text.strip()
            except:
                job['title'] = None
            
            try:
                company_elem = element.find_element(By.CSS_SELECTOR, "span[data-testid='company-name'], span.companyName")
                job['company'] = company_elem.text.strip()
            except:
                job['company'] = None
            
            try:
                location_elem = element.find_element(By.CSS_SELECTOR, "div[data-testid='text-location'], div.companyLocation")
                job['location'] = location_elem.text.strip()
            except:
                job['location'] = None
            
            try:
                summary_elem = element.find_element(By.CSS_SELECTOR, "div.job-snippet, ul")
                job['summary'] = summary_elem.text.strip()
            except:
                job['summary'] = None
            
            # Get detailed info from job page (salary, posted date)
            detailed_info = self.get_job_details(job['link'])
            job.update(detailed_info)
            
            return job if job.get('title') else None
            
        except Exception as e:
            return None
    
    def get_job_details(self, job_url):
        """Visit individual job page to get salary and posted date"""
        details = {'salary': None, 'posted_date': None}
        
        try:
            # Save current window handle
            original_window = self.driver.current_window_handle
            
            # Open new tab for job details
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Navigate to job page
            self.driver.get(job_url)
            time.sleep(random.uniform(1, 2))  # Quick delay
            
            # Extract salary with multiple selectors
            salary_selectors = [
                "#salaryInfoAndJobType span",
                "span[data-testid='viewJobBodyJobCompensation']",
                "div[data-testid='viewJobBodyJobCompensation']",
                ".js-match-insights-provider-compensation span",
                ".css-14jvju9",
                ".jobsearch-JobMetadataHeader-item span",
            ]
            
            for selector in salary_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and ('$' in text or 'year' in text or 'hour' in text):
                            details['salary'] = text
                            break
                    if details['salary']:
                        break
                except:
                    continue
            
            # Extract posted date with multiple selectors  
            date_selectors = [
                "div[data-testid='jobEventDate']",
                ".jobsearch-JobMetadataHeader-iconLabel",
                "span[data-testid='posted-date']", 
                ".js-match-insights-provider-tvoc span",
                "time",
                "span[aria-label*='ago']",
            ]
            
            for selector in date_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and ('ago' in text or 'day' in text or 'hour' in text or 'Posted' in text):
                            details['posted_date'] = text
                            break
                    if details['posted_date']:
                        break
                except:
                    continue
            
            # Close tab and return to original window
            self.driver.close()
            self.driver.switch_to.window(original_window)
            
        except Exception as e:
            # Make sure we return to original window even if error occurs
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
        
        return details
    
    def save_jobs(self, jobs: List[Dict], output_file: str) -> int:
        """Save jobs to database and file"""
        if not jobs:
            return 0
        
        saved_count = 0
        
        for job in jobs:
            # Save to database
            try:
                self.supabase.table('indeed_jobs').insert(job).execute()
                self.existing_links.add(job['link'])
                saved_count += 1
            except Exception as e:
                logger.error(f"DB error: {e}")
            
            # Save to file
            try:
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write("=" * 80 + "\n")
                    f.write(f"TITLE: {job.get('title', 'N/A')}\n")
                    f.write(f"COMPANY: {job.get('company', 'N/A')}\n")
                    f.write(f"LOCATION: {job.get('location', 'N/A')}\n")
                    f.write(f"SALARY: {job.get('salary', 'N/A')}\n")
                    f.write(f"POSTED: {job.get('posted_date', 'N/A')}\n")
                    f.write(f"LINK: {job.get('link', 'N/A')}\n")
                    f.write(f"SUMMARY: {job.get('summary', 'N/A')}\n")
                    f.write("=" * 80 + "\n\n")
            except Exception as e:
                logger.error(f"File error: {e}")
        
        return saved_count


def main():
    """Interactive scraper"""
    print("\n" + "="*60)
    print("INDEED JOB SCRAPER (SELENIUM VERSION)")
    print("="*60 + "\n")
    
    # Get user input
    keywords_input = input("What jobs? (e.g., python developer, data analyst): ").strip()
    keywords = [k.strip() for k in keywords_input.split(',') if k.strip()] or ["software engineer"]
    
    locations_input = input("Where? (e.g., New York, Remote): ").strip()
    locations = [l.strip() for l in locations_input.split(',') if l.strip()] or ["Remote"]
    
    pages_input = input("How many pages? (1-5): ").strip()
    try:
        max_pages = int(pages_input)
        max_pages = max(1, min(5, max_pages))
    except:
        max_pages = 2
    
    print(f"\n✓ Searching {len(keywords)} keywords in {len(locations)} locations")
    print(f"✓ {max_pages} pages per search")
    
    confirm = input("\nReady? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    print("\nStarting scraper...")
    print("NOTE: This uses Selenium which opens a browser in the background.\n")
    
    try:
        scraper = IndeedScraperV2()
        total = scraper.scrape_jobs(keywords, locations, max_pages)
        print(f"\n✓ Complete! Found {total} jobs")
    except ImportError:
        print("\n❌ Selenium not installed!")
        print("Install it with: pip install selenium")
        print("You also need Chrome browser installed.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
