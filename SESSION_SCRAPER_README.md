# Session-Based Proxy Scraper with Automatic Authentication

## Overview
A sophisticated web scraping system that automatically handles proxy authentication, rotates proxies per session (not per request), and simulates human-like browsing behavior to avoid detection and CAPTCHAs.

## Key Features

### 🔐 Automatic Proxy Authentication
- **No Manual Login**: Automatically handles proxies with username/password without browser popups
- **Multiple Formats**: Supports both `host:port` and `host:port:username:password` formats
- **Chrome Extension**: Creates temporary Chrome extensions for seamless authentication
- **Smart Detection**: Automatically detects which proxies need authentication

### 🔄 Session-Based Proxy Rotation
- **Session Lifecycle**: Each session lasts 5-10 pages before rotating to a new proxy
- **Health Tracking**: Monitors proxy performance and removes failing proxies
- **Intelligent Selection**: Chooses healthiest proxies using weighted random selection
- **CAPTCHA Handling**: Automatically blacklists proxies that trigger CAPTCHAs

### 🤖 Human-Like Behavior Simulation
- **Realistic Browsing**: Varied scrolling patterns, reading speeds, and mouse movements
- **Session Breaks**: Natural delays between pages within sessions
- **Multiple Patterns**: Quick scanning, detailed reading, selective browsing, comparison browsing
- **Attention Simulation**: Random distractions and multitasking behaviors

### 📊 Health Monitoring
- **Proxy Scoring**: 5-level health system (Excellent → Blacklisted)
- **Success Tracking**: Monitors success rates, response times, CAPTCHA counts
- **Automatic Cooldowns**: Temporarily removes problematic proxies
- **Persistent Stats**: Saves proxy performance data between runs

## File Structure

```
Indeed-scrapper/
├── proxy_auth_manager.py      # Automatic proxy authentication
├── session_manager.py         # Session lifecycle and health tracking  
├── human_behavior.py          # Human-like browsing simulation
├── chrome_driver_manager.py   # Chrome version detection & driver setup
├── scraper_v3.py             # Main scraper with session integration
├── main_v3.py                # CLI interface
├── proxies.txt               # Proxy list (auto-parsed)
└── proxy_stats.json          # Persistent proxy health data
```

## Proxy Format

### Supported Formats
```
# No authentication
192.168.1.1:8080

# With authentication  
proxy.example.com:8080:username:password
```

### Your Current Format (All Authenticated)
```
72.46.139.137:6697:tnfqnyqb:bsjia1uasdxr
45.196.40.119:6197:tnfqnyqb:bsjia1uasdxr
156.238.179.127:6695:tnfqnyqb:bsjia1uasdxr
...
```

## Usage

### Basic Usage
```python
from scraper_v3 import IndeedScraperV3

# Create scraper (automatically loads proxies.txt)
scraper = IndeedScraperV3(
    "https://www.indeed.com/jobs?q=python+developer&l=Minnesota", 
    pages=15
)

# Run with automatic proxy rotation and authentication
jobs = scraper.scrape_all_pages()
```

### Direct Proxy Testing
```python
from proxy_auth_manager import ProxyAuthManager

# Test proxy authentication
manager = ProxyAuthManager("proxies.txt")
driver = manager.create_driver_with_proxy()

# Test navigation
driver.get("https://httpbin.org/ip")
```

### CLI Usage
```bash
python main_v3.py
# Enter URL and page count when prompted
```

## How It Works

### 1. Session Initialization
```
1. Load proxies from proxies.txt
2. Parse authentication requirements  
3. Select healthiest proxy using weighted selection
4. Create Chrome extension for authentication (if needed)
5. Initialize driver with proxy + extension
6. Start human behavior simulator
```

### 2. Session Lifecycle
```
1. Session handles 5-10 pages (random)
2. Each page: human arrival → browse jobs → record results
3. Inter-page delays with realistic human breaks
4. Monitor for CAPTCHAs and failures
5. End session and update proxy health scores
```

### 3. Proxy Rotation
```
1. Check if current session can handle more pages
2. If not, end session and clean up driver
3. Select new healthy proxy (weighted by performance)
4. Create new session with fresh authentication
5. Continue scraping with new proxy/session
```

### 4. Health Management
```
┌─────────────┬─────────────────┬──────────────────┐
│ Health      │ Success Rate    │ Action           │
├─────────────┼─────────────────┼──────────────────┤
│ Excellent   │ 90%+           │ Preferred choice │
│ Good        │ 75-90%         │ Regular use      │
│ Fair        │ 50-75%         │ Limited use      │
│ Poor        │ 30-50%         │ Backup only      │
│ Blacklisted │ <30% or CAPTCHA│ Never use        │
└─────────────┴─────────────────┴──────────────────┘
```

## Anti-Detection Features

### Browser-Level
- Undetected ChromeDriver with automatic version detection
- Custom user agents per session
- Disabled automation flags
- Random window sizes and positions

### Behavioral
- Realistic human reading speeds (150-400 WPM)
- Varied scrolling patterns per session
- Mouse movements during reading
- Random navigation mistakes (back/forward)
- Attention span simulation with distractions

### Proxy-Level
- Session-based rotation (not per-request)
- Automatic authentication without popups
- Health-based selection prioritizing working proxies
- CAPTCHA avoidance through proxy blacklisting

## Configuration

### Proxy Settings
- **Session Length**: 5-10 pages per session (randomized)
- **Health Threshold**: Minimum 30% success rate
- **CAPTCHA Limit**: 3 CAPTCHAs = permanent blacklist
- **Cooldown**: 2 hours for CAPTCHA-triggered proxies

### Human Behavior
- **Reading Speed**: 150-400 words per minute (randomized per session)
- **Scroll Patterns**: Gradual, quick, or mixed (chosen per session)
- **Session Breaks**: 2-8 seconds between pages
- **Attention Span**: 30-120 seconds before "distraction"

### Browser
- **Chrome Version**: Auto-detected with fallback strategies
- **Extensions**: Temporary proxy auth extensions (auto-cleanup)
- **User Agents**: Realistic Chrome user agents
- **Viewport**: 1920x1080 standard

## Troubleshooting

### Common Issues

**"No healthy proxies available"**
- Check proxies.txt format
- Verify proxy credentials
- Wait for cooldown periods to expire

**"CAPTCHA detected"**
- Normal behavior - proxy will be temporarily blacklisted
- System will rotate to next healthy proxy automatically

**"Chrome driver failed"**
- Chrome version auto-detection will find compatible driver
- Fallback to webdriver-manager if needed

### Monitoring

**Check proxy health:**
```python
manager = SessionManager()
status = manager.get_proxy_pool_status()
print(status)
```

**View session history:**
```python
for session in manager.session_history:
    print(session)
```

## Performance

### Expected Metrics
- **Session Success Rate**: 70-90% (healthy proxy pool)
- **Pages per Session**: 5-10 pages average
- **CAPTCHA Rate**: <5% with proper rotation
- **Speed**: 30-60 seconds per page (including human simulation)

### Scaling
- **Proxy Pool**: Recommended 20+ proxies for continuous operation
- **Session Overlap**: Handles multiple concurrent sessions
- **Memory**: Auto-cleanup of old session data and extensions

## Security & Ethics

### Best Practices
- Respect robots.txt and rate limits
- Use residential/mobile proxies when possible
- Monitor for IP blocks and adjust behavior
- Keep session duration realistic (not too fast)

### Legal Considerations
- Educational and research purposes only
- Comply with website terms of service
- Don't overload target servers
- Use proper attribution when required

## Maintenance

### Regular Tasks
- **Proxy Refresh**: Update proxies.txt with fresh proxies
- **Health Review**: Check proxy_stats.json for blacklisted proxies
- **Performance Tuning**: Adjust session lengths based on success rates

### Updates
- Chrome browser updates handled automatically
- Proxy authentication system adapts to Chrome changes
- Human behavior patterns can be extended/customized