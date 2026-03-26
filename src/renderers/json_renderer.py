import json
import logging
from typing import List

from core import RepositoryData

from .base_renderer import BaseRenderer

logger = logging.getLogger(__name__)


class JSONRenderer(BaseRenderer):
    """Renderer pour le format JSON."""

    def _get_file_extension(self) -> str:
        """Retourne l'extension de fichier JSON.

        Returns:
            str: Extension "json".
        """
        return "json"

    def _generate_content(self, language: str, trending_data: List[RepositoryData]) -> str:
        """Génère le contenu JSON complet.

        Args:
            language (str): Le nom du langage de programmation.
            trending_data (List[Dict]): La liste des repositories.

        Returns:
            str: Le contenu JSON formaté.
        """
        # Calculer les stats
        stats = self._calculate_summary_stats(trending_data)

        # Structure du document JSON
        document = {
            "metadata": {
                "date": self.today_date,
                "language": language,
                "total_repositories": stats["total_repos"],
                "total_stars": stats["total_stars"],
                "total_forks": stats["total_forks"],
                "generated_by": "GitHub Trending Scraper",
                "format_version": "1.0"
            },
            "repositories": []
        }

        # Ajouter chaque repository
        for rank, repo in enumerate(trending_data, 1):
            repo_data = {
                "rank": rank,
                "name": repo["name"],
                "url": repo["url"],
                "description": repo["description"],
                "language": repo["language"],
                "stars": repo["stars"],
                "forks": repo["forks"],
                "stars_today": repo["stars_today"],
                "built_by": repo.get("built_by", [])
            }
            document["repositories"].append(repo_data)

        # Convertir en JSON avec indentation
        return json.dumps(document, indent=2, ensure_ascii=False)
