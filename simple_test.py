"""
Simple Test - Check what Indeed returns
========================================
This will open Indeed and save the HTML to see what we're getting.
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_indeed():
    """Open Indeed and check what we get."""
    url = "https://www.indeed.com/jobs?q=python&l=remote"
    
    print("🚀 Opening Indeed...")
    print(f"URL: {url}\n")
    
    # Create driver
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')
    
    try:
        driver = uc.Chrome(options=options, version_main=None)
        
        print("📄 Loading page...")
        driver.get(url)
        
        print("⏳ Waiting 10 seconds...")
        time.sleep(10)
        
        # Get info
        title = driver.title
        url_now = driver.current_url
        
        print(f"\n✓ Page loaded!")
        print(f"Title: {title}")
        print(f"URL: {url_now}\n")
        
        # Check for various elements
        print("🔍 Checking for elements...\n")
        
        checks = [
            ("Cloudflare text", "cloudflare", "page_source"),
            ("CAPTCHA text", "captcha", "page_source"),
            ("'Just a moment'", "just a moment", "page_source"),
            ("Job cards (.job_seen_beacon)", ".job_seen_beacon", "css"),
            ("[data-jk] elements", "[data-jk]", "css"),
            ("Job titles (h2.jobTitle)", "h2.jobTitle", "css"),
            ("Result content (td.resultContent)", "td.resultContent", "css"),
        ]
        
        for name, selector, check_type in checks:
            try:
                if check_type == "page_source":
                    if selector.lower() in driver.page_source.lower():
                        print(f"  ✓ Found: {name}")
                    else:
                        print(f"  ✗ Not found: {name}")
                else:  # css
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"  ✓ Found {len(elements)}: {name}")
                    else:
                        print(f"  ✗ Not found: {name}")
            except Exception as e:
                print(f"  ✗ Error checking {name}: {str(e)}")
        
        # Save HTML
        html_file = "output/simple_test.html"
        import os
        os.makedirs('output', exist_ok=True)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        
        print(f"\n💾 HTML saved to: {html_file}")
        print(f"   File size: {len(driver.page_source)} bytes")
        
        # Check specific content
        page_text = driver.page_source.lower()
        if "blocked" in page_text or "access denied" in page_text:
            print("\n⚠️  WARNING: Might be blocked!")
        
        if "captcha" in page_text or "cloudflare" in page_text:
            print("⚠️  WARNING: Cloudflare/CAPTCHA detected!")
        
        # Check if it's the real Indeed page
        if "indeed" not in title.lower():
            print("\n⚠️  WARNING: This might not be Indeed!")
        
        print("\n⏸️  Browser will stay open for 30 seconds...")
        print("   Check if you can see job listings!")
        time.sleep(30)
        
        driver.quit()
        print("\n✓ Test complete! Check output/simple_test.html")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    test_indeed()
