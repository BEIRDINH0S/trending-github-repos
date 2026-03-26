"""Styles CSS pour les renderers HTML - Style Data Dashboard."""

# CSS de base commun à tous les renderers HTML
BASE_CSS = """
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

            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: #FFFFFF;
                min-height: 100vh;
                box-shadow: 0 0 0 1px #E5E7EB;
            }

            .header {
                background: #1E293B;
                color: white;
                padding: 2rem 2.5rem;
                border-bottom: 3px solid #334155;
            }

            .header h1 {
                font-size: 1.75rem;
                margin-bottom: 0.25rem;
                font-weight: 600;
                color: #FFFFFF;
            }

            .header .subtitle {
                font-size: 0.875rem;
                color: #94A3B8;
                font-weight: 400;
            }

            .summary {
                background: #F8F9FA;
                padding: 2rem 2.5rem;
                border-bottom: 1px solid #E5E7EB;
            }

            .summary h2 {
                color: #1E293B;
                margin-bottom: 1rem;
                font-size: 1.25rem;
                font-weight: 600;
            }

            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
                margin-top: 1rem;
            }

            .summary-item {
                background: white;
                padding: 1.25rem;
                border-radius: 6px;
                border: 1px solid #E5E7EB;
            }

            .summary-item .label {
                font-size: 0.8125rem;
                color: #64748B;
                margin-bottom: 0.5rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                font-weight: 500;
            }

            .summary-item .value {
                font-size: 1.75rem;
                font-weight: 600;
                color: #1E293B;
            }

            .content {
                padding: 2rem 2.5rem;
            }

            .section-title {
                font-size: 1.5rem;
                color: #1E293B;
                margin-bottom: 1.5rem;
                padding-bottom: 0.75rem;
                border-bottom: 2px solid #E5E7EB;
                font-weight: 600;
            }

            .badge {
                display: inline-block;
                padding: 0.25rem 0.625rem;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 500;
                margin-right: 0.5rem;
            }

            .badge-stars {
                background: #FEF3C7;
                color: #92400E;
            }

            .badge-forks {
                background: #DBEAFE;
                color: #1E40AF;
            }

            .badge-language {
                background: #D1FAE5;
                color: #065F46;
            }

            .badge-today {
                background: #FEE2E2;
                color: #991B1B;
            }

            .badge-consistent {
                background: #D1FAE5;
                color: #065F46;
            }

            .badge-trending {
                background: #FEF3C7;
                color: #92400E;
            }

            .badge-new {
                background: #DBEAFE;
                color: #1E40AF;
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
                .header {
                    padding: 1.5rem;
                }

                .summary {
                    padding: 1.5rem;
                }

                .content {
                    padding: 1.5rem;
                }

                .summary-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """

# CSS spécifique pour les cartes de repos (daily reports)
REPO_CARD_CSS = """
        <style>
            .repo-card {
                background: white;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                transition: box-shadow 0.2s, border-color 0.2s;
            }

            .repo-card:hover {
                border-color: #334155;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            }

            .repo-header {
                display: flex;
                align-items: flex-start;
                gap: 1rem;
                margin-bottom: 1rem;
            }

            .repo-rank {
                background: #334155;
                color: white;
                min-width: 36px;
                height: 36px;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 1rem;
                flex-shrink: 0;
            }

            .repo-title {
                flex: 1;
            }

            .repo-title a {
                color: #1E293B;
                text-decoration: none;
                font-size: 1.125rem;
                font-weight: 600;
            }

            .repo-title a:hover {
                color: #334155;
                text-decoration: underline;
            }

            .repo-description {
                color: #64748B;
                margin-bottom: 1rem;
                line-height: 1.6;
                font-size: 0.9375rem;
            }

            .repo-stats {
                display: flex;
                gap: 1.5rem;
                flex-wrap: wrap;
                margin-bottom: 1rem;
            }

            .contributors {
                margin-top: 1rem;
                padding-top: 1rem;
                border-top: 1px solid #E5E7EB;
            }

            .contributors-label {
                font-size: 0.8125rem;
                color: #64748B;
                margin-bottom: 0.5rem;
                font-weight: 500;
            }

            .contributors-list {
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
            }

            .contributor-link {
                color: #334155;
                text-decoration: none;
                font-size: 0.8125rem;
                font-weight: 500;
            }

            .contributor-link:hover {
                text-decoration: underline;
                color: #1E293B;
            }
        </style>
        """

# CSS spécifique pour les tableaux de repos (period reports)
REPO_TABLE_CSS = """
        <style>
            .section {
                margin-bottom: 2rem;
            }

            .repo-table {
                width: 100%;
                border-collapse: collapse;
                background: white;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                overflow: hidden;
                font-size: 0.9375rem;
            }

            .repo-table th {
                background: #F8F9FA;
                padding: 0.875rem 1rem;
                text-align: left;
                font-weight: 600;
                color: #1E293B;
                border-bottom: 2px solid #E5E7EB;
                font-size: 0.8125rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }

            .repo-table td {
                padding: 1rem;
                border-bottom: 1px solid #E5E7EB;
                vertical-align: middle;
            }

            .repo-table tbody tr {
                transition: background-color 0.15s;
            }

            .repo-table tbody tr:nth-child(even) {
                background: #F8F9FA;
            }

            .repo-table tbody tr:hover {
                background: #F1F5F9;
            }

            .repo-table tr:last-child td {
                border-bottom: none;
            }

            .repo-name {
                font-weight: 600;
            }

            .repo-name a {
                color: #1E293B;
                text-decoration: none;
            }

            .repo-name a:hover {
                color: #334155;
                text-decoration: underline;
            }

            .repo-description {
                color: #64748B;
                font-size: 0.875rem;
                margin-top: 0.25rem;
                line-height: 1.5;
            }

            .rank-badge {
                background: #334155;
                color: white;
                min-width: 28px;
                height: 28px;
                border-radius: 4px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 0.8125rem;
            }

            .appearances {
                color: #059669;
                font-weight: 600;
            }

            .stats-inline {
                color: #64748B;
                font-size: 0.875rem;
            }

            .contributors {
                font-size: 0.75rem;
                color: #64748B;
            }

            .contributor-link {
                color: #334155;
                text-decoration: none;
                font-weight: 500;
            }

            .contributor-link:hover {
                text-decoration: underline;
                color: #1E293B;
            }

            @media (max-width: 768px) {
                .repo-table {
                    font-size: 0.875rem;
                }

                .repo-table th,
                .repo-table td {
                    padding: 0.625rem 0.75rem;
                }
            }
        </style>
        """


def get_daily_report_css() -> str:
    """Retourne le CSS complet pour les rapports quotidiens.

    Returns:
        str: CSS combiné (base + cartes).
    """
    return BASE_CSS + REPO_CARD_CSS


def get_period_report_css() -> str:
    """Retourne le CSS complet pour les rapports de période.

    Returns:
        str: CSS combiné (base + tableaux).
    """
    return BASE_CSS + REPO_TABLE_CSS
