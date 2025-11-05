"""
Chrome Driver Manager - Universal Chrome Version Detection & Driver Setup
=========================================================================
Automatically detects Chrome version and initializes compatible driver.
"""

import os
import re
import sys
import subprocess
import platform
from typing import Optional, Tuple
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def detect_chrome_version() -> Optional[str]:
    """
    Detect installed Chrome version across Windows, Mac, and Linux.
    
    Returns:
        str: Chrome version (e.g., '120', '119') or None if not found
    """
    system = platform.system().lower()
    
    try:
        if system == "windows":
            return _detect_chrome_version_windows()
        elif system == "darwin":  # macOS
            return _detect_chrome_version_mac()
        elif system == "linux":
            return _detect_chrome_version_linux()
        else:
            print(f"⚠️  Unsupported OS: {system}")
            return None
    except Exception as e:
        print(f"⚠️  Chrome version detection failed: {e}")
        return None


def _detect_chrome_version_windows() -> Optional[str]:
    """Detect Chrome version on Windows using registry and file checks."""
    import winreg
    
    # Method 1: Registry check
    try:
        key_path = r"SOFTWARE\Google\Chrome\BLBeacon"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            version, _ = winreg.QueryValueEx(key, "version")
            major_version = version.split('.')[0]
            print(f"✓ Chrome version detected (registry): {version} -> major: {major_version}")
            return major_version
    except (FileNotFoundError, OSError, winreg.error):
        pass
    
    # Method 2: Chrome executable version check
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path):
            try:
                result = subprocess.run(
                    [chrome_path, "--version"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if result.returncode == 0:
                    version_match = re.search(r'Chrome (\d+)\.', result.stdout)
                    if version_match:
                        major_version = version_match.group(1)
                        print(f"✓ Chrome version detected (executable): {result.stdout.strip()} -> major: {major_version}")
                        return major_version
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                continue
    
    return None


def _detect_chrome_version_mac() -> Optional[str]:
    """Detect Chrome version on macOS."""
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chrome.app/Contents/MacOS/Chrome"
    ]
    
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path):
            try:
                result = subprocess.run(
                    [chrome_path, "--version"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                if result.returncode == 0:
                    version_match = re.search(r'Chrome (\d+)\.', result.stdout)
                    if version_match:
                        major_version = version_match.group(1)
                        print(f"✓ Chrome version detected (macOS): {result.stdout.strip()} -> major: {major_version}")
                        return major_version
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                continue
    
    return None


def _detect_chrome_version_linux() -> Optional[str]:
    """Detect Chrome version on Linux."""
    chrome_commands = [
        "google-chrome",
        "google-chrome-stable", 
        "chromium",
        "chromium-browser"
    ]
    
    for command in chrome_commands:
        try:
            result = subprocess.run(
                [command, "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            if result.returncode == 0:
                version_match = re.search(r'Chrome (\d+)\.', result.stdout)
                if version_match:
                    major_version = version_match.group(1)
                    print(f"✓ Chrome version detected (Linux): {result.stdout.strip()} -> major: {major_version}")
                    return major_version
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    return None


def get_driver(use_proxy: bool = False, proxy_config: Optional[dict] = None) -> uc.Chrome:
    """
    Universal Chrome driver initialization with automatic version detection.
    
    Args:
        use_proxy: Whether to use proxy
        proxy_config: Proxy configuration dict (optional)
    
    Returns:
        uc.Chrome: Working Chrome driver instance
    
    Raises:
        Exception: If no working driver can be initialized
    """
    print("🚀 Initializing Chrome driver with automatic version detection...")
    
    # Detect Chrome version
    chrome_version = detect_chrome_version()
    
    # Setup common Chrome options
    options = uc.ChromeOptions()
    
    # Stealth options for anti-bot protection
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Add proxy if specified
    if use_proxy and proxy_config:
        proxy_server = proxy_config.get('server', '').replace('http://', '')
        if proxy_server:
            options.add_argument(f'--proxy-server={proxy_server}')
            print(f"📡 Using proxy: {proxy_server}")
    
    # Strategy 1: Try undetected-chromedriver with detected version
    if chrome_version:
        try:
            print(f"🔧 Attempting undetected-chromedriver with Chrome {chrome_version}...")
            driver = uc.Chrome(options=options, version_main=int(chrome_version))
            driver.set_window_size(1920, 1080)
            
            # Quick test to ensure driver works
            driver.get("data:text/html,<html><body><h1>Driver Test</h1></body></html>")
            print(f"✅ Success! Using undetected-chromedriver with Chrome {chrome_version}")
            return driver
            
        except Exception as e:
            print(f"⚠️  undetected-chromedriver with version {chrome_version} failed: {e}")
            try:
                driver.quit()
            except:
                pass
    
    # Strategy 2: Try undetected-chromedriver without specific version (auto-detect)
    try:
        print("🔧 Attempting undetected-chromedriver with auto-detection...")
        driver = uc.Chrome(options=options, version_main=None)
        driver.set_window_size(1920, 1080)
        
        # Quick test
        driver.get("data:text/html,<html><body><h1>Driver Test</h1></body></html>")
        print("✅ Success! Using undetected-chromedriver with auto-detection")
        return driver
        
    except Exception as e:
        print(f"⚠️  undetected-chromedriver auto-detection failed: {e}")
        try:
            driver.quit()
        except:
            pass
    
    # Strategy 3: Fallback to webdriver-manager + standard selenium
    try:
        print("🔧 Falling back to webdriver-manager...")
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Convert uc.ChromeOptions to standard Options
        standard_options = Options()
        for arg in options.arguments:
            standard_options.add_argument(arg)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=standard_options)
        driver.set_window_size(1920, 1080)
        
        # Quick test
        driver.get("data:text/html,<html><body><h1>Driver Test</h1></body></html>")
        print("✅ Success! Using webdriver-manager fallback")
        print("⚠️  Note: Using standard Selenium (may be detected by anti-bot systems)")
        return driver
        
    except Exception as e:
        print(f"❌ webdriver-manager fallback failed: {e}")
        try:
            driver.quit()
        except:
            pass
    
    # If all strategies fail
    raise Exception(
        "❌ Failed to initialize Chrome driver with all strategies:\n"
        "1. undetected-chromedriver with detected version\n"
        "2. undetected-chromedriver auto-detection\n"
        "3. webdriver-manager fallback\n\n"
        "Please ensure Chrome is installed and try manually updating ChromeDriver."
    )


def test_driver_initialization():
    """Test function to verify driver initialization works."""
    print("🧪 Testing driver initialization...")
    
    try:
        driver = get_driver()
        
        # Test basic functionality
        driver.get("https://httpbin.org/user-agent")
        title = driver.title
        print(f"✅ Driver test successful! Page title: {title}")
        
        # Check user agent
        user_agent = driver.execute_script("return navigator.userAgent;")
        print(f"🕵️  User agent: {user_agent}")
        
        driver.quit()
        print("✅ Driver cleanup successful!")
        
    except Exception as e:
        print(f"❌ Driver test failed: {e}")
        raise


if __name__ == "__main__":
    # Quick test when run directly
    test_driver_initialization()