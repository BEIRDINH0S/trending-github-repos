"""Styles CSS pour les renderers HTML — Thème Aurora Dark."""

# ── Design tokens & base (shared by all report pages) ─────────────────────────
BASE_CSS = """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            /* ── Design tokens ── */
            :root {
                /* Backgrounds */
                --bg-base:          #080C14;
                --bg-surface:       rgba(8, 18, 36, 0.72);
                --bg-elevated:      rgba(14, 28, 54, 0.80);
                --bg-hover:         rgba(22, 42, 78, 0.60);

                /* Borders */
                --border-default:   rgba(255, 255, 255, 0.06);
                --border-subtle:    rgba(255, 255, 255, 0.04);
                --border-hover:     rgba(56, 189, 248, 0.35);
                --border-glow:      rgba(139, 92, 246, 0.30);

                /* Accent palette */
                --color-primary:      #38BDF8;
                --color-primary-dark: #0EA5E9;
                --color-violet:       #A78BFA;
                --color-emerald:      #34D399;
                --color-amber:        #FBBF24;
                --color-rose:         #FB7185;
                --color-orange:       #FB923C;

                /* Glows */
                --glow-primary:  rgba(56, 189, 248, 0.14);
                --glow-violet:   rgba(167, 139, 250, 0.12);
                --glow-emerald:  rgba(52, 211, 153, 0.10);
                --glow-amber:    rgba(251, 191, 36, 0.14);

                /* Text */
                --text-primary:  #E2E8F0;
                --text-secondary:#94A3B8;
                --text-muted:    #64748B;
                --text-dim:      #475569;

                /* Navbar */
                --nav-bg:          rgba(6, 10, 20, 0.88);
                --nav-border:      rgba(255, 255, 255, 0.07);
                --nav-hover-bg:    rgba(255, 255, 255, 0.05);
                --nav-text:        #E2E8F0;
                --nav-text-muted:  #94A3B8;
                --nav-text-dim:    #64748B;
                --nav-accent:      #38BDF8;

                /* Sidebar aliases (used by index_generator too) */
                --sidebar-bg:      #080C14;
                --sidebar-hover:   rgba(255,255,255,0.05);
                --sidebar-border:  rgba(255,255,255,0.07);
                --sidebar-accent:  #38BDF8;

                /* Legacy aliases for backward-compat with renderer code */
                --color-background:    #080C14;
                --color-surface:       rgba(8, 18, 36, 0.72);
                --color-border:        rgba(255,255,255,0.08);
                --color-border-subtle: rgba(255,255,255,0.05);
                --color-text:          #E2E8F0;
                --color-text-muted:    #94A3B8;
                --color-text-subtle:   #64748B;
                --color-secondary:     #38BDF8;
                --color-accent:        #FBBF24;
                --color-primary-dark:  #0EA5E9;
            }

            /* ── Reset ── */
            *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

            /* ── Body + aurora background ── */
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                line-height: 1.65;
                color: var(--text-primary);
                background: var(--bg-base);
                min-height: 100vh;
                overflow-x: hidden;
            }

            /* Animated aurora mesh */
            body::before {
                content: '';
                position: fixed;
                inset: 0;
                background:
                    radial-gradient(ellipse 90% 60% at 15% 5%,  rgba(56, 189, 248, 0.08) 0%, transparent 60%),
                    radial-gradient(ellipse 70% 55% at 85% 85%, rgba(139, 92, 246, 0.07) 0%, transparent 55%),
                    radial-gradient(ellipse 55% 45% at 55% 40%, rgba(52, 211, 153, 0.04) 0%, transparent 50%),
                    radial-gradient(ellipse 40% 35% at 30% 75%, rgba(251, 191, 36, 0.03) 0%, transparent 50%);
                animation: aurora 24s ease-in-out infinite alternate;
                pointer-events: none;
                z-index: 0;
            }

            /* Dot-grid overlay */
            body::after {
                content: '';
                position: fixed;
                inset: 0;
                background-image: radial-gradient(rgba(255, 255, 255, 0.028) 1px, transparent 1px);
                background-size: 26px 26px;
                pointer-events: none;
                z-index: 0;
            }

            /* ── Keyframes ── */
            @keyframes aurora {
                0%   { opacity: 0.85; transform: scale(1.00) rotate(0deg); }
                40%  { opacity: 1.00; transform: scale(1.04) rotate(1.2deg); }
                100% { opacity: 0.90; transform: scale(1.02) rotate(-0.8deg); }
            }

            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(18px); }
                to   { opacity: 1; transform: translateY(0); }
            }

            @keyframes glowPulse {
                0%, 100% { box-shadow: 0 0 0 0   rgba(56,189,248,0.40); }
                50%       { box-shadow: 0 0 0 7px rgba(56,189,248,0.00); }
            }

            @keyframes shimmerSlide {
                0%   { background-position: -200% center; }
                100% { background-position:  200% center; }
            }

            @media (prefers-reduced-motion: reduce) {
                body::before { animation: none; }
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    transition-duration: 0.01ms !important;
                }
            }

            /* ── Links ── */
            a { color: inherit; text-decoration: none; }

            /* ── Scrollbar ── */
            ::-webkit-scrollbar          { width: 6px; height: 6px; }
            ::-webkit-scrollbar-track    { background: transparent; }
            ::-webkit-scrollbar-thumb    { background: rgba(255,255,255,0.10); border-radius: 3px; }
            ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.20); }

            /* ── Layout container ── */
            .container {
                max-width: 1400px;
                margin: 0 auto;
                min-height: 100vh;
                position: relative;
                z-index: 1;
            }

            /* ── Page header ── */
            .header {
                padding: 3rem 2.5rem 2.25rem;
                position: relative;
                overflow: hidden;
            }

            .header::before {
                content: '';
                position: absolute;
                inset: 0;
                background: linear-gradient(135deg,
                    rgba(56,189,248,0.07) 0%,
                    rgba(139,92,246,0.05) 50%,
                    transparent 100%);
                pointer-events: none;
            }

            /* Bottom accent line */
            .header::after {
                content: '';
                position: absolute;
                bottom: 0; left: 0; right: 0;
                height: 1px;
                background: linear-gradient(90deg,
                    transparent 0%,
                    rgba(56,189,248,0.50) 30%,
                    rgba(139,92,246,0.40) 70%,
                    transparent 100%);
            }

            .header h1 {
                font-family: 'Fira Code', monospace;
                font-size: 1.875rem;
                font-weight: 700;
                position: relative;
                z-index: 1;
                /* Gradient text */
                background: linear-gradient(120deg, #F1F5F9 0%, #38BDF8 45%, #A78BFA 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 0.5rem;
                line-height: 1.25;
                /* Shimmer effect */
                background-size: 200% auto;
                animation: shimmerSlide 6s linear infinite;
            }

            .header .subtitle {
                color: var(--text-secondary);
                font-size: 0.9375rem;
                position: relative;
                z-index: 1;
            }

            /* ── Summary ── */
            .summary {
                padding: 2rem 2.5rem;
                border-bottom: 1px solid var(--border-default);
                position: relative;
                z-index: 1;
            }

            .summary h2 {
                font-size: 0.6875rem;
                color: var(--text-muted);
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                margin-bottom: 1.25rem;
            }

            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
                gap: 1rem;
            }

            .summary-item {
                background: var(--bg-surface);
                padding: 1.25rem 1.5rem;
                border-radius: 12px;
                border: 1px solid var(--border-default);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
                animation: fadeInUp 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
            }

            .summary-item:nth-child(1) { animation-delay: 0.04s; }
            .summary-item:nth-child(2) { animation-delay: 0.09s; }
            .summary-item:nth-child(3) { animation-delay: 0.14s; }
            .summary-item:nth-child(4) { animation-delay: 0.19s; }
            .summary-item:nth-child(5) { animation-delay: 0.24s; }

            .summary-item:hover {
                border-color: var(--border-hover);
                box-shadow: 0 0 24px var(--glow-primary), 0 8px 32px rgba(0,0,0,0.3);
                transform: translateY(-2px);
            }

            .summary-item .label {
                font-size: 0.6875rem;
                color: var(--text-muted);
                margin-bottom: 0.625rem;
                text-transform: uppercase;
                letter-spacing: 0.09em;
                font-weight: 600;
            }

            .summary-item .value {
                font-family: 'Fira Code', monospace;
                font-size: 1.875rem;
                font-weight: 700;
                color: var(--color-primary);
                text-shadow: 0 0 18px rgba(56,189,248,0.35);
                line-height: 1;
            }

            /* ── Content area ── */
            .content {
                padding: 2rem 2.5rem;
                position: relative;
                z-index: 1;
            }

            .section-title {
                font-size: 0.75rem;
                color: var(--text-muted);
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.10em;
                margin-bottom: 1.5rem;
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }

            .section-title::after {
                content: '';
                flex: 1;
                height: 1px;
                background: linear-gradient(90deg, var(--border-default), transparent);
            }

            /* ── Badges ── */
            .badge {
                display: inline-flex;
                align-items: center;
                gap: 0.375rem;
                padding: 0.25rem 0.625rem;
                border-radius: 6px;
                font-size: 0.7rem;
                font-weight: 700;
                margin-right: 0.375rem;
                font-family: 'Fira Code', monospace;
                border: 1px solid transparent;
                letter-spacing: 0.02em;
                transition: box-shadow 0.2s;
            }

            .badge svg { flex-shrink: 0; }

            .badge-stars {
                background: rgba(251,191,36, 0.10);
                color: var(--color-amber);
                border-color: rgba(251,191,36, 0.22);
            }
            .badge-stars:hover { box-shadow: 0 0 10px var(--glow-amber); }

            .badge-forks {
                background: rgba(56,189,248, 0.10);
                color: var(--color-primary);
                border-color: rgba(56,189,248, 0.22);
            }

            .badge-language {
                background: rgba(52,211,153, 0.10);
                color: var(--color-emerald);
                border-color: rgba(52,211,153, 0.22);
            }

            .badge-today {
                background: rgba(251,113,133, 0.10);
                color: var(--color-rose);
                border-color: rgba(251,113,133, 0.22);
            }

            .badge-consistent {
                background: rgba(52,211,153, 0.10);
                color: var(--color-emerald);
                border-color: rgba(52,211,153, 0.22);
            }

            .badge-trending {
                background: rgba(251,191,36, 0.10);
                color: var(--color-amber);
                border-color: rgba(251,191,36, 0.22);
            }

            .badge-new {
                background: rgba(167,139,250, 0.10);
                color: var(--color-violet);
                border-color: rgba(167,139,250, 0.22);
            }

            /* ── Footer ── */
            .footer {
                padding: 2rem 2.5rem;
                text-align: center;
                color: var(--text-muted);
                font-size: 0.8125rem;
                border-top: 1px solid var(--border-default);
                position: relative;
                z-index: 1;
            }

            .footer a:hover { color: var(--color-primary); }

            /* ── Responsive ── */
            @media (max-width: 768px) {
                .header  { padding: 2rem 1.25rem 1.75rem; }
                .header h1 { font-size: 1.375rem; }
                .summary { padding: 1.5rem 1.25rem; }
                .content { padding: 1.5rem 1.25rem; }
                .summary-grid { grid-template-columns: repeat(2, 1fr); }
            }

            @media (max-width: 480px) {
                .summary-grid { grid-template-columns: 1fr; }
            }
        </style>"""

# ── Repo cards (daily reports) ────────────────────────────────────────────────
REPO_CARD_CSS = """
        <style>
            .repo-card {
                background: var(--bg-surface);
                border: 1px solid var(--border-default);
                border-radius: 14px;
                padding: 1.5rem;
                margin-bottom: 0.75rem;
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
                cursor: default;
                position: relative;
                overflow: hidden;
                animation: fadeInUp 0.45s cubic-bezier(0.22, 1, 0.36, 1) both;
            }

            /* Stagger entrance by position */
            .repo-card:nth-child(1)  { animation-delay: 0.03s; }
            .repo-card:nth-child(2)  { animation-delay: 0.07s; }
            .repo-card:nth-child(3)  { animation-delay: 0.11s; }
            .repo-card:nth-child(4)  { animation-delay: 0.15s; }
            .repo-card:nth-child(5)  { animation-delay: 0.19s; }
            .repo-card:nth-child(6)  { animation-delay: 0.23s; }
            .repo-card:nth-child(7)  { animation-delay: 0.27s; }
            .repo-card:nth-child(8)  { animation-delay: 0.31s; }
            .repo-card:nth-child(9)  { animation-delay: 0.35s; }
            .repo-card:nth-child(10) { animation-delay: 0.39s; }
            .repo-card:nth-child(n+11) { animation-delay: 0.43s; }

            /* Top-edge glow line, visible on hover */
            .repo-card::before {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, var(--color-primary), transparent);
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .repo-card:hover {
                border-color: rgba(56, 189, 248, 0.28);
                box-shadow:
                    0 0 0 1px rgba(56,189,248,0.10),
                    0 0 28px rgba(56,189,248,0.08),
                    0 8px 36px rgba(0,0,0,0.35);
                transform: translateY(-2px);
            }

            .repo-card:hover::before { opacity: 1; }

            /* ── Rank #1 gold / #2 silver / #3 bronze distinctions ── */
            .repo-card:nth-child(1) {
                border-color: rgba(251,191,36,0.20);
            }
            .repo-card:nth-child(1):hover {
                border-color: rgba(251,191,36,0.40);
                box-shadow:
                    0 0 0 1px rgba(251,191,36,0.15),
                    0 0 30px rgba(251,191,36,0.10),
                    0 8px 36px rgba(0,0,0,0.35);
            }
            .repo-card:nth-child(1)::before {
                background: linear-gradient(90deg, transparent, #FBBF24, transparent);
                opacity: 0.5;
            }

            .repo-card:nth-child(2) {
                border-color: rgba(203,213,225,0.12);
            }

            .repo-card:nth-child(3) {
                border-color: rgba(249,115,22,0.15);
            }

            /* ── Header row ── */
            .repo-header {
                display: flex;
                align-items: flex-start;
                gap: 1rem;
                margin-bottom: 0.875rem;
            }

            .repo-rank {
                min-width: 36px;
                height: 36px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: 'Fira Code', monospace;
                font-weight: 700;
                font-size: 0.875rem;
                flex-shrink: 0;
                color: #060B14;
                background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
                box-shadow: 0 0 12px rgba(56,189,248,0.28);
            }

            /* #1 gold badge + pulse animation */
            .repo-card:nth-child(1) .repo-rank {
                background: linear-gradient(135deg, #FBBF24, #F59E0B);
                box-shadow: 0 0 14px rgba(251,191,36,0.45);
                animation: glowPulse 2.8s ease-in-out infinite;
                color: #1A0F00;
            }

            /* #2 silver */
            .repo-card:nth-child(2) .repo-rank {
                background: linear-gradient(135deg, #CBD5E1, #94A3B8);
                box-shadow: 0 0 10px rgba(203,213,225,0.28);
                color: #1E293B;
            }

            /* #3 bronze */
            .repo-card:nth-child(3) .repo-rank {
                background: linear-gradient(135deg, #FB923C, #EA580C);
                box-shadow: 0 0 12px rgba(249,115,22,0.32);
                color: #1A0800;
            }

            .repo-title { flex: 1; min-width: 0; }

            .repo-title a {
                color: var(--text-primary);
                text-decoration: none;
                font-size: 1.0625rem;
                font-weight: 600;
                transition: color 0.15s, text-shadow 0.15s;
                cursor: pointer;
                display: block;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }

            .repo-title a:hover {
                color: var(--color-primary);
                text-shadow: 0 0 14px rgba(56,189,248,0.30);
            }

            .repo-description {
                color: var(--text-secondary);
                margin-bottom: 0.875rem;
                line-height: 1.65;
                font-size: 0.9375rem;
            }

            .repo-stats {
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
                margin-bottom: 0.875rem;
            }

            .contributors {
                margin-top: 0.875rem;
                padding-top: 0.875rem;
                border-top: 1px solid var(--border-default);
            }

            .contributors-label {
                font-size: 0.75rem;
                color: var(--text-muted);
                margin-bottom: 0.375rem;
                font-weight: 500;
            }

            .contributors-list {
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
            }

            .contributor-link {
                color: var(--text-secondary);
                text-decoration: none;
                font-size: 0.8125rem;
                font-weight: 500;
                transition: color 0.15s;
                cursor: pointer;
            }

            .contributor-link:hover { color: var(--color-primary); }
        </style>"""

# ── Repo table (weekly/monthly period reports) ────────────────────────────────
REPO_TABLE_CSS = """
        <style>
            .section { margin-bottom: 2rem; }

            .table-wrapper {
                width: 100%;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
                border-radius: 14px;
                border: 1px solid var(--border-default);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                animation: fadeInUp 0.45s cubic-bezier(0.22, 1, 0.36, 1) 0.08s both;
            }

            .repo-table {
                width: 100%;
                border-collapse: collapse;
                background: var(--bg-surface);
                font-size: 0.9375rem;
                min-width: 700px;
            }

            .repo-table th {
                background: rgba(255,255,255,0.025);
                padding: 0.875rem 1rem;
                text-align: left;
                font-weight: 700;
                color: var(--text-muted);
                border-bottom: 1px solid var(--border-default);
                font-size: 0.6875rem;
                text-transform: uppercase;
                letter-spacing: 0.10em;
                font-family: 'Fira Code', monospace;
                white-space: nowrap;
            }

            .repo-table td {
                padding: 1rem;
                border-bottom: 1px solid var(--border-subtle);
                vertical-align: middle;
                color: var(--text-secondary);
            }

            .repo-table tbody tr {
                transition: background-color 0.15s;
            }

            .repo-table tbody tr:hover {
                background: var(--bg-hover);
            }

            .repo-table tr:last-child td { border-bottom: none; }

            .repo-name { font-weight: 600; }

            .repo-name a {
                color: var(--text-primary);
                text-decoration: none;
                transition: color 0.15s;
                cursor: pointer;
            }

            .repo-name a:hover { color: var(--color-primary); }

            .repo-description {
                color: var(--text-muted);
                font-size: 0.8125rem;
                margin-top: 0.25rem;
                line-height: 1.5;
            }

            .rank-badge {
                background: linear-gradient(135deg, rgba(56,189,248,0.15), rgba(56,189,248,0.07));
                color: var(--color-primary);
                border: 1px solid rgba(56,189,248,0.20);
                min-width: 28px;
                height: 28px;
                border-radius: 6px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-family: 'Fira Code', monospace;
                font-weight: 700;
                font-size: 0.8125rem;
            }

            .appearances {
                color: var(--color-emerald);
                font-family: 'Fira Code', monospace;
                font-weight: 700;
                font-size: 0.875rem;
                text-shadow: 0 0 10px rgba(52,211,153,0.25);
            }

            .stats-inline {
                color: var(--text-secondary);
                font-family: 'Fira Code', monospace;
                font-size: 0.875rem;
            }

            .contributors {
                font-size: 0.75rem;
                color: var(--text-muted);
            }

            .contributor-link {
                color: var(--text-secondary);
                text-decoration: none;
                font-weight: 500;
                transition: color 0.15s;
                cursor: pointer;
            }

            .contributor-link:hover { color: var(--color-primary); }

            @media (max-width: 768px) {
                .repo-table th,
                .repo-table td { padding: 0.625rem 0.75rem; }
            }
        </style>"""

# ── Top navbar (glassmorphism — daily + period reports) ───────────────────────
# Note: depends on --nav-* tokens from BASE_CSS :root — always load BASE_CSS first.
TOP_NAV_CSS = """
        <style>
            .top-nav {
                background: var(--nav-bg, rgba(6,10,20,0.88));
                border-bottom: 1px solid var(--nav-border, rgba(255,255,255,0.07));
                position: sticky;
                top: 0;
                z-index: 200;
                backdrop-filter: blur(20px) saturate(160%);
                -webkit-backdrop-filter: blur(20px) saturate(160%);
            }

            .top-nav-inner {
                max-width: 1400px;
                margin: 0 auto;
                padding: 0 2.5rem;
                height: 52px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1.5rem;
            }

            .top-nav-left {
                display: flex;
                align-items: center;
                gap: 1.25rem;
                min-width: 0;
                overflow: hidden;
            }

            .nav-logo {
                font-family: 'Fira Code', monospace;
                font-size: 0.875rem;
                font-weight: 700;
                color: var(--nav-text, #E2E8F0);
                text-decoration: none;
                white-space: nowrap;
                flex-shrink: 0;
                transition: color 0.2s, text-shadow 0.2s;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .nav-logo:hover {
                color: var(--nav-accent, #38BDF8);
                text-shadow: 0 0 14px rgba(56,189,248,0.50);
            }

            .nav-divider {
                width: 1px;
                height: 16px;
                background: var(--nav-border, rgba(255,255,255,0.08));
                flex-shrink: 0;
            }

            .top-nav-breadcrumbs {
                display: flex;
                align-items: center;
                gap: 0.45rem;
                font-size: 0.8125rem;
                min-width: 0;
                overflow: hidden;
            }

            .nav-breadcrumb-link {
                color: var(--nav-text-muted, #94A3B8);
                text-decoration: none;
                white-space: nowrap;
                flex-shrink: 0;
                transition: color 0.15s;
            }

            .nav-breadcrumb-link:hover { color: var(--nav-accent, #38BDF8); }

            .nav-breadcrumb-sep {
                color: rgba(255,255,255,0.18);
                flex-shrink: 0;
                user-select: none;
            }

            .nav-breadcrumb-current {
                color: #CBD5E1;
                font-weight: 500;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            .top-nav-right {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                flex-shrink: 0;
            }

            .format-label {
                font-size: 0.75rem;
                color: var(--nav-text-dim, #64748B);
                white-space: nowrap;
            }

            .format-pill {
                display: inline-flex;
                align-items: center;
                padding: 0.2rem 0.625rem;
                border-radius: 6px;
                text-decoration: none;
                font-size: 0.6875rem;
                font-weight: 700;
                font-family: 'Fira Code', monospace;
                border: 1px solid transparent;
                letter-spacing: 0.04em;
                transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
                cursor: pointer;
                white-space: nowrap;
            }

            .format-pill:hover { transform: translateY(-1px); }

            .pill-json {
                background: rgba(251,191,36, 0.10);
                color: #FBBF24;
                border-color: rgba(251,191,36, 0.22);
            }
            .pill-json:hover {
                background: rgba(251,191,36, 0.18);
                box-shadow: 0 0 12px rgba(251,191,36,0.22);
            }

            .pill-md {
                background: rgba(52,211,153, 0.10);
                color: #34D399;
                border-color: rgba(52,211,153, 0.22);
            }
            .pill-md:hover {
                background: rgba(52,211,153, 0.18);
                box-shadow: 0 0 12px rgba(52,211,153,0.22);
            }

            .pill-csv {
                background: rgba(167,139,250, 0.10);
                color: #A78BFA;
                border-color: rgba(167,139,250, 0.22);
            }
            .pill-csv:hover {
                background: rgba(167,139,250, 0.18);
                box-shadow: 0 0 12px rgba(167,139,250,0.22);
            }

            .pill-html {
                background: rgba(56,189,248, 0.10);
                color: #38BDF8;
                border-color: rgba(56,189,248, 0.22);
            }
            .pill-html:hover {
                background: rgba(56,189,248, 0.18);
                box-shadow: 0 0 12px rgba(56,189,248,0.22);
            }

            @media (max-width: 768px) {
                .top-nav-inner { padding: 0 1rem; gap: 0.75rem; }
                .format-label  { display: none; }
                .nav-divider   { display: none; }
                .top-nav-breadcrumbs { font-size: 0.75rem; }
            }
        </style>"""


def get_daily_report_css() -> str:
    """Retourne le CSS complet pour les rapports quotidiens."""
    return BASE_CSS + TOP_NAV_CSS + REPO_CARD_CSS


def get_period_report_css() -> str:
    """Retourne le CSS complet pour les rapports de période (weekly/monthly)."""
    return BASE_CSS + TOP_NAV_CSS + REPO_TABLE_CSS
