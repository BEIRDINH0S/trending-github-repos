"""
Script de régénération de tous les rapports HTML existants depuis les JSON sources.
Utilisé pour appliquer les changements de CSS/navbar sans re-scraper GitHub.
"""
import json
import logging
import os
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.dirname(__file__))

from aggregator import TrendingAggregator
from renderers import HTMLRenderer, PeriodRenderer

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DOCS_DIR = Path(__file__).parent.parent / "docs"


def regenerate_daily_reports() -> int:
    """Régénère tous les rapports HTML quotidiens depuis les JSON.

    Returns:
        int: Nombre de fichiers régénérés.
    """
    count = 0
    for json_path in sorted(DOCS_DIR.rglob("report.json")):
        date_dir = json_path.parent
        html_path = date_dir / "report.html"

        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)

            language = data["metadata"]["language"]
            date = data["metadata"]["date"]
            repos = data["repositories"]

            # Instancier le renderer et forcer la date du rapport
            renderer = HTMLRenderer(base_dir=str(DOCS_DIR))
            renderer.today_date = date

            content = renderer._generate_content(language, repos)

            with open(html_path, "w", encoding="utf-8") as f:
                f.write(content)

            count += 1
            logger.info("✓ %s / %s", language, date)

        except Exception as e:
            logger.error("✗ %s : %s", json_path, e)

    return count


def regenerate_period_reports() -> int:
    """Régénère tous les rapports HTML de période (weekly/monthly).

    Returns:
        int: Nombre de fichiers régénérés.
    """
    count = 0
    aggregator = TrendingAggregator(base_dir=str(DOCS_DIR))
    period_renderer = PeriodRenderer(base_dir=str(DOCS_DIR))

    for language_dir in sorted(DOCS_DIR.iterdir()):
        if not language_dir.is_dir() or language_dir.name.startswith('.'):
            continue
        language = language_dir.name

        for year_dir in sorted(language_dir.iterdir()):
            if not year_dir.is_dir():
                continue
            year = int(year_dir.name)

            # Weekly
            weekly_dir = year_dir / "weekly"
            if weekly_dir.exists():
                for html_file in sorted(weekly_dir.glob("*.html")):
                    period_str = html_file.stem  # ex: 2026-W15
                    try:
                        week = int(period_str.split("-W")[1])
                        data = aggregator.aggregate_weekly(language, year, week)
                        if data:
                            period_renderer.render(data, "weekly")
                            count += 1
                            logger.info("✓ %s / weekly / %s", language, period_str)
                    except Exception as e:
                        logger.error("✗ %s weekly %s : %s", language, period_str, e)

            # Monthly
            monthly_dir = year_dir / "monthly"
            if monthly_dir.exists():
                for html_file in sorted(monthly_dir.glob("*.html")):
                    period_str = html_file.stem  # ex: 2026-03
                    try:
                        month = int(period_str.split("-")[1])
                        data = aggregator.aggregate_monthly(language, year, month)
                        if data:
                            period_renderer.render(data, "monthly")
                            count += 1
                            logger.info("✓ %s / monthly / %s", language, period_str)
                    except Exception as e:
                        logger.error("✗ %s monthly %s : %s", language, period_str, e)

    return count


if __name__ == "__main__":
    logger.info("=== Régénération des rapports HTML ===")

    logger.info("--- Rapports quotidiens ---")
    daily_count = regenerate_daily_reports()
    logger.info("Régénérés : %d rapports quotidiens", daily_count)

    logger.info("--- Rapports de période ---")
    period_count = regenerate_period_reports()
    logger.info("Régénérés : %d rapports de période", period_count)

    logger.info("=== Total : %d fichiers HTML mis à jour ===", daily_count + period_count)
