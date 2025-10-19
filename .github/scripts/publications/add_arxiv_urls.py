#!/usr/bin/env python3
"""
Search arXiv for publications and add url_paper fields to BibTeX.
Uses the arxiv Python library to search by title.
"""

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from pathlib import Path
import time
import re
import sys

try:
    import arxiv
except ImportError:
    print("Error: arxiv library not found!")
    print("Install it with: uv pip install arxiv")
    sys.exit(1)


def normalize_title(title):
    """Normalize title for comparison."""
    # Remove special characters, convert to lowercase
    title = title.lower()
    title = re.sub(r'[^a-z0-9\s]', '', title)
    title = ' '.join(title.split())  # Normalize whitespace
    return title


def search_arxiv_for_paper(title, authors=None, max_results=5):
    """
    Search arXiv for a paper by title.

    Args:
        title: Paper title
        authors: Optional author names for better matching
        max_results: Maximum number of results to check

    Returns:
        arXiv URL if found, None otherwise
    """
    try:
        # Create search query
        query = f'ti:"{title}"'

        # Search arXiv
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        normalized_title = normalize_title(title)

        for result in search.results():
            result_title = normalize_title(result.title)

            # Check if titles match (allowing for minor differences)
            if normalized_title in result_title or result_title in normalized_title:
                # Calculate similarity
                words_query = set(normalized_title.split())
                words_result = set(result_title.split())

                # If at least 70% of words match, consider it a match
                if len(words_query & words_result) / len(words_query | words_result) > 0.7:
                    return result.entry_id  # This is the arXiv URL

        return None

    except Exception as e:
        print(f"      Error searching arXiv: {e}")
        return None


def has_paper_url(entry):
    """Check if entry already has url_paper field."""
    return bool(entry.get('url_paper'))


def update_bibtex_with_arxiv(input_file, output_file=None):
    """
    Read BibTeX file, search arXiv for each entry, and add url_paper fields.

    Args:
        input_file: Path to input BibTeX file
        output_file: Path to output file (if None, overwrites input)
    """
    if output_file is None:
        output_file = input_file

    print("=" * 80)
    print("arXiv URL Finder for BibTeX")
    print("=" * 80)
    print()

    # Read BibTeX file
    print(f"Reading BibTeX file: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        parser = BibTexParser(common_strings=True)
        parser.customization = convert_to_unicode
        bib_database = bibtexparser.load(f, parser=parser)

    total = len(bib_database.entries)
    print(f"Found {total} entries\n")

    # Statistics
    stats = {
        'already_has_url': 0,
        'found_on_arxiv': 0,
        'not_found': 0,
        'errors': 0
    }

    updated_entries = []

    for i, entry in enumerate(bib_database.entries, 1):
        title = entry.get('title', 'Unknown')
        authors = entry.get('author', '')
        year = entry.get('year', '')

        print(f"[{i}/{total}] {title[:60]}...")

        # Check if already has url_paper field
        if has_paper_url(entry):
            print(f"      ✓ Already has url_paper field")
            stats['already_has_url'] += 1
            updated_entries.append(entry)
            continue

        # Search arXiv
        print(f"      Searching arXiv...")
        arxiv_url = search_arxiv_for_paper(title, authors)

        if arxiv_url:
            print(f"      ✓ Found: {arxiv_url}")
            # Add url_paper field
            entry['url_paper'] = arxiv_url
            stats['found_on_arxiv'] += 1
        else:
            print(f"      ✗ Not found on arXiv")
            stats['not_found'] += 1

        updated_entries.append(entry)

        # Rate limiting: be nice to arXiv servers
        if i < total:
            time.sleep(1)  # 1 second delay between requests

    # Update database with modified entries
    bib_database.entries = updated_entries

    # Write updated BibTeX file
    print(f"\n{'=' * 80}")
    print("Writing updated BibTeX file...")

    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("% Carlo Ciliberto - Publications\n")
        f.write("% BibTeX file with arXiv URLs added\n")
        f.write(f"% Total entries: {len(updated_entries)}\n")
        f.write("% arXiv URLs added automatically\n\n")

        # Write each entry
        for entry in updated_entries:
            f.write(format_bibtex_entry(entry))
            f.write("\n\n")

    # Print statistics
    print(f"✓ Updated BibTeX file written to: {output_file}")
    print()
    print("=" * 80)
    print("STATISTICS")
    print("=" * 80)
    print(f"Total entries:           {total}")
    print(f"Already had URL:         {stats['already_has_url']}")
    print(f"Found on arXiv:          {stats['found_on_arxiv']}")
    print(f"Not found on arXiv:      {stats['not_found']}")
    print()
    print("Next steps:")
    print("1. Review the updated file")
    print("2. Run: uv run python .github/scripts/publications/bibtex_to_data.py")
    print("3. Restart Jekyll to see changes")
    print()


def format_bibtex_entry(entry):
    """Format a BibTeX entry for writing, preserving ALL original fields."""
    entry_type = entry.get('ENTRYTYPE', 'misc')
    entry_id = entry.get('ID', 'unknown')

    lines = [f"@{entry_type}{{{entry_id},"]

    # Preferred order of fields for readability
    field_order = [
        'title', 'author', 'booktitle', 'journal', 'howpublished', 'publisher',
        'pages', 'volume', 'number', 'year', 'month', 'organization',
        'url_paper', 'url', 'pdf', 'doi', 'eprint', 'archivePrefix', 'primaryClass',
        'url_code', 'local_code', 'code',
        'url_slides', 'local_slides', 'slides',
        'url_video', 'local_video', 'video',
        'abstract', 'note'
    ]

    # Track which fields we've added
    added_fields = set()

    # Add fields in preferred order
    for field in field_order:
        if field in entry and field not in ['ENTRYTYPE', 'ID']:
            value = entry[field]
            lines.append(f"  {field} = {{{value}}},")
            added_fields.add(field)

    # Add any remaining fields not in the standard order (to preserve everything)
    for field, value in sorted(entry.items()):
        if field not in added_fields and field not in ['ENTRYTYPE', 'ID']:
            lines.append(f"  {field} = {{{value}}},")

    lines.append("}")

    return "\n".join(lines)


def main():
    """Main function."""
    input_file = Path('.github/data/publications.bib')
    output_file = Path('.github/data/publications_with_arxiv.bib')

    if not input_file.exists():
        print(f"Error: {input_file} not found!")
        return

    print("This script will search arXiv for publications without url_paper field")
    print("and add url_paper with arXiv URL if found.")
    print()
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print()
    print("Note: This will take several minutes due to rate limiting (1 req/sec)")
    print("      to be respectful to arXiv servers.")
    print()

    response = input("Continue? [y/N] ")
    if response.lower() != 'y':
        print("Aborted.")
        return

    print()
    update_bibtex_with_arxiv(input_file, output_file)


if __name__ == "__main__":
    main()
