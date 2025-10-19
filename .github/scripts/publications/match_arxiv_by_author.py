#!/usr/bin/env python3
"""
Fetch all arXiv papers by author and match them to BibTeX entries.
Much more efficient than searching one-by-one!
"""

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from pathlib import Path
import re
import sys

try:
    import arxiv
except ImportError:
    print("Error: arxiv library not found!")
    print("Install it with: uv pip install arxiv")
    sys.exit(1)


def normalize_title(title):
    """Normalize title for comparison - removes punctuation and lowercases."""
    title = title.lower()
    # Remove all non-alphanumeric except spaces
    title = re.sub(r'[^a-z0-9\s]', '', title)
    # Normalize whitespace
    title = ' '.join(title.split())
    return title


def fetch_all_arxiv_papers(author_name):
    """
    Fetch all papers by an author from arXiv.

    Args:
        author_name: Author name (e.g., "Carlo Ciliberto" or "C. Ciliberto")

    Returns:
        Dictionary mapping normalized title to arXiv URL
    """
    print(f"Fetching all arXiv papers by: {author_name}")
    print("This may take a minute...")
    print()

    # Search for all papers by author
    search = arxiv.Search(
        query=f'au:"{author_name}"',
        max_results=500,  # Adjust if you have more papers
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    arxiv_papers = {}
    client = arxiv.Client()

    try:
        for result in client.results(search):
            normalized = normalize_title(result.title)
            arxiv_papers[normalized] = result.entry_id
            print(f"  ✓ {result.title[:70]}...")
    except Exception as e:
        print(f"Error fetching arXiv papers: {e}")
        return {}

    print(f"\nFound {len(arxiv_papers)} papers on arXiv")
    return arxiv_papers


def calculate_title_similarity(title1, title2):
    """
    Calculate word-based similarity between two titles.

    Returns:
        Float between 0 and 1 (1 = perfect match)
    """
    words1 = set(title1.split())
    words2 = set(title2.split())

    if not words1 or not words2:
        return 0.0

    intersection = words1 & words2
    union = words1 | words2

    return len(intersection) / len(union)


def match_bibtex_to_arxiv(bibtex_entry, arxiv_papers, threshold=0.8):
    """
    Try to match a BibTeX entry to an arXiv paper.

    Args:
        bibtex_entry: BibTeX entry dict
        arxiv_papers: Dict of normalized_title -> arxiv_url
        threshold: Minimum similarity score (0-1) to consider a match

    Returns:
        arXiv URL if match found, None otherwise
    """
    title = bibtex_entry.get('title', '')
    if not title:
        return None

    normalized_title = normalize_title(title)

    # First try exact match
    if normalized_title in arxiv_papers:
        return arxiv_papers[normalized_title]

    # Try fuzzy match
    best_match = None
    best_score = threshold

    for arxiv_title, arxiv_url in arxiv_papers.items():
        similarity = calculate_title_similarity(normalized_title, arxiv_title)
        if similarity > best_score:
            best_score = similarity
            best_match = arxiv_url

    return best_match


def update_bibtex_with_arxiv_matches(input_file, output_file, author_name):
    """
    Match BibTeX entries to arXiv papers and add url_paper fields.

    Args:
        input_file: Path to input BibTeX file
        output_file: Path to output BibTeX file
        author_name: Author name to search on arXiv
    """
    print("=" * 80)
    print("arXiv Matcher - Match BibTeX entries to author's arXiv papers")
    print("=" * 80)
    print()

    # Fetch all arXiv papers
    arxiv_papers = fetch_all_arxiv_papers(author_name)

    if not arxiv_papers:
        print("\nNo arXiv papers found or error occurred!")
        return

    print()
    print("=" * 80)
    print("Matching BibTeX entries to arXiv papers")
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
        'matched': 0,
        'not_matched': 0
    }

    updated_entries = []

    for i, entry in enumerate(bib_database.entries, 1):
        title = entry.get('title', 'Unknown')

        print(f"[{i}/{total}] {title[:60]}...")

        # Check if already has url_paper
        if entry.get('url_paper'):
            print(f"      ✓ Already has url_paper")
            stats['already_has_url'] += 1
            updated_entries.append(entry)
            continue

        # Try to match
        arxiv_url = match_bibtex_to_arxiv(entry, arxiv_papers)

        if arxiv_url:
            print(f"      ✓ Matched: {arxiv_url}")
            entry['url_paper'] = arxiv_url
            stats['matched'] += 1
        else:
            print(f"      ✗ No match found")
            stats['not_matched'] += 1

        updated_entries.append(entry)

    # Update database
    bib_database.entries = updated_entries

    # Write updated BibTeX file
    print(f"\n{'=' * 80}")
    print("Writing updated BibTeX file...")

    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write(f"% {author_name} - Publications\n")
        f.write("% BibTeX file with arXiv URLs matched by author\n")
        f.write(f"% Total entries: {len(updated_entries)}\n\n")

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
    print(f"Total BibTeX entries:    {total}")
    print(f"Total arXiv papers:      {len(arxiv_papers)}")
    print(f"Already had url_paper:   {stats['already_has_url']}")
    print(f"Newly matched to arXiv:  {stats['matched']}")
    print(f"Not matched:             {stats['not_matched']}")
    print()

    if stats['not_matched'] > 0:
        print("⚠️  Some entries couldn't be matched to arXiv papers.")
        print("   This is normal for conference-only papers or papers under different names.")
        print()

    print("Next steps:")
    print(f"1. Review {output_file}")
    print(f"2. If looks good: mv {output_file} .github/data/publications.bib")
    print("3. Run: uv run python .github/scripts/publications/bibtex_to_data.py")
    print("4. Restart Jekyll to see changes")
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
    # Configuration
    AUTHOR_NAME = "Carlo Ciliberto"  # or "C. Ciliberto"

    input_file = Path('.github/data/publications.bib')
    output_file = Path('.github/data/publications_with_arxiv.bib')

    if not input_file.exists():
        print(f"Error: {input_file} not found!")
        return

    print("This script will:")
    print(f"1. Fetch all arXiv papers by '{AUTHOR_NAME}'")
    print(f"2. Match them to entries in {input_file}")
    print(f"3. Add url_paper fields for matches")
    print()
    print(f"Output: {output_file}")
    print()

    response = input("Continue? [y/N] ")
    if response.lower() != 'y':
        print("Aborted.")
        return

    print()
    update_bibtex_with_arxiv_matches(input_file, output_file, AUTHOR_NAME)


if __name__ == "__main__":
    main()
