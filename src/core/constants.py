"""Constantes globales du projet."""

# URLs
GITHUB_BASE_URL = "https://github.com"

# Chemins
DEFAULT_OUTPUT_DIR = "./docs"

# Formats de sortie
VALID_OUTPUT_FORMATS = ["html", "json", "markdown", "csv"]

# Validation des périodes
MIN_WEEK_NUMBER = 1
MAX_WEEK_NUMBER = 53
MIN_MONTH_NUMBER = 1
MAX_MONTH_NUMBER = 12

# Badges et seuils
BADGE_CONSISTENT_THRESHOLD = 7  # Jours minimum pour être "consistent"
BADGE_TRENDING_THRESHOLD = 3    # Jours minimum pour être "trending"
MAX_CONTRIBUTORS_DISPLAY = 5    # Nombre max de contributeurs affichés

# Noms des mois
MONTH_NAMES = [
    "",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]
