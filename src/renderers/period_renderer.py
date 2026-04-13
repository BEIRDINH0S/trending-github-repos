import html
import logging
import os
from typing import Optional

from core import (
    BADGE_CONSISTENT_THRESHOLD,
    BADGE_TRENDING_THRESHOLD,
    DEFAULT_OUTPUT_DIR,
    GITHUB_BASE_URL,
    MAX_CONTRIBUTORS_DISPLAY,
    MONTH_NAMES,
    AggregatedData,
    AggregatedRepository,
    display_language,
)

from .css_styles import get_period_report_css

logger = logging.getLogger(__name__)

_ICON_HOME = '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'


class PeriodRenderer:
    """Renderer pour les rapports de période (hebdomadaire/mensuel)."""

    # Cache pour le CSS
    _css_cache: str = None

    GITHUB_BASE_URL = GITHUB_BASE_URL

    def __init__(self, base_dir: str = DEFAULT_OUTPUT_DIR):
        """Initialise le renderer.

        Args:
            base_dir (str): Dossier de base pour les rapports.
        """
        self.base_dir = base_dir

    @staticmethod
    def _format_number(number: int) -> str:
        """Formate un nombre avec des séparateurs.

        Args:
            number (int): Nombre à formater.

        Returns:
            str: Nombre formaté.
        """
        return f"{number:,}"

    @staticmethod
    def _escape_html(text: str) -> str:
        """Échappe le HTML.

        Args:
            text (str): Texte à échapper.

        Returns:
            str: Texte échappé.
        """
        return html.escape(text)

    def _generate_css(self) -> str:
        """Génère le CSS (avec cache)."""
        if PeriodRenderer._css_cache is None:
            PeriodRenderer._css_cache = get_period_report_css()
        return PeriodRenderer._css_cache

    def _generate_navbar(self, language: str, period_type: str, period_label: str) -> str:
        """Génère la barre de navigation supérieure pour les rapports de période.

        Args:
            language (str): Nom du langage.
            period_type (str): "weekly" ou "monthly".
            period_label (str): Libellé de la période (ex: "Week 15 - 2026").

        Returns:
            str: HTML de la navbar.
        """
        lang_cap = html.escape(display_language(language))
        lang_anchor = html.escape(language)
        period_type_cap = period_type.capitalize()
        period_label_esc = html.escape(period_label)

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
                    <a href="../../index.html#{period_type}" class="nav-breadcrumb-link">{period_type_cap}</a>
                    <span class="nav-breadcrumb-sep" aria-hidden="true">/</span>
                    <span class="nav-breadcrumb-current" aria-current="page">{period_label_esc}</span>
                </div>
            </div>
            <div class="top-nav-right" aria-label="Navigation">
                <a href="../../index.html#{period_type}" class="format-pill pill-html" aria-label="Back to dashboard">
                    ← Dashboard
                </a>
            </div>
        </div>
    </nav>"""

    def _generate_repo_row(self, repo: AggregatedRepository, index: int) -> str:
        """Génère une ligne de tableau pour un repo.

        Args:
            repo (Dict): Données du repo.
            index (int): Index (1-based).

        Returns:
            str: HTML de la ligne.
        """
        name = self._escape_html(repo["name"])
        url = self._escape_html(repo["url"])
        description = self._escape_html(repo["description"])
        language = self._escape_html(repo["language"])

        appearances = repo["appearances"]
        best_rank = repo["best_rank"]
        stars = self._format_number(repo["total_stars"])
        forks = self._format_number(repo["total_forks"])

        # Badges
        badges = []
        if appearances >= BADGE_CONSISTENT_THRESHOLD:
            badges.append('<span class="badge badge-consistent">Consistent</span>')
        elif appearances >= BADGE_TRENDING_THRESHOLD:
            badges.append('<span class="badge badge-trending">Trending</span>')
        elif appearances == 1:
            badges.append('<span class="badge badge-new">New</span>')

        badges_html = "".join(badges)

        # Contributeurs
        contributors = repo.get("built_by", [])[:MAX_CONTRIBUTORS_DISPLAY]
        contributors_html = ", ".join(
            f'<a href="{self.GITHUB_BASE_URL}/{self._escape_html(c)}" class="contributor-link">@{self._escape_html(c)}</a>'
            for c in contributors
        )

        return f"""
            <tr>
                <td><span class="rank-badge">{index}</span></td>
                <td>
                    <div class="repo-name"><a href="{url}" target="_blank">{name}</a></div>
                    <div class="repo-description">{description}</div>
                    {badges_html}
                </td>
                <td><span class="appearances">{appearances}d</span></td>
                <td>#{best_rank}</td>
                <td class="stats-inline">{stars}</td>
                <td class="stats-inline">{forks}</td>
                <td class="stats-inline">{language}</td>
                <td class="contributors">{contributors_html if contributors_html else "-"}</td>
            </tr>
        """

    def render(self, aggregated_data: AggregatedData, period_type: str) -> None:
        """Rend un rapport de période en HTML.

        Args:
            aggregated_data (Dict): Données agrégées.
            period_type (str): "weekly" ou "monthly".
        """
        if not aggregated_data:
            logger.warning("Aucune donnée agrégée à rendre")
            return

        metadata = aggregated_data["metadata"]
        repos = aggregated_data["repositories"]

        language = metadata["language"]
        period = metadata["period"]

        # Titre selon le type
        if period_type == "weekly":
            title = f"Week {metadata['week']} – {metadata['year']}"
            subtitle = f"{metadata['start_date']} to {metadata['end_date']}"
        else:  # monthly
            month_name = MONTH_NAMES[metadata['month']]
            title = f"{month_name} {metadata['year']}"
            subtitle = f"{metadata['start_date']} to {metadata['end_date']}"

        navbar = self._generate_navbar(language, period_type, title)

        # HTML
        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'    <title>{display_language(language)} Trending – {title} | GitHub Trends</title>',
            self._generate_css(),
            '</head>',
            '<body>',
            navbar,
            '    <div class="container">',
            '        <div class="header">',
            f'            <h1>{display_language(language)} Trending Repositories</h1>',
            f'            <div class="subtitle">{title}</div>',
            f'            <div class="subtitle">{subtitle}</div>',
            '        </div>',
            '        <div class="summary">',
            '            <h2>Summary</h2>',
            '            <div class="summary-grid">',
            '                <div class="summary-item">',
            '                    <div class="label">Period</div>',
            f'                    <div class="value">{title}</div>',
            '                </div>',
            '                <div class="summary-item">',
            '                    <div class="label">Days Analyzed</div>',
            f'                    <div class="value">{metadata["total_days"]}</div>',
            '                </div>',
            '                <div class="summary-item">',
            '                    <div class="label">Unique Repos</div>',
            f'                    <div class="value">{metadata["unique_repos"]}</div>',
            '                </div>',
            '                <div class="summary-item">',
            '                    <div class="label">Language</div>',
            f'                    <div class="value">{display_language(language)}</div>',
            '                </div>',
            '            </div>',
            '        </div>',
            '        <div class="content">',
            '            <div class="section">',
            '                <h2 class="section-title">Top Trending Repositories</h2>',
            '                <div class="table-wrapper">',
            '                <table class="repo-table">',
            '                    <thead>',
            '                        <tr>',
            '                            <th>#</th>',
            '                            <th>Repository</th>',
            '                            <th>Days</th>',
            '                            <th>Best Rank</th>',
            '                            <th>Stars</th>',
            '                            <th>Forks</th>',
            '                            <th>Language</th>',
            '                            <th>Built By</th>',
            '                        </tr>',
            '                    </thead>',
            '                    <tbody>',
        ]

        # Ajouter les repos
        for idx, repo in enumerate(repos, 1):
            html_parts.append(self._generate_repo_row(repo, idx))

        # Footer
        html_parts.extend([
            '                    </tbody>',
            '                </table>',
            '                </div>',  # .table-wrapper
            '            </div>',
            '        </div>',
            '        <div class="footer">',
            f'            <p>Generated on {metadata["end_date"]} &mdash; <a href="../../index.html" style="color:inherit">Back to {display_language(language)}</a></p>',
            '            <p>GitHub Trending Scraper</p>',
            '        </div>',
            '    </div>',
            '</body>',
            '</html>',
        ])

        # Créer le dossier
        folder = f"{period_type}"
        output_dir = os.path.join(self.base_dir, language, str(metadata["year"]), folder)
        os.makedirs(output_dir, exist_ok=True)

        # Nom du fichier
        filename = os.path.join(output_dir, f"{period}.html")

        # Écrire le fichier
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(html_parts))

            logger.info("Rapport %s créé : %s", period_type, filename)
        except Exception as e:
            logger.error("Erreur lors de la création de %s: %s", filename, e)
