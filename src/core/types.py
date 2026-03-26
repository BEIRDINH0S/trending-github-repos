"""Types personnalisés pour le projet."""

from typing import List, TypedDict


class RepositoryData(TypedDict):
    """Structure de données pour un repository."""

    name: str
    url: str
    description: str
    language: str
    stars: int
    forks: int
    stars_today: str
    rank: int
    built_by: List[str]


class SummaryStats(TypedDict):
    """Statistiques de résumé."""

    total_repos: int
    total_stars: int
    total_forks: int


class AggregatedRepository(TypedDict):
    """Structure de données pour un repository agrégé."""

    name: str
    url: str
    description: str
    language: str
    appearances: int
    best_rank: int
    total_stars: int
    total_forks: int
    dates_seen: List[str]
    built_by: List[str]


class PeriodMetadata(TypedDict):
    """Métadonnées pour un rapport de période."""

    language: str
    year: int
    period: str
    start_date: str
    end_date: str
    total_days: int
    unique_repos: int


class WeeklyMetadata(PeriodMetadata):
    """Métadonnées pour un rapport hebdomadaire."""

    week: int


class MonthlyMetadata(PeriodMetadata):
    """Métadonnées pour un rapport mensuel."""

    month: int


class AggregatedData(TypedDict):
    """Structure de données pour les données agrégées."""

    metadata: PeriodMetadata
    repositories: List[AggregatedRepository]


class DailyData(TypedDict):
    """Structure de données pour un jour de données."""

    date: str
    data: dict
