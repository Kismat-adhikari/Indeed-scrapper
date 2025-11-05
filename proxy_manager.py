"""
Proxy Manager Module
====================
Handles loading, parsing, and rotating proxies for the scraper.
Supports proxy authentication with username/password.
"""

from typing import List, Dict, Optional
from pathlib import Path


class ProxyManager:
    """
    Manages proxy loading and rotation for web scraping.
    """
    
    def __init__(self, proxy_file: str):
        """
        Initialize proxy manager.
        
        Args:
            proxy_file: Path to proxies.txt file
        """
        self.proxy_file = proxy_file
        self.proxies = []
    
    def load_proxies(self) -> List[Dict]:
        """
        Load and parse proxies from file.
        
        Expected format in proxies.txt:
            host:port:username:password
            
        Example:
            72.46.139.137:6697:tnfqnyqb:bsjia1uasdxr
        
        Returns:
            List of proxy configuration dictionaries
        """
        proxies = []
        
        try:
            proxy_path = Path(self.proxy_file)
            
            if not proxy_path.exists():
                print(f"⚠️  Proxy file not found: {self.proxy_file}")
                return []
            
            with open(proxy_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                try:
                    proxy = self._parse_proxy_line(line)
                    if proxy:
                        proxies.append(proxy)
                except Exception as e:
                    print(f"⚠️  Error parsing proxy on line {line_num}: {str(e)}")
                    continue
            
            self.proxies = proxies
            return proxies
            
        except Exception as e:
            print(f"❌ Error loading proxies: {str(e)}")
            return []
    
    def _parse_proxy_line(self, line: str) -> Optional[Dict]:
        """
        Parse a single proxy line into Playwright proxy format.
        
        Args:
            line: Proxy string in format host:port:username:password
            
        Returns:
            Dictionary with proxy configuration for Playwright
        """
        parts = line.split(':')
        
        if len(parts) == 2:
            # Format: host:port (no authentication)
            host, port = parts
            return {
                'server': f'http://{host}:{port}'
            }
        
        elif len(parts) == 4:
            # Format: host:port:username:password
            host, port, username, password = parts
            return {
                'server': f'http://{host}:{port}',
                'username': username,
                'password': password
            }
        
        elif len(parts) == 3:
            # Ambiguous format - assume host:port:username (no password)
            host, port, username = parts
            return {
                'server': f'http://{host}:{port}',
                'username': username
            }
        
        else:
            print(f"⚠️  Invalid proxy format: {line}")
            return None
    
    def get_proxy_count(self) -> int:
        """
        Get the number of loaded proxies.
        
        Returns:
            Number of proxies available
        """
        return len(self.proxies)
    
    def validate_proxy(self, proxy: Dict) -> bool:
        """
        Validate a proxy configuration.
        
        Args:
            proxy: Proxy configuration dictionary
            
        Returns:
            True if proxy is valid, False otherwise
        """
        required_keys = ['server']
        
        for key in required_keys:
            if key not in proxy:
                return False
        
        # Check if server URL is properly formatted
        if not proxy['server'].startswith('http'):
            return False
        
        return True
    
    def get_proxy_info(self, proxy: Dict) -> str:
        """
        Get human-readable proxy information.
        
        Args:
            proxy: Proxy configuration dictionary
            
        Returns:
            String representation of proxy
        """
        server = proxy.get('server', 'Unknown')
        username = proxy.get('username', 'No auth')
        
        if username != 'No auth':
            return f"{server} (user: {username})"
        else:
            return server


# FUTURE EXPANSION (commented):
# - Proxy health checking:
#   Test each proxy before use with a simple HTTP request
#   Remove dead proxies from rotation
#
# - Proxy performance tracking:
#   Track success rate and response time for each proxy
#   Prioritize faster, more reliable proxies
#
# - Automatic proxy fetching:
#   Integrate with free proxy APIs to auto-populate proxies.txt
#   e.g., ProxyBroker, Free-Proxy-List APIs
#
# - Proxy rotation strategies:
#   - Round-robin (current)
#   - Random selection
#   - Weighted by performance
#   - Geographic rotation
#
# - Proxy pool management:
#   Support multiple proxy providers
#   Automatic failover between providers
