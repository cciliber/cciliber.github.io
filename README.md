# Carlo Ciliberto - Academic Website

Personal academic website built with [AcademicPages](https://academicpages.github.io/) Jekyll template.

**Live site:** [cciliber.github.io](https://cciliber.github.io)

---

## Quick Start

### Update Publications

**Option 1: Manual BibTeX editing**
```bash
# 1. Edit BibTeX file
vim .github/data/publications.bib

# 2. Add arXiv URLs automatically (optional)
uv run python .github/scripts/publications/match_arxiv_by_author.py

# 3. Regenerate data file
uv run python .github/scripts/publications/bibtex_to_data.py

# 4. Preview locally
docker compose -f .github/dev/docker-compose.yaml up

# 5. Visit http://localhost:4000/publications/
```

**Option 2: Export from Google Scholar**
1. Visit your [Google Scholar profile](https://scholar.google.com/citations?user=XUcUAisAAAAJ)
2. Select publications → Export → BibTeX
3. Save to `.github/data/publications.bib`
4. Run step 2-5 above

**See [.github/docs/PUBLICATION_MANAGEMENT.md](.github/docs/PUBLICATION_MANAGEMENT.md) for complete guide.**

---

## Repository Structure

```
cciliber.github.io/
├── _config.yml                   # Main Jekyll configuration
├── _pages/                       # Site pages (about, publications, CV, etc.)
├── _data/                        # YAML data files (publications, navigation, etc.)
├── files/                        # Public files (PDFs, papers, etc.)
├── images/                       # Images and profile photos
├── .github/                      # Repository meta files
│   ├── data/
│   │   └── publications.bib      # BibTeX source of truth
│   ├── scripts/publications/     # Publication management scripts
│   ├── docs/                     # Documentation
│   └── dev/                      # Docker development setup
└── old_site_backup/              # Backup of original HTML site
```

---

## Local Development

### Using Docker (Recommended)

The easiest way to preview your site locally:

```bash
docker compose -f .github/dev/docker-compose.yaml up
```

Visit: http://localhost:4000

Changes to markdown and HTML files will auto-reload. Configuration changes require restart.

### Using Local Ruby/Jekyll

If you prefer not to use Docker:

**macOS:**
```bash
brew install ruby node
gem install bundler
bundle install
bundle exec jekyll serve -l -H localhost
```

**Linux/WSL:**
```bash
sudo apt install ruby-dev ruby-bundler nodejs build-essential gcc make
bundle install
bundle exec jekyll serve -l -H localhost
```

**Note:** You may encounter Ruby gem compatibility issues on macOS. Docker is recommended for reliable local development.

---

## Managing Publications

### Source of Truth

**Edit this file:** `.github/data/publications.bib`

### Workflow

1. **Edit BibTeX file:** Add/edit/delete publications
2. **Regenerate data:** `uv run python .github/scripts/publications/bibtex_to_data.py`
3. **Preview:** `docker compose -f .github/dev/docker-compose.yaml up`
4. **Commit:** `git add .github/data/publications.bib _data/publications.yml && git commit -m "Update publications"`

### Adding Links

```bibtex
@inproceedings{paper2024,
  title = {My Paper Title},
  author = {Carlo Ciliberto and Others},
  year = {2024},
  url_paper = {https://arxiv.org/abs/...},               % External paper link
  local_paper = {papers/my-paper-2024.pdf},              % Local PDF (relative to files/)
  url_code = {https://github.com/user/repo},             % Code repository
  local_slides = {slides/presentation-2024.pdf},         % Local slides
}
```

**Note:** Old field names (`url`, `pdf`, `code`, etc.) still work for backward compatibility.

**Full documentation:** [.github/docs/PUBLICATION_MANAGEMENT.md](.github/docs/PUBLICATION_MANAGEMENT.md)

---

## Site Configuration

### Personal Information

Edit `_config.yml`:

```yaml
# Site settings
title: "Carlo Ciliberto"
name: "Carlo Ciliberto"
description: "Personal academic website"
author:
  name: "Carlo Ciliberto"
  bio: "Associate Professor @ UCL"
  location: "London, UK"
  employer: "University College London"
  # ... social links
```

### Theme Customization

**Current theme:** "default" (supports light/dark mode)

**Edit colors:**
- Dark mode: `_sass/theme/_default_dark.scss`
- Light mode: `_sass/theme/_default_light.scss`

### Navigation Menu

Edit `_data/navigation.yml`

---

## Common Tasks

### Update Profile Photo

1. Add image to `images/` directory
2. Update `_config.yml`:
   ```yaml
   avatar: "images/your-photo.jpg"
   ```

### Update CV

Replace `files/carlo_ciliberto_cv.pdf` with your latest CV.

### Update Biography

Edit `_pages/about.md`

### Add a New Page

1. Create markdown file in `_pages/`
2. Add to `_data/navigation.yml`

---

## Scripts

### Publication Management

| Script | Purpose |
|--------|---------|
| `.github/scripts/publications/match_arxiv_by_author.py` | Add arXiv URLs by fetching author's papers (recommended) |
| `.github/scripts/publications/bibtex_to_data.py` | Convert BibTeX → YAML data file (required) |
| `.github/scripts/publications/add_arxiv_urls.py` | Add arXiv URLs by searching one-by-one (slower alternative) |
| `.github/scripts/publications/bibtex_to_publications.py` | Convert BibTeX → Markdown files (alternative workflow) |
| `.github/scripts/publications/extract_to_bibtex.py` | Extract from legacy markdown → Temporary BibTeX file |

**Usage:**
```bash
uv run python .github/scripts/publications/bibtex_to_data.py
```

---

## Documentation

- **[.github/docs/PUBLICATION_MANAGEMENT.md](.github/docs/PUBLICATION_MANAGEMENT.md)** - Complete publication workflow guide
- **[.github/docs/MIGRATION_HISTORY.md](.github/docs/MIGRATION_HISTORY.md)** - Technical migration notes from HTML to Jekyll
- **[.github/docs/CONTRIBUTING.md](.github/docs/CONTRIBUTING.md)** - Contribution guidelines

---

## Deployment

### GitHub Pages

The site automatically deploys via GitHub Pages when you push to the `master` branch.

**Check deployment status:**
1. Go to repository settings
2. Navigate to "Pages" section
3. Verify source is set to `master` branch

**Site URL:** https://cciliber.github.io

### Build Status

GitHub Pages will automatically:
1. Run Jekyll build on push
2. Deploy to GitHub CDN
3. Update site within ~1 minute

**Note:** Local Ruby compatibility issues do NOT affect GitHub Pages builds. GitHub's servers have the correct Ruby/Jekyll environment.

---

## Troubleshooting

### Publications not showing

1. Did you run `bibtex_to_data.py`?
2. Did you restart Jekyll?
3. Check `_data/publications.yml` exists

### Site not updating

1. Check you pushed to `master` branch
2. Check GitHub Pages is enabled in repository settings
3. Wait 1-2 minutes for deployment

### Docker issues

```bash
# Full rebuild
docker compose -f .github/dev/docker-compose.yaml down
docker compose -f .github/dev/docker-compose.yaml up --build
```

### Ruby gem errors

Use Docker instead of local Ruby to avoid compatibility issues.

---

## Backup

The original HTML site is preserved in:
- **Directory:** `old_site_backup/`
- **Git branch:** `backup-original-site` (if created)

---

## About AcademicPages Template

This site is based on the [AcademicPages](https://academicpages.github.io/) template, which is a fork of the [Minimal Mistakes Jekyll Theme](https://mmistakes.github.io/minimal-mistakes/).

**Template Credits:**
- Originally forked by [Stuart Geiger](https://github.com/staeiou)
- Currently maintained by [Robert Zupko](https://github.com/rjzupkoii)
- Based on Minimal Mistakes by Michael Rose

**License:** MIT (see LICENSE file)

---

## Getting Help

1. Check documentation in `.github/docs/` directory
2. Review [AcademicPages documentation](https://academicpages.github.io/)
3. Check [Jekyll documentation](https://jekyllrb.com/docs/)
4. Open an issue on [AcademicPages GitHub](https://github.com/academicpages/academicpages.github.io/issues)

---

**Last updated:** October 2025
