"""
Indeed Job Scraper - Main Entry Point
=====================================
CLI application to scrape Indeed job listings locally.
No API keys required. Uses Playwright for dynamic scraping.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

from scraper import IndeedScraper
from proxy_manager import ProxyManager

console = Console()


def get_user_input() -> tuple[str, int]:
    """
    Prompt user for Indeed URL and number of pages to scrape.
    
    Returns:
        tuple: (indeed_url, page_count)
    """
    console.print("\n[bold cyan]🔍 Indeed Job Scraper[/bold cyan]", style="bold")
    console.print("[dim]Scrape job listings from Indeed.com locally[/dim]\n")
    
    # Get Indeed URL
    url = console.input("[yellow]Enter Indeed search URL:[/yellow] ").strip()
    
    # Validate URL
    if not url.startswith("https://www.indeed.com"):
        console.print("[red]⚠️  Warning: URL should start with https://www.indeed.com[/red]")
    
    # Get number of pages
    while True:
        try:
            pages = int(console.input("[yellow]Enter number of pages to scrape:[/yellow] ").strip())
            if pages < 1:
                console.print("[red]Please enter a positive number[/red]")
                continue
            break
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
    
    return url, pages


def generate_output_filename() -> str:
    """
    Generate a unique output filename with timestamp.
    
    Returns:
        Path to output JSON file with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results_{timestamp}.json"
    return os.path.join("output", filename)


def save_results(jobs: List[Dict], output_path: str) -> None:
    """
    Save scraped job data to JSON file.
    
    Args:
        jobs: List of job dictionaries
        output_path: Path to output JSON file
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to JSON with pretty printing
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)


def display_summary(jobs: List[Dict], pages_scraped: int, output_path: str) -> None:
    """
    Display a summary of the scraping results.
    
    Args:
        jobs: List of scraped jobs
        pages_scraped: Number of pages scraped
        output_path: Path where results were saved
    """
    console.print("\n")
    console.print(Panel.fit(
        f"[bold green]✅ Scraping Complete![/bold green]\n\n"
        f"[cyan]Jobs Scraped:[/cyan] {len(jobs)}\n"
        f"[cyan]Pages Scraped:[/cyan] {pages_scraped}\n"
        f"[cyan]Output File:[/cyan] {output_path}",
        border_style="green"
    ))
    
    # Display sample of scraped jobs
    if jobs:
        console.print("\n[bold]📋 Sample of Scraped Jobs:[/bold]\n")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Title", style="cyan", width=30)
        table.add_column("Company", style="green", width=20)
        table.add_column("Location", style="yellow", width=20)
        
        # Show first 5 jobs
        for job in jobs[:5]:
            table.add_row(
                job.get('title', 'N/A')[:30],
                job.get('company', 'N/A')[:20],
                job.get('location', 'N/A')[:20]
            )
        
        console.print(table)
        
        if len(jobs) > 5:
            console.print(f"\n[dim]... and {len(jobs) - 5} more jobs[/dim]")


async def main():
    """
    Main execution flow.
    """
    try:
        # Get user input
        url, page_count = get_user_input()
        
        console.print(f"\n[green]🚀 Starting scraper...[/green]")
        console.print(f"[dim]URL: {url}[/dim]")
        console.print(f"[dim]Pages: {page_count}[/dim]\n")
        
        # Load proxies
        proxy_file = Path(__file__).parent / "proxies.txt"
        proxy_manager = ProxyManager(str(proxy_file))
        proxies = proxy_manager.load_proxies()
        
        if not proxies:
            console.print("[yellow]⚠️  No proxies loaded. Proceeding without proxy rotation.[/yellow]")
        else:
            console.print(f"[green]✓ Loaded {len(proxies)} proxies[/green]\n")
        
        # Initialize scraper
        scraper = IndeedScraper(url, page_count, proxies)
        
        # Run scraping with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Scraping jobs...", total=None)
            jobs = await scraper.scrape_all_pages()
            progress.update(task, completed=True)
        
        # Save results to unique filename
        output_path = generate_output_filename()
        save_results(jobs, output_path)
        
        # Display summary
        display_summary(jobs, page_count, output_path)
        
    except KeyboardInterrupt:
        console.print("\n[red]❌ Scraping interrupted by user[/red]")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {str(e)}[/red]")
        console.print("[dim]Check your URL and try again.[/dim]")


if __name__ == "__main__":
    asyncio.run(main())


# FUTURE EXPANSION IDEAS (commented placeholders):
# - Add CLI flags for automation: argparse for --url, --pages, --output
# - AI-based selector repair: detect when Indeed changes HTML structure
# - Database integration: save to Supabase/MongoDB instead of JSON
# - Email notifications: send results when scraping completes
# - Scheduler: run scraper periodically with schedule library
# - Filter options: by salary range, date posted, job type
# - Export formats: CSV, Excel in addition to JSON
