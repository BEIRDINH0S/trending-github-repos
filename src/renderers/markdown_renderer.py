import logging
from typing import List

from core import RepositoryData, SummaryStats

from .base_renderer import BaseRenderer

logger = logging.getLogger(__name__)


class MarkdownRenderer(BaseRenderer):
    """Renderer pour le format Markdown."""

    # Constantes spécifiques au Markdown
    BADGE_BASE_URL = "https://img.shields.io/badge"
    BADGE_COLORS = {
        "stars": "yellow",
        "forks": "blue",
        "language": "green"
    }

    def _get_file_extension(self) -> str:
        """Retourne l'extension de fichier Markdown.

        Returns:
            str: Extension "md".
        """
        return "md"

    def _escape_badge_text(self, text: str) -> str:
        """Échappe le texte pour les badges shields.io.

        Args:
            text (str): Texte à échapper.

        Returns:
            str: Texte échappé.
        """
        # Remplacer les caractères spéciaux pour les badges
        return text.replace("-", "--").replace("_", "__").replace(" ", "_")

    def _generate_repo_badges(self, repo: RepositoryData) -> str:
        """Génère les badges pour un repository.

        Args:
            repo (Dict): Données du repository.

        Returns:
            str: Ligne avec les badges.
        """
        stars_text = self._escape_badge_text(self._format_number(repo["stars"]))
        forks_text = self._escape_badge_text(self._format_number(repo["forks"]))
        language_text = self._escape_badge_text(repo["language"])

        badges = [
            f"![Stars]({self.BADGE_BASE_URL}/Stars-{stars_text}-{self.BADGE_COLORS['stars']})",
            f"![Forks]({self.BADGE_BASE_URL}/Forks-{forks_text}-{self.BADGE_COLORS['forks']})",
            f"![Language]({self.BADGE_BASE_URL}/Language-{language_text}-{self.BADGE_COLORS['language']})"
        ]

        return " ".join(badges)

    def _generate_repo_card(self, repo: RepositoryData, rank: int) -> str:
        """Génère une carte Markdown détaillée pour un repository.

        Args:
            repo (Dict): Dictionnaire contenant les données du repository.
            rank (int): Position dans le classement.

        Returns:
            str: Carte Markdown formatée.
        """
        lines = []

        # Titre avec rang et nom
        lines.append(f"### {rank}. [{repo['name']}]({repo['url']})")
        lines.append("")

        # Badges de statistiques
        lines.append(self._generate_repo_badges(repo))
        lines.append("")

        # Description
        lines.append(f"**Description:** {repo['description']}")
        lines.append("")

        # Statistiques détaillées
        lines.append("**Stats:**")
        lines.append(f"- **Total Stars:** {self._format_number(repo['stars'])}")
        lines.append(f"- **Forks:** {self._format_number(repo['forks'])}")
        lines.append(f"- **Today:** {repo['stars_today']}")
        lines.append(f"- **Language:** {repo['language']}")
        lines.append("")

        # Contributeurs
        built_by = repo.get('built_by', [])
        if built_by:
            contributors_list = ", ".join(
                f"[{c}]({self.GITHUB_BASE_URL}/{c})" for c in built_by[:5]
            )
            lines.append(f"**Built by:** {contributors_list}")
            lines.append("")

        # Séparateur
        lines.append("---")
        lines.append("")

        return "\n".join(lines)

    def _generate_summary_section(self, language: str, stats: SummaryStats) -> str:
        """Génère la section de résumé du rapport.

        Args:
            language (str): Langage de programmation.
            stats (Dict[str, object]): Statistiques calculées.

        Returns:
            str: Section de résumé formatée.
        """
        lines = [
            "## Summary",
            "",
            f"- **Date:** {self.today_date}",
            f"- **Total Repositories:** {stats['total_repos']}",
            f"- **Total Stars:** {self._format_number(stats['total_stars'])}",
            f"- **Total Forks:** {self._format_number(stats['total_forks'])}",
            f"- **Language:** {language.capitalize()}",
            "",
            "---",
            ""
        ]

        return "\n".join(lines)

    def _generate_table_of_contents(self, trending_data: List[RepositoryData]) -> str:
        """Génère une table des matières pour naviguer rapidement.

        Args:
            trending_data (List[Dict]): Liste des repositories.

        Returns:
            str: Table des matières formatée.
        """
        lines = [
            "## Table of Contents",
            ""
        ]

        for idx, repo in enumerate(trending_data, 1):
            # Créer un lien d'ancre vers chaque repo
            repo_link = repo['name'].lower().replace('/', '')
            lines.append(f"{idx}. [{repo['name']}](#{idx}-{repo_link})")

        lines.append("")
        lines.append("---")
        lines.append("")

        return "\n".join(lines)

    def _generate_content(self, language: str, trending_data: List[RepositoryData]) -> str:
        """Génère le contenu Markdown complet.

        Args:
            language (str): Le nom du langage de programmation.
            trending_data (List[Dict]): La liste des repositories.

        Returns:
            str: Le contenu formaté en syntaxe Markdown.
        """
        lines = []

        # En-tête principal
        lines.append(f"# Trending {language.capitalize()} Repositories")
        lines.append(f"### {self.today_date}")
        lines.append("")
        lines.append("> Daily report of trending repositories in the GitHub community")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Calculer les stats une seule fois
        stats = self._calculate_summary_stats(trending_data)

        # Section de résumé
        lines.append(self._generate_summary_section(language, stats))

        # Table des matières
        lines.append(self._generate_table_of_contents(trending_data))

        # Section des repositories
        lines.append("## Trending Repositories")
        lines.append("")

        # Générer une carte pour chaque repo
        for idx, repo in enumerate(trending_data, 1):
            lines.append(self._generate_repo_card(repo, idx))

        # Footer
        lines.append("---")
        lines.append("")
        lines.append(f"*Last updated: {self.today_date}*")
        lines.append("")
        lines.append("*Generated by GitHub Trending Scraper*")
        lines.append("")

        return "\n".join(lines)
