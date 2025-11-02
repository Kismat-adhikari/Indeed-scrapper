"""
View and analyze scraped jobs from Supabase database
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime
import json


def view_recent_jobs(limit=10):
    """Display the most recently scraped jobs"""
    load_dotenv()
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    print("\n" + "="*80)
    print(f"MOST RECENT {limit} JOBS")
    print("="*80 + "\n")
    
    response = supabase.table('indeed_jobs')\
        .select('*')\
        .order('scraped_at', desc=True)\
        .limit(limit)\
        .execute()
    
    if not response.data:
        print("No jobs found in database.")
        return
    
    for i, job in enumerate(response.data, 1):
        print(f"{i}. {job.get('title', 'N/A')}")
        print(f"   Company: {job.get('company', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   Salary: {job.get('salary', 'N/A')}")
        print(f"   Posted: {job.get('posted_date', 'N/A')}")
        print(f"   Link: {job.get('link', 'N/A')}")
        print(f"   Scraped: {job.get('scraped_at', 'N/A')}")
        print()


def get_statistics():
    """Display statistics about scraped jobs"""
    load_dotenv()
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    print("\n" + "="*80)
    print("DATABASE STATISTICS")
    print("="*80 + "\n")
    
    # Total jobs
    response = supabase.table('indeed_jobs').select('id', count='exact').execute()
    total = response.count if hasattr(response, 'count') else len(response.data)
    print(f"Total Jobs: {total}")
    
    # Jobs with salary
    response = supabase.table('indeed_jobs')\
        .select('id')\
        .not_.is_('salary', 'null')\
        .execute()
    with_salary = len(response.data)
    print(f"Jobs with Salary Info: {with_salary}")
    
    # Top companies
    response = supabase.table('indeed_jobs')\
        .select('company')\
        .limit(1000)\
        .execute()
    
    companies = {}
    for job in response.data:
        company = job.get('company')
        if company:
            companies[company] = companies.get(company, 0) + 1
    
    print(f"\nTop 10 Companies:")
    sorted_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10]
    for company, count in sorted_companies:
        print(f"  {company}: {count} jobs")
    
    # Top locations
    response = supabase.table('indeed_jobs')\
        .select('location')\
        .limit(1000)\
        .execute()
    
    locations = {}
    for job in response.data:
        location = job.get('location')
        if location:
            locations[location] = locations.get(location, 0) + 1
    
    print(f"\nTop 10 Locations:")
    sorted_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:10]
    for location, count in sorted_locations:
        print(f"  {location}: {count} jobs")
    
    print()


def search_jobs(keyword, limit=20):
    """Search jobs by keyword in title or company"""
    load_dotenv()
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    print("\n" + "="*80)
    print(f"SEARCH RESULTS FOR: '{keyword}'")
    print("="*80 + "\n")
    
    # Search in title
    response = supabase.table('indeed_jobs')\
        .select('*')\
        .ilike('title', f'%{keyword}%')\
        .order('scraped_at', desc=True)\
        .limit(limit)\
        .execute()
    
    if not response.data:
        print(f"No jobs found matching '{keyword}'")
        return
    
    print(f"Found {len(response.data)} jobs:\n")
    
    for i, job in enumerate(response.data, 1):
        print(f"{i}. {job.get('title', 'N/A')}")
        print(f"   Company: {job.get('company', 'N/A')}")
        print(f"   Location: {job.get('location', 'N/A')}")
        print(f"   Salary: {job.get('salary', 'N/A')}")
        print(f"   Link: {job.get('link', 'N/A')}")
        print()


def export_to_json(filename='jobs_export.json'):
    """Export all jobs to JSON file"""
    load_dotenv()
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    print("\n" + "="*80)
    print(f"EXPORTING JOBS TO: {filename}")
    print("="*80 + "\n")
    
    response = supabase.table('indeed_jobs')\
        .select('*')\
        .order('scraped_at', desc=True)\
        .execute()
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(response.data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Exported {len(response.data)} jobs to {filename}")
    print()


def delete_old_jobs(days=30):
    """Delete jobs older than specified days (use with caution!)"""
    load_dotenv()
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    
    from datetime import datetime, timedelta
    cutoff_date = datetime.now() - timedelta(days=days)
    
    print("\n" + "="*80)
    print(f"WARNING: This will delete jobs older than {days} days")
    print("="*80 + "\n")
    
    confirm = input(f"Are you sure? Type 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    # Note: This requires timestamp comparison, adjust as needed
    print("Deletion feature requires manual implementation based on your needs.")
    print("Use Supabase dashboard for safe deletion.")


def main():
    """Main menu"""
    while True:
        print("\n" + "="*80)
        print("INDEED JOBS DATABASE VIEWER")
        print("="*80)
        print("\n1. View Recent Jobs")
        print("2. View Statistics")
        print("3. Search Jobs")
        print("4. Export to JSON")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            limit = input("How many jobs to show? (default: 10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            view_recent_jobs(limit)
            
        elif choice == '2':
            get_statistics()
            
        elif choice == '3':
            keyword = input("Enter search keyword: ").strip()
            if keyword:
                limit = input("Max results? (default: 20): ").strip()
                limit = int(limit) if limit.isdigit() else 20
                search_jobs(keyword, limit)
            
        elif choice == '4':
            filename = input("Filename (default: jobs_export.json): ").strip()
            filename = filename if filename else 'jobs_export.json'
            export_to_json(filename)
            
        elif choice == '5':
            print("\nGoodbye!")
            break
            
        else:
            print("\nInvalid option. Please try again.")


if __name__ == "__main__":
    main()
