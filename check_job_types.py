#!/usr/bin/env python3
"""Check why some jobs have job_type and others don't."""

import re
import json

# Load debug HTML
with open('output/debug_v3_page_1.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract JSON
pattern = r'window\.mosaic\.providerData\["mosaic-provider-jobcards"\]\s*=\s*({.*?});'
match = re.search(pattern, html, re.DOTALL)
data = json.loads(match.group(1))
jobs = data['metaData']['mosaicProviderJobCardsModel']['results']

print("=" * 70)
print("ANALYZING JOB_TYPE EXTRACTION")
print("=" * 70)

for i, job in enumerate(jobs[:5]):
    print(f"\n--- Job {i+1}: {job.get('title', 'No title')[:50]} ---")
    print(f"jobTypes field: {job.get('jobTypes')}")
    print(f"taxonomyAttributes: {job.get('taxonomyAttributes', [])[:2]}")
    
    # Check for job type in attributes
    attrs = job.get('attributes', [])
    if attrs:
        print(f"attributes: {attrs[:2]}")
    
    # Check extractedSalary
    if 'extractedSalary' in job:
        print(f"extractedSalary.type: {job['extractedSalary'].get('type')}")
