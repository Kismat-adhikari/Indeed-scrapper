"""
Simple runner script for Indeed Job Scraper
Uses settings from config.py
"""

from indeed_scraper import IndeedScraper
import config
import logging

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


def run_scraper():
    """Run the scraper with settings from config.py"""
    try:
        logger.info("="*60)
        logger.info("Starting Indeed Job Scraper")
        logger.info("="*60)
        
        # Initialize scraper
        scraper = IndeedScraper()
        
        # Run scraping
        total_jobs = scraper.scrape_jobs(
            keywords=config.KEYWORDS,
            locations=config.LOCATIONS,
            max_pages=config.MAX_PAGES_PER_SEARCH,
            delay_range=(config.DELAY_MIN, config.DELAY_MAX)
        )
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✓ Scraping completed successfully!")
        logger.info(f"✓ Total new jobs saved: {total_jobs}")
        logger.info(f"{'='*60}\n")
        
        return total_jobs
        
    except KeyboardInterrupt:
        logger.warning("\n\nScraping interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"\n\nError during scraping: {e}", exc_info=True)
        return 0


if __name__ == "__main__":
    run_scraper()
