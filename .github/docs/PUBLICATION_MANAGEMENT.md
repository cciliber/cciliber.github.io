# Publication Management Guide

**Complete guide to managing publications on your Jekyll academic website.**

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Workflow Overview](#workflow-overview)
3. [Managing Your BibTeX File](#managing-your-bibtex-file)
4. [Adding Publication Links](#adding-publication-links)
5. [Link Validation](#link-validation)
6. [Common Tasks](#common-tasks)
7. [Scripts Reference](#scripts-reference)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### The 4-Step Update Process

```bash
# 1. Edit BibTeX file
vim files/publications.bib

# 2. Regenerate data file with validation
uv run python .github/scripts/publications/bibtex_to_data.py

# 3. Preview locally
docker compose -f .github/dev/docker-compose.yaml up

# 4. Visit http://localhost:4000/publications/
```

### Source of Truth

**📄 Edit this file:** `files/publications.bib`

**🚫 Don't edit:** `_publications/*.md` files (auto-generated, may be deprecated)

---

## Workflow Overview

Your publications flow through this pipeline:

```
┌─────────────────────────┐
│ files/publications.bib  │ ← Edit this (source of truth)
└──────────┬──────────────┘
           │
           │ uv run python .github/scripts/publications/bibtex_to_data.py
           ▼
┌─────────────────────────┐
│ _data/publications.yml  │ ← Auto-generated YAML data file
└──────────┬──────────────┘
           │
           │ Jekyll reads data file directly
           ▼
┌─────────────────────────┐
│  /publications/ page    │ ← Rendered on website
└─────────────────────────┘
```

**Key advantage:** Publications page reads directly from the data file. No intermediate markdown files needed!

---

## Managing Your BibTeX File

### File Location

**Location:** `files/publications.bib`

### Entry Types

- `@inproceedings{}` - Conference papers
- `@article{}` - Journal articles
- `@misc{}` - Preprints, technical reports
- `@phdthesis{}` - PhD thesis
- `@book{}` - Books

### Required Fields

```bibtex
@inproceedings{citationkey2024,
  title = {Paper Title},                      % Required
  author = {Author One and Author Two},       % Required (use " and " separator)
  year = {2024},                              % Required
  booktitle = {Conference Name},              % Required for @inproceedings
}
```

### Optional Fields

```bibtex
@inproceedings{citationkey2024,
  title = {Paper Title},
  author = {Carlo Ciliberto and Others},
  year = {2024},
  booktitle = {NeurIPS},

  % Links (all optional) - NEW naming scheme
  url_paper = {https://arxiv.org/abs/...},           % External paper link
  local_paper = {papers/my-paper-2024.pdf},          % Local PDF (relative to files/)
  url_code = {https://github.com/user/repo},         % External code repository
  local_code = {code/my-project-2024.zip},           % Local code archive
  url_slides = {https://slides.com/...},             % External slides
  local_slides = {slides/presentation-2024.pdf},     % Local slides PDF
  url_video = {https://youtube.com/watch?v=...},     % External video
  local_video = {videos/presentation-2024.mp4},      % Local video file
}
```

**Backward compatibility:** The old field names (`url`, `pdf`, `code`, `slides`, `video`) still work!

**Priority:** `url_*` is checked first, then `local_*`, then old field names.

**Recommendation:** Use the new `url_*` / `local_*` naming for clarity when tracking materials.

### Citation Keys

Use format: `firstauthorYEARkeyword`

Examples:
- `ciliberto2024operator`
- `novelli2023meta`
- `smith2025learning`

### Author Name Formatting

Your name will be **automatically bolded** if it appears as:
- "Carlo Ciliberto"
- "C. Ciliberto"

**Important:** Separate authors with " and " (with spaces):
```bibtex
# ✓ Correct
author = {Alice Smith and Bob Jones and Carlo Ciliberto}

# ✗ Wrong
author = {Alice Smith, Bob Jones, Carlo Ciliberto}
```

---

## Adding Publication Links

### Option 1: External URL

Add external links to papers (ArXiv, conference proceedings, etc.):

```bibtex
@inproceedings{paper2024,
  title = {My Paper Title},
  author = {Carlo Ciliberto and Others},
  year = {2024},
  url = {https://proceedings.neurips.cc/paper/...},  % ← Add this
}
```

**Best sources for URLs:**
- Conference proceedings (NeurIPS, ICML, CVPR, etc.)
- ArXiv: `https://arxiv.org/abs/...`
- Journal websites
- Your institutional repository

### Option 2: Local PDF

If you have a local copy of the paper:

**1. Copy PDF to the correct directory:**
```bash
cp ~/Downloads/my-paper.pdf files/papers/my-paper-2024.pdf
```

**2. Update BibTeX entry:**
```bibtex
@inproceedings{paper2024,
  title = {My Paper},
  author = {Carlo Ciliberto},
  year = {2024},
  pdf = {papers/my-paper-2024.pdf},  % Relative to files/ directory
}
```

**3. Naming convention (recommended):**
- Use lowercase with hyphens
- Include year in filename
- Example: `learning-kernel-methods-2024.pdf`

### Option 3: Both URL and Local PDF

You can have both! Local PDF will take priority.

```bibtex
@inproceedings{paper2024,
  title = {My Paper Title},
  author = {Carlo Ciliberto and Others},
  year = {2024},
  url = {https://arxiv.org/abs/...},           % External link
  pdf = {papers/my-paper-2024.pdf},            % Local PDF
  code = {https://github.com/username/repo},   % Optional: code
  slides = {https://slides.com/...},           % Optional: slides
  video = {https://youtube.com/...},           % Optional: video
}
```

### No Link (Intentional)

For unpublished work or papers you don't want to link, simply omit `url` and `pdf` fields.

---

## Link Validation

### Running Validation

The `bibtex_to_data.py` script automatically validates all links:

```bash
uv run python .github/scripts/publications/bibtex_to_data.py
```

### Validation Report

After running, you'll see a color-coded report:

```
================================================================================
PUBLICATION LINK VALIDATION REPORT
================================================================================

Summary:
  Total publications: 74
  ✓ With valid links: 60
  ⚠ Without any links: 10
  ✗ With link issues: 4

Publications without links:
  ⚠ [2023] My Unpublished Work
     BibTeX key: unpublished2023

Publications with link issues:
  ✗ [2022] Paper with Broken Link
     BibTeX key: paper2022
     - url: HTTP 404
```

### Understanding Validation Results

- **✓ With valid links** (green) - All good!
- **⚠ Without any links** (yellow) - Need to add `url` or `pdf`
- **✗ With link issues** (red) - URL returns error (403/404/timeout)

### Common Validation Issues

**HTTP 403/418 errors:** Some websites block automated requests. The links likely work fine in browsers. You can:
1. Keep the URL anyway (it will work for users)
2. Add a local PDF instead
3. Disable validation (see below)

**PDF not found:** Make sure the path is correct:
```bibtex
# ✅ Correct
pdf = {papers/my-file.pdf}  % Relative to files/

# ❌ Wrong (includes 'files/' prefix)
pdf = {files/papers/my-file.pdf}

# ❌ Wrong (absolute path)
pdf = {/Users/carlo/files/papers/my-file.pdf}
```

---

## Common Tasks

### Add a New Publication

1. Open `files/publications.bib`
2. Add new entry at the top or bottom:

```bibtex
@inproceedings{mycitation2025,
  title = {My New Paper Title},
  author = {Author One and Author Two and Carlo Ciliberto},
  booktitle = {NeurIPS},
  year = {2025},
  url = {https://arxiv.org/abs/2025.xxxxx},
}
```

3. Run: `uv run python .github/scripts/publications/bibtex_to_data.py`
4. Restart Jekyll: `docker compose down && docker compose -f .github/dev/docker-compose.yaml up`

### Delete a Publication

1. Open `files/publications.bib`
2. Find and delete the entire entry (from `@type{key,` to closing `}`)
3. Run: `uv run python .github/scripts/publications/bibtex_to_data.py`
4. Restart Jekyll

### Edit a Publication

1. Open `files/publications.bib`
2. Find the entry by searching for the title or author
3. Edit any field
4. Run: `uv run python .github/scripts/publications/bibtex_to_data.py`
5. Restart Jekyll

### Migrate PDFs from Old Site

If you have PDFs in `old_site_backup/papers/`:

```bash
# Find PDFs in old site
find old_site_backup/papers -name "*.pdf" -type f

# Copy relevant ones
cp old_site_backup/papers/weakly-supervised-13/weakly_supervised.pdf \
   files/papers/weakly-supervised-2013.pdf
```

Then update BibTeX entry with: `pdf = {papers/weakly-supervised-2013.pdf}`

### Search for a Paper

```bash
grep -i "paper title" files/publications.bib
```

### Count Publications

```bash
grep -c "^@" files/publications.bib
```

---

## Scripts Reference

### Primary Script: `bibtex_to_data.py`

**Location:** `.github/scripts/publications/bibtex_to_data.py`

**Purpose:** Converts BibTeX → YAML data file with link validation

**Usage:**
```bash
uv run python .github/scripts/publications/bibtex_to_data.py
```

**What it does:**
- Reads `files/publications.bib`
- Generates `_data/publications.yml`
- Validates all external URLs (5-second timeout)
- Checks for local PDF files
- Generates validation report

### Alternative Script: `bibtex_to_publications.py`

**Location:** `.github/scripts/publications/bibtex_to_publications.py`

**Purpose:** Converts BibTeX → Individual markdown files

**Usage:**
```bash
uv run python .github/scripts/publications/bibtex_to_publications.py
```

**Note:** This script may be deprecated if you're using the data file workflow.

### Configuration Options

Edit the script to adjust validation behavior:

```python
# Disable URL validation (faster but less thorough)
VALIDATE_URLS = False  # Line 26

# Adjust timeout for slow connections
TIMEOUT = 10  # Line 25 (default is 5 seconds)
```

---

## Troubleshooting

### Publications not showing on website

**Check:**
1. Did you run `bibtex_to_data.py` after editing BibTeX?
2. Did you restart Jekyll? (`docker compose down && docker compose -f .github/dev/docker-compose.yaml up`)
3. Check `_data/publications.yml` was generated
4. Visit `http://localhost:4000/publications/`

### PDF link doesn't work

**Check:**
1. PDF file exists in `files/papers/` directory
2. Path in BibTeX is relative to `files/` (not absolute)
3. No `files/` prefix in the `pdf` field
4. Jekyll includes `files` in `_config.yml`:
   ```yaml
   include:
     - files
   ```

### URL validation fails but link works in browser

Some websites block automated requests. Options:
1. Keep the URL anyway (it will work for users)
2. Disable URL validation: `VALIDATE_URLS = False`
3. Use a local PDF instead

### Site not updating after changes

**Try:**
```bash
# Full restart
docker compose down
docker compose -f .github/dev/docker-compose.yaml up --build

# Clear browser cache
# Hard reload: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)
```

### Author name not bolded

Make sure your name appears exactly as:
- "Carlo Ciliberto" or
- "C. Ciliberto"

Check the `_pages/publications.html` template if you need different formatting.

---

## File Structure

```
your-site/
├── files/
│   ├── publications.bib          ← Source of truth (edit this!)
│   └── papers/                    ← Local PDFs go here
│       ├── paper-name-2024.pdf
│       ├── another-paper-2023.pdf
│       └── ...
├── _data/
│   └── publications.yml           ← Auto-generated (don't edit)
├── _publications/                 ← May be deprecated (check if used)
│   ├── 2024-01-paper-name.md
│   └── ...
├── scripts/
│   └── publications/
│       ├── bibtex_to_data.py      ← Main script
│       ├── bibtex_to_publications.py
│       └── extract_to_bibtex.py
└── _pages/
    └── publications.html          ← Template (reads from data file)
```

---

## Example Workflow Session

Complete workflow from start to finish:

```bash
# 1. Edit BibTeX file
vim files/publications.bib

# 2. Add a local PDF (if needed)
cp ~/Downloads/awesome-paper.pdf files/papers/awesome-paper-2024.pdf

# 3. Update BibTeX entry
# (add: pdf = {papers/awesome-paper-2024.pdf})

# 4. Regenerate and validate
uv run python .github/scripts/publications/bibtex_to_data.py

# 5. Review validation report
# (fix any issues identified)

# 6. Preview locally
docker compose -f .github/dev/docker-compose.yaml up

# 7. Check in browser
open http://localhost:4000/publications/

# 8. Commit changes
git add files/publications.bib files/papers/ _data/publications.yml
git commit -m "Update publications"
git push
```

---

## Tips & Best Practices

1. **Prefer official sources** for URLs (conference proceedings, journals, ArXiv)
2. **Use local PDFs** for papers not available online
3. **Run validation regularly** before committing changes
4. **Organize PDFs consistently** (e.g., `paper-name-year.pdf`)
5. **Check validation report** to catch broken links early
6. **Keep BibTeX file clean** - use consistent formatting
7. **Test locally** before pushing to GitHub

---

## Current Status

- **Total publications:** 74
- **Format:** BibTeX (`files/publications.bib`)
- **Main script:** `.github/scripts/publications/bibtex_to_data.py`

---

## Getting Help

If you encounter issues:
1. Check this guide first
2. Review the validation report output
3. Check [MIGRATION_HISTORY.md](MIGRATION_HISTORY.md) for technical migration details
4. Search existing BibTeX entries for examples

---

## Summary

**Key Points:**
- ✅ `files/publications.bib` is your single source of truth
- ✅ Use `url` for external links, `pdf` for local files
- ✅ Place local PDFs in `files/papers/`
- ✅ Run `uv run python .github/scripts/publications/bibtex_to_data.py` after changes
- ✅ Review validation report and fix issues
- ✅ Preview with `docker compose -f .github/dev/docker-compose.yaml up` before pushing
- ✅ Publications page reads directly from `_data/publications.yml`

---

**End of Guide**
