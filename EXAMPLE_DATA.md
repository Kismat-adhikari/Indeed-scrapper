# Example Jobs Data Structure

This document shows examples of the data structure that will be stored in your Supabase database.

## Sample Job Entry

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Senior Software Engineer",
  "company": "Google",
  "location": "New York, NY",
  "salary": "$150,000 - $200,000 a year",
  "summary": "We are looking for a Senior Software Engineer to join our team. You will work on cutting-edge projects using Python, Java, and cloud technologies. Must have 5+ years of experience...",
  "link": "https://www.indeed.com/viewjob?jk=abc123def456",
  "posted_date": "Just posted",
  "scraped_at": "2024-11-02T10:30:45.123Z"
}
```

## Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | UUID | Auto-generated unique identifier | `a1b2c3d4-...` |
| `title` | TEXT | Job title/position | "Senior Software Engineer" |
| `company` | TEXT | Company name | "Google" |
| `location` | TEXT | Job location | "New York, NY" or "Remote" |
| `salary` | TEXT | Salary information (if available) | "$150,000 - $200,000 a year" |
| `summary` | TEXT | Job description/snippet | "We are looking for..." |
| `link` | TEXT | Direct link to job posting | "https://www.indeed.com/viewjob?jk=..." |
| `posted_date` | TEXT | When job was posted | "Just posted", "3 days ago" |
| `scraped_at` | TIMESTAMP | When we scraped it | "2024-11-02T10:30:45Z" |

## Example Queries

### Get all jobs from a specific company
```sql
SELECT * FROM indeed_jobs 
WHERE company ILIKE '%google%'
ORDER BY scraped_at DESC;
```

### Get jobs with salary information
```sql
SELECT * FROM indeed_jobs 
WHERE salary IS NOT NULL 
ORDER BY scraped_at DESC;
```

### Get remote jobs
```sql
SELECT * FROM indeed_jobs 
WHERE location ILIKE '%remote%'
ORDER BY scraped_at DESC;
```

### Count jobs by company
```sql
SELECT company, COUNT(*) as job_count 
FROM indeed_jobs 
GROUP BY company 
ORDER BY job_count DESC 
LIMIT 10;
```

### Get jobs posted today
```sql
SELECT * FROM indeed_jobs 
WHERE posted_date ILIKE '%just posted%' 
   OR posted_date ILIKE '%today%'
ORDER BY scraped_at DESC;
```

## Sample Dataset (3 jobs)

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Python Developer",
    "company": "Microsoft",
    "location": "Seattle, WA",
    "salary": "$120,000 - $160,000 a year",
    "summary": "Join our Azure team as a Python Developer. Work with cutting-edge cloud technologies and AI/ML projects. Requirements: 3+ years Python experience, knowledge of Django/Flask...",
    "link": "https://www.indeed.com/viewjob?jk=xyz789abc123",
    "posted_date": "2 days ago",
    "scraped_at": "2024-11-02T10:35:21.456Z"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Data Analyst - Remote",
    "company": "Amazon",
    "location": "Remote",
    "salary": null,
    "summary": "We're seeking a Data Analyst to join our analytics team. You'll work with large datasets, create dashboards, and provide insights to drive business decisions...",
    "link": "https://www.indeed.com/viewjob?jk=def456ghi789",
    "posted_date": "Just posted",
    "scraped_at": "2024-11-02T10:36:42.789Z"
  },
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "title": "DevOps Engineer",
    "company": "Apple",
    "location": "Cupertino, CA",
    "salary": "$140,000 - $180,000 a year",
    "summary": "Looking for an experienced DevOps Engineer to manage our CI/CD pipelines and cloud infrastructure. Strong knowledge of Kubernetes, Docker, and AWS required...",
    "link": "https://www.indeed.com/viewjob?jk=jkl012mno345",
    "posted_date": "1 day ago",
    "scraped_at": "2024-11-02T10:38:15.012Z"
  }
]
```

## Data Quality Notes

### Fields That May Be Null
- `salary`: Many job postings don't include salary information
- `summary`: Rare, but some jobs may not have a description snippet
- `posted_date`: Usually present, but format varies

### Common Salary Formats
- "$100,000 - $150,000 a year"
- "$50 - $70 an hour"
- "From $80,000 a year"
- "$5,000 - $8,000 a month"
- Not listed (null)

### Common Posted Date Formats
- "Just posted"
- "Today"
- "1 day ago"
- "2 days ago"
- "3 weeks ago"
- "30+ days ago"

### Location Formats
- "City, State" (e.g., "New York, NY")
- "Remote"
- "Remote in State" (e.g., "Remote in California")
- "Hybrid remote in City"
- Multiple locations

## Using the Data

### In Python (via Supabase client)
```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Get all remote jobs
response = supabase.table('indeed_jobs')\
    .select('*')\
    .ilike('location', '%remote%')\
    .execute()

for job in response.data:
    print(f"{job['title']} at {job['company']}")
```

### Export to CSV
```python
import csv
from supabase import create_client

# ... connect to supabase ...

response = supabase.table('indeed_jobs').select('*').execute()

with open('jobs.csv', 'w', newline='', encoding='utf-8') as f:
    if response.data:
        writer = csv.DictWriter(f, fieldnames=response.data[0].keys())
        writer.writeheader()
        writer.writerows(response.data)
```

### Export to Excel
```python
import pandas as pd
from supabase import create_client

# ... connect to supabase ...

response = supabase.table('indeed_jobs').select('*').execute()
df = pd.DataFrame(response.data)
df.to_excel('jobs.xlsx', index=False)
```

## Data Analysis Ideas

1. **Salary Analysis**: Average salaries by role, location, company
2. **Posting Trends**: Track how quickly new jobs appear
3. **Location Insights**: Remote vs on-site distribution
4. **Company Analysis**: Which companies post most frequently
5. **Keyword Trends**: Popular skills mentioned in descriptions
6. **Market Research**: Job availability by region/role

---

**Your scraper will automatically populate this data structure!** 🎉
