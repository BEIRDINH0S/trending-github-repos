import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from core import (
    DEFAULT_OUTPUT_DIR,
    MAX_MONTH_NUMBER,
    MAX_WEEK_NUMBER,
    MIN_MONTH_NUMBER,
    MIN_WEEK_NUMBER,
    AggregatedData,
    DailyData,
)

logger = logging.getLogger(__name__)


class TrendingAggregator:
    """Agrège les données quotidiennes en rapports hebdomadaires et mensuels."""

    def __init__(self, base_dir: str = DEFAULT_OUTPUT_DIR):
        """Initialise l'agrégateur.

        Args:
            base_dir (str): Dossier contenant les rapports quotidiens.
        """
        self.base_dir = Path(base_dir)

    def _load_daily_json(self, language: str, year: str, date_str: str) -> Optional[Dict]:
        """Charge un fichier JSON quotidien.

        Args:
            language (str): Langage de programmation.
            year (str): Année (ex: "2026").
            date_str (str): Date au format YYYY-MM-DD.

        Returns:
            Optional[Dict]: Données JSON ou None si le fichier n'existe pas.
        """
        json_path = self.base_dir / language / year / date_str / "report.json"

        if not json_path.exists():
            logger.debug("Fichier non trouvé : %s", json_path)
            return None

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Erreur lors de la lecture de %s: %s", json_path, e)
            return None

    def _get_week_dates(self, year: int, week: int) -> Tuple[str, str]:
        """Calcule les dates de début et fin d'une semaine ISO.

        Args:
            year (int): Année.
            week (int): Numéro de semaine ISO (1-53).

        Returns:
            Tuple[str, str]: (date_debut, date_fin) au format YYYY-MM-DD.
        """
        # Utiliser fromisocalendar pour obtenir le lundi de la semaine
        week_start = datetime.fromisocalendar(year, week, 1)
        week_end = week_start + timedelta(days=6)

        return week_start.strftime("%Y-%m-%d"), week_end.strftime("%Y-%m-%d")

    def _get_month_dates(self, year: int, month: int) -> Tuple[str, str]:
        """Calcule les dates de début et fin d'un mois.

        Args:
            year (int): Année.
            month (int): Mois (1-12).

        Returns:
            Tuple[str, str]: (date_debut, date_fin) au format YYYY-MM-DD.
        """
        month_start = datetime(year, month, 1)

        # Dernier jour du mois
        if month == 12:
            month_end = datetime(year, 12, 31)
        else:
            next_month = datetime(year, month + 1, 1)
            month_end = next_month - timedelta(days=1)

        return month_start.strftime("%Y-%m-%d"), month_end.strftime("%Y-%m-%d")

    def _collect_daily_data(
        self,
        language: str,
        start_date: str,
        end_date: str
    ) -> List[DailyData]:
        """Collecte les données quotidiennes pour une période.

        Args:
            language (str): Langage de programmation.
            start_date (str): Date de début (YYYY-MM-DD).
            end_date (str): Date de fin (YYYY-MM-DD).

        Returns:
            List[Dict]: Liste des données quotidiennes.
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        daily_data = []
        current = start

        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            year_str = current.strftime("%Y")

            data = self._load_daily_json(language, year_str, date_str)
            if data:
                daily_data.append({
                    "date": date_str,
                    "data": data
                })

            current += timedelta(days=1)

        logger.info(
            "Collecté %d jours de données pour %s (%s à %s)",
            len(daily_data),
            language,
            start_date,
            end_date
        )

        return daily_data

    def _calculate_aggregated_stats(self, daily_data: List[DailyData]) -> Dict:
        """Calcule les statistiques agrégées à partir des données quotidiennes.

        Args:
            daily_data (List[Dict]): Données quotidiennes collectées.

        Returns:
            Dict: Statistiques agrégées.
        """
        # Dictionnaire pour accumuler les stats par repo
        repo_stats = defaultdict(lambda: {
            "name": "",
            "url": "",
            "description": "",
            "language": "",
            "appearances": 0,
            "best_rank": 999,
            "total_stars": 0,
            "total_forks": 0,
            "dates_seen": [],
            "built_by": set()
        })

        # Traiter chaque jour
        for day_info in daily_data:
            date = day_info["date"]
            repos = day_info["data"].get("repositories", [])

            for repo in repos:
                name = repo["name"]
                stats = repo_stats[name]

                # Mise à jour des infos de base (prendre les plus récentes)
                stats["name"] = name
                stats["url"] = repo["url"]
                stats["description"] = repo["description"]
                stats["language"] = repo["language"]

                # Compteurs
                stats["appearances"] += 1
                stats["best_rank"] = min(stats["best_rank"], repo.get("rank", 999))
                stats["total_stars"] = repo["stars"]  # Prendre la dernière valeur
                stats["total_forks"] = repo["forks"]
                stats["dates_seen"].append(date)

                # Contributeurs
                for contributor in repo.get("built_by", []):
                    stats["built_by"].add(contributor)

        # Convertir en liste et nettoyer
        aggregated_repos = []
        for name, stats in repo_stats.items():
            aggregated_repos.append({
                "name": stats["name"],
                "url": stats["url"],
                "description": stats["description"],
                "language": stats["language"],
                "appearances": stats["appearances"],
                "best_rank": stats["best_rank"],
                "total_stars": stats["total_stars"],
                "total_forks": stats["total_forks"],
                "dates_seen": sorted(stats["dates_seen"]),
                "built_by": sorted(list(stats["built_by"]))
            })

        # Trier par nombre d'apparitions, puis par best_rank
        aggregated_repos.sort(
            key=lambda x: (-x["appearances"], x["best_rank"])
        )

        return {
            "repositories": aggregated_repos,
            "total_days": len(daily_data),
            "unique_repos": len(aggregated_repos)
        }

    def aggregate_weekly(
        self,
        language: str,
        year: int,
        week: int
    ) -> Optional[AggregatedData]:
        """Agrège les données hebdomadaires.

        Args:
            language (str): Langage de programmation.
            year (int): Année.
            week (int): Numéro de semaine ISO.

        Returns:
            Optional[Dict]: Données agrégées ou None si pas de données.

        Raises:
            ValueError: Si week n'est pas entre 1 et 53.
        """
        if not MIN_WEEK_NUMBER <= week <= MAX_WEEK_NUMBER:
            raise ValueError(f"Week must be between 1 and 53, got {week}")

        logger.info("Agrégation hebdomadaire: %s - %d-W%02d", language, year, week)

        start_date, end_date = self._get_week_dates(year, week)
        daily_data = self._collect_daily_data(language, start_date, end_date)

        if not daily_data:
            logger.warning("Aucune donnée trouvée pour %s semaine %d-%02d", language, year, week)
            return None

        stats = self._calculate_aggregated_stats(daily_data)

        return {
            "metadata": {
                "language": language,
                "year": year,
                "week": week,
                "period": f"{year}-W{week:02d}",
                "start_date": start_date,
                "end_date": end_date,
                "total_days": stats["total_days"],
                "unique_repos": stats["unique_repos"]
            },
            "repositories": stats["repositories"]
        }

    def aggregate_monthly(
        self,
        language: str,
        year: int,
        month: int
    ) -> Optional[AggregatedData]:
        """Agrège les données mensuelles.

        Args:
            language (str): Langage de programmation.
            year (int): Année.
            month (int): Mois (1-12).

        Returns:
            Optional[Dict]: Données agrégées ou None si pas de données.

        Raises:
            ValueError: Si month n'est pas entre 1 et 12.
        """
        if not MIN_MONTH_NUMBER <= month <= MAX_MONTH_NUMBER:
            raise ValueError(f"Month must be between 1 and 12, got {month}")

        logger.info("Agrégation mensuelle: %s - %d-%02d", language, year, month)

        start_date, end_date = self._get_month_dates(year, month)
        daily_data = self._collect_daily_data(language, start_date, end_date)

        if not daily_data:
            logger.warning("Aucune donnée trouvée pour %s mois %d-%02d", language, year, month)
            return None

        stats = self._calculate_aggregated_stats(daily_data)

        return {
            "metadata": {
                "language": language,
                "year": year,
                "month": month,
                "period": f"{year}-{month:02d}",
                "start_date": start_date,
                "end_date": end_date,
                "total_days": stats["total_days"],
                "unique_repos": stats["unique_repos"]
            },
            "repositories": stats["repositories"]
        }
