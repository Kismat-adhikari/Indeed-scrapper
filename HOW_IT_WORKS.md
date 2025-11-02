# 🤔 How Does the Indeed Job Scraper Work?

## Simple Explanation (Plain English)

### What It Does
Think of this scraper as a robot that goes to Indeed.com, searches for jobs you want, copies down all the job details, and saves them for you. It's like having an assistant who spends all day browsing Indeed and writing down every job they find.

---

## Step-by-Step: What Happens When You Run It

### 1️⃣ **You Tell It What to Find**
   - You type in what jobs you want (like "python developer")
   - You type in where (like "New York" or "Remote")
   - You say how many pages to check (each page has ~10-15 jobs)

### 2️⃣ **It Goes to Indeed.com**
   - The scraper opens Indeed.com (just like you would in a browser)
   - It searches for your keywords in your locations
   - Example: It types "python developer" in the search box and "New York" in the location box

### 3️⃣ **It Pretends to Be a Real Person**
   - Uses different "disguises" (proxies and user agents) so Indeed thinks it's different people
   - Waits random amounts of time between searches (3-10 seconds) like a human would
   - This prevents getting blocked by Indeed

### 4️⃣ **It Reads the Job Listings**
   - Looks at each job card on the page
   - Copies down:
     - Job title (e.g., "Senior Python Developer")
     - Company name (e.g., "Google")
     - Location (e.g., "New York, NY")
     - Salary (if shown, e.g., "$120,000-$150,000")
     - Job description snippet
     - Link to the full job posting
     - When it was posted (e.g., "2 days ago")

### 5️⃣ **It Saves Everything**
   - **In Your Database**: Saves to Supabase (online storage)
   - **In a Text File**: Saves to a `.txt` file on your computer (NEW!)
   - Checks if it already saved this job before (no duplicates)

### 6️⃣ **It Keeps Going**
   - Moves to the next page of results
   - Repeats until it's checked all the pages you asked for
   - Then moves to the next keyword or location
   - Keeps going until it's done with all your searches

### 7️⃣ **It Tells You What It Found**
   - Shows you a summary of how many jobs it found
   - Creates a text file you can open and read
   - Everything is also in your database for later

---

## 🎯 Simple Example

**You say:**
- Find "data analyst" jobs
- In "Remote" locations
- Check 3 pages

**What happens:**
1. Scraper goes to Indeed.com
2. Searches for "data analyst" + "Remote"
3. Looks at page 1 (finds ~12 jobs) → saves them
4. Waits 5 seconds (random)
5. Looks at page 2 (finds ~11 jobs) → saves them
6. Waits 7 seconds (random)
7. Looks at page 3 (finds ~13 jobs) → saves them
8. Done! You now have ~36 jobs in your database and text file

---

## 📁 Where Does the Data Go?

### Option 1: Supabase Database (Online)
- Like a spreadsheet in the cloud
- You can search it, filter it, analyze it
- Access it from anywhere
- Use `python view_jobs.py` to see it

### Option 2: Text File (Your Computer)
- **NEW!** Now also saves to a `.txt` file
- File name: `scraped_jobs_20251102_145830.txt` (with timestamp)
- You can open it with Notepad
- Easy to read, easy to share
- Each job looks like this:

```
================================================================================
TITLE: Senior Python Developer
COMPANY: Google
LOCATION: New York, NY
SALARY: $150,000 - $180,000 a year
POSTED: 1 day ago
LINK: https://www.indeed.com/viewjob?jk=abc123
SUMMARY: We're looking for an experienced Python developer...
================================================================================
```

---

## 🛡️ How It Avoids Getting Blocked

### Problem: 
Websites don't like robots scraping them because it looks suspicious.

### Solutions:

1. **Proxies** (Different IPs)
   - Each request comes from a different "address"
   - Like calling from different phone numbers
   - You have 10 different proxies loaded

2. **Random Delays**
   - Waits 4-10 seconds between requests
   - Humans don't click instantly
   - Makes it look natural

3. **Different User Agents**
   - Pretends to be different browsers
   - Chrome, Firefox, Safari, etc.
   - Changes every request

4. **Retry Logic**
   - If something fails, tries again
   - Waits longer if site is busy
   - Doesn't give up easily

---

## 🔄 Two Ways to Run It

### Method 1: Interactive (NEW - EASIER!)
```bash
python scraper_interactive.py
```

**What happens:**
1. It asks: "What jobs do you want?"
2. You type: `python developer, data analyst`
3. It asks: "Where?"
4. You type: `New York, Remote`
5. It asks: "How many pages?"
6. You type: `3`
7. It shows a summary and asks: "Ready?"
8. You type: `yes`
9. It starts scraping!

**Benefits:**
- No need to edit config files
- Easy to change searches
- See what you're searching before it starts
- Perfect for quick searches

### Method 2: Config File (Original)
```bash
python run_scraper.py
```

**What happens:**
1. Edit `config.py` with your keywords
2. Run the script
3. It uses your saved settings
4. Good for repeated/scheduled searches

---

## 📊 What You Get

### After It Finishes:

**1. A Text File** (NEW!)
```
scraped_jobs_20251102_145830.txt
```
- Open with Notepad
- All jobs in readable format
- Easy to share or print
- Timestamped filename

**2. Database Entries**
- All jobs in Supabase
- Can search and filter
- Permanent storage
- No duplicates

**3. Log File**
```
scraper.log
```
- Technical details
- Errors and warnings
- What happened step-by-step
- For troubleshooting

---

## 💡 Think of It Like This

**Amazon vs. Your Scraper:**

When you shop on Amazon, you:
1. Search for "laptop"
2. Look through pages of results
3. Read product details
4. Maybe save some to a list

Your scraper does the same thing on Indeed:
1. Searches for jobs
2. Looks through pages of results
3. Reads job details
4. Saves them ALL to your list

The difference? It's automated and saves everything in an organized way!

---

## 🎮 Quick Start (Interactive Mode)

1. **Open terminal in your folder**
2. **Run this command:**
   ```bash
   python scraper_interactive.py
   ```
3. **Answer the questions:**
   - What jobs? → Type: `software engineer`
   - Where? → Type: `Remote`
   - How many pages? → Type: `3`
   - Ready? → Type: `yes`
4. **Wait while it works** (you'll see progress messages)
5. **Open your text file when done!**

---

## 🐛 If Something Goes Wrong

### "No jobs found"
- Maybe Indeed changed their website
- Try different keywords
- Check if your internet is working

### "Proxy errors"
- Your proxies might not be working
- Try without proxies (slower but works)
- Get fresh proxies

### "It's taking forever"
- This is normal! Each page takes ~10 seconds
- If you asked for 5 keywords × 3 locations × 5 pages = 75 pages
- That's about 12-15 minutes
- You can press `Ctrl+C` to stop it

---

## 📝 Summary

**In One Sentence:**
This scraper is a robot that goes to Indeed, searches for jobs you want, and saves all the details in a text file and database so you don't have to.

**Why It's Useful:**
- Saves hours of manual searching
- Finds jobs you might miss
- Organizes everything neatly
- Updates easily (run it daily)
- Helps you find the perfect job faster!

**Key Files:**
- `scraper_interactive.py` ← **USE THIS** (asks you what to search)
- `scraped_jobs_TIMESTAMP.txt` ← **READ THIS** (your results)
- `scraper.log` ← **CHECK THIS** (if problems)

---

## 🚀 Now Try It!

Run this command:
```bash
python scraper_interactive.py
```

Follow the prompts, and in a few minutes, you'll have a text file full of job listings! 🎉

**That's it! No complicated tech stuff, just search and get results!**
