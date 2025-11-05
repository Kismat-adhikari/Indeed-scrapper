"""
Main Script for V3 Scraper (Anti-Bot Protection)
================================================
"""

import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

from scraper_v3 import IndeedScraperV3
from proxy_manager import ProxyManager

console = Console()


def generate_output_filename() -> tuple[str, str]:
    """Generate unique output filenames for both JSON and CSV."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_filename = f"results_{timestamp}.json"
    csv_filename = f"results_{timestamp}.csv"
    return (
        os.path.join("output", json_filename),
        os.path.join("output", csv_filename)
    )


def save_results(jobs, json_path: str, csv_path: str):
    """Save results to both JSON and CSV formats."""
    # Create output directory
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    
    # Save JSON file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)
    
    # Save CSV file
    if jobs:
        try:
            df = pd.DataFrame(jobs)
            # Reorder columns for better readability
            column_order = ['title', 'company', 'location', 'salary', 'salary_period', 
                          'job_type', 'posted_date', 'summary', 'url', 'scraped_from_page']
            # Only include columns that exist in the data
            existing_columns = [col for col in column_order if col in df.columns]
            df = df[existing_columns]
            
            # Save to CSV
            df.to_csv(csv_path, index=False, encoding='utf-8')
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not save CSV file: {e}[/yellow]")
            console.print("[dim]JSON file saved successfully though![/dim]")


def main():
    """Main execution."""
    try:
        console.print("\n[bold cyan]🔍 Indeed Job Scraper v3.0[/bold cyan]")
        console.print("[dim]Anti-Bot Protection Bypass Edition[/dim]\n")
        
        # Get input
        url = console.input("[yellow]Enter Indeed search URL:[/yellow] ").strip()
        while True:
            try:
                pages = int(console.input("[yellow]Enter number of pages:[/yellow] ").strip())
                if pages < 1:
                    console.print("[red]Please enter a positive number[/red]")
                    continue
                break
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")
        
        console.print(f"\n[green]🚀 Starting scraper...[/green]")
        console.print(f"[dim]URL: {url}[/dim]")
        console.print(f"[dim]Pages: {pages}[/dim]\n")
        
        # Load proxies
        proxy_file = Path(__file__).parent / "proxies.txt"
        proxy_manager = ProxyManager(str(proxy_file))
        proxies = proxy_manager.load_proxies()
        
        if proxies:
            console.print(f"[green]✓ Loaded {len(proxies)} proxies[/green]")
        
        console.print(f"[yellow]⚠️  Browser will open - DO NOT CLOSE IT![/yellow]")
        console.print(f"[yellow]   If you see CAPTCHA, solve it manually.[/yellow]\n")
        
        # Run scraper
        scraper = IndeedScraperV3(url, pages, proxies)
        jobs = scraper.scrape_all_pages()
        
        # Save results
        json_path, csv_path = generate_output_filename()
        save_results(jobs, json_path, csv_path)
        
        # Display summary
        console.print("\n")
        console.print(Panel.fit(
            f"[bold green]✅ Scraping Complete![/bold green]\n\n"
            f"[cyan]Jobs Scraped:[/cyan] {len(jobs)}\n"
            f"[cyan]Pages Scraped:[/cyan] {pages}\n"
            f"[cyan]JSON File:[/cyan] {json_path}\n"
            f"[cyan]CSV File:[/cyan] {csv_path}",
            border_style="green"
        ))
        
        # Sample jobs
        if jobs:
            console.print("\n[bold]📋 Sample of Scraped Jobs:[/bold]\n")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Title", style="cyan", width=30)
            table.add_column("Company", style="green", width=20)
            table.add_column("Location", style="yellow", width=20)
            
            for job in jobs[:5]:
                table.add_row(
                    job.get('title', 'N/A')[:30],
                    job.get('company', 'N/A')[:20],
                    job.get('location', 'N/A')[:20]
                )
            
            console.print(table)
            
            if len(jobs) > 5:
                console.print(f"\n[dim]... and {len(jobs) - 5} more jobs[/dim]")
        else:
            console.print("\n[red]❌ No jobs scraped[/red]")
            console.print("[yellow]This might be due to:[/yellow]")
            console.print("  • Cloudflare protection not bypassed")
            console.print("  • CAPTCHA not solved")
            console.print("  • Invalid search URL")
            console.print("  • Indeed changed their HTML structure")
        
    except KeyboardInterrupt:
        console.print("\n[red]❌ Scraping interrupted by user[/red]")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {str(e)}[/red]")


if __name__ == "__main__":
    main()
