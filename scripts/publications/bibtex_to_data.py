#!/usr/bin/env python3
"""
Convert BibTeX file to Jekyll data file (YAML).
This allows the publications page to read directly from data without markdown files.
"""

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from pathlib import Path
import yaml

def format_author_list(authors):
    """Format author list for citation."""
    if not authors:
        return ""

    author_list = [a.strip() for a in authors.split(' and ')]

    if len(author_list) == 1:
        return author_list[0]
    elif len(author_list) == 2:
        return f"{author_list[0]} and {author_list[1]}"
    else:
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

def bibtex_to_dict(entry):
    """Convert BibTeX entry to dictionary for Jekyll."""
    authors = format_author_list(entry.get('author', ''))
    title = entry.get('title', '')
    year = entry.get('year', '')
    venue = get_venue_from_entry(entry)

    # Create formatted citation
    citation = f'{authors}. "{title}"'
    if venue and venue != "Preprint":
        citation += f'. {venue}'
    if year:
        citation += f', {year}'
    citation += '.'

    return {
        'key': entry.get('ID', ''),
        'title': title,
        'authors': authors,
        'year': year,
        'venue': venue,
        'citation': citation,
        'url': entry.get('url', ''),
        'code': entry.get('code', ''),
        'slides': entry.get('slides', ''),
        'video': entry.get('video', ''),
        'abstract': entry.get('abstract', ''),
    }

def main():
    bibtex_file = Path('files/publications.bib')
    output_file = Path('_data/publications.yml')

    if not bibtex_file.exists():
        print(f"Error: {bibtex_file} not found!")
        return

    print(f"Reading BibTeX file: {bibtex_file}")

    with open(bibtex_file, 'r', encoding='utf-8') as f:
        parser = BibTexParser(common_strings=True)
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.load(f, parser=parser)

    print(f"Found {len(bib_database.entries)} entries")

    # Convert to list of dictionaries
    publications = []
    for entry in bib_database.entries:
        pub_dict = bibtex_to_dict(entry)
        publications.append(pub_dict)

    # Sort by year (descending)
    publications.sort(key=lambda x: x.get('year', '0000'), reverse=True)

    # Ensure _data directory exists
    output_file.parent.mkdir(exist_ok=True)

    # Write to YAML
    print(f"Writing to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(publications, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"✓ Created {output_file}")
    print(f"\nNext steps:")
    print(f"1. Publications page will now read from _data/publications.yml")
    print(f"2. To update: edit files/publications.bib and run this script")
    print(f"3. Restart Jekyll: docker compose down && docker compose up")

if __name__ == "__main__":
    main()
