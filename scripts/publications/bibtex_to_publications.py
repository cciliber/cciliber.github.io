#!/usr/bin/env python3
"""
Convert BibTeX file to Jekyll publication markdown files with link validation.
This is the source of truth - edit files/publications.bib and run this script.

Features:
- Validates external URLs (checks if reachable)
- Supports local PDF files in files/papers/
- Generates validation report for publication links
- Maintains BibTeX as single source of truth
"""

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from pathlib import Path
import re
import shutil
import urllib.request
import urllib.error
from typing import Dict, List, Tuple, Optional
import socket

# Configuration
TIMEOUT = 5  # seconds for URL validation
VALIDATE_URLS = True  # Set to False to skip URL validation
FILES_DIR = Path('files')
PAPERS_DIR = FILES_DIR / 'papers'

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def format_author_list(authors):
    """Format author list for citation."""
    if not authors:
        return ""

    # Split authors by 'and'
    author_list = [a.strip() for a in authors.split(' and ')]

    if len(author_list) == 1:
        return author_list[0]
    elif len(author_list) == 2:
        return f"{author_list[0]} and {author_list[1]}"
    else:
        # Multiple authors: list all with commas and 'and' before last
        return ", ".join(author_list[:-1]) + f", and {author_list[-1]}"

def get_venue_from_entry(entry):
    """Extract venue from BibTeX entry."""
    if 'booktitle' in entry:
        return entry['booktitle']
    elif 'journal' in entry:
        return entry['journal']
    elif 'howpublished' in entry:
        return entry['howpublished']
    elif 'publisher' in entry:
        return entry['publisher']
    else:
        return "Preprint"

def create_citation(entry):
    """Create formatted citation from BibTeX entry."""
    authors = format_author_list(entry.get('author', ''))
    title = entry.get('title', '')
    year = entry.get('year', '')
    venue = get_venue_from_entry(entry)

    # Format: Authors. "Title". Venue, Year.
    citation = f'{authors}. "{title}"'
    if venue and venue != "Preprint":
        citation += f'. {venue}'
    if year:
        citation += f', {year}'
    citation += '.'

    return citation

def sanitize_filename(s):
    """Create a safe filename from string."""
    # Remove special characters
    s = re.sub(r'[^\w\s-]', '', s.lower())
    # Replace spaces with hyphens
    s = re.sub(r'[-\s]+', '-', s)
    # Limit length
    return s[:80]

def validate_url(url: str) -> Tuple[bool, str]:
    """
    Validate if a URL is reachable.

    Returns:
        (is_valid, message)
    """
    if not url:
        return False, "Empty URL"

    try:
        # Set timeout for connection
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            status = response.status
            if 200 <= status < 400:
                return True, "OK"
            else:
                return False, f"HTTP {status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return False, f"URL Error: {e.reason}"
    except socket.timeout:
        return False, "Timeout"
    except Exception as e:
        return False, f"Error: {str(e)[:50]}"

def check_local_pdf(pdf_path: str) -> Tuple[bool, str, Optional[Path]]:
    """
    Check if local PDF file exists.

    Args:
        pdf_path: Relative path from files/ directory (e.g., 'papers/my-paper.pdf')

    Returns:
        (exists, message, full_path)
    """
    full_path = FILES_DIR / pdf_path

    if full_path.exists() and full_path.is_file():
        return True, "Found", full_path
    else:
        return False, "Not found", full_path

def get_publication_links(entry: Dict) -> Dict[str, any]:
    """
    Extract and validate all links from a BibTeX entry.

    Returns:
        Dictionary with link information and validation status
    """
    links = {
        'url': entry.get('url', ''),
        'pdf': entry.get('pdf', ''),
        'code': entry.get('code', ''),
        'slides': entry.get('slides', ''),
        'video': entry.get('video', ''),
        'has_any_link': False,
        'validation': {}
    }

    # Validate external URL
    if links['url']:
        if VALIDATE_URLS:
            is_valid, message = validate_url(links['url'])
            links['validation']['url'] = {'valid': is_valid, 'message': message}
        else:
            links['validation']['url'] = {'valid': True, 'message': 'Skipped'}
        links['has_any_link'] = True

    # Check local PDF
    if links['pdf']:
        exists, message, full_path = check_local_pdf(links['pdf'])
        links['validation']['pdf'] = {'valid': exists, 'message': message, 'path': full_path}
        links['has_any_link'] = True

    # Validate other URLs (code, slides, video)
    for field in ['code', 'slides', 'video']:
        if links[field]:
            if VALIDATE_URLS:
                is_valid, message = validate_url(links[field])
                links['validation'][field] = {'valid': is_valid, 'message': message}
            else:
                links['validation'][field] = {'valid': True, 'message': 'Skipped'}
            links['has_any_link'] = True

    return links

def entry_to_markdown(entry: Dict, index: int, validation_report: List) -> Tuple[str, str]:
    """Convert BibTeX entry to Jekyll markdown file."""
    title = entry.get('title', 'Untitled')
    year = entry.get('year', '')

    # Create filename
    filename_base = sanitize_filename(title)
    if year:
        filename = f"{year}-{index:02d}-{filename_base}.md"
        date = f"{year}-01-01"
    else:
        filename = f"-{index:02d}-{filename_base}.md"
        date = "-01-01"

    # Extract fields
    citation = create_citation(entry)
    venue = get_venue_from_entry(entry)
    abstract = entry.get('abstract', '')

    # Get and validate links
    links = get_publication_links(entry)

    # Add to validation report
    report_entry = {
        'title': title,
        'year': year,
        'links': links,
        'bibtex_key': entry.get('ID', 'unknown')
    }
    validation_report.append(report_entry)

    # Determine category
    entry_type = entry.get('ENTRYTYPE', 'misc').lower()
    if entry_type in ['inproceedings', 'conference']:
        category = 'conferences'
    elif entry_type == 'article':
        category = 'manuscripts'
    else:
        category = 'conferences'

    # Create markdown content
    frontmatter = f"""---
category: {category}
citation: '{citation}'
collection: publications
date: {date}
title: {title}
venue: {venue}
"""

    # Add external URL
    if links['url']:
        frontmatter += f"paperurl: {links['url']}\n"

    # Add local PDF (convert to site-relative path)
    if links['pdf']:
        # Convert files/papers/xyz.pdf to /files/papers/xyz.pdf (site-relative)
        pdf_site_path = f"/{links['pdf']}"
        frontmatter += f"paperurl: {pdf_site_path}\n"

    # Add other links
    if links['code']:
        frontmatter += f"codeurl: {links['code']}\n"
    if links['slides']:
        frontmatter += f"slidesurl: {links['slides']}\n"
    if links['video']:
        frontmatter += f"videourl: {links['video']}\n"

    frontmatter += "---\n\n"

    if abstract:
        content = frontmatter + abstract + "\n"
    else:
        content = frontmatter

    return filename, content

def print_validation_report(validation_report: List):
    """Print a summary of link validation results."""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}PUBLICATION LINK VALIDATION REPORT{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*80}{Colors.RESET}\n")

    total = len(validation_report)
    with_links = sum(1 for r in validation_report if r['links']['has_any_link'])
    without_links = total - with_links

    # Count validation issues
    issues = []
    valid_count = 0

    for report in validation_report:
        has_issue = False
        entry_issues = []

        for field, validation in report['links']['validation'].items():
            if not validation['valid']:
                has_issue = True
                entry_issues.append(f"{field}: {validation['message']}")

        if has_issue:
            issues.append({
                'title': report['title'],
                'year': report['year'],
                'issues': entry_issues,
                'bibtex_key': report['bibtex_key']
            })
        else:
            if report['links']['has_any_link']:
                valid_count += 1

    # Summary statistics
    print(f"{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"  Total publications: {total}")
    print(f"  {Colors.GREEN}✓ With valid links: {valid_count}{Colors.RESET}")
    print(f"  {Colors.YELLOW}⚠ Without any links: {without_links}{Colors.RESET}")
    print(f"  {Colors.RED}✗ With link issues: {len(issues)}{Colors.RESET}\n")

    # Publications without links
    if without_links > 0:
        print(f"{Colors.BOLD}{Colors.YELLOW}Publications without links:{Colors.RESET}")
        for report in validation_report:
            if not report['links']['has_any_link']:
                year = report['year'] or 'N/A'
                print(f"  ⚠ [{year}] {report['title'][:70]}")
                print(f"     BibTeX key: {report['bibtex_key']}")
        print()

    # Publications with link issues
    if issues:
        print(f"{Colors.BOLD}{Colors.RED}Publications with link issues:{Colors.RESET}")
        for issue in issues:
            year = issue['year'] or 'N/A'
            print(f"  ✗ [{year}] {issue['title'][:70]}")
            print(f"     BibTeX key: {issue['bibtex_key']}")
            for issue_msg in issue['issues']:
                print(f"     - {issue_msg}")
        print()

    # Tips
    print(f"{Colors.BOLD}Tips:{Colors.RESET}")
    print(f"  • For external papers: Add 'url = {{https://...}}' to BibTeX entry")
    print(f"  • For local PDFs: Add 'pdf = {{papers/filename.pdf}}' to BibTeX entry")
    print(f"  • Place PDF files in: {PAPERS_DIR}/")
    print(f"  • To skip URL validation: Set VALIDATE_URLS = False in script")
    print(f"\n{Colors.BOLD}{'='*80}{Colors.RESET}\n")

def main():
    bibtex_file = Path('files/publications.bib')
    pubs_dir = Path('_publications')

    if not bibtex_file.exists():
        print(f"{Colors.RED}Error: {bibtex_file} not found!{Colors.RESET}")
        print("Please create your BibTeX file first.")
        return

    # Ensure papers directory exists
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"{Colors.BOLD}BibTeX to Publications Converter (Enhanced){Colors.RESET}")
    print(f"Reading BibTeX file: {bibtex_file}")
    print(f"URL validation: {'Enabled' if VALIDATE_URLS else 'Disabled'}\n")

    with open(bibtex_file, 'r', encoding='utf-8') as f:
        parser = BibTexParser(common_strings=True)
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.load(f, parser=parser)

    print(f"Found {len(bib_database.entries)} entries in BibTeX file\n")

    # Backup existing publications
    if pubs_dir.exists():
        backup_dir = Path('_publications_backup')
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        print(f"Backing up existing publications to {backup_dir}/")
        shutil.copytree(pubs_dir, backup_dir)
        shutil.rmtree(pubs_dir)

    pubs_dir.mkdir(exist_ok=True)

    print(f"Generating markdown files in {pubs_dir}/\n")

    # Sort entries by year (descending)
    entries_sorted = sorted(
        bib_database.entries,
        key=lambda x: x.get('year', '0000'),
        reverse=True
    )

    validation_report = []

    for idx, entry in enumerate(entries_sorted, 1):
        filename, content = entry_to_markdown(entry, idx, validation_report)
        filepath = pubs_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        title = entry.get('title', 'Untitled')[:60]
        print(f"  ✓ [{idx:2d}] {title}...")

    print(f"\n{Colors.GREEN}✓ Generated {len(entries_sorted)} publication files{Colors.RESET}")

    # Print validation report
    print_validation_report(validation_report)

    print(f"{Colors.BOLD}Next steps:{Colors.RESET}")
    print(f"1. Review validation report above")
    print(f"2. Add missing PDFs to {PAPERS_DIR}/")
    print(f"3. Update {bibtex_file} with pdf/url fields as needed")
    print(f"4. Restart Jekyll: docker compose down && docker compose up")
    print(f"5. Check publications page at http://localhost:4000/publications/")
    print(f"\n{Colors.BOLD}To make changes:{Colors.RESET}")
    print(f"1. Edit {bibtex_file}")
    print(f"2. Run: uv run python bibtex_to_publications.py")

if __name__ == "__main__":
    main()
