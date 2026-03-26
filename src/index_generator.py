import logging
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class IndexGenerator:
    """Génère la page d'accueil index.html pour GitHub Pages."""

    def __init__(self, docs_dir: str = "./docs"):
        """Initialise le générateur d'index.

        Args:
            docs_dir (str): Chemin vers le dossier docs/.
        """
        self.docs_dir = Path(docs_dir)

    def _scan_reports(self) -> Dict[str, Dict[str, List[Dict]]]:
        """Scanne le dossier docs/ pour trouver tous les rapports.

        Returns:
            Dict[str, Dict[str, List[Dict]]]: {langage: {type: [rapports]}}.
            Types: "daily", "weekly", "monthly"
        """
        reports = defaultdict(lambda: {"daily": [], "weekly": [], "monthly": []})

        if not self.docs_dir.exists():
            logger.warning("Le dossier %s n'existe pas", self.docs_dir)
            return reports

        # Parcourir les dossiers de langages
        for language_dir in self.docs_dir.iterdir():
            if not language_dir.is_dir() or language_dir.name.startswith('.'):
                continue

            language = language_dir.name

            # Parcourir les années
            for year_dir in language_dir.iterdir():
                if not year_dir.is_dir():
                    continue

                year = year_dir.name

                # Rapports quotidiens (dans des sous-dossiers par date)
                for date_dir in year_dir.iterdir():
                    if not date_dir.is_dir() or date_dir.name in ["weekly", "monthly"]:
                        continue

                    date_str = date_dir.name

                    report_info = {
                        "date": date_str,
                        "year": year,
                        "language": language,
                        "files": {}
                    }

                    # Chercher report.html, report.json, etc.
                    for ext in ["html", "json", "md", "csv"]:
                        file_path = date_dir / f"report.{ext}"
                        if file_path.exists():
                            rel_path = file_path.relative_to(self.docs_dir)
                            report_info["files"][ext] = str(rel_path).replace("\\", "/")

                    if report_info["files"]:
                        reports[language]["daily"].append(report_info)

                # Rapports hebdomadaires
                weekly_dir = year_dir / "weekly"
                if weekly_dir.exists():
                    for html_file in weekly_dir.glob("*.html"):
                        period_str = html_file.stem  # 2026-W12
                        report_info = {
                            "period": period_str,
                            "year": year,
                            "language": language,
                            "type": "weekly",
                            "files": {
                                "html": str(html_file.relative_to(self.docs_dir)).replace("\\", "/")
                            }
                        }
                        reports[language]["weekly"].append(report_info)

                # Rapports mensuels
                monthly_dir = year_dir / "monthly"
                if monthly_dir.exists():
                    for html_file in monthly_dir.glob("*.html"):
                        period_str = html_file.stem  # 2026-03
                        report_info = {
                            "period": period_str,
                            "year": year,
                            "language": language,
                            "type": "monthly",
                            "files": {
                                "html": str(html_file.relative_to(self.docs_dir)).replace("\\", "/")
                            }
                        }
                        reports[language]["monthly"].append(report_info)

        # Trier par date/période (plus récent en premier)
        for language in reports:
            reports[language]["daily"].sort(key=lambda x: x["date"], reverse=True)
            reports[language]["weekly"].sort(key=lambda x: x["period"], reverse=True)
            reports[language]["monthly"].sort(key=lambda x: x["period"], reverse=True)

        return dict(reports)

    def _generate_css(self) -> str:
        """Génère le CSS pour la page d'accueil - Style Data Dashboard avec Sidebar.

        Returns:
            str: Code CSS.
        """
        return """
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #111827;
                background: #F8F9FA;
                min-height: 100vh;
            }

            .layout {
                display: flex;
                min-height: 100vh;
            }

            .sidebar {
                width: 260px;
                background: #1E293B;
                color: white;
                position: fixed;
                height: 100vh;
                overflow-y: auto;
                border-right: 1px solid #334155;
                z-index: 100;
            }

            .sidebar-header {
                padding: 2rem 1.5rem;
                border-bottom: 1px solid #334155;
            }

            .sidebar-title {
                font-size: 1.25rem;
                font-weight: 600;
                color: #FFFFFF;
                margin-bottom: 0.25rem;
            }

            .sidebar-subtitle {
                font-size: 0.75rem;
                color: #94A3B8;
            }

            .sidebar-search {
                padding: 1rem 1.5rem;
                border-bottom: 1px solid #334155;
            }

            .search-input {
                width: 100%;
                padding: 0.625rem 0.875rem;
                background: #334155;
                border: 1px solid #475569;
                border-radius: 4px;
                color: white;
                font-size: 0.875rem;
            }

            .search-input::placeholder {
                color: #94A3B8;
            }

            .search-input:focus {
                outline: none;
                border-color: #64748B;
            }

            .sidebar-nav {
                padding: 1rem 0;
            }

            .nav-item {
                padding: 0.75rem 1.5rem;
                cursor: pointer;
                transition: background 0.2s;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .nav-item:hover {
                background: #334155;
            }

            .nav-item.active {
                background: #334155;
                border-left: 3px solid #60A5FA;
            }

            .nav-item-name {
                font-size: 0.9375rem;
                font-weight: 500;
                color: #FFFFFF;
            }

            .nav-item-count {
                font-size: 0.75rem;
                color: #94A3B8;
                background: #475569;
                padding: 0.125rem 0.5rem;
                border-radius: 10px;
            }

            .main-content {
                flex: 1;
                margin-left: 260px;
                background: #FFFFFF;
            }

            .header {
                background: white;
                padding: 1.5rem 2.5rem;
                border-bottom: 1px solid #E5E7EB;
                position: sticky;
                top: 0;
                z-index: 50;
            }

            .breadcrumbs {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-size: 0.875rem;
                color: #64748B;
                margin-bottom: 1rem;
            }

            .breadcrumb-item {
                color: #64748B;
                text-decoration: none;
            }

            .breadcrumb-item:hover {
                color: #1E293B;
            }

            .breadcrumb-separator {
                color: #CBD5E1;
            }

            .breadcrumb-current {
                color: #1E293B;
                font-weight: 500;
            }

            .page-title {
                font-size: 1.75rem;
                font-weight: 600;
                color: #1E293B;
            }

            .content {
                padding: 2rem 2.5rem;
            }

            .stats {
                background: #F8F9FA;
                padding: 2rem;
                border-radius: 6px;
                margin-bottom: 2rem;
                border: 1px solid #E5E7EB;
            }

            .stats h2 {
                color: #1E293B;
                margin-bottom: 1rem;
                font-size: 1.25rem;
                font-weight: 600;
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
            }

            .stat-item {
                background: white;
                padding: 1.25rem;
                border-radius: 6px;
                border: 1px solid #E5E7EB;
                text-align: center;
            }

            .stat-value {
                font-size: 2rem;
                font-weight: 600;
                color: #1E293B;
            }

            .stat-label {
                font-size: 0.8125rem;
                color: #64748B;
                margin-top: 0.5rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                font-weight: 500;
            }

            .language-section {
                margin-bottom: 3rem;
            }

            .language-title {
                font-size: 1.5rem;
                color: #1E293B;
                margin-bottom: 1.5rem;
                padding-bottom: 0.75rem;
                border-bottom: 2px solid #E5E7EB;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 1rem;
            }

            .language-badge {
                background: #334155;
                color: white;
                padding: 0.375rem 0.875rem;
                border-radius: 4px;
                font-size: 0.8125rem;
                font-weight: 500;
            }

            .tabs {
                display: flex;
                gap: 0.5rem;
                border-bottom: 2px solid #E5E7EB;
                margin-bottom: 1.5rem;
            }

            .tab {
                padding: 0.75rem 1.25rem;
                background: transparent;
                border: none;
                border-bottom: 3px solid transparent;
                cursor: pointer;
                font-size: 0.9375rem;
                font-weight: 500;
                color: #64748B;
                transition: all 0.2s;
                margin-bottom: -2px;
            }

            .tab:hover {
                color: #1E293B;
                background: #F8F9FA;
            }

            .tab.active {
                color: #1E293B;
                border-bottom-color: #334155;
            }

            .tab-content {
                display: none;
            }

            .tab-content.active {
                display: block;
            }

            .reports-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                gap: 1rem;
            }

            .report-card {
                background: white;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                padding: 1.25rem;
                transition: box-shadow 0.2s, border-color 0.2s;
            }

            .report-card:hover {
                border-color: #334155;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            }

            .report-date {
                font-size: 1rem;
                font-weight: 600;
                color: #1E293B;
                margin-bottom: 0.875rem;
            }

            .report-links {
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
            }

            .format-link {
                display: inline-block;
                padding: 0.5rem 0.875rem;
                border-radius: 4px;
                text-decoration: none;
                font-size: 0.8125rem;
                font-weight: 500;
                transition: opacity 0.2s;
            }

            .format-link:hover {
                opacity: 0.85;
            }

            .format-html {
                background: #334155;
                color: white;
            }

            .format-json {
                background: #059669;
                color: white;
            }

            .format-md {
                background: #D97706;
                color: white;
            }

            .format-csv {
                background: #0891B2;
                color: white;
            }

            .footer {
                background: #F8F9FA;
                padding: 1.5rem 2.5rem;
                text-align: center;
                color: #64748B;
                font-size: 0.8125rem;
                border-top: 1px solid #E5E7EB;
            }

            @media (max-width: 768px) {
                .sidebar {
                    display: none;
                }

                .main-content {
                    margin-left: 0;
                }

                .header {
                    padding: 1.5rem;
                }

                .content {
                    padding: 1.5rem;
                }

                .reports-grid {
                    grid-template-columns: 1fr;
                }

                .tabs {
                    overflow-x: auto;
                }
            }

            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }

            ::-webkit-scrollbar-track {
                background: #1E293B;
            }

            ::-webkit-scrollbar-thumb {
                background: #475569;
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: #64748B;
            }
        </style>
        """

    def _generate_html(self, reports: Dict[str, Dict[str, List[Dict]]]) -> str:
        """Génère le HTML de la page d'accueil.

        Args:
            reports (Dict[str, List[Dict]]): Rapports trouvés.

        Returns:
            str: HTML complet.
        """
        # Calculer les stats
        total_reports = sum(
            len(lang_reports["daily"]) + len(lang_reports["weekly"]) + len(lang_reports["monthly"])
            for lang_reports in reports.values()
        )
        total_languages = len(reports)

        latest_date = ""
        if reports:
            all_dates = []
            for lang_reports in reports.values():
                for report in lang_reports["daily"]:
                    all_dates.append(report["date"])
            if all_dates:
                latest_date = max(all_dates)

        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '    <title>GitHub Trending Reports</title>',
            self._generate_css(),
            '</head>',
            '<body>',
            '    <div class="layout">',
            '        <!-- Sidebar -->',
            '        <div class="sidebar">',
            '            <div class="sidebar-header">',
            '                <div class="sidebar-title">GitHub Trends</div>',
            '                <div class="sidebar-subtitle">Repository Analytics</div>',
            '            </div>',
            '            <div class="sidebar-search">',
            '                <input type="text" class="search-input" placeholder="Search language..." id="searchInput" onkeyup="filterLanguages()">',
            '            </div>',
            '            <nav class="sidebar-nav" id="sidebarNav">',
        ]

        # Ajouter les items de navigation pour chaque langage
        for language, lang_reports in sorted(reports.items()):
            total = len(lang_reports["daily"]) + len(lang_reports["weekly"]) + len(lang_reports["monthly"])
            html_parts.extend([
                f'                <div class="nav-item" onclick="scrollToLanguage(\'{language}\')">',
                f'                    <span class="nav-item-name">{language.capitalize()}</span>',
                f'                    <span class="nav-item-count">{total}</span>',
                '                </div>',
            ])

        html_parts.extend([
            '            </nav>',
            '        </div>',
            '',
            '        <!-- Main Content -->',
            '        <div class="main-content">',
            '            <div class="header">',
            '                <div class="breadcrumbs">',
            '                    <a href="#" class="breadcrumb-item">Home</a>',
            '                    <span class="breadcrumb-separator">/</span>',
            '                    <span class="breadcrumb-current">Dashboard</span>',
            '                </div>',
            '                <h1 class="page-title">GitHub Trending Reports</h1>',
            '            </div>',
            '            <div class="content">',
        ])

        # Stats
        html_parts.extend([
            '            <div class="stats">',
            '                <h2>Statistics</h2>',
            '                <div class="stats-grid">',
            '                    <div class="stat-item">',
            f'                        <div class="stat-value">{total_languages}</div>',
            '                        <div class="stat-label">Languages</div>',
            '                    </div>',
            '                    <div class="stat-item">',
            f'                        <div class="stat-value">{total_reports}</div>',
            '                        <div class="stat-label">Total Reports</div>',
            '                    </div>',
            '                    <div class="stat-item">',
            f'                        <div class="stat-value">{latest_date if latest_date else "N/A"}</div>',
            '                        <div class="stat-label">Latest Update</div>',
            '                    </div>',
            '                </div>',
            '            </div>',
        ])

        # Section par langage
        for language, lang_reports in sorted(reports.items()):
            daily_reports = lang_reports.get("daily", [])
            weekly_reports = lang_reports.get("weekly", [])
            monthly_reports = lang_reports.get("monthly", [])

            total = len(daily_reports) + len(weekly_reports) + len(monthly_reports)

            html_parts.extend([
                f'            <div class="language-section" id="section-{language}">',
                '                <div class="language-title">',
                f'                    {language.capitalize()}',
                f'                    <span class="language-badge">{total} reports</span>',
                '                </div>',
                '                <div class="tabs">',
                f'                    <button class="tab active" onclick="showTab(event, \'{language}-daily\')">Daily ({len(daily_reports)})</button>',
                f'                    <button class="tab" onclick="showTab(event, \'{language}-weekly\')">Weekly ({len(weekly_reports)})</button>',
                f'                    <button class="tab" onclick="showTab(event, \'{language}-monthly\')">Monthly ({len(monthly_reports)})</button>',
                '                </div>',
            ])

            # Onglet Daily
            html_parts.extend([
                f'                <div id="{language}-daily" class="tab-content active">',
                '                    <div class="reports-grid">',
            ])

            for report in daily_reports:
                html_parts.append('                        <div class="report-card">')
                html_parts.append(f'                            <div class="report-date">{report["date"]}</div>')
                html_parts.append('                            <div class="report-links">')

                format_labels = {
                    "html": "HTML",
                    "json": "JSON",
                    "md": "MD",
                    "csv": "CSV"
                }

                for ext, label in format_labels.items():
                    if ext in report.get("files", {}):
                        file_path = report["files"][ext]
                        download_attr = ' download' if ext in ["json", "csv"] else ''
                        html_parts.append(
                            f'                                <a href="{file_path}" class="format-link format-{ext}"{download_attr}>{label}</a>'
                        )

                html_parts.append('                            </div>')
                html_parts.append('                        </div>')

            html_parts.extend([
                '                    </div>',
                '                </div>',
            ])

            # Onglet Weekly
            html_parts.extend([
                f'                <div id="{language}-weekly" class="tab-content">',
                '                    <div class="reports-grid">',
            ])

            for report in weekly_reports:
                html_parts.append('                        <div class="report-card">')
                html_parts.append(f'                            <div class="report-date">{report["period"]}</div>')
                html_parts.append('                            <div class="report-links">')

                if "html" in report.get("files", {}):
                    file_path = report["files"]["html"]
                    html_parts.append(
                        f'                                <a href="{file_path}" class="format-link format-html">View Report</a>'
                    )

                html_parts.append('                            </div>')
                html_parts.append('                        </div>')

            html_parts.extend([
                '                    </div>',
                '                </div>',
            ])

            # Onglet Monthly
            html_parts.extend([
                f'                <div id="{language}-monthly" class="tab-content">',
                '                    <div class="reports-grid">',
            ])

            for report in monthly_reports:
                html_parts.append('                        <div class="report-card">')
                html_parts.append(f'                            <div class="report-date">{report["period"]}</div>')
                html_parts.append('                            <div class="report-links">')

                if "html" in report.get("files", {}):
                    file_path = report["files"]["html"]
                    html_parts.append(
                        f'                                <a href="{file_path}" class="format-link format-html">View Report</a>'
                    )

                html_parts.append('                            </div>')
                html_parts.append('                        </div>')

            html_parts.extend([
                '                    </div>',
                '                </div>',
                '            </div>',
            ])

        # Footer
        current_year = datetime.now().year
        html_parts.extend([
            '            </div>',
            '            <div class="footer">',
            f'                <p>&copy; {current_year} GitHub Trending Scraper</p>',
            '                <p>Generated automatically with Python</p>',
            '            </div>',
            '        </div>',
            '    </div>',
            '    <script>',
            '        function showTab(event, tabId) {',
            '            const button = event.currentTarget;',
            '            const parent = button.parentElement.parentElement;',
            '            ',
            '            // Hide all tab contents in this section',
            '            parent.querySelectorAll(".tab-content").forEach(content => {',
            '                content.classList.remove("active");',
            '            });',
            '            ',
            '            // Deactivate all tabs in this section',
            '            parent.querySelectorAll(".tab").forEach(tab => {',
            '                tab.classList.remove("active");',
            '            });',
            '            ',
            '            // Show selected tab content',
            '            document.getElementById(tabId).classList.add("active");',
            '            button.classList.add("active");',
            '        }',
            '        ',
            '        function scrollToLanguage(language) {',
            '            const section = document.getElementById("section-" + language);',
            '            if (section) {',
            '                section.scrollIntoView({ behavior: "smooth", block: "start" });',
            '                ',
            '                // Highlight active nav item',
            '                document.querySelectorAll(".nav-item").forEach(item => {',
            '                    item.classList.remove("active");',
            '                });',
            '                event.currentTarget.classList.add("active");',
            '            }',
            '        }',
            '        ',
            '        function filterLanguages() {',
            '            const input = document.getElementById("searchInput");',
            '            const filter = input.value.toLowerCase();',
            '            const navItems = document.querySelectorAll(".nav-item");',
            '            ',
            '            navItems.forEach(item => {',
            '                const name = item.querySelector(".nav-item-name").textContent.toLowerCase();',
            '                if (name.includes(filter)) {',
            '                    item.style.display = "";',
            '                } else {',
            '                    item.style.display = "none";',
            '                }',
            '            });',
            '        }',
            '    </script>',
            '</body>',
            '</html>',
        ])

        return "\n".join(html_parts)

    def generate(self) -> None:
        """Génère le fichier index.html."""
        logger.info("Génération de index.html...")

        # Scanner les rapports
        reports = self._scan_reports()

        if not reports:
            logger.warning("Aucun rapport trouvé dans %s", self.docs_dir)
            # Créer quand même une page vide
            reports = {}

        # Générer le HTML
        html_content = self._generate_html(reports)

        # Écrire le fichier
        index_path = self.docs_dir / "index.html"
        index_path.parent.mkdir(parents=True, exist_ok=True)

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info("index.html créé avec succès : %s", index_path)
        logger.info("Langages trouvés : %s", ", ".join(reports.keys()) if reports else "aucun")
        logger.info("Total de rapports : %d", sum(len(r) for r in reports.values()))
