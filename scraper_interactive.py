"""
Interactive Indeed Job Scraper
Asks user for keywords, locations, and pages before scraping
"""

from indeed_scraper import IndeedScraper
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Print a nice banner"""
    print("\n" + "="*60)
    print("           INDEED JOB SCRAPER")
    print("="*60 + "\n")


def get_user_input():
    """Get search parameters from user"""
    print("Let's set up your job search!\n")
    
    # Get keywords
    print("📌 What job titles are you looking for?")
    print("   (Examples: python developer, data analyst, software engineer)")
    keywords_input = input("   Enter keywords (separate with commas): ").strip()
    keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
    
    if not keywords:
        print("❌ No keywords entered. Using default: 'software engineer'")
        keywords = ["software engineer"]
    
    print(f"✓ Searching for: {', '.join(keywords)}\n")
    
    # Get locations
    print("📍 Where should I search?")
    print("   (Examples: New York, NY | Remote | San Francisco, CA)")
    locations_input = input("   Enter locations (separate with commas): ").strip()
    locations = [l.strip() for l in locations_input.split(',') if l.strip()]
    
    if not locations:
        print("❌ No locations entered. Using default: 'Remote'")
        locations = ["Remote"]
    
    print(f"✓ Searching in: {', '.join(locations)}\n")
    
    # Get pages
    print("📄 How many pages should I scrape per search?")
    print("   (Each page = ~10-15 jobs. Recommended: 2-5 pages)")
    pages_input = input("   Enter number of pages (1-10): ").strip()
    
    try:
        max_pages = int(pages_input)
        if max_pages < 1 or max_pages > 10:
            print("❌ Invalid number. Using default: 3 pages")
            max_pages = 3
    except ValueError:
        print("❌ Invalid input. Using default: 3 pages")
        max_pages = 3
    
    print(f"✓ Scraping {max_pages} pages per search\n")
    
    # Calculate estimates
    total_searches = len(keywords) * len(locations)
    total_pages = total_searches * max_pages
    estimated_jobs = total_pages * 12  # average jobs per page
    estimated_time_minutes = (total_pages * 10) / 60  # 10 seconds per page average
    
    print("\n" + "="*60)
    print("SEARCH SUMMARY")
    print("="*60)
    print(f"Keywords: {len(keywords)}")
    print(f"Locations: {len(locations)}")
    print(f"Total searches: {total_searches}")
    print(f"Total pages: {total_pages}")
    print(f"Estimated jobs: {estimated_jobs}")
    print(f"Estimated time: {estimated_time_minutes:.1f} minutes")
    print("="*60 + "\n")
    
    # Confirm
    confirm = input("Ready to start? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("\n❌ Scraping cancelled.")
        return None
    
    return {
        'keywords': keywords,
        'locations': locations,
        'max_pages': max_pages
    }


def run_scraper():
    """Run the scraper with user input"""
    try:
        clear_screen()
        print_banner()
        
        # Get user input
        params = get_user_input()
        if not params:
            return 0
        
        print("\n" + "="*60)
        print("STARTING SCRAPER...")
        print("="*60 + "\n")
        
        # Create timestamp for output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"scraped_jobs_{timestamp}.txt"
        
        # Clear the output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"INDEED JOB SCRAPER - Results from {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n")
            f.write(f"Keywords: {', '.join(params['keywords'])}\n")
            f.write(f"Locations: {', '.join(params['locations'])}\n")
            f.write(f"Pages per search: {params['max_pages']}\n")
            f.write("=" * 80 + "\n\n")
        
        # Initialize scraper
        scraper = IndeedScraper()
        
        # Override the save_to_txt to use our custom filename
        original_save_to_txt = scraper.save_to_txt
        scraper.save_to_txt = lambda jobs: original_save_to_txt(jobs, output_file)
        
        # Run scraping
        total_jobs = scraper.scrape_jobs(
            keywords=params['keywords'],
            locations=params['locations'],
            max_pages=params['max_pages'],
            delay_range=(4, 10)
        )
        
        print("\n" + "="*60)
        print("✓ SCRAPING COMPLETED!")
        print("="*60)
        print(f"✓ Total new jobs saved to database: {total_jobs}")
        print(f"✓ Results also saved to: {output_file}")
        print(f"✓ Detailed logs saved to: scraper.log")
        print("="*60 + "\n")
        
        # Show summary in text file
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"SCRAPING COMPLETED - Total Jobs Saved: {total_jobs}\n")
            f.write("=" * 80 + "\n")
        
        print("View your results:")
        print(f"  1. Open '{output_file}' to see all jobs")
        print(f"  2. Run 'python view_jobs.py' to query database")
        print(f"  3. Check 'scraper.log' for detailed logs\n")
        
        return total_jobs
        
    except KeyboardInterrupt:
        print("\n\n⚠ Scraping interrupted by user (Ctrl+C)")
        print("Partial results may have been saved.\n")
        return 0
    except Exception as e:
        logger.error(f"\n\n❌ Error during scraping: {e}", exc_info=True)
        print(f"\n❌ An error occurred. Check scraper.log for details.\n")
        return 0


if __name__ == "__main__":
    run_scraper()
