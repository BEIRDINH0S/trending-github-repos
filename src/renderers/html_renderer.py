import html
import logging
from typing import List

from core import RepositoryData, SummaryStats

from .css_styles import get_daily_report_css

from .base_renderer import BaseRenderer

logger = logging.getLogger(__name__)


class HTMLRenderer(BaseRenderer):
    """Renderer pour le format HTML avec style CSS moderne."""

    # Cache pour le CSS
    _css_cache: str = None

    def _get_file_extension(self) -> str:
        """Retourne l'extension de fichier HTML.

        Returns:
            str: Extension "html".
        """
        return "html"

    @staticmethod
    def _escape_html(text: str) -> str:
        """Échappe le HTML pour éviter les injections.

        Args:
            text (str): Texte à échapper.

        Returns:
            str: Texte échappé.
        """
        return html.escape(text)

    def _generate_css(self) -> str:
        """Génère le CSS moderne pour le document HTML (avec cache).

        Returns:
            str: Code CSS.
        """
        if HTMLRenderer._css_cache is None:
            HTMLRenderer._css_cache = get_daily_report_css()
        return HTMLRenderer._css_cache

    def _generate_repo_card(self, repo: RepositoryData, rank: int) -> str:
        """Génère une carte HTML pour un repository.

        Args:
            repo (Dict): Données du repository.
            rank (int): Position dans le classement.

        Returns:
            str: HTML de la carte.
        """
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
            f'        <div class="repo-rank">{rank}</div>',
            '        <div class="repo-title">',
            f'            <a href="{url}" target="_blank" rel="noopener noreferrer">{name}</a>',
            '        </div>',
            '    </div>',
            f'    <div class="repo-description">{description}</div>',
            '    <div class="repo-stats">',
            f'        <span class="badge badge-stars">⭐ {stars} stars</span>',
            f'        <span class="badge badge-forks">🍴 {forks} forks</span>',
            f'        <span class="badge badge-language">💻 {language}</span>',
            f'        <span class="badge badge-today">🔥 {stars_today}</span>',
            '    </div>',
        ]

        # Contributeurs
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
        """Génère la section de résumé en HTML.

        Args:
            language (str): Langage de programmation.
            stats (Dict[str, object]): Statistiques calculées.

        Returns:
            str: HTML de la section de résumé.
        """
        return f"""
        <div class="summary">
            <h2>Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="label">Date</div>
                    <div class="value">{self.today_date}</div>
                </div>
                <div class="summary-item">
                    <div class="label">Total Repositories</div>
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
                    <div class="value">{language.capitalize()}</div>
                </div>
            </div>
        </div>
        """

    def _generate_content(self, language: str, trending_data: List[RepositoryData]) -> str:
        """Génère le contenu HTML complet.

        Args:
            language (str): Le nom du langage de programmation.
            trending_data (List[Dict]): La liste des repositories.

        Returns:
            str: Le contenu HTML complet.
        """
        escaped_language = self._escape_html(language.capitalize())

        # Calculer les stats une seule fois
        stats = self._calculate_summary_stats(trending_data)

        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'    <title>Trending {escaped_language} Repositories - {self.today_date}</title>',
            self._generate_css(),
            '</head>',
            '<body>',
            '    <div class="container">',
            '        <div class="header">',
            f'            <h1>Trending {escaped_language} Repositories</h1>',
            f'            <div class="subtitle">{self.today_date}</div>',
            '        </div>',
            self._generate_summary_section(language, stats),
            '        <div class="content">',
            '            <h2 class="section-title">Trending Repositories</h2>',
        ]

        # Générer les cartes de repos
        for idx, repo in enumerate(trending_data, 1):
            html_parts.append(self._generate_repo_card(repo, idx))

        # Footer
        html_parts.extend([
            '        </div>',
            '        <div class="footer">',
            f'            <p>Last updated: {self.today_date}</p>',
            '            <p>Generated by GitHub Trending Scraper</p>',
            '        </div>',
            '    </div>',
            '</body>',
            '</html>',
        ])

        return "\n".join(html_parts)
