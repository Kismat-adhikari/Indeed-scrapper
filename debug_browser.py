"""
Debug Scraper - Run with visible browser to see what's happening
================================================================
"""

import asyncio
from playwright.async_api import async_playwright


async def debug_scrape():
    """
    Open Indeed in a visible browser to see what's happening.
    """
    url = "https://www.indeed.com/jobs?q=software+engineer&l=San+Francisco"
    
    print("🔍 Opening Indeed in browser...")
    print(f"URL: {url}\n")
    
    playwright = await async_playwright().start()
    
    # Launch browser in NON-headless mode
    browser = await playwright.chromium.launch(
        headless=False,  # Show the browser
        args=['--start-maximized']
    )
    
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    
    page = await context.new_page()
    
    print("⏳ Navigating to Indeed...")
    await page.goto(url, timeout=60000)
    
    print("✓ Page loaded!")
    print("\n🔍 Inspecting page content...\n")
    
    # Wait a bit for content to load
    await asyncio.sleep(5)
    
    # Check for various elements
    checks = [
        ('.job_seen_beacon', 'Job cards with job_seen_beacon'),
        ('[data-jk]', 'Elements with data-jk'),
        ('h2.jobTitle', 'Job titles'),
        ('.jobsearch-ResultsList', 'Results list'),
        ('#mosaic-provider-jobcards', 'Mosaic provider'),
        ('td.resultContent', 'Table results'),
    ]
    
    for selector, description in checks:
        try:
            elements = await page.query_selector_all(selector)
            count = len(elements)
            if count > 0:
                print(f"✓ Found {count} elements: {description} ({selector})")
            else:
                print(f"✗ Not found: {description} ({selector})")
        except Exception as e:
            print(f"✗ Error checking {description}: {str(e)}")
    
    # Get page title and some text
    title = await page.title()
    print(f"\n📄 Page Title: {title}")
    
    # Check if we hit a CAPTCHA or block
    content = await page.content()
    if 'captcha' in content.lower():
        print("\n⚠️  WARNING: CAPTCHA detected!")
    if 'blocked' in content.lower() or 'access denied' in content.lower():
        print("\n⚠️  WARNING: Access might be blocked!")
    
    # Save HTML for inspection
    with open('output/debug_indeed.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\n💾 Full HTML saved to: output/debug_indeed.html")
    
    print("\n⏸️  Browser will stay open for 30 seconds so you can inspect...")
    print("    Check if you see job listings on the page.")
    await asyncio.sleep(30)
    
    await browser.close()
    await playwright.stop()
    
    print("\n✓ Debug complete!")


if __name__ == "__main__":
    asyncio.run(debug_scrape())
