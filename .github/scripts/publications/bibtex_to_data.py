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

def format_author_name(author):
    """
    Format a single author name to: Surname, I.
    Examples:
        "Carlo Ciliberto" -> "C. Ciliberto"
        "Ciliberto, Carlo" -> "C. Ciliberto"
        "John Smith" -> "J. Smith"
    """
    author = author.strip()

    # Handle "Last, First Middle" format (common in BibTeX)
    if ',' in author:
        parts = author.split(',', 1)
        last_name = parts[0].strip()
        first_names = parts[1].strip()
    else:
        # Handle "First Middle Last" format
        parts = author.split()
        if len(parts) == 0:
            return author
        last_name = parts[-1]
        first_names = ' '.join(parts[:-1])

    # Extract initials from first names
    if not first_names:
        return last_name

    # Get first letter of each first name
    initials = []
    for name in first_names.split():
        if name:  # Skip empty strings
            initials.append(name[0].upper() + '.')

    # Format: I. Last or I. M. Last
    if initials:
        return ' '.join(initials) + ' ' + last_name
    else:
        return last_name

def format_author_list(authors):
    """Format author list for citation with initials."""
    if not authors:
        return ""

    author_list = [format_author_name(a.strip()) for a in authors.split(' and ')]

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

def get_material_url(entry, material_type):
    """
    Get URL for a material (paper, code, slides, video).
    Checks url_* first, then local_*, then falls back to old field names.

    Args:
        entry: BibTeX entry dictionary
        material_type: Type of material ('paper', 'code', 'slides', 'video')

    Returns:
        URL string or empty string if not found
    """
    # Check new naming scheme first
    url_field = f'url_{material_type}'
    local_field = f'local_{material_type}'

    if url_field in entry:
        return entry[url_field]
    elif local_field in entry:
        return entry[local_field]

    # Fall back to old field names for backward compatibility
    old_field_map = {
        'paper': ['url', 'pdf'],  # url or pdf for paper
        'code': ['code'],
        'slides': ['slides'],
        'video': ['video']
    }

    for old_field in old_field_map.get(material_type, []):
        if old_field in entry:
            return entry[old_field]

    return ''

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
        'url': get_material_url(entry, 'paper'),
        'code': get_material_url(entry, 'code'),
        'slides': get_material_url(entry, 'slides'),
        'video': get_material_url(entry, 'video'),
        'abstract': entry.get('abstract', ''),
    }

def main():
    bibtex_file = Path('.github/data/publications.bib')
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
    print(f"2. To update: edit .github/data/publications.bib and run this script")
    print(f"3. Jekyll will auto-reload (or restart: docker compose down && docker compose -f .github/dev/docker-compose.yaml up)")

if __name__ == "__main__":
    main()
