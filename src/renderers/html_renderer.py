import html
import logging
from typing import List

from core import RepositoryData, SummaryStats, display_language

from .css_styles import get_daily_report_css

from .base_renderer import BaseRenderer

logger = logging.getLogger(__name__)

# SVG icons (Lucide style, stroke-based)
_ICON_STAR = '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>'
_ICON_FORK = '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><circle cx="18" cy="6" r="3"/><path d="M18 9v2c0 .6-.4 1-1 1H7c-.6 0-1-.4-1-1V9"/><line x1="12" y1="12" x2="12" y2="15"/></svg>'
_ICON_CODE = '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>'
_ICON_TREND = '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>'
_ICON_HOME = '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'


class HTMLRenderer(BaseRenderer):
    """Renderer pour le format HTML avec style CSS moderne."""

    # Cache pour le CSS
    _css_cache: str = None

    def _get_file_extension(self) -> str:
        return "html"

    @staticmethod
    def _escape_html(text: str) -> str:
        return html.escape(text)

    def _generate_css(self) -> str:
        if HTMLRenderer._css_cache is None:
            HTMLRenderer._css_cache = get_daily_report_css()
        return HTMLRenderer._css_cache

    def _generate_navbar(self, language: str) -> str:
        """Génère la barre de navigation supérieure.

        Args:
            language (str): Nom du langage (pour le breadcrumb et l'ancre index).

        Returns:
            str: HTML de la navbar.
        """
        lang_cap = self._escape_html(display_language(language))
        lang_anchor = self._escape_html(language)
        date = self._escape_html(self.today_date)

        return f"""
    <nav class="top-nav" aria-label="Site navigation">
        <div class="top-nav-inner">
            <div class="top-nav-left">
                <a href="../../../index.html" class="nav-logo" aria-label="GitHub Trends home">
                    {_ICON_HOME} GitHub Trends
                </a>
                <div class="nav-divider" aria-hidden="true"></div>
                <div class="top-nav-breadcrumbs" aria-label="Breadcrumb">
                    <a href="../../../index.html" class="nav-breadcrumb-link">Home</a>
                    <span class="nav-breadcrumb-sep" aria-hidden="true">/</span>
                    <a href="../../index.html" class="nav-breadcrumb-link">{lang_cap}</a>
                    <span class="nav-breadcrumb-sep" aria-hidden="true">/</span>
                    <a href="../../index.html#daily" class="nav-breadcrumb-link">Daily</a>
                    <span class="nav-breadcrumb-sep" aria-hidden="true">/</span>
                    <span class="nav-breadcrumb-current" aria-current="page">{date}</span>
                </div>
            </div>
            <div class="top-nav-right" aria-label="Other formats">
                <span class="format-label">Also available:</span>
                <a href="report.json" class="format-pill pill-json" download aria-label="Download JSON report">JSON</a>
                <a href="report.md" class="format-pill pill-md" download aria-label="Download Markdown report">MD</a>
                <a href="report.csv" class="format-pill pill-csv" download aria-label="Download CSV report">CSV</a>
            </div>
        </div>
    </nav>"""

    def _generate_repo_card(self, repo: RepositoryData, rank: int) -> str:
        """Génère une carte HTML pour un repository."""
        name = self._escape_html(repo["name"])
        url = self._escape_html(repo["url"])
        description = self._escape_html(repo["description"])
        language = self._escape_html(repo["language"])
        stars_today = self._escape_html(repo["stars_today"])

        stars = self._format_number(repo["stars"])
        forks = self._format_number(repo["forks"])

        html_parts = [
            '<div class="repo-card">',
            '    <div class="repo-header">',
            f'        <div class="repo-rank" aria-label="Rank {rank}">{rank}</div>',
            '        <div class="repo-title">',
            f'            <a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>',
            '        </div>',
            '    </div>',
            f'    <p class="repo-description">{description}</p>',
            '    <div class="repo-stats">',
            f'        <span class="badge badge-stars">{_ICON_STAR} {stars} stars</span>',
            f'        <span class="badge badge-forks">{_ICON_FORK} {forks} forks</span>',
            f'        <span class="badge badge-language">{_ICON_CODE} {language}</span>',
            f'        <span class="badge badge-today">{_ICON_TREND} {stars_today}</span>',
            '    </div>',
        ]

        built_by = repo.get('built_by', [])
        if built_by:
            html_parts.append('    <div class="contributors">')
            html_parts.append('        <div class="contributors-label">Built by:</div>')
            html_parts.append('        <div class="contributors-list">')

            for contributor in built_by[:5]:
                escaped_contributor = self._escape_html(contributor)
                contributor_url = f"{self.GITHUB_BASE_URL}/{escaped_contributor}"
                html_parts.append(
                    f'            <a href="{contributor_url}" class="contributor-link" target="_blank" rel="noopener noreferrer">@{escaped_contributor}</a>'
                )

            html_parts.append('        </div>')
            html_parts.append('    </div>')

        html_parts.append('</div>')
        return "\n".join(html_parts)

    def _generate_summary_section(self, language: str, stats: SummaryStats) -> str:
        """Génère la section de résumé en HTML."""
        return f"""
        <div class="summary">
            <h2>Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="label">Date</div>
                    <div class="value">{self.today_date}</div>
                </div>
                <div class="summary-item">
                    <div class="label">Repositories</div>
                    <div class="value">{stats['total_repos']}</div>
                </div>
                <div class="summary-item">
                    <div class="label">Total Stars</div>
                    <div class="value">{self._format_number(stats['total_stars'])}</div>
                </div>
                <div class="summary-item">
                    <div class="label">Total Forks</div>
                    <div class="value">{self._format_number(stats['total_forks'])}</div>
                </div>
                <div class="summary-item">
                    <div class="label">Language</div>
                    <div class="value">{display_language(language)}</div>
                </div>
            </div>
        </div>
        """

    def _generate_content(self, language: str, trending_data: List[RepositoryData]) -> str:
        """Génère le contenu HTML complet."""
        lang_display = self._escape_html(display_language(language))
        stats = self._calculate_summary_stats(trending_data)

        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'    <title>Trending {lang_display} – {self.today_date} | GitHub Trends</title>',
            self._generate_css(),
            '</head>',
            '<body>',
            self._generate_navbar(language),
            '    <div class="container">',
            '        <div class="header">',
            f'            <h1>Trending {lang_display} Repositories</h1>',
            f'            <div class="subtitle">{self.today_date}</div>',
            '        </div>',
            self._generate_summary_section(language, stats),
            '        <div class="content">',
            '            <h2 class="section-title">Trending Repositories</h2>',
        ]

        for idx, repo in enumerate(trending_data, 1):
            html_parts.append(self._generate_repo_card(repo, idx))

        html_parts.extend([
            '        </div>',
            '        <div class="footer">',
            f'            <p>Last updated: {self.today_date} &mdash; <a href="../../../index.html" style="color:inherit">Back to dashboard</a></p>',
            '            <p>Generated by GitHub Trending Scraper</p>',
            '        </div>',
            '    </div>',
            '</body>',
            '</html>',
        ])

        return "\n".join(html_parts)
