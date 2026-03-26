"""Énumérations du projet."""

from enum import Enum


class OutputFormat(Enum):
    """Formats de sortie supportés."""

    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    CSV = "csv"

    @classmethod
    def from_string(cls, value: str) -> "OutputFormat":
        """Convertit une chaîne en OutputFormat.

        Args:
            value (str): Valeur string (case-insensitive).

        Returns:
            OutputFormat: Format correspondant.

        Raises:
            ValueError: Si le format n'est pas valide.
        """
        try:
            return cls(value.lower())
        except ValueError:
            valid_formats = [fmt.value for fmt in cls]
            raise ValueError(
                f"Invalid output format: {value}. "
                f"Valid formats: {', '.join(valid_formats)}"
            )


class PeriodType(Enum):
    """Types de périodes pour les rapports agrégés."""

    WEEKLY = "weekly"
    MONTHLY = "monthly"
