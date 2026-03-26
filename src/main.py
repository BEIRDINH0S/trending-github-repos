import logging
from datetime import datetime
from typing import List

from aggregator import TrendingAggregator
from core import DEFAULT_OUTPUT_DIR, VALID_OUTPUT_FORMATS, OutputFormat
from index_generator import IndexGenerator
from renderers import CSVRenderer, HTMLRenderer, JSONRenderer, MarkdownRenderer, PeriodRenderer
from scraper import GitHubTrendingScraper

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)


def generate_period_reports(
    languages: List[str],
    output_dir: str = DEFAULT_OUTPUT_DIR
) -> None:
    """Génère les rapports hebdomadaires et mensuels.

    Args:
        languages (List[str]): Liste des langages.
        output_dir (str): Dossier de sortie.
    """
    logger.info("-" * 60)
    logger.info("Génération des rapports de période...")

    aggregator = TrendingAggregator(base_dir=output_dir)
    period_renderer = PeriodRenderer(base_dir=output_dir)

    # Date actuelle
    now = datetime.now()
    year = now.year
    week = now.isocalendar()[1]
    month = now.month

    for lang in languages:
        # Rapport hebdomadaire
        logger.info("Génération du rapport hebdomadaire pour %s (semaine %d)", lang, week)
        try:
            weekly_data = aggregator.aggregate_weekly(lang, year, week)
            if weekly_data:
                period_renderer.render(weekly_data, "weekly")
            else:
                logger.warning("Pas assez de données pour le rapport hebdomadaire de %s", lang)
        except Exception as e:
            logger.error("Erreur lors du rapport hebdomadaire pour %s: %s", lang, e)

        # Rapport mensuel
        logger.info("Génération du rapport mensuel pour %s (mois %d)", lang, month)
        try:
            monthly_data = aggregator.aggregate_monthly(lang, year, month)
            if monthly_data:
                period_renderer.render(monthly_data, "monthly")
            else:
                logger.warning("Pas assez de données pour le rapport mensuel de %s", lang)
        except Exception as e:
            logger.error("Erreur lors du rapport mensuel pour %s: %s", lang, e)


def main(
    languages: List[str],
    output_formats: List[str] = None,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    generate_periods: bool = True
) -> None:
    """Point d'entrée principal du scraper.

    Args:
        languages (List[str]): Liste des langages à scraper.
        output_formats (List[str]): Liste des formats de sortie.
                                   Par défaut: ["html", "json", "markdown", "csv"].
        output_dir (str): Dossier de sortie. Par défaut "./docs" pour GitHub Pages.
        generate_periods (bool): Générer les rapports hebdomadaires/mensuels.
    """
    if output_formats is None:
        output_formats = VALID_OUTPUT_FORMATS

    logger.info("=" * 60)
    logger.info("Démarrage du scraper GitHub Trending")
    logger.info("=" * 60)
    logger.info("Langages: %s", ", ".join(languages))
    logger.info("Formats de sortie: %s", ", ".join(output_formats))
    logger.info("Dossier de sortie: %s", output_dir)
    logger.info("Rapports de période: %s", "Oui" if generate_periods else "Non")
    logger.info("-" * 60)

    # Initialisation du scraper
    scraper = GitHubTrendingScraper(languages=languages)

    # Scraper les données une seule fois
    logger.info("Scraping des données...")
    results = scraper.scrape_all()

    # Mapping format -> renderer
    renderer_classes = {
        OutputFormat.HTML.value: HTMLRenderer,
        OutputFormat.MARKDOWN.value: MarkdownRenderer,
        OutputFormat.JSON.value: JSONRenderer,
        OutputFormat.CSV.value: CSVRenderer
    }

    # Générer les rapports dans chaque format
    for output_format in output_formats:
        try:
            # Valider le format
            format_enum = OutputFormat.from_string(output_format)
            format_value = format_enum.value
        except ValueError as e:
            logger.error("%s", e)
            continue

        logger.info("Génération des rapports au format %s", format_value)

        renderer_class = renderer_classes[format_value]
        renderer = renderer_class(base_dir=output_dir)

        # Rendre chaque langage
        for lang, data in results.items():
            if data:
                try:
                    renderer.render(lang, data)
                except Exception as e:
                    logger.error(
                        "Erreur lors du rendu %s pour %s: %s",
                        format_value,
                        lang,
                        e
                    )

    # Générer les rapports de période
    if generate_periods:
        generate_period_reports(languages, output_dir)

    # Générer la page d'accueil index.html
    logger.info("-" * 60)
    logger.info("Génération de la page d'accueil...")
    try:
        index_gen = IndexGenerator(docs_dir=output_dir)
        index_gen.generate()
    except Exception as e:
        logger.error("Erreur lors de la génération de index.html: %s", e)

    logger.info("=" * 60)
    logger.info("Scraping terminé avec succès!")
    logger.info("=" * 60)


if __name__ == "__main__":
    # Configuration
    MY_LANGUAGES = ["python", "javascript"]
    MY_FORMATS = VALID_OUTPUT_FORMATS  # Tous les formats
    MY_OUTPUT_DIR = DEFAULT_OUTPUT_DIR  # Pour GitHub Pages
    GENERATE_PERIODS = True  # Générer rapports hebdomadaires/mensuels

    # Exécution
    main(
        languages=MY_LANGUAGES,
        output_formats=MY_FORMATS,
        output_dir=MY_OUTPUT_DIR,
        generate_periods=GENERATE_PERIODS
    )
