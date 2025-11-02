"""
Indeed Job Scraper with Proxy Rotation and Supabase Integration
Scrapes job listings from Indeed and stores them in Supabase database
"""

import os
import time
import random
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import List, Dict, Optional
from urllib.parse import urlencode, quote_plus
from fake_useragent import UserAgent
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProxyRotator:
    """Handles proxy rotation from proxies.txt file"""
    
    def __init__(self, proxy_file: str = "proxies.txt"):
        self.proxies = []
        self.load_proxies(proxy_file)
        self.current_index = 0
        
    def load_proxies(self, proxy_file: str):
        """Load proxies from file"""
        try:
            with open(proxy_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # Parse format: ip:port:username:password
                        parts = line.split(':')
                        if len(parts) == 4:
                            ip, port, username, password = parts
                            proxy_url = f"http://{username}:{password}@{ip}:{port}"
                            self.proxies.append({
                                'http': proxy_url,
                                'https': proxy_url
                            })
            logger.info(f"Loaded {len(self.proxies)} proxies")
        except FileNotFoundError:
            logger.warning(f"Proxy file {proxy_file} not found. Running without proxies.")
        except Exception as e:
            logger.error(f"Error loading proxies: {e}")
    
    def get_random_proxy(self) -> Optional[Dict]:
        """Get a random proxy from the list"""
        if not self.proxies:
            return None
        return random.choice(self.proxies)
    
    def get_next_proxy(self) -> Optional[Dict]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy


class IndeedScraper:
    """Main scraper class for Indeed job listings"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Initialize proxy rotator
        self.proxy_rotator = ProxyRotator()
        
        # Initialize user agent generator
        self.ua = UserAgent()
        
        # Base URL for Indeed
        self.base_url = "https://www.indeed.com"
        
        # Store existing job links to avoid duplicates
        self.existing_links = set()
        self.load_existing_links()
        
    def load_existing_links(self):
        """Load existing job links from database to avoid duplicates"""
        try:
            response = self.supabase.table('indeed_jobs').select('link').execute()
            self.existing_links = {job['link'] for job in response.data if job.get('link')}
            logger.info(f"Loaded {len(self.existing_links)} existing job links from database")
        except Exception as e:
            logger.error(f"Error loading existing links: {e}")
    
    def get_headers(self) -> Dict:
        """Generate random headers to avoid detection"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    
    def build_search_url(self, keyword: str, location: str, start: int = 0) -> str:
        """Build Indeed search URL with parameters"""
        params = {
            'q': keyword,
            'l': location,
            'start': start,
            'sort': 'date'  # Sort by date to get recent jobs
        }
        return f"{self.base_url}/jobs?{urlencode(params)}"
    
    def make_request(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Make HTTP request with proxy rotation and retries"""
        for attempt in range(max_retries):
            try:
                proxy = self.proxy_rotator.get_random_proxy()
                headers = self.get_headers()
                
                logger.info(f"Making request to {url[:100]}... (Attempt {attempt + 1}/{max_retries})")
                
                response = requests.get(
                    url,
                    headers=headers,
                    proxies=proxy,
                    timeout=30,
                    allow_redirects=True
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    logger.warning("Rate limited. Waiting longer...")
                    time.sleep(random.uniform(10, 20))
                else:
                    logger.warning(f"Status code {response.status_code}")
                    
            except requests.exceptions.ProxyError:
                logger.warning(f"Proxy error on attempt {attempt + 1}")
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
            except Exception as e:
                logger.error(f"Request error: {e}")
            
            # Wait before retry with exponential backoff
            if attempt < max_retries - 1:
                wait_time = random.uniform(3, 8) * (attempt + 1)
                logger.info(f"Waiting {wait_time:.2f}s before retry...")
                time.sleep(wait_time)
        
        logger.error(f"Failed to fetch {url} after {max_retries} attempts")
        return None
    
    def parse_job_card(self, card) -> Optional[Dict]:
        """Parse individual job card and extract information"""
        try:
            job_data = {}
            
            # Extract title
            title_elem = card.find('h2', class_='jobTitle')
            if title_elem:
                title_link = title_elem.find('a')
                if title_link:
                    job_data['title'] = title_link.get_text(strip=True)
                    # Extract job link
                    job_id = title_link.get('data-jk') or title_link.get('id', '').replace('job_', '')
                    if job_id:
                        job_data['link'] = f"{self.base_url}/viewjob?jk={job_id}"
                else:
                    job_data['title'] = title_elem.get_text(strip=True)
            
            # Skip if no link or already exists
            if not job_data.get('link') or job_data['link'] in self.existing_links:
                return None
            
            # Extract company
            company_elem = card.find('span', {'data-testid': 'company-name'})
            if not company_elem:
                company_elem = card.find('span', class_='companyName')
            job_data['company'] = company_elem.get_text(strip=True) if company_elem else None
            
            # Extract location
            location_elem = card.find('div', {'data-testid': 'text-location'})
            if not location_elem:
                location_elem = card.find('div', class_='companyLocation')
            job_data['location'] = location_elem.get_text(strip=True) if location_elem else None
            
            # Extract salary
            salary_elem = card.find('div', {'data-testid': 'attribute_snippet_testid'})
            if not salary_elem:
                salary_elem = card.find('div', class_='salary-snippet')
            if not salary_elem:
                salary_elem = card.find('span', class_='salary-snippet-container')
            job_data['salary'] = salary_elem.get_text(strip=True) if salary_elem else None
            
            # Extract summary/description
            summary_elem = card.find('div', class_='job-snippet')
            if not summary_elem:
                summary_elem = card.find('div', {'data-testid': 'job-snippet'})
            if not summary_elem:
                summary_elem = card.find('ul')
            job_data['summary'] = summary_elem.get_text(strip=True) if summary_elem else None
            
            # Extract posted date
            date_elem = card.find('span', class_='date')
            if not date_elem:
                date_elem = card.find('span', {'data-testid': 'myJobsStateDate'})
            job_data['posted_date'] = date_elem.get_text(strip=True) if date_elem else None
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error parsing job card: {e}")
            return None
    
    def scrape_search_page(self, keyword: str, location: str, start: int = 0) -> List[Dict]:
        """Scrape a single search results page"""
        url = self.build_search_url(keyword, location, start)
        response = self.make_request(url)
        
        if not response:
            return []
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Find all job cards
        job_cards = soup.find_all('div', class_='job_seen_beacon')
        if not job_cards:
            # Try alternative selector
            job_cards = soup.find_all('div', {'data-testid': 'slider_item'})
        if not job_cards:
            # Try another alternative
            job_cards = soup.find_all('a', class_='jcs-JobTitle')
            
        logger.info(f"Found {len(job_cards)} job cards on page")
        
        jobs = []
        for card in job_cards:
            job_data = self.parse_job_card(card)
            if job_data:
                jobs.append(job_data)
        
        logger.info(f"Parsed {len(jobs)} valid jobs from page")
        return jobs
    
    def save_to_supabase(self, jobs: List[Dict]) -> int:
        """Save jobs to Supabase database"""
        if not jobs:
            return 0
        
        saved_count = 0
        for job in jobs:
            try:
                # Check if link already exists (double check)
                if job.get('link') in self.existing_links:
                    continue
                
                # Insert into database
                response = self.supabase.table('indeed_jobs').insert(job).execute()
                
                if response.data:
                    saved_count += 1
                    self.existing_links.add(job['link'])
                    logger.info(f"Saved: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
                    
            except Exception as e:
                logger.error(f"Error saving job to database: {e}")
        
        return saved_count
    
    def save_to_txt(self, jobs: List[Dict], filename: str = "scraped_jobs.txt"):
        """Save jobs to a text file for easy viewing"""
        if not jobs:
            return
        
        try:
            with open(filename, 'a', encoding='utf-8') as f:
                for job in jobs:
                    f.write("=" * 80 + "\n")
                    f.write(f"TITLE: {job.get('title', 'N/A')}\n")
                    f.write(f"COMPANY: {job.get('company', 'N/A')}\n")
                    f.write(f"LOCATION: {job.get('location', 'N/A')}\n")
                    f.write(f"SALARY: {job.get('salary', 'N/A')}\n")
                    f.write(f"POSTED: {job.get('posted_date', 'N/A')}\n")
                    f.write(f"LINK: {job.get('link', 'N/A')}\n")
                    f.write(f"SUMMARY: {job.get('summary', 'N/A')}\n")
                    f.write("=" * 80 + "\n\n")
            logger.info(f"Saved {len(jobs)} jobs to {filename}")
        except Exception as e:
            logger.error(f"Error saving to text file: {e}")
    
    def scrape_jobs(self, keywords: List[str], locations: List[str], 
                    max_pages: int = 5, delay_range: tuple = (3, 8)):
        """
        Main scraping function
        
        Args:
            keywords: List of search keywords (e.g., ["software engineer", "data analyst"])
            locations: List of locations (e.g., ["New York", "Remote", "London"])
            max_pages: Maximum number of pages to scrape per keyword/location combo
            delay_range: Random delay range between requests (min, max) in seconds
        """
        total_saved = 0
        
        logger.info(f"Starting scrape for {len(keywords)} keywords and {len(locations)} locations")
        logger.info(f"Will scrape up to {max_pages} pages per combination")
        
        for keyword in keywords:
            for location in locations:
                logger.info(f"\n{'='*60}")
                logger.info(f"Scraping: '{keyword}' in '{location}'")
                logger.info(f"{'='*60}\n")
                
                for page in range(max_pages):
                    start = page * 10  # Indeed shows 10 results per page
                    
                    logger.info(f"Processing page {page + 1}/{max_pages} (start={start})")
                    
                    # Scrape the page
                    jobs = self.scrape_search_page(keyword, location, start)
                    
                    if not jobs:
                        logger.info("No more jobs found, moving to next combination")
                        break
                    
                    # Save to database
                    saved = self.save_to_supabase(jobs)
                    total_saved += saved
                    logger.info(f"Saved {saved} new jobs from this page")
                    
                    # Save to text file
                    self.save_to_txt(jobs)
                    
                    # Random delay between pages
                    if page < max_pages - 1 and jobs:
                        delay = random.uniform(*delay_range)
                        logger.info(f"Waiting {delay:.2f}s before next page...\n")
                        time.sleep(delay)
                
                # Delay between different keyword/location combinations
                delay = random.uniform(*delay_range)
                logger.info(f"Waiting {delay:.2f}s before next search combination...\n")
                time.sleep(delay)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Scraping completed! Total new jobs saved: {total_saved}")
        logger.info(f"{'='*60}\n")
        
        return total_saved


def main():
    """Main function to run the scraper"""
    
    # Initialize scraper
    scraper = IndeedScraper()
    
    # Define search parameters
    keywords = [
        "software engineer",
        "python developer",
        "data analyst",
        "remote developer"
    ]
    
    locations = [
        "New York, NY",
        "San Francisco, CA",
        "Remote",
        "London, UK"
    ]
    
    # Start scraping
    # max_pages: number of pages per keyword/location combination
    # delay_range: random delay between requests (min, max) in seconds
    scraper.scrape_jobs(
        keywords=keywords,
        locations=locations,
        max_pages=3,  # Scrape 3 pages per combination (30 jobs max)
        delay_range=(4, 10)  # Random delay between 4-10 seconds
    )


if __name__ == "__main__":
    main()
