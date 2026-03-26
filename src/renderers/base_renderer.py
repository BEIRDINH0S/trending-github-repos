import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from core import DEFAULT_OUTPUT_DIR, GITHUB_BASE_URL, RepositoryData, SummaryStats

logger = logging.getLogger(__name__)


class BaseRenderer(ABC):
    """Classe de base abstraite pour tous les renderers."""

    # Constante héritée
    GITHUB_BASE_URL = GITHUB_BASE_URL

    def __init__(self, base_dir: str = DEFAULT_OUTPUT_DIR):
        """Initialise le renderer avec le dossier de base et les dates actuelles.

        Args:
            base_dir (str): Le chemin du dossier principal où stocker les rapports.
        """
        self.base_dir = base_dir
        self.today_date = datetime.now().strftime("%Y-%m-%d")
        self.current_year = datetime.now().strftime("%Y")

    @staticmethod
    def _format_number(number: int) -> str:
        """Formate un nombre avec des séparateurs de milliers.

        Args:
            number (int): Le nombre à formater.

        Returns:
            str: Nombre formaté (ex: 1234 -> "1,234").
        """
        return f"{number:,}"

    @staticmethod
    def _validate_repo(repo: RepositoryData) -> bool:
        """Valide qu'un repo contient toutes les données nécessaires.

        Args:
            repo (Dict): Dictionnaire du repository.

        Returns:
            bool: True si valide, False sinon.
        """
        required_fields = ["name", "url", "description", "stars", "forks", "language", "stars_today"]

        for field in required_fields:
            if field not in repo:
                logger.warning("Champ manquant '%s' dans le repo", field)
                return False

        return True

    def _calculate_summary_stats(self, trending_data: List[RepositoryData]) -> SummaryStats:
        """Calcule les statistiques de résumé.

        Args:
            trending_data (List[Dict]): Liste des repositories.

        Returns:
            Dict[str, object]: Statistiques calculées.
        """
        return {
            "total_repos": len(trending_data),
            "total_stars": sum(repo.get("stars", 0) for repo in trending_data),
            "total_forks": sum(repo.get("forks", 0) for repo in trending_data),
        }

    @abstractmethod
    def _generate_content(self, language: str, trending_data: List[RepositoryData]) -> str:
        """Génère le contenu dans le format spécifique du renderer.

        Args:
            language (str): Langage de programmation.
            trending_data (List[Dict]): Liste des repositories.

        Returns:
            str: Contenu formaté.
        """
        pass

    @abstractmethod
    def _get_file_extension(self) -> str:
        """Retourne l'extension de fichier pour ce format.

        Returns:
            str: Extension (ex: "md", "html", "json").
        """
        pass

    def render(self, language: str, trending_data: List[RepositoryData]) -> None:
        """Coordonne la création de l'arborescence et l'écriture du fichier.

        Args:
            language (str): Le nom du langage de programmation.
            trending_data (List[Dict]): La liste des repositories.
        """
        if not trending_data:
            logger.warning("Aucune donnée trouvée pour %s. Fichier ignoré.", language)
            return

        # Filtrer les repos invalides
        valid_repos = [repo for repo in trending_data if self._validate_repo(repo)]

        if not valid_repos:
            logger.error("Aucun repo valide trouvé pour %s", language)
            return

        if len(valid_repos) < len(trending_data):
            logger.warning(
                "Certains repos invalides ont été ignorés pour %s (%d/%d valides)",
                language,
                len(valid_repos),
                len(trending_data)
            )

        # Créer le dossier par date
        date_dir = os.path.join(self.base_dir, language, self.current_year, self.today_date)
        os.makedirs(date_dir, exist_ok=True)

        # Générer le nom de fichier
        extension = self._get_file_extension()
        filename = os.path.join(date_dir, f"report.{extension}")
        logger.info("Création du fichier : %s", filename)

        try:
            content = self._generate_content(language, valid_repos)

            with open(filename, "w", encoding="utf-8") as file:
                file.write(content)

            logger.info("Résultats pour %s enregistrés avec succès (%d repos)", language, len(valid_repos))
        except Exception as e:
            logger.error("Erreur lors de la création du fichier pour %s: %s", language, e)
