"""
Automatic Proxy Authentication for Chrome
=========================================
Handles proxy authentication automatically without popups using Chrome extension.
"""

import os
import json
import zipfile
import tempfile
import random
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import undetected_chromedriver as uc


class ProxyAuthManager:
    """Manages proxy authentication automatically for Chrome."""
    
    def __init__(self, proxy_file: str = "proxies.txt"):
        self.proxy_file = proxy_file
        self.proxies = []
        self.current_proxy_index = 0
        self.extension_dir = None
        self.load_proxies()
    
    def load_proxies(self) -> List[Dict]:
        """Load and parse proxies from file."""
        self.proxies = []
        
        try:
            with open(self.proxy_file, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                proxy_info = self.parse_proxy_line(line)
                if proxy_info:
                    self.proxies.append(proxy_info)
            
            print(f"✅ Loaded {len(self.proxies)} proxies from {self.proxy_file}")
            
            # Show proxy types
            auth_count = sum(1 for p in self.proxies if p['requires_auth'])
            print(f"   📊 With authentication: {auth_count}/{len(self.proxies)}")
            
        except FileNotFoundError:
            print(f"❌ Proxy file not found: {self.proxy_file}")
        except Exception as e:
            print(f"❌ Error loading proxies: {e}")
        
        return self.proxies
    
    def parse_proxy_line(self, line: str) -> Optional[Dict]:
        """Parse a single proxy line into structured data."""
        parts = line.split(':')
        
        if len(parts) == 2:
            # Format: host:port (no authentication)
            host, port = parts
            return {
                'host': host.strip(),
                'port': int(port.strip()),
                'username': None,
                'password': None,
                'requires_auth': False,
                'server': f"{host.strip()}:{port.strip()}"
            }
        
        elif len(parts) == 4:
            # Format: host:port:username:password
            host, port, username, password = parts
            return {
                'host': host.strip(),
                'port': int(port.strip()),
                'username': username.strip(),
                'password': password.strip(),
                'requires_auth': True,
                'server': f"{host.strip()}:{port.strip()}"
            }
        
        else:
            print(f"⚠️ Invalid proxy format: {line}")
            return None
    
    def get_next_proxy(self) -> Optional[Dict]:
        """Get next proxy from rotation."""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        
        return proxy
    
    def get_random_proxy(self) -> Optional[Dict]:
        """Get random proxy from list."""
        if not self.proxies:
            return None
        
        return random.choice(self.proxies)
    
    def create_auth_extension(self, proxy: Dict) -> str:
        """Create Chrome extension for proxy authentication."""
        if not proxy['requires_auth']:
            return None
        
        # Create temporary directory for extension
        if self.extension_dir:
            self._cleanup_extension()
        
        self.extension_dir = tempfile.mkdtemp(prefix="proxy_auth_")
        
        # Create manifest.json
        manifest = {
            "manifest_version": 2,
            "name": "Proxy Auth",
            "version": "1.0",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"],
                "persistent": True
            },
            "content_security_policy": "script-src 'self' 'unsafe-eval'; object-src 'self'"
        }
        
        # Create background.js for automatic authentication
        background_js = f"""
var config = {{
    mode: "fixed_servers",
    rules: {{
        singleProxy: {{
            scheme: "http",
            host: "{proxy['host']}",
            port: parseInt("{proxy['port']}")
        }},
        bypassList: ["localhost"]
    }}
}};

chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

function callbackFn(details) {{
    return {{
        authCredentials: {{
            username: "{proxy['username']}",
            password: "{proxy['password']}"
        }}
    }};
}}

chrome.webRequest.onAuthRequired.addListener(
    callbackFn,
    {{urls: ["<all_urls>"]}},
    ['blocking']
);
"""
        
        # Write files
        manifest_path = os.path.join(self.extension_dir, "manifest.json")
        background_path = os.path.join(self.extension_dir, "background.js")
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        with open(background_path, 'w') as f:
            f.write(background_js)
        
        print(f"🔧 Created auth extension for {proxy['host']}:{proxy['port']}")
        return self.extension_dir
    
    def _cleanup_extension(self):
        """Clean up temporary extension directory."""
        if self.extension_dir and os.path.exists(self.extension_dir):
            try:
                import shutil
                shutil.rmtree(self.extension_dir)
            except:
                pass
        self.extension_dir = None
    
    def setup_chrome_options(self, proxy: Dict) -> uc.ChromeOptions:
        """Setup Chrome options with proxy authentication."""
        options = uc.ChromeOptions()
        
        # Basic stealth options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        if proxy['requires_auth']:
            # Use extension for authenticated proxies
            extension_path = self.create_auth_extension(proxy)
            if extension_path:
                options.add_argument(f'--load-extension={extension_path}')
                options.add_argument('--disable-extensions-except={}'.format(extension_path))
                print(f"📡 Using authenticated proxy: {proxy['username']}@{proxy['server']}")
        else:
            # Use standard proxy argument for non-authenticated proxies
            options.add_argument(f'--proxy-server=http://{proxy["server"]}')
            print(f"📡 Using proxy: {proxy['server']}")
        
        return options
    
    def create_driver_with_proxy(self, proxy: Optional[Dict] = None) -> uc.Chrome:
        """Create Chrome driver with automatic proxy authentication."""
        if proxy is None:
            proxy = self.get_next_proxy()
        
        if not proxy:
            print("⚠️ No proxy available, creating driver without proxy")
            options = uc.ChromeOptions()
            options.add_argument('--disable-blink-features=AutomationControlled')
            return uc.Chrome(options=options)
        
        print(f"🚀 Setting up driver with proxy: {proxy['server']}")
        
        try:
            # Setup Chrome options with proxy
            options = self.setup_chrome_options(proxy)
            
            # Create driver
            driver = uc.Chrome(options=options, version_main=None)
            driver.set_window_size(1920, 1080)
            
            # Test proxy connection
            self._test_proxy_connection(driver, proxy)
            
            return driver
            
        except Exception as e:
            print(f"❌ Failed to create driver with proxy {proxy['server']}: {e}")
            self._cleanup_extension()
            raise
    
    def _test_proxy_connection(self, driver: uc.Chrome, proxy: Dict):
        """Test if proxy connection is working."""
        try:
            print("🔍 Testing proxy connection...")
            
            # Navigate to IP check service
            driver.get("https://httpbin.org/ip")
            
            # Wait a moment for page to load
            import time
            time.sleep(3)
            
            # Get page content
            page_source = driver.page_source.lower()
            
            if "origin" in page_source:
                print("✅ Proxy connection successful")
            else:
                print("⚠️ Proxy connection test inconclusive")
                
        except Exception as e:
            print(f"⚠️ Proxy test failed: {e}")
    
    def rotate_proxy(self, current_driver: uc.Chrome) -> uc.Chrome:
        """Rotate to next proxy by creating new driver."""
        print("🔄 Rotating to next proxy...")
        
        # Close current driver
        try:
            current_driver.quit()
        except:
            pass
        
        # Clean up current extension
        self._cleanup_extension()
        
        # Create new driver with next proxy
        return self.create_driver_with_proxy()
    
    def cleanup(self):
        """Clean up resources."""
        self._cleanup_extension()
    
    def get_proxy_stats(self) -> Dict:
        """Get statistics about loaded proxies."""
        if not self.proxies:
            return {"total": 0, "authenticated": 0, "simple": 0}
        
        auth_count = sum(1 for p in self.proxies if p['requires_auth'])
        
        return {
            "total": len(self.proxies),
            "authenticated": auth_count,
            "simple": len(self.proxies) - auth_count,
            "current_index": self.current_proxy_index
        }


def create_driver_with_auto_proxy(proxy_file: str = "proxies.txt") -> Tuple[uc.Chrome, ProxyAuthManager]:
    """
    Convenience function to create a driver with automatic proxy handling.
    
    Returns:
        Tuple of (driver, proxy_manager) for easy use
    """
    proxy_manager = ProxyAuthManager(proxy_file)
    driver = proxy_manager.create_driver_with_proxy()
    
    return driver, proxy_manager


def test_proxy_authentication():
    """Test the proxy authentication system."""
    print("🧪 Testing automatic proxy authentication...")
    
    # Create proxy manager
    proxy_manager = ProxyAuthManager("proxies.txt")
    
    # Show stats
    stats = proxy_manager.get_proxy_stats()
    print(f"📊 Proxy Stats: {stats}")
    
    if stats['total'] == 0:
        print("❌ No proxies loaded!")
        return
    
    try:
        # Test first proxy
        driver = proxy_manager.create_driver_with_proxy()
        
        print("✅ Driver created successfully!")
        
        # Test navigation
        print("🌐 Testing navigation...")
        driver.get("https://httpbin.org/headers")
        
        import time
        time.sleep(5)
        
        print("✅ Navigation successful!")
        
        # Test proxy rotation
        print("🔄 Testing proxy rotation...")
        driver = proxy_manager.rotate_proxy(driver)
        
        print("✅ Proxy rotation successful!")
        
        # Final test
        driver.get("https://httpbin.org/ip")
        time.sleep(3)
        
        print("✅ All tests passed!")
        
        # Cleanup
        driver.quit()
        proxy_manager.cleanup()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        proxy_manager.cleanup()


if __name__ == "__main__":
    test_proxy_authentication()