#!/usr/bin/env python3
"""
Fetch publications from Google Scholar and generate BibTeX file.
Uses the scholarly library to scrape Google Scholar.
"""

from pathlib import Path
import sys

try:
    from scholarly import scholarly, ProxyGenerator
except ImportError:
    print("Error: scholarly library not found!")
    print("Install it with: uv pip install scholarly")
    sys.exit(1)


def setup_proxy():
    """Setup proxy to avoid rate limiting (optional)."""
    # Uncomment to use FreeProxy (slower but more reliable)
    # pg = ProxyGenerator()
    # pg.FreeProxies()
    # scholarly.use_proxy(pg)
    pass


def fetch_author_publications(author_name, author_id=None):
    """
    Fetch all publications for an author from Google Scholar.

    Args:
        author_name: Name of the author (e.g., "Carlo Ciliberto")
        author_id: Optional Google Scholar author ID (more reliable if provided)

    Returns:
        List of publication dictionaries
    """
    print(f"Searching for author: {author_name}")

    if author_id:
        # Direct lookup by ID (more reliable)
        print(f"Using author ID: {author_id}")
        author = scholarly.search_author_id(author_id)
    else:
        # Search by name
        search_query = scholarly.search_author(author_name)
        author = next(search_query, None)

        if not author:
            print(f"Error: Author '{author_name}' not found on Google Scholar")
            return []

    # Fill in author details including publications
    print(f"Fetching publications for: {author['name']}")
    author = scholarly.fill(author, sections=['publications'])

    publications = []
    total_pubs = len(author['publications'])

    print(f"Found {total_pubs} publications. Fetching details...")

    for i, pub in enumerate(author['publications'], 1):
        try:
            print(f"  [{i}/{total_pubs}] Fetching: {pub['bib']['title'][:60]}...")

            # Fill in complete publication details
            filled_pub = scholarly.fill(pub)
            publications.append(filled_pub)

        except Exception as e:
            print(f"  ⚠️  Error fetching publication: {e}")
            # Add the partial data anyway
            publications.append(pub)

    return publications


def pub_to_bibtex(pub, index):
    """
    Convert a scholarly publication to BibTeX format.

    Args:
        pub: Publication dictionary from scholarly
        index: Publication index (for generating citation key)

    Returns:
        BibTeX string
    """
    bib = pub.get('bib', {})

    # Extract fields
    title = bib.get('title', 'Unknown Title')
    authors = bib.get('author', 'Unknown Author')
    year = bib.get('pub_year', '')
    venue = bib.get('venue', bib.get('journal', bib.get('conference', '')))
    abstract = bib.get('abstract', '')

    # Get URL
    url = pub.get('pub_url', pub.get('eprint_url', ''))

    # Generate citation key
    # Use first author's last name + year + index
    first_author = authors.split(' and ')[0] if ' and ' in authors else authors.split(',')[0] if ',' in authors else authors
    last_name = first_author.split()[-1].lower().replace('.', '')
    key = f"{last_name}{year}_{index:02d}" if year else f"{last_name}_{index:02d}"

    # Determine entry type based on venue
    entry_type = 'inproceedings'  # Default
    venue_lower = venue.lower() if venue else ''

    if 'arxiv' in venue_lower or not venue:
        entry_type = 'misc'
        venue = 'arXiv' if 'arxiv' in venue_lower else 'Preprint'
    elif 'journal' in venue_lower or any(j in venue_lower for j in ['ieee', 'acm', 'transactions']):
        entry_type = 'article'
    elif 'phd' in venue_lower or 'thesis' in venue_lower:
        entry_type = 'phdthesis'

    # Build BibTeX entry
    lines = [f"@{entry_type}{{{key},"]
    lines.append(f"  title = {{{title}}},")

    if authors:
        # Convert author format: "First Last, Second Author" -> "First Last and Second Author"
        authors_cleaned = authors.replace(', ', ' and ')
        lines.append(f"  author = {{{authors_cleaned}}},")

    if venue:
        if entry_type == 'article':
            lines.append(f"  journal = {{{venue}}},")
        elif entry_type == 'inproceedings':
            lines.append(f"  booktitle = {{{venue}}},")
        else:
            lines.append(f"  howpublished = {{{venue}}},")

    if year:
        lines.append(f"  year = {{{year}}},")

    if url:
        lines.append(f"  url_paper = {{{url}}},")

    if abstract:
        # Clean abstract
        abstract_clean = abstract.replace('\n', ' ').replace('{', '').replace('}', '')
        lines.append(f"  abstract = {{{abstract_clean}}},")

    lines.append("}")

    return "\n".join(lines)


def main():
    """Main function."""
    # Configuration
    AUTHOR_NAME = "Carlo Ciliberto"
    # Google Scholar author ID for reliable results
    # From: https://scholar.google.com/citations?user=XUcUAisAAAAJ
    AUTHOR_ID = "XUcUAisAAAAJ"

    output_file = Path('files/publications_from_scholar.bib')

    print("=" * 80)
    print("Google Scholar to BibTeX Converter")
    print("=" * 80)
    print()

    # Setup proxy if needed
    setup_proxy()

    # Fetch publications
    try:
        publications = fetch_author_publications(AUTHOR_NAME, AUTHOR_ID)
    except Exception as e:
        print(f"\n✗ Error: Google Scholar is blocking requests")
        print(f"   Details: {e}")
        print()
        print("Alternative approaches:")
        print("1. Use Google Scholar's 'Export' feature:")
        print("   - Visit: https://scholar.google.com/citations?user=XUcUAisAAAAJ")
        print("   - Select publications → Click 'Export' → Choose BibTeX")
        print("   - Save to files/publications_from_scholar.bib")
        print()
        print("2. Use a reference manager (Zotero, Mendeley):")
        print("   - Import from Google Scholar")
        print("   - Export as BibTeX")
        print()
        print("3. Try again later (Google may have rate-limited your IP)")
        print()
        return

    if not publications:
        print("\nNo publications found!")
        return

    print(f"\n✓ Successfully fetched {len(publications)} publications")
    print(f"\nWriting to {output_file}...")

    # Write to BibTeX file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"% {AUTHOR_NAME} - Publications from Google Scholar\n")
        f.write(f"% Auto-generated from Google Scholar\n")
        f.write(f"% Total entries: {len(publications)}\n")
        f.write(f"% WARNING: This is a TEMPORARY file for review\n")
        f.write(f"% Review and merge entries into files/publications.bib\n\n")

        for i, pub in enumerate(publications, 1):
            bibtex = pub_to_bibtex(pub, i)
            f.write(bibtex)
            f.write("\n\n")

    print(f"✓ Created {output_file}")
    print()
    print("⚠️  IMPORTANT:")
    print(f"   This file does NOT overwrite your main publications.bib")
    print(f"   Review {output_file} and manually merge entries you want")
    print()
    print("Next steps:")
    print(f"1. Review {output_file}")
    print(f"2. Compare with files/publications.bib")
    print(f"3. Merge/update entries in files/publications.bib")
    print(f"4. Fix any venue names, author formats, or add missing fields")
    print(f"5. Run: uv run python .github/scripts/publications/bibtex_to_data.py")
    print(f"6. Restart Jekyll to see changes")
    print()
    print("Note: Google Scholar scraping can be slow and may hit rate limits.")
    print("      If you have many publications, this script may take several minutes.")
    print("      Consider setting AUTHOR_ID for more reliable results.")


if __name__ == "__main__":
    main()
