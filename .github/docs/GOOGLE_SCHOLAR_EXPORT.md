# Exporting Publications from Google Scholar

**Quick guide to importing your publications from Google Scholar to your website.**

---

## Method 1: Manual Export (Recommended)

This is the **easiest and most reliable** method since Google Scholar provides a built-in BibTeX export feature.

### Step-by-Step Instructions

1. **Visit your Google Scholar profile:**
   ```
   https://scholar.google.com/citations?user=XUcUAisAAAAJ
   ```

2. **Select publications to export:**
   - Click the checkbox next to each publication you want to export
   - Or click the checkbox in the header to select all publications

3. **Export to BibTeX:**
   - Click the "Export" button at the top
   - Choose "BibTeX" format
   - This will download a file like `citations.bib`

4. **Save the file:**
   ```bash
   # Move/rename the downloaded file to your repo
   mv ~/Downloads/citations.bib files/publications_from_scholar.bib
   ```

5. **Review and merge:**
   - Open `files/publications_from_scholar.bib` in your editor
   - Compare with `files/publications.bib`
   - Copy over entries or replace the entire file

6. **Update your site:**
   ```bash
   # Regenerate YAML data
   uv run python .github/scripts/publications/bibtex_to_data.py

   # Preview
   docker compose -f .github/dev/docker-compose.yaml up
   ```

---

## Method 2: Export Individual Papers

If you only want to update specific publications:

1. **Go to individual publication page:**
   - Click on the publication title in Google Scholar

2. **Get BibTeX citation:**
   - Click "Cite" button
   - Click "BibTeX" link
   - Copy the BibTeX entry

3. **Add to your file:**
   - Paste into `files/publications.bib`
   - Adjust the citation key if needed

---

## Method 3: Automated Script (May be blocked)

We have a Python script that attempts to scrape Google Scholar automatically:

```bash
uv run python .github/scripts/publications/google_scholar_to_bibtex.py
```

**Note:** Google Scholar often blocks automated scraping. If this fails, use Method 1 instead.

---

## Cleaning Up Exported BibTeX

Google Scholar's exported BibTeX may need some cleanup:

### Common Issues

1. **Missing venue information:**
   - Some entries may have incomplete venue names
   - Manually add or fix the `booktitle` or `journal` field

2. **Author name formatting:**
   - Google Scholar uses "Last, First and Last, First" format
   - Our script converts to "First Last and First Last"

3. **URLs:**
   - Google Scholar exports use `url` field
   - Consider using our new naming: `url_paper`, `local_paper`, etc.

### Example Cleanup

**Before (from Google Scholar):**
```bibtex
@inproceedings{ciliberto2024operator,
  title={Operator world models for reinforcement learning},
  author={Novelli, Pietro and Prattic{\`o}, Marco and Pontil, Massimiliano and Ciliberto, Carlo},
  booktitle={Advances in Neural Information Processing Systems},
  year={2024},
  url={https://proceedings.neurips.cc/paper_files/paper/2024/hash/c9da56addea9c977cf4ba873e1da979d-Abstract-Conference.html}
}
```

**After (cleaned up with new naming):**
```bibtex
@inproceedings{ciliberto2024operator,
  title = {Operator world models for reinforcement learning},
  author = {Pietro Novelli and Marco Pratticò and Massimiliano Pontil and Carlo Ciliberto},
  booktitle = {NeurIPS},
  year = {2024},
  url_paper = {https://proceedings.neurips.cc/paper_files/paper/2024/hash/c9da56addea9c977cf4ba873e1da979d-Abstract-Conference.html},
}
```

---

## Using a Reference Manager

If you use Zotero, Mendeley, or another reference manager:

### Zotero

1. Install Zotero browser extension
2. Visit your Google Scholar profile
3. Click Zotero icon to save all publications
4. Export from Zotero: File → Export Library → BibTeX format
5. Save to `files/publications_from_scholar.bib`

### Mendeley

1. Import from Google Scholar (similar to Zotero)
2. File → Export → BibTeX
3. Save to `files/publications_from_scholar.bib`

---

## Recommended Workflow

1. **Initial import:** Use Method 1 to export all publications
2. **Regular updates:** Add new publications individually (Method 2)
3. **Major refresh:** Re-export all publications annually

---

## Next Steps

After exporting from Google Scholar:

1. Review `files/publications_from_scholar.bib`
2. Clean up venue names, author formatting
3. Add missing fields (code, slides, video URLs)
4. Merge into `files/publications.bib`
5. Run: `uv run python .github/scripts/publications/bibtex_to_data.py`
6. Commit: `git add files/publications.bib _data/publications.yml && git commit -m "Update publications from Google Scholar"`

---

## Troubleshooting

### Publications missing from Google Scholar

- Check if they're in your profile at all
- Add missing publications manually to Google Scholar first
- Then re-export

### BibTeX export not working

- Try exporting fewer publications at once
- Use Method 2 (individual export) for problematic entries

### Venue names are messy

- Google Scholar often abbreviates or misspells venue names
- Manually edit the `booktitle` or `journal` fields
- Common fixes:
  - `Advances in Neural Information Processing Systems` → `NeurIPS`
  - `Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition` → `CVPR`
  - `International Conference on Machine Learning` → `ICML`

---

**Last updated:** October 2025
