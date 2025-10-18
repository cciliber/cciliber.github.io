#!/usr/bin/env python3
"""
Extract publications from markdown files to BibTeX format.
"""

import os
import re
from pathlib import Path
import yaml

def clean_string(s):
    """Remove extra whitespace and clean string."""
    if not s:
        return ""
    return " ".join(s.split())

def generate_bibtex_key(title, year):
    """Generate a BibTeX key from title and year."""
    # Take first few words of title
    words = re.findall(r'\w+', title.lower())
    key_words = words[:3] if len(words) >= 3 else words
    key = "".join(key_words) + str(year) if year else "".join(key_words)
    return key

def parse_markdown_publication(file_path):
    """Parse a markdown publication file and extract fields."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split frontmatter and body
    parts = content.split('---')
    if len(parts) < 3:
        return None

    try:
        frontmatter = yaml.safe_load(parts[1])
    except:
        return None

    # Extract year from date or citation
    year = ""
    if frontmatter.get('date'):
        date_str = str(frontmatter['date'])
        year_match = re.search(r'(\d{4})', date_str)
        if year_match:
            year = year_match.group(1)

    if not year and frontmatter.get('citation'):
        citation = frontmatter['citation']
        year_match = re.search(r'\b(19|20)\d{2}\b', citation)
        if year_match:
            year = year_match.group(0)

    # Extract authors from citation
    authors = ""
    if frontmatter.get('citation'):
        citation = frontmatter['citation']
        # Try to extract authors (everything before the first quote or period)
        author_match = re.match(r'^([^"\.]+)', citation)
        if author_match:
            authors = clean_string(author_match.group(1))
            # Clean up "and" to use proper BibTeX format
            authors = authors.replace(' and ', ' and ')

    title = clean_string(frontmatter.get('title', ''))
    venue = clean_string(frontmatter.get('venue', ''))

    return {
        'key': generate_bibtex_key(title, year),
        'title': title,
        'authors': authors,
        'year': year,
        'venue': venue,
        'url': frontmatter.get('paperurl', ''),
        'code': frontmatter.get('codeurl', ''),
        'slides': frontmatter.get('slidesurl', ''),
        'video': frontmatter.get('videourl', ''),
        'category': frontmatter.get('category', 'misc'),
    }

def determine_entry_type(category, venue):
    """Determine BibTeX entry type."""
    category = category.lower() if category else ''
    venue = venue.lower() if venue else ''

    if 'conference' in category or 'workshop' in venue:
        return 'inproceedings'
    elif 'journal' in category or 'article' in category:
        return 'article'
    elif 'book' in category:
        return 'book'
    elif 'thesis' in category or 'phd' in venue:
        return 'phdthesis'
    elif 'preprint' in venue or 'arxiv' in venue:
        return 'misc'
    else:
        return 'inproceedings'  # Default to conference paper

def publication_to_bibtex(pub):
    """Convert publication dict to BibTeX entry."""
    entry_type = determine_entry_type(pub['category'], pub['venue'])

    lines = [f"@{entry_type}{{{pub['key']},"]

    if pub['title']:
        lines.append(f"  title = {{{pub['title']}}},")
    if pub['authors']:
        lines.append(f"  author = {{{pub['authors']}}},")
    if pub['venue']:
        if entry_type == 'article':
            lines.append(f"  journal = {{{pub['venue']}}},")
        elif entry_type == 'inproceedings':
            lines.append(f"  booktitle = {{{pub['venue']}}},")
        else:
            lines.append(f"  howpublished = {{{pub['venue']}}},")
    if pub['year']:
        lines.append(f"  year = {{{pub['year']}}},")
    if pub['url']:
        lines.append(f"  url = {{{pub['url']}}},")
    if pub['code']:
        lines.append(f"  code = {{{pub['code']}}},")
    if pub['slides']:
        lines.append(f"  slides = {{{pub['slides']}}},")
    if pub['video']:
        lines.append(f"  video = {{{pub['video']}}},")

    lines.append("}")
    return "\n".join(lines)

def main():
    pubs_dir = Path('_publications')
    output_file = Path('files/publications.bib')

    publications = []

    print("Extracting publications from markdown files...")
    for md_file in sorted(pubs_dir.glob('*.md')):
        pub = parse_markdown_publication(md_file)
        if pub and pub['title']:
            publications.append(pub)
            print(f"  ✓ {pub['title'][:60]}...")

    print(f"\nFound {len(publications)} publications")
    print(f"Writing to {output_file}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("% Carlo Ciliberto - Publications\n")
        f.write("% Auto-generated from _publications/ markdown files\n")
        f.write(f"% Total entries: {len(publications)}\n\n")

        for pub in publications:
            f.write(publication_to_bibtex(pub))
            f.write("\n\n")

    print(f"✓ BibTeX file created: {output_file}")
    print(f"\nNext steps:")
    print(f"1. Review and edit {output_file}")
    print(f"2. Delete wrong entries, fix authors, add missing info")
    print(f"3. Run: uv run python bibtex_to_publications.py")
    print(f"4. Restart Jekyll: docker compose down && docker compose up")

if __name__ == "__main__":
    main()
