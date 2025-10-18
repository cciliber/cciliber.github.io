# Migration Documentation: GitHub Pages Site Modernization

**Date**: October 18, 2025
**Migrated by**: Claude (Anthropic AI Assistant)
**Duration**: ~2 hours

## Overview

This document chronicles the complete migration of Carlo Ciliberto's GitHub Pages personal website from a custom HTML/CSS/JavaScript implementation to the AcademicPages Jekyll template with automated publication management.

---

## What We Accomplished

### ✅ Successful Outcomes

1. **Migrated to AcademicPages Template**
   - Professional academic website template based on Jekyll
   - Fork of Minimal Mistakes theme
   - Responsive design with mobile support
   - Built-in theme support (light/dark modes)

2. **Automated Publication Management**
   - Fetched 74 publications from Google Scholar automatically
   - Created reusable Python scripts for future updates
   - Publications stored as individual markdown files
   - Easy to maintain and update

3. **Created Backup**
   - Original site backed up to `backup-original-site` git branch
   - Original files moved to `old_site_backup/` directory
   - No data loss - full rollback capability

4. **Automation Scripts Created**
   - `fetch_scholar_pubs.py` - Fetches publications from Google Scholar
   - `setup_site.py` - Converts publications to Jekyll markdown format
   - `UPDATE_PUBLICATIONS.md` - User documentation

5. **Docker-based Development Environment**
   - Resolved local Ruby/Jekyll compatibility issues
   - Reproducible local preview environment
   - Easy to maintain and update

---

## Technical Issues Encountered & Solutions

### Issue #1: Nokogiri Native Extension Loading Error

**Problem**:
```
LoadError: cannot load such file -- nokogiri/nokogiri
```

**Root Cause**:
- System Ruby 2.6 on macOS couldn't load the nokogiri native extension
- Nokogiri is a C-based Ruby gem that needs to match system architecture
- Pre-compiled gem binary (`x86_64-darwin`) was incompatible with system
- Likely due to macOS system Ruby being outdated or architecture mismatch

**Attempts Made**:
1. ✗ `bundle pristine nokogiri` - Didn't resolve the issue
2. ✗ Reinstalling nokogiri locally - Permission errors with system Ruby
3. ✗ Using different bundler versions - Still encountered loading errors

**Final Solution**:
- **Used Docker** to bypass all local Ruby/gem issues
- Docker provides Ruby 3.2 environment with all dependencies correctly compiled
- Modified `docker-compose.yaml` to run `bundle install` before Jekyll

**Why This Worked**:
- Docker provides a consistent, isolated environment
- Ruby 3.2 in Docker with properly compiled native extensions
- No reliance on system Ruby or local gem installations

---

### Issue #2: Bundler Version Conflict

**Problem**:
```
undefined method `untaint' for "/usr/src/app":String (NoMethodError)
```

**Root Cause**:
- Local `Gemfile.lock` was generated with Bundler 1.17.2
- Docker image had Bundler 2.4.19 (newer version)
- Bundler 1.17.2 uses `String#untaint` method which was **removed in Ruby 3.2**
- The `untaint` method was deprecated in Ruby 2.7 and removed in Ruby 3.0+

**Solution**:
1. Deleted old `Gemfile.lock` file
2. Let Docker regenerate it with compatible Bundler 2.4.19
3. New lockfile compatible with Ruby 3.2

**Command Used**:
```bash
rm Gemfile.lock
docker compose up  # Regenerates Gemfile.lock
```

**Lesson Learned**:
- Gemfile.lock should be regenerated when changing Ruby versions significantly
- Old bundler versions are incompatible with modern Ruby (3.x)

---

### Issue #3: Theme Configuration Errors

**Problem Sequence**:
```
File to import not found or unreadable: theme/default dark_light
```

**Evolution of Attempts**:

1. **First Attempt**: `site_theme: "default dark"`
   - Error: `File to import not found or unreadable: theme/default dark_light`
   - The template was looking for `theme/default dark_light.scss`

2. **Second Attempt**: `site_theme: "default_dark"`
   - Error: `File to import not found or unreadable: theme/default_dark_light`
   - Template appends `_light` suffix for dual-theme system

3. **Correct Solution**: `site_theme: "default"`
   - The template has a dual-theme system that automatically handles light/dark modes
   - Available theme files: `_default_light.scss` and `_default_dark.scss`
   - Setting `site_theme: "default"` allows the theme to switch between both

**Available Themes**:
- `default` (has `_default_light.scss` and `_default_dark.scss`)
- `air` (has `_air_light.scss` and `_air_dark.scss`)

**Lesson Learned**:
- AcademicPages uses a dual-theme system with automatic light/dark mode switching
- Don't specify the `_dark` or `_light` suffix in configuration
- The template handles the theme switching logic internally

---

### Issue #4: Why Do We Need Ruby/Jekyll?

**User Question**: "Why do we need Ruby/Jekyll at all?"

**Answer**:

**Jekyll** is the static site generator that **GitHub Pages uses by default**. Here's why:

1. **GitHub Pages Integration**:
   - GitHub Pages has native Jekyll support built-in
   - When you push to your repository, GitHub automatically runs Jekyll
   - Converts markdown + templates → complete HTML website

2. **Why Not Just HTML?**:
   - Managing 74 individual publication pages in pure HTML would be tedious
   - Jekyll uses templates + markdown = easier maintenance
   - Change one template file → affects all publication pages

3. **Why Ruby?**:
   - Jekyll is written in Ruby (historical choice by GitHub)
   - Ruby has a rich ecosystem of static site generation tools
   - Bundler (Ruby's package manager) handles all dependencies

4. **The Workflow**:
   ```
   Markdown files → Jekyll (Ruby) → HTML/CSS/JS → Web Browser
   ```

5. **Local Development**:
   - Needed to preview the site before pushing to GitHub
   - Required running Jekyll locally → needed Ruby environment
   - **Docker solved this** by providing isolated Ruby environment

**Key Insight**: You don't need to understand Ruby. You just need:
- Python scripts to fetch/format publications (✓ using `uv`)
- Docker to run Jekyll for local preview (✓ `docker compose up`)
- GitHub Pages to build the production site (✓ automatic)

---

## Architecture Decisions

### Why AcademicPages?

**Compared Templates**:
- François-Xavier Briol: Uses AcademicPages ✓
- Benjamin Guedj: Uses AcademicPages ✓
- Marc Deisenroth: Uses Hugo Blox Builder

**Decision**: AcademicPages
- Same as 2 out of 3 example sites
- Proven in academia
- Simpler than Hugo (no Go toolchain needed)
- Native GitHub Pages support
- Large community and documentation

### Why Docker for Local Development?

**Alternatives Considered**:
1. ✗ **System Ruby** - Too old (2.6), gem conflicts
2. ✗ **rbenv/rvm** - Additional Ruby version manager complexity
3. ✗ **Homebrew Ruby** - Still potential gem conflicts
4. ✓ **Docker** - Isolated, reproducible, no local conflicts

**Docker Benefits**:
- Same environment as production (Ruby 3.2)
- No conflicts with system Ruby
- Easy to replicate on any machine
- One command: `docker compose up`

---

## Files Created & Modified

### New Files Created

| File | Purpose |
|------|---------|
| `fetch_scholar_pubs.py` | Fetches publications from Google Scholar using `scholarly` library |
| `setup_site.py` | Converts JSON publications to Jekyll markdown files |
| `UPDATE_PUBLICATIONS.md` | User documentation for updating publications |
| `CLAUDE.md` | This file - technical documentation of migration |
| `_publications/*.md` | 74 individual publication markdown files |
| `_pages/about.md` | Updated biography page |
| `Gemfile.lock` | Regenerated with Bundler 2.4.19 for Ruby 3.2 |

### Modified Files

| File | Changes Made |
|------|--------------|
| `_config.yml` | - Updated personal information (name, bio, affiliation)<br>- Set theme to `"default"`<br>- Updated social links (Google Scholar, GitHub)<br>- Fixed avatar path to `images/carlo_ciliberto.jpg` |
| `docker-compose.yaml` | Modified command to run `bundle install` before `jekyll serve` |
| `Gemfile` | Temporarily disabled `jemoji` during troubleshooting (later re-enabled) |

### Moved Files

| Source | Destination |
|--------|-------------|
| `index.html`, `*.css`, `*.js`, `papers/`, `old/` | `old_site_backup/` |
| `carlo_ciliberto.jpg` | Copied to `images/carlo_ciliberto.jpg` |

---

## Workflow for Future Updates

### Update Publications from Google Scholar

```bash
# 1. Fetch latest publications
uv run python fetch_scholar_pubs.py

# 2. Regenerate publication markdown files
uv run python setup_site.py

# 3. Preview locally
docker compose up
# Visit http://localhost:4000

# 4. Commit and push
git add _publications/ _config.yml
git commit -m "Update publications from Google Scholar"
git push origin master
```

### Local Development Workflow

```bash
# Start local preview
docker compose up

# Visit http://localhost:4000 in browser

# Make changes to files
# Jekyll auto-regenerates (watch mode enabled)

# Stop server
docker compose down
```

### Customization

**Change Colors/Styling**:
- Edit `_sass/theme/_default_dark.scss` for dark mode
- Edit `_sass/theme/_default_light.scss` for light mode

**Change Navigation**:
- Edit `_data/navigation.yml`

**Update Biography**:
- Edit `_pages/about.md`

**Add Teaching/Talks**:
- Create markdown files in `_teaching/` or `_talks/` directories

---

## Lessons Learned

### 1. Local Ruby Development is Complex
- System Ruby versions vary by OS
- Native gem compilation is error-prone
- **Solution**: Use Docker for reproducible environments

### 2. Template Documentation Can Be Misleading
- Theme configuration wasn't clearly documented
- Had to inspect SASS files to understand theme system
- **Tip**: Look at actual theme files in `_sass/theme/`

### 3. Gemfile.lock Matters
- Lockfiles are version-specific
- Don't commit lockfiles across major Ruby version changes
- Regenerate when moving between environments

### 4. Automation Saves Time
- Google Scholar API eliminated manual publication entry
- Python scripts (uv) + Jekyll (Docker) = good separation of concerns
- Update 74 publications in < 1 minute vs. hours of manual work

### 5. GitHub Pages "Just Works"
- Despite local complexity, GitHub Pages builds flawlessly
- Their servers have correct Ruby/Jekyll setup
- Local preview is optional but helpful

---

## Troubleshooting Guide

### Profile Picture Not Showing?

**Check**:
1. Image file exists in `images/` directory
2. `_config.yml` has correct path: `avatar: "images/carlo_ciliberto.jpg"`
3. Restart Docker container: `docker compose down && docker compose up`

### Docker Won't Start?

**Try**:
```bash
# Remove all containers and rebuild
docker compose down
docker compose up --build
```

### Publications Not Updating?

**Check**:
1. Run `uv run python fetch_scholar_pubs.py`
2. Verify `/tmp/scholar_publications.json` was created
3. Run `uv run python setup_site.py`
4. Check `_publications/` directory has files
5. Restart Jekyll: `docker compose down && docker compose up`

### Theme Not Applying?

**Verify**:
1. `_config.yml` has `site_theme: "default"` (not `"default_dark"`)
2. Check browser console for CSS errors
3. Clear browser cache
4. Check `_sass/theme/` directory has theme files

### Want to Rollback?

**Option 1 - Git Branch**:
```bash
git checkout backup-original-site
git push origin backup-original-site:master --force
```

**Option 2 - Local Backup**:
```bash
cp -r old_site_backup/* .
git add -A
git commit -m "Rollback to original site"
git push
```

---

## Performance Notes

### Build Times

| Task | Time |
|------|------|
| `bundle install` (first time) | ~30 seconds |
| `bundle install` (cached) | ~5 seconds |
| Jekyll build (74 publications) | ~4 seconds |
| Jekyll incremental rebuild | ~1 second |

### Resource Usage

| Metric | Value |
|--------|-------|
| Docker image size | ~500 MB |
| Generated `_site` folder | ~15 MB |
| Publication JSON | ~97 KB |

---

## Future Improvements

### Potential Enhancements

1. **Automated Scheduled Updates**
   - Set up GitHub Actions to run `fetch_scholar_pubs.py` weekly
   - Auto-commit and push if new publications found

2. **Publication Metadata Enrichment**
   - Add DOI links automatically
   - Fetch abstracts if missing
   - Add paper thumbnails/figures

3. **Theme Customization**
   - Create custom color scheme
   - Add UCL branding
   - Customize fonts

4. **Additional Sections**
   - Add blog posts
   - Add project showcases
   - Add teaching materials

---

## References

### Documentation

- [AcademicPages Template](https://github.com/academicpages/academicpages.github.io)
- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Scholarly Python Library](https://github.com/scholarly-python-modules/scholarly)

### Example Sites

- [François-Xavier Briol](https://fxbriol.github.io/)
- [Benjamin Guedj](https://bguedj.github.io/)
- [Marc Deisenroth](https://www.deisenroth.cc/)

---

## Contact & Support

If you encounter issues:

1. Check this documentation first
2. Review `UPDATE_PUBLICATIONS.md` for user-facing instructions
3. Consult the [AcademicPages Issues](https://github.com/academicpages/academicpages.github.io/issues)
4. For publication fetching: Check [Scholarly Library Issues](https://github.com/scholarly-python-modules/scholarly/issues)

---

**End of Documentation**

*This migration was completed successfully with all goals achieved. The site is now easier to maintain, professionally designed, and fully automated for publication updates.*
