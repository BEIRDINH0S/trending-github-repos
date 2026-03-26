import logging
import time
from typing import Dict, List, Optional, Protocol

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Renderer(Protocol):
    """Protocol définissant l'interface attendue pour le renderer."""

    def render(self, language: str, data: List[Dict]) -> None:
        """Rend les données pour un langage donné."""
        ...


class GitHubTrendingScraper:
    """Classe responsable de l'extraction des données depuis GitHub Trending."""

    # Sélecteurs CSS pour le parsing HTML
    SELECTORS = {
        "repository_block": "article",
        "repository_class": "Box-row",
        "title_container": "h2",
        "description": "p",
        "stats_container": "div",
        "language_item": "span[itemprop='programmingLanguage']",
        "stars_today": "span.float-sm-right",
        "avatar_img": "img.avatar",
    }

    # Constantes de configuration
    DEFAULT_RATE_LIMIT_DELAY = 2.0
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_TIMEOUT = 10
    NORMAL_BACKOFF_BASE = 2
    RATE_LIMIT_BACKOFF_BASE = 5

    # Constantes pour les valeurs par défaut
    GITHUB_BASE_URL = "https://github.com"
    DEFAULT_DESCRIPTION = "Pas de description"
    DEFAULT_STARS_TODAY = "0 stars today"

    def __init__(
        self,
        languages: List[str],
        rate_limit_delay: float = DEFAULT_RATE_LIMIT_DELAY,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        """Initialise le scraper avec une session persistante.

        Args:
            languages (List[str]): Liste des langages à scraper.
            rate_limit_delay (float): Délai en secondes entre chaque requête.
            max_retries (int): Nombre maximum de tentatives en cas d'échec.
        """
        self.languages = languages
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

    @staticmethod
    def _calculate_backoff(attempt: int, base: int = NORMAL_BACKOFF_BASE) -> float:
        """Calcule le délai de backoff exponentiel.

        Args:
            attempt (int): Numéro de la tentative.
            base (int): Base pour le calcul exponentiel.

        Returns:
            float: Délai en secondes.
        """
        return base**attempt

    def _get_page_soup(self, url: str, language: str) -> Optional[BeautifulSoup]:
        """Gère la partie réseau et transforme le HTML en objet exploitable avec retry.

        Args:
            url (str): URL à charger.
            language (str): Nom du langage pour le log d'erreur.

        Returns:
            Optional[BeautifulSoup]: L'objet BeautifulSoup ou None en cas d'échec.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    "Tentative %d/%d pour %s", attempt, self.max_retries, language
                )
                response = self.session.get(url, timeout=self.DEFAULT_TIMEOUT)
                response.raise_for_status()

                if not response.text.strip():
                    logger.warning("Réponse vide reçue pour %s", language)
                    return None

                return BeautifulSoup(response.text, "html.parser")

            except requests.exceptions.Timeout:
                logger.error(
                    "Timeout lors de la requête pour %s (tentative %d)",
                    language,
                    attempt,
                )
                if attempt < self.max_retries:
                    time.sleep(self._calculate_backoff(attempt))

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    logger.error("Rate limit atteint pour %s", language)
                    if attempt < self.max_retries:
                        time.sleep(
                            self._calculate_backoff(
                                attempt, self.RATE_LIMIT_BACKOFF_BASE
                            )
                        )
                else:
                    logger.error(
                        "Erreur HTTP %d pour %s: %s",
                        e.response.status_code,
                        language,
                        e,
                    )
                    return None

            except requests.exceptions.RequestException as e:
                logger.error("Erreur réseau pour %s: %s", language, e)
                if attempt < self.max_retries:
                    time.sleep(self._calculate_backoff(attempt))

        logger.error("Échec après %d tentatives pour %s", self.max_retries, language)
        return None

    @staticmethod
    def _parse_number(text: str) -> int:
        """Parse un nombre avec suffixes k/K (milliers) ou m/M (millions).

        Args:
            text (str): Texte contenant le nombre (ex: "1.2k", "3.5M", "1,234").

        Returns:
            int: Nombre parsé.
        """
        if not text:
            return 0

        text = text.strip().replace(",", "").lower()

        try:
            if "k" in text:
                return int(float(text.replace("k", "")) * 1000)
            elif "m" in text:
                return int(float(text.replace("m", "")) * 1000000)
            else:
                return int(text)
        except (ValueError, AttributeError):
            logger.warning("Impossible de parser le nombre: %s", text)
            return 0

    def _parse_basic_info(self, article) -> Dict[str, str]:
        """Extrait les informations textuelles de base (nom, url, desc).

        Args:
            article: Bloc HTML du dépôt (BeautifulSoup element).

        Returns:
            Dict[str, str]: Dictionnaire contenant name, url et description.
        """
        try:
            h2 = article.find(self.SELECTORS["title_container"])
            if not h2:
                logger.debug("Élément h2 non trouvé dans l'article")
                return {}

            a_tag = h2.find("a")
            if not a_tag or not a_tag.get("href"):
                logger.debug("Lien de dépôt non trouvé ou href manquant")
                return {}

            href = a_tag.get("href", "").strip("/")
            if not href:
                logger.debug("href vide après nettoyage")
                return {}

            p_tag = article.find(self.SELECTORS["description"])
            description = p_tag.text.strip() if p_tag else self.DEFAULT_DESCRIPTION

            return {
                "name": href,
                "url": f"{self.GITHUB_BASE_URL}/{href}",
                "description": description,
            }
        except Exception as e:
            logger.error("Erreur lors du parsing des infos de base: %s", e)
            return {}

    def _parse_stars_and_forks(self, stats_div) -> Dict[str, int]:
        """Extrait le nombre de stars et forks.

        Args:
            stats_div: Div contenant les statistiques.

        Returns:
            Dict[str, int]: Dictionnaire avec stars et forks.
        """
        data = {"stars": 0, "forks": 0}

        for a in stats_div.find_all("a"):
            try:
                href = a.get("href", "")
                text = a.text.strip()

                if href.endswith("/stargazers"):
                    data["stars"] = self._parse_number(text)
                elif href.endswith("/forks"):
                    data["forks"] = self._parse_number(text)
            except Exception as e:
                logger.debug("Erreur lors du parsing d'un lien de stats: %s", e)
                continue

        return data

    def _parse_stars_today(self, stats_div) -> str:
        """Extrait le nombre de stars aujourd'hui.

        Args:
            stats_div: Div contenant les statistiques.

        Returns:
            str: Texte des stars aujourd'hui.
        """
        try:
            today = stats_div.select_one(self.SELECTORS["stars_today"])
            if today:
                return today.text.strip()
        except Exception as e:
            logger.debug("Erreur lors du parsing des stars aujourd'hui: %s", e)

        return self.DEFAULT_STARS_TODAY

    def _parse_contributors(self, stats_div) -> List[str]:
        """Extrait la liste des contributeurs.

        Args:
            stats_div: Div contenant les statistiques.

        Returns:
            List[str]: Liste des noms de contributeurs.
        """
        try:
            return [
                img.get("alt", "").strip("@")
                for img in stats_div.select(self.SELECTORS["avatar_img"])
                if img.get("alt")
            ]
        except Exception as e:
            logger.debug("Erreur lors du parsing des contributeurs: %s", e)
            return []

    def _parse_stats(self, article) -> Dict[str, object]:
        """Extrait les compteurs et les contributeurs du bloc HTML.

        Args:
            article: Bloc HTML du dépôt (BeautifulSoup element).

        Returns:
            Dict[str, object]: Dictionnaire contenant stars, forks, stars_today et built_by.
        """
        data = {
            "stars": 0,
            "forks": 0,
            "stars_today": self.DEFAULT_STARS_TODAY,
            "built_by": [],
        }

        try:
            stats_div = article.find(self.SELECTORS["stats_container"], class_="f6")
            if not stats_div:
                logger.debug("Stats div non trouvé")
                return data

            data.update(self._parse_stars_and_forks(stats_div))
            data["stars_today"] = self._parse_stars_today(stats_div)
            data["built_by"] = self._parse_contributors(stats_div)

        except Exception as e:
            logger.error("Erreur lors du parsing des stats: %s", e)

        return data

    def _validate_repo_data(self, repo: Dict[str, object]) -> bool:
        """Valide qu'un dépôt contient les données minimales requises.

        Args:
            repo (Dict[str, object]): Données du dépôt à valider.

        Returns:
            bool: True si les données sont valides, False sinon.
        """
        required_fields = ["name", "url", "description", "language"]

        for field in required_fields:
            if field not in repo or not repo[field]:
                logger.warning("Dépôt invalide: champ '%s' manquant ou vide", field)
                return False

        if not repo["url"].startswith(f"{self.GITHUB_BASE_URL}/"):
            logger.warning("URL invalide: %s", repo["url"])
            return False

        return True

    def fetch_repos(self, language: str) -> List[Dict[str, object]]:
        """Orchestre l'extraction pour un langage donné.

        Args:
            language (str): Langage cible.

        Returns:
            List[Dict[str, object]]: Liste des dépôts avec leurs métadonnées complètes.
        """
        url = f"{self.GITHUB_BASE_URL}/trending/{language}?since=daily"
        soup = self._get_page_soup(url, language)
        if not soup:
            logger.error("Impossible de charger la page pour %s", language)
            return []

        repos = []
        try:
            articles = soup.find_all(
                self.SELECTORS["repository_block"],
                class_=self.SELECTORS["repository_class"],
            )

            if not articles:
                logger.warning(
                    "Aucun article trouvé pour %s. La structure HTML a peut-être changé.",
                    language,
                )
                return []

            logger.info("Trouvé %d dépôts pour %s", len(articles), language)

            for idx, article in enumerate(articles, 1):
                try:
                    basic_info = self._parse_basic_info(article)
                    if not basic_info:
                        logger.debug(
                            "Impossible de parser l'article %d pour %s", idx, language
                        )
                        continue

                    repo_info = {**basic_info, **self._parse_stats(article)}

                    lang_tag = article.select_one(self.SELECTORS["language_item"])
                    repo_info["language"] = (
                        lang_tag.text.strip() if lang_tag else language.capitalize()
                    )

                    if self._validate_repo_data(repo_info):
                        repos.append(repo_info)
                    else:
                        logger.debug("Dépôt %d invalide pour %s", idx, language)

                except Exception as e:
                    logger.error(
                        "Erreur lors du traitement de l'article %d pour %s: %s",
                        idx,
                        language,
                        e,
                    )
                    continue

        except Exception as e:
            logger.error("Erreur lors du parsing des articles pour %s: %s", language, e)
            return []

        logger.info("Scraping réussi: %d dépôts valides pour %s", len(repos), language)
        return repos

    def scrape_all(self) -> Dict[str, List[Dict[str, object]]]:
        """Scrape tous les langages configurés.

        Returns:
            Dict[str, List[Dict[str, object]]]: Dictionnaire {langage: [repos]}.
        """
        logger.info("Début du scraping pour : %s", ", ".join(self.languages))
        logger.info("Délai entre requêtes : %.1fs", self.rate_limit_delay)
        logger.info("-" * 60)

        results = {}
        for idx, lang in enumerate(self.languages, 1):
            logger.info("[%d/%d] Traitement de %s...", idx, len(self.languages), lang)

            try:
                data = self.fetch_repos(lang)
                results[lang] = data

                if not data:
                    logger.warning("Aucun dépôt trouvé pour %s", lang)

            except Exception as e:
                logger.error("Erreur lors du traitement de %s: %s", lang, e)
                results[lang] = []

            if idx < len(self.languages):
                logger.debug(
                    "Pause de %.1fs avant la prochaine requête...",
                    self.rate_limit_delay,
                )
                time.sleep(self.rate_limit_delay)

        total_repos = sum(len(repos) for repos in results.values())
        logger.info("-" * 60)
        logger.info(
            "Scraping terminé: %d dépôts au total pour %d langages",
            total_repos,
            len(self.languages),
        )

        return results

    def run(self, renderer: Renderer) -> None:
        """Lance le processus complet de scraping et de rendu.

        Args:
            renderer (Renderer): Instance d'une classe possédant une méthode render.
        """
        results = self.scrape_all()

        for lang, data in results.items():
            if data:
                try:
                    renderer.render(lang, data)
                except Exception as e:
                    logger.error("Erreur lors du rendu pour %s: %s", lang, e)
