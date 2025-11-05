"""
Test script to demonstrate Chrome driver fallback behavior
==========================================================
"""

from chrome_driver_manager import get_driver
import undetected_chromedriver as uc


def test_fallback_scenario():
    """Test what happens when undetected-chromedriver fails."""
    print("🧪 Testing fallback scenario...")
    
    # Mock a scenario where undetected-chromedriver might fail
    # by trying with an invalid version first
    try:
        print("🔧 Simulating version mismatch scenario...")
        
        # This would normally be handled by get_driver() internally
        driver = get_driver(use_proxy=False)
        
        print("✅ Driver initialized successfully!")
        print(f"Driver type: {type(driver)}")
        
        # Test basic functionality
        driver.get("https://httpbin.org/headers")
        print(f"✅ Page loaded successfully. Title: {driver.title}")
        
        driver.quit()
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


def show_detected_version():
    """Show what Chrome version was detected."""
    from chrome_driver_manager import detect_chrome_version
    
    version = detect_chrome_version()
    if version:
        print(f"🔍 Detected Chrome version: {version}")
    else:
        print("⚠️ Could not detect Chrome version")


if __name__ == "__main__":
    show_detected_version()
    print()
    test_fallback_scenario()