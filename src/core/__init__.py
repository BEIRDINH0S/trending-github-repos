"""Module core contenant les constantes, enums et types du projet."""

from .constants import (
    BADGE_CONSISTENT_THRESHOLD,
    BADGE_TRENDING_THRESHOLD,
    DEFAULT_OUTPUT_DIR,
    GITHUB_BASE_URL,
    MAX_CONTRIBUTORS_DISPLAY,
    MAX_MONTH_NUMBER,
    MAX_WEEK_NUMBER,
    MIN_MONTH_NUMBER,
    MIN_WEEK_NUMBER,
    MONTH_NAMES,
    VALID_OUTPUT_FORMATS,
)
from .enums import OutputFormat, PeriodType
from .types import (
    AggregatedData,
    AggregatedRepository,
    DailyData,
    MonthlyMetadata,
    PeriodMetadata,
    RepositoryData,
    SummaryStats,
    WeeklyMetadata,
)

__all__ = [
    # Constants
    "GITHUB_BASE_URL",
    "DEFAULT_OUTPUT_DIR",
    "VALID_OUTPUT_FORMATS",
    "MIN_WEEK_NUMBER",
    "MAX_WEEK_NUMBER",
    "MIN_MONTH_NUMBER",
    "MAX_MONTH_NUMBER",
    "BADGE_CONSISTENT_THRESHOLD",
    "BADGE_TRENDING_THRESHOLD",
    "MAX_CONTRIBUTORS_DISPLAY",
    "MONTH_NAMES",
    # Enums
    "OutputFormat",
    "PeriodType",
    # Types
    "RepositoryData",
    "SummaryStats",
    "AggregatedRepository",
    "PeriodMetadata",
    "WeeklyMetadata",
    "MonthlyMetadata",
    "AggregatedData",
    "DailyData",
]
