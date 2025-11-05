"""
Session-Based Proxy Management System
====================================
Manages proxy sessions with health tracking, rotation, and anti-detection features.
"""

import time
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading
from proxy_auth_manager import ProxyAuthManager


class ProxyHealth(Enum):
    """Proxy health status levels."""
    EXCELLENT = 5    # No failures, fast response
    GOOD = 4        # Minor issues, acceptable performance  
    FAIR = 3        # Some failures, slower response
    POOR = 2        # Many failures, very slow
    BLACKLISTED = 1 # Permanently banned/unusable


@dataclass
class ProxyStats:
    """Statistics and health tracking for a proxy."""
    success_count: int = 0
    failure_count: int = 0
    captcha_count: int = 0
    avg_response_time: float = 0.0
    last_used: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    health_score: ProxyHealth = ProxyHealth.EXCELLENT
    total_sessions: int = 0
    successful_sessions: int = 0
    cooldown_until: Optional[datetime] = None
    
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        total = self.success_count + self.failure_count
        return (self.success_count / total * 100) if total > 0 else 100.0
    
    def session_success_rate(self) -> float:
        """Calculate session success rate percentage."""
        return (self.successful_sessions / self.total_sessions * 100) if self.total_sessions > 0 else 100.0
    
    def is_healthy(self) -> bool:
        """Check if proxy is healthy enough to use."""
        if self.health_score == ProxyHealth.BLACKLISTED:
            return False
        if self.cooldown_until and datetime.now() < self.cooldown_until:
            return False
        if self.consecutive_failures >= 5:
            return False
        return self.success_rate() >= 30.0  # Minimum 30% success rate


@dataclass 
class ProxySession:
    """Represents a single proxy session with lifecycle management."""
    proxy: Dict
    stats: ProxyStats
    session_id: str
    pages_scraped: int = 0
    max_pages: int = 8  # Default 8 pages per session
    start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    user_agent: str = ""
    session_cookies: Dict = field(default_factory=dict)
    is_active: bool = True
    captcha_triggered: bool = False
    
    def __post_init__(self):
        """Initialize session with random parameters."""
        if not self.user_agent:
            self.user_agent = self._generate_random_user_agent()
        self.max_pages = random.randint(5, 10)  # Random session length
    
    def _generate_random_user_agent(self) -> str:
        """Generate realistic user agent for this session."""
        chrome_versions = ["119.0.0.0", "120.0.0.0", "121.0.0.0", "122.0.0.0"]
        windows_versions = ["Windows NT 10.0; Win64; x64", "Windows NT 11.0; Win64; x64"]
        
        chrome_ver = random.choice(chrome_versions)
        windows_ver = random.choice(windows_versions)
        
        return f"Mozilla/5.0 ({windows_ver}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36"
    
    def can_scrape_more(self) -> bool:
        """Check if session can handle more pages."""
        if not self.is_active or self.captcha_triggered:
            return False
        if self.pages_scraped >= self.max_pages:
            return False
        
        # Check session age (max 30 minutes per session)
        session_age = datetime.now() - self.start_time
        if session_age > timedelta(minutes=30):
            return False
            
        return True
    
    def record_page_success(self):
        """Record successful page scrape."""
        self.pages_scraped += 1
        self.last_activity = datetime.now()
        self.stats.success_count += 1
        
        # Reset consecutive failures on success
        if self.stats.consecutive_failures > 0:
            self.stats.consecutive_failures = 0
    
    def record_page_failure(self, is_captcha: bool = False):
        """Record failed page scrape."""
        self.last_activity = datetime.now()
        self.stats.failure_count += 1
        self.stats.consecutive_failures += 1
        self.stats.last_failure = datetime.now()
        
        if is_captcha:
            self.stats.captcha_count += 1
            self.captcha_triggered = True
            self.is_active = False
            
            # Apply cooldown for CAPTCHA
            self.stats.cooldown_until = datetime.now() + timedelta(hours=2)
    
    def end_session(self, successful: bool = True):
        """End the proxy session and update stats."""
        self.is_active = False
        self.stats.total_sessions += 1
        self.stats.last_used = datetime.now()
        
        if successful and not self.captcha_triggered:
            self.stats.successful_sessions += 1
        
        # Update health score based on session performance
        self._update_health_score()
    
    def _update_health_score(self):
        """Update proxy health score based on performance."""
        success_rate = self.stats.success_rate()
        session_rate = self.stats.session_success_rate()
        
        # Blacklist if too many CAPTCHAs or failures
        if self.stats.captcha_count >= 3 or self.stats.consecutive_failures >= 10:
            self.stats.health_score = ProxyHealth.BLACKLISTED
            return
        
        # Score based on combined metrics
        combined_rate = (success_rate + session_rate) / 2
        
        if combined_rate >= 90:
            self.stats.health_score = ProxyHealth.EXCELLENT
        elif combined_rate >= 75:
            self.stats.health_score = ProxyHealth.GOOD
        elif combined_rate >= 50:
            self.stats.health_score = ProxyHealth.FAIR
        elif combined_rate >= 30:
            self.stats.health_score = ProxyHealth.POOR
        else:
            self.stats.health_score = ProxyHealth.BLACKLISTED
    
    def get_session_info(self) -> Dict:
        """Get session information for logging."""
        return {
            "session_id": self.session_id,
            "proxy_server": self.proxy.get('server', 'unknown'),
            "pages_scraped": self.pages_scraped,
            "max_pages": self.max_pages,
            "session_age_minutes": (datetime.now() - self.start_time).total_seconds() / 60,
            "health_score": self.stats.health_score.name,
            "success_rate": self.stats.success_rate(),
            "is_active": self.is_active,
            "captcha_triggered": self.captcha_triggered
        }


class SessionManager:
    """Manages multiple proxy sessions with intelligent rotation."""
    
    def __init__(self, proxy_file: str = "proxies.txt"):
        self.proxy_auth_manager = ProxyAuthManager(proxy_file)
        self.proxies = self.proxy_auth_manager.proxies
        self.proxy_stats: Dict[str, ProxyStats] = {}
        self.current_session: Optional[ProxySession] = None
        self.session_history: List[Dict] = []
        self.lock = threading.Lock()
        
        # Initialize proxy statistics
        for proxy in self.proxies:
            proxy_key = self._get_proxy_key(proxy)
            self.proxy_stats[proxy_key] = ProxyStats()
    
    def _get_proxy_key(self, proxy: Dict) -> str:
        """Generate unique key for proxy."""
        return proxy.get('server', 'unknown')
    
    def get_healthy_proxies(self) -> List[Dict]:
        """Get list of healthy proxies available for use."""
        healthy = []
        
        for proxy in self.proxies:
            proxy_key = self._get_proxy_key(proxy)
            stats = self.proxy_stats.get(proxy_key)
            
            if stats and stats.is_healthy():
                healthy.append(proxy)
        
        # Sort by health score and success rate
        healthy.sort(key=lambda p: (
            self.proxy_stats[self._get_proxy_key(p)].health_score.value,
            self.proxy_stats[self._get_proxy_key(p)].success_rate()
        ), reverse=True)
        
        return healthy
    
    def start_new_session(self) -> Optional[ProxySession]:
        """Start a new proxy session with best available proxy."""
        with self.lock:
            # End current session if active
            if self.current_session and self.current_session.is_active:
                self.current_session.end_session(successful=True)
                self._log_session_end()
            
            # Get healthy proxies
            healthy_proxies = self.get_healthy_proxies()
            
            if not healthy_proxies:
                print("⚠️  No healthy proxies available!")
                return None
            
            # Select proxy (weighted random based on health)
            selected_proxy = self._select_weighted_proxy(healthy_proxies)
            proxy_key = self._get_proxy_key(selected_proxy)
            
            # Create new session
            session_id = f"session_{int(time.time())}_{random.randint(1000, 9999)}"
            self.current_session = ProxySession(
                proxy=selected_proxy,
                stats=self.proxy_stats[proxy_key],
                session_id=session_id
            )
            
            print(f"🔄 Started new session: {session_id}")
            print(f"   Proxy: {selected_proxy.get('server', 'unknown')}")
            print(f"   Health: {self.proxy_stats[proxy_key].health_score.name}")
            print(f"   Max pages: {self.current_session.max_pages}")
            
            return self.current_session
    
    def _select_weighted_proxy(self, proxies: List[Dict]) -> Dict:
        """Select proxy using weighted random based on health scores."""
        if len(proxies) == 1:
            return proxies[0]
        
        # Calculate weights based on health scores
        weights = []
        for proxy in proxies:
            proxy_key = self._get_proxy_key(proxy)
            stats = self.proxy_stats[proxy_key]
            weight = stats.health_score.value * (1 + stats.success_rate() / 100)
            weights.append(weight)
        
        # Weighted random selection
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(proxies)
        
        rand_val = random.uniform(0, total_weight)
        current_weight = 0
        
        for i, weight in enumerate(weights):
            current_weight += weight
            if rand_val <= current_weight:
                return proxies[i]
        
        return proxies[-1]  # Fallback
    
    def record_success(self):
        """Record successful page scrape for current session."""
        if self.current_session:
            self.current_session.record_page_success()
    
    def record_failure(self, is_captcha: bool = False):
        """Record failed page scrape for current session."""
        if self.current_session:
            self.current_session.record_page_failure(is_captcha)
            
            if is_captcha:
                print(f"🛡️  CAPTCHA detected! Ending session {self.current_session.session_id}")
                self._log_session_end()
    
    def should_rotate_session(self) -> bool:
        """Check if current session should be rotated."""
        if not self.current_session:
            return True
        
        return not self.current_session.can_scrape_more()
    
    def get_current_session(self) -> Optional[ProxySession]:
        """Get current active session."""
        return self.current_session
    
    def _log_session_end(self):
        """Log session end information."""
        if self.current_session:
            info = self.current_session.get_session_info()
            self.session_history.append(info)
            
            print(f"📊 Session ended: {info['session_id']}")
            print(f"   Pages scraped: {info['pages_scraped']}/{info['max_pages']}")
            print(f"   Success rate: {info['success_rate']:.1f}%")
            print(f"   Health: {info['health_score']}")
    
    def get_proxy_pool_status(self) -> Dict:
        """Get status of entire proxy pool."""
        healthy = self.get_healthy_proxies()
        
        health_distribution = {health.name: 0 for health in ProxyHealth}
        for stats in self.proxy_stats.values():
            health_distribution[stats.health_score.name] += 1
        
        return {
            "total_proxies": len(self.proxies),
            "healthy_proxies": len(healthy),
            "health_distribution": health_distribution,
            "sessions_completed": len(self.session_history),
            "current_session_active": self.current_session is not None and self.current_session.is_active
        }
    
    def cleanup_old_sessions(self):
        """Clean up old session data to prevent memory leaks."""
        # Keep only last 100 session records
        if len(self.session_history) > 100:
            self.session_history = self.session_history[-100:]
    
    def save_proxy_stats(self, filepath: str):
        """Save proxy statistics to file for persistence."""
        data = {}
        for proxy_key, stats in self.proxy_stats.items():
            data[proxy_key] = {
                "success_count": stats.success_count,
                "failure_count": stats.failure_count,
                "captcha_count": stats.captcha_count,
                "health_score": stats.health_score.name,
                "total_sessions": stats.total_sessions,
                "successful_sessions": stats.successful_sessions,
                "last_used": stats.last_used.isoformat() if stats.last_used else None,
                "cooldown_until": stats.cooldown_until.isoformat() if stats.cooldown_until else None
            }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_proxy_stats(self, filepath: str):
        """Load proxy statistics from file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            for proxy_key, stats_data in data.items():
                if proxy_key in self.proxy_stats:
                    stats = self.proxy_stats[proxy_key]
                    stats.success_count = stats_data.get("success_count", 0)
                    stats.failure_count = stats_data.get("failure_count", 0)
                    stats.captcha_count = stats_data.get("captcha_count", 0)
                    stats.total_sessions = stats_data.get("total_sessions", 0)
                    stats.successful_sessions = stats_data.get("successful_sessions", 0)
                    
                    # Parse health score
                    health_name = stats_data.get("health_score", "EXCELLENT")
                    stats.health_score = ProxyHealth[health_name]
                    
                    # Parse dates
                    if stats_data.get("last_used"):
                        stats.last_used = datetime.fromisoformat(stats_data["last_used"])
                    if stats_data.get("cooldown_until"):
                        stats.cooldown_until = datetime.fromisoformat(stats_data["cooldown_until"])
                        
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"⚠️  Could not load proxy stats: {e}")