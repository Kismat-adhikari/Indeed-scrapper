"""
Test script to verify Indeed scraper setup
Checks all dependencies and configurations before running the full scraper
"""

import os
import sys


def check_dependencies():
    """Check if all required packages are installed"""
    print("\n" + "="*60)
    print("Checking Dependencies...")
    print("="*60 + "\n")
    
    required_packages = [
        'requests',
        'bs4',  # beautifulsoup4
        'dotenv',  # python-dotenv
        'supabase',
        'lxml',
        'fake_useragent'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("\nInstall them with: pip install -r requirements.txt")
        return False
    else:
        print("\n✓ All dependencies installed!")
        return True


def check_env_file():
    """Check if .env file exists and has required variables"""
    print("\n" + "="*60)
    print("Checking Environment Configuration...")
    print("="*60 + "\n")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url:
        print("❌ SUPABASE_URL not found in .env")
        return False
    else:
        print(f"✓ SUPABASE_URL: {supabase_url[:30]}...")
    
    if not supabase_key:
        print("❌ SUPABASE_KEY not found in .env")
        return False
    else:
        print(f"✓ SUPABASE_KEY: {supabase_key[:30]}...")
    
    print("\n✓ Environment configuration OK!")
    return True


def check_proxies():
    """Check if proxies.txt exists and has valid format"""
    print("\n" + "="*60)
    print("Checking Proxies...")
    print("="*60 + "\n")
    
    if not os.path.exists('proxies.txt'):
        print("⚠ proxies.txt not found!")
        print("  The scraper will work without proxies, but it's not recommended.")
        return True
    
    with open('proxies.txt', 'r') as f:
        proxies = [line.strip() for line in f if line.strip()]
    
    if not proxies:
        print("⚠ proxies.txt is empty!")
        return True
    
    print(f"✓ Found {len(proxies)} proxies")
    
    # Check format of first proxy
    first_proxy = proxies[0]
    parts = first_proxy.split(':')
    if len(parts) == 4:
        print(f"✓ Proxy format looks correct: {parts[0]}:{parts[1]}:***:***")
    else:
        print(f"⚠ Proxy format might be incorrect: {first_proxy}")
        print("  Expected format: ip:port:username:password")
    
    print("\n✓ Proxies configuration OK!")
    return True


def test_supabase_connection():
    """Test connection to Supabase"""
    print("\n" + "="*60)
    print("Testing Supabase Connection...")
    print("="*60 + "\n")
    
    try:
        from dotenv import load_dotenv
        from supabase import create_client
        
        load_dotenv()
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        supabase = create_client(supabase_url, supabase_key)
        
        # Try to query the table
        response = supabase.table('indeed_jobs').select('id').limit(1).execute()
        
        print("✓ Successfully connected to Supabase!")
        print(f"✓ Table 'indeed_jobs' is accessible")
        
        # Count existing jobs
        count_response = supabase.table('indeed_jobs').select('id', count='exact').execute()
        job_count = count_response.count if hasattr(count_response, 'count') else 0
        print(f"✓ Current jobs in database: {job_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        print("\nPlease check:")
        print("  1. Your SUPABASE_URL and SUPABASE_KEY are correct")
        print("  2. The 'indeed_jobs' table exists in your database")
        print("  3. Your API key has the necessary permissions")
        return False


def test_internet_connection():
    """Test if we can reach Indeed.com"""
    print("\n" + "="*60)
    print("Testing Internet Connection...")
    print("="*60 + "\n")
    
    try:
        import requests
        response = requests.get('https://www.indeed.com', timeout=10)
        if response.status_code == 200:
            print("✓ Successfully reached Indeed.com")
            return True
        else:
            print(f"⚠ Indeed.com returned status code: {response.status_code}")
            return True
    except Exception as e:
        print(f"❌ Cannot reach Indeed.com: {e}")
        return False


def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("INDEED JOB SCRAPER - SETUP VERIFICATION")
    print("="*60)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Environment", check_env_file),
        ("Proxies", check_proxies),
        ("Supabase Connection", test_supabase_connection),
        ("Internet Connection", test_internet_connection)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error during {name} check: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60 + "\n")
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ ALL CHECKS PASSED!")
        print("="*60)
        print("\nYou're ready to run the scraper!")
        print("\nRun: python run_scraper.py")
    else:
        print("✗ SOME CHECKS FAILED")
        print("="*60)
        print("\nPlease fix the issues above before running the scraper.")
    print()
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
