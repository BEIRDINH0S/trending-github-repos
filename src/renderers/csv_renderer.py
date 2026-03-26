import csv
import io
import logging
from typing import List

from core import RepositoryData

from .base_renderer import BaseRenderer

logger = logging.getLogger(__name__)


class CSVRenderer(BaseRenderer):
    """Renderer pour le format CSV."""

    def _get_file_extension(self) -> str:
        """Retourne l'extension de fichier CSV.

        Returns:
            str: Extension "csv".
        """
        return "csv"

    def _generate_content(self, language: str, trending_data: List[RepositoryData]) -> str:
        """Génère le contenu CSV complet.

        Args:
            language (str): Le nom du langage de programmation.
            trending_data (List[Dict]): La liste des repositories.

        Returns:
            str: Le contenu CSV formaté.
        """
        # Utiliser StringIO pour construire le CSV en mémoire
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        # En-tête du CSV
        headers = [
            "Rank",
            "Name",
            "URL",
            "Description",
            "Language",
            "Stars",
            "Forks",
            "Stars Today",
            "Contributors"
        ]
        writer.writerow(headers)

        # Ajouter chaque repository
        for rank, repo in enumerate(trending_data, 1):
            # Joindre les contributeurs en une seule chaîne
            contributors = "; ".join(repo.get("built_by", []))

            row = [
                rank,
                repo["name"],
                repo["url"],
                repo["description"],
                repo["language"],
                repo["stars"],
                repo["forks"],
                repo["stars_today"],
                contributors
            ]
            writer.writerow(row)

        # Récupérer le contenu
        content = output.getvalue()
        output.close()

        return content
