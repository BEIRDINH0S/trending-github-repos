# GitHub Trending Scraper

Automated daily scraper for GitHub trending repositories with multi-format reports and analytics dashboard.

## Features

- Daily scraping of GitHub trending repositories
- Multi-language support (Python, JavaScript, TypeScript, etc.)
- Multiple output formats: HTML, JSON, Markdown, CSV
- Weekly and monthly aggregated reports
- Professional analytics dashboard with sidebar navigation
- Automated GitHub Actions workflow

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/trending-github-repos.git
cd trending-github-repos

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Run manually

```bash
python src/main.py
```

Reports are generated in the `docs/` directory.

### Configure languages

Edit `src/main.py`:

```python
MY_LANGUAGES = ["python", "javascript", "rust"]  # Add your languages
```

### Automated daily execution

The GitHub Actions workflow runs automatically every day at midnight UTC.

Manually trigger: **Actions** > **Daily Trending Repos Scraper** > **Run workflow**

## Output Structure

```
docs/
├── index.html              # Dashboard homepage
├── python/
│   └── 2026/
│       ├── 2026-03-26/     # Daily reports
│       │   ├── report.html
│       │   ├── report.json
│       │   ├── report.md
│       │   └── report.csv
│       ├── weekly/         # Weekly aggregations
│       │   └── 2026-W13.html
│       └── monthly/        # Monthly aggregations
│           └── 2026-03.html
└── javascript/
    └── ...
```

## GitHub Pages

Enable GitHub Pages in your repository settings:
- **Source**: Deploy from a branch
- **Branch**: `main`
- **Folder**: `/docs`

Your dashboard will be available at: `https://yourusername.github.io/trending-github-repos/`

## Configuration

All settings are in `src/core/constants.py`:

```python
DEFAULT_OUTPUT_DIR = "./docs"
VALID_OUTPUT_FORMATS = ["html", "json", "markdown", "csv"]
```

## License

MIT
