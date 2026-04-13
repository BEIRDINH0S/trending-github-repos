"""
Générateur de pages HTML statiques pour GitHub Pages.

Architecture des pages :
  docs/index.html                     → dashboard global (cards par langage)
  docs/{language}/index.html          → page dédiée par langage (tabs daily/weekly/monthly)
  docs/{language}/2026/{date}/report.html  → rapport quotidien
  docs/{language}/2026/weekly/*.html  → rapports hebdomadaires
  docs/{language}/2026/monthly/*.html → rapports mensuels
"""

import logging
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from core.constants import display_language

logger = logging.getLogger(__name__)


# ── CSS partagé (design tokens + fonts) ───────────────────────────────────────

_SHARED_HEAD = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">"""

_TOKENS_CSS = """
        <style>
            /* ── Aurora Dark — Design tokens ── */
            :root {
                --bg-base:          #080C14;
                --bg-surface:       rgba(8, 18, 36, 0.72);
                --bg-elevated:      rgba(14, 28, 54, 0.80);
                --bg-hover:         rgba(22, 42, 78, 0.60);

                --border-default:   rgba(255,255,255,0.06);
                --border-subtle:    rgba(255,255,255,0.04);
                --border-hover:     rgba(56,189,248,0.35);

                --color-primary:      #38BDF8;
                --color-primary-dark: #0EA5E9;
                --color-violet:       #A78BFA;
                --color-emerald:      #34D399;
                --color-amber:        #FBBF24;
                --color-rose:         #FB7185;

                --glow-primary:  rgba(56,189,248,0.14);
                --glow-violet:   rgba(167,139,250,0.12);
                --glow-emerald:  rgba(52,211,153,0.10);
                --glow-amber:    rgba(251,191,36,0.14);

                --text-primary:  #E2E8F0;
                --text-secondary:#94A3B8;
                --text-muted:    #64748B;
                --text-dim:      #475569;

                --nav-bg:          rgba(6,10,20,0.90);
                --nav-border:      rgba(255,255,255,0.07);
                --nav-hover-bg:    rgba(255,255,255,0.05);
                --nav-text:        #E2E8F0;
                --nav-text-muted:  #94A3B8;
                --nav-text-dim:    #64748B;
                --nav-accent:      #38BDF8;

                --sidebar-bg:      #07090F;
                --sidebar-hover:   rgba(255,255,255,0.05);
                --sidebar-border:  rgba(255,255,255,0.07);
                --sidebar-accent:  #38BDF8;

                /* Legacy aliases (renderers use these) */
                --color-background:    #080C14;
                --color-surface:       rgba(8,18,36,0.72);
                --color-border:        rgba(255,255,255,0.08);
                --color-border-subtle: rgba(255,255,255,0.05);
                --color-text:          #E2E8F0;
                --color-text-muted:    #94A3B8;
                --color-text-subtle:   #64748B;
                --color-secondary:     #38BDF8;
                --color-accent:        #FBBF24;
            }

            *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

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
                    radial-gradient(ellipse 90% 60% at 15% 5%,  rgba(56,189,248,0.07) 0%, transparent 60%),
                    radial-gradient(ellipse 70% 55% at 85% 85%, rgba(139,92,246,0.06) 0%, transparent 55%),
                    radial-gradient(ellipse 55% 45% at 55% 40%, rgba(52,211,153,0.04) 0%, transparent 50%);
                animation: aurora 24s ease-in-out infinite alternate;
                pointer-events: none;
                z-index: 0;
            }

            /* Dot-grid overlay */
            body::after {
                content: '';
                position: fixed;
                inset: 0;
                background-image: radial-gradient(rgba(255,255,255,0.028) 1px, transparent 1px);
                background-size: 26px 26px;
                pointer-events: none;
                z-index: 0;
            }

            @keyframes aurora {
                0%   { opacity: 0.85; transform: scale(1.00) rotate(0deg); }
                50%  { opacity: 1.00; transform: scale(1.04) rotate(1.2deg); }
                100% { opacity: 0.90; transform: scale(1.02) rotate(-0.8deg); }
            }

            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(16px); }
                to   { opacity: 1; transform: translateY(0); }
            }

            @keyframes glowPulse {
                0%, 100% { box-shadow: 0 0 0 0   rgba(56,189,248,0.40); }
                50%       { box-shadow: 0 0 0 7px rgba(56,189,248,0.00); }
            }

            @media (prefers-reduced-motion: reduce) {
                body::before { animation: none; }
                *, *::before, *::after {
                    animation-duration: 0.01ms !important;
                    transition-duration: 0.01ms !important;
                }
            }

            a { color: inherit; text-decoration: none; }

            ::-webkit-scrollbar          { width: 6px; height: 6px; }
            ::-webkit-scrollbar-track    { background: transparent; }
            ::-webkit-scrollbar-thumb    { background: rgba(255,255,255,0.10); border-radius: 3px; }
            ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.20); }
        </style>"""

# ── CSS sidebar (main index uniquement) ───────────────────────────────────────

_SIDEBAR_CSS = """
        <style>
            /* ── Layout ── */
            .layout { display: flex; min-height: 100vh; position: relative; z-index: 1; }

            /* ── Sidebar ── */
            .sidebar {
                width: 252px;
                background: var(--sidebar-bg);
                color: var(--text-primary);
                position: fixed;
                height: 100vh;
                overflow-y: auto;
                border-right: 1px solid var(--sidebar-border);
                z-index: 100;
                display: flex;
                flex-direction: column;
            }

            .sidebar-header {
                padding: 1.5rem 1.25rem 1.25rem;
                border-bottom: 1px solid var(--sidebar-border);
                position: relative;
            }

            /* Accent glow under header */
            .sidebar-header::after {
                content: '';
                position: absolute;
                bottom: 0; left: 1.25rem; right: 1.25rem;
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(56,189,248,0.35), transparent);
            }

            .sidebar-logo {
                font-family: 'Fira Code', monospace;
                font-size: 0.9375rem;
                font-weight: 700;
                color: var(--text-primary);
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                margin-bottom: 0.25rem;
                transition: color 0.2s;
            }
            .sidebar-logo:hover {
                color: var(--color-primary);
                text-shadow: 0 0 12px rgba(56,189,248,0.40);
            }

            .sidebar-subtitle {
                font-size: 0.6875rem;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 600;
            }

            .sidebar-search {
                padding: 0.875rem 1.25rem;
                border-bottom: 1px solid var(--sidebar-border);
            }

            .search-input {
                width: 100%;
                padding: 0.5rem 0.75rem;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 8px;
                color: var(--text-primary);
                font-family: 'Inter', sans-serif;
                font-size: 0.8125rem;
                transition: border-color 0.2s, box-shadow 0.2s;
            }
            .search-input::placeholder { color: var(--text-muted); }
            .search-input:focus {
                outline: none;
                border-color: rgba(56,189,248,0.40);
                box-shadow: 0 0 0 3px rgba(56,189,248,0.08);
            }

            .sidebar-section-label {
                padding: 1rem 1.25rem 0.375rem;
                font-size: 0.625rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                color: var(--text-dim);
            }

            .sidebar-nav { flex: 1; padding-bottom: 1rem; }

            .sidebar-nav-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.5rem 1.25rem;
                text-decoration: none;
                color: var(--text-secondary);
                font-size: 0.875rem;
                font-weight: 500;
                transition: background 0.15s, color 0.15s;
                cursor: pointer;
                border-left: 2px solid transparent;
            }
            .sidebar-nav-item:hover {
                background: var(--sidebar-hover);
                color: var(--text-primary);
                border-left-color: rgba(56,189,248,0.35);
            }
            .sidebar-nav-item.active {
                background: rgba(56,189,248,0.06);
                color: var(--color-primary);
                border-left-color: var(--color-primary);
            }

            .nav-count {
                font-family: 'Fira Code', monospace;
                font-size: 0.6875rem;
                font-weight: 600;
                color: var(--text-dim);
                background: rgba(255,255,255,0.06);
                padding: 0.125rem 0.5rem;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.06);
            }

            /* ── Main content ── */
            .main-content {
                flex: 1;
                margin-left: 252px;
                position: relative;
                z-index: 1;
            }

            /* ── Sticky page header ── */
            .page-header {
                padding: 1.25rem 2rem;
                border-bottom: 1px solid var(--border-default);
                position: sticky;
                top: 0;
                z-index: 50;
                backdrop-filter: blur(20px) saturate(150%);
                -webkit-backdrop-filter: blur(20px) saturate(150%);
                background: rgba(6,10,20,0.85);
            }

            .page-header h1 {
                font-family: 'Fira Code', monospace;
                font-size: 1.25rem;
                font-weight: 700;
                background: linear-gradient(120deg, #F1F5F9 0%, #38BDF8 60%, #A78BFA 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .page-header-sub {
                font-size: 0.8125rem;
                color: var(--text-muted);
                margin-top: 0.25rem;
            }

            /* ── Content area ── */
            .content { padding: 2rem; }

            /* ── Stats bar ── */
            .stats-bar {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
                gap: 1rem;
                margin-bottom: 2rem;
            }

            .stat-card {
                background: var(--bg-surface);
                border: 1px solid var(--border-default);
                border-radius: 12px;
                padding: 1.25rem 1.5rem;
                text-align: center;
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                transition: border-color 0.22s, box-shadow 0.22s, transform 0.22s;
                animation: fadeInUp 0.45s cubic-bezier(0.22,1,0.36,1) both;
            }
            .stat-card:nth-child(1) { animation-delay: 0.04s; }
            .stat-card:nth-child(2) { animation-delay: 0.09s; }
            .stat-card:nth-child(3) { animation-delay: 0.14s; }
            .stat-card:hover {
                border-color: var(--border-hover);
                box-shadow: 0 0 20px var(--glow-primary);
                transform: translateY(-2px);
            }

            .stat-card-value {
                font-family: 'Fira Code', monospace;
                font-size: 1.875rem;
                font-weight: 700;
                color: var(--color-primary);
                text-shadow: 0 0 16px rgba(56,189,248,0.30);
                line-height: 1;
                margin-bottom: 0.5rem;
            }

            .stat-card-label {
                font-size: 0.6875rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.10em;
                color: var(--text-muted);
            }

            /* ── Section title ── */
            .section-title {
                font-size: 0.6875rem;
                font-weight: 700;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 0.12em;
                margin-bottom: 1rem;
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

            /* ── Language cards grid ── */
            .lang-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(265px, 1fr));
                gap: 1rem;
                margin-bottom: 3rem;
            }

            .lang-card {
                background: var(--bg-surface);
                border: 1px solid var(--border-default);
                border-radius: 14px;
                padding: 1.5rem;
                text-decoration: none;
                color: inherit;
                display: flex;
                flex-direction: column;
                gap: 1rem;
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                transition: border-color 0.25s, box-shadow 0.25s, transform 0.25s;
                position: relative;
                overflow: hidden;
                animation: fadeInUp 0.45s cubic-bezier(0.22,1,0.36,1) both;
            }

            .lang-card:nth-child(1) { animation-delay: 0.04s; }
            .lang-card:nth-child(2) { animation-delay: 0.09s; }
            .lang-card:nth-child(3) { animation-delay: 0.14s; }
            .lang-card:nth-child(4) { animation-delay: 0.19s; }
            .lang-card:nth-child(5) { animation-delay: 0.24s; }
            .lang-card:nth-child(6) { animation-delay: 0.29s; }
            .lang-card:nth-child(7) { animation-delay: 0.34s; }
            .lang-card:nth-child(n+8) { animation-delay: 0.39s; }

            /* Top glow line */
            .lang-card::before {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 1px;
                background: linear-gradient(90deg, transparent, var(--color-primary), transparent);
                opacity: 0;
                transition: opacity 0.3s;
            }

            .lang-card:hover {
                border-color: rgba(56,189,248,0.30);
                box-shadow: 0 0 28px rgba(56,189,248,0.09), 0 8px 32px rgba(0,0,0,0.30);
                transform: translateY(-3px);
            }
            .lang-card:hover::before { opacity: 1; }

            .lang-card-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .lang-card-name {
                font-family: 'Fira Code', monospace;
                font-size: 1.125rem;
                font-weight: 700;
                color: var(--color-primary);
            }

            .lang-card-badge {
                background: rgba(56,189,248,0.12);
                color: var(--color-primary);
                border: 1px solid rgba(56,189,248,0.22);
                font-size: 0.6875rem;
                font-weight: 700;
                font-family: 'Fira Code', monospace;
                padding: 0.2rem 0.625rem;
                border-radius: 6px;
            }

            .lang-card-stats {
                display: flex;
                gap: 1.5rem;
            }

            .lang-stat {
                display: flex;
                flex-direction: column;
                gap: 0.125rem;
            }

            .lang-stat-value {
                font-family: 'Fira Code', monospace;
                font-size: 1.25rem;
                font-weight: 700;
                color: var(--text-primary);
            }

            .lang-stat-label {
                font-size: 0.6875rem;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 0.07em;
                font-weight: 600;
            }

            .lang-card-footer {
                font-size: 0.8125rem;
                color: var(--text-muted);
                display: flex;
                align-items: center;
                gap: 0.375rem;
            }

            .lang-card-cta {
                margin-top: auto;
                display: inline-flex;
                align-items: center;
                gap: 0.375rem;
                font-size: 0.8125rem;
                font-weight: 600;
                color: var(--color-primary);
                opacity: 0.8;
                transition: opacity 0.15s, gap 0.2s;
            }
            .lang-card:hover .lang-card-cta {
                opacity: 1;
                gap: 0.5rem;
            }

            /* ── Footer ── */
            .footer {
                border-top: 1px solid var(--border-default);
                padding: 1.25rem 2rem;
                text-align: center;
                font-size: 0.8125rem;
                color: var(--text-muted);
            }

            /* ── Responsive ── */
            @media (max-width: 768px) {
                .sidebar { display: none; }
                .main-content { margin-left: 0; }
                .content { padding: 1.25rem; }
                .lang-grid { grid-template-columns: 1fr; }
                .stats-bar { grid-template-columns: repeat(2, 1fr); }
            }
        </style>"""

# ── CSS navbar + tabs (language pages) ────────────────────────────────────────

_LANG_PAGE_CSS = """
        <style>
            /* ── Top navbar — glassmorphism ── */
            .top-nav {
                background: var(--nav-bg);
                border-bottom: 1px solid var(--nav-border);
                position: sticky;
                top: 0;
                z-index: 200;
                backdrop-filter: blur(20px) saturate(160%);
                -webkit-backdrop-filter: blur(20px) saturate(160%);
            }
            .top-nav-inner {
                max-width: 1280px;
                margin: 0 auto;
                padding: 0 2rem;
                height: 52px;
                display: flex;
                align-items: center;
                gap: 1.25rem;
            }
            .nav-logo {
                font-family: 'Fira Code', monospace;
                font-size: 0.875rem;
                font-weight: 700;
                color: var(--nav-text);
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                flex-shrink: 0;
                transition: color 0.2s, text-shadow 0.2s;
            }
            .nav-logo:hover {
                color: var(--nav-accent);
                text-shadow: 0 0 12px rgba(56,189,248,0.45);
            }

            .nav-divider {
                width: 1px; height: 16px;
                background: var(--nav-border);
                flex-shrink: 0;
            }
            .nav-breadcrumbs {
                display: flex;
                align-items: center;
                gap: 0.45rem;
                font-size: 0.8125rem;
                min-width: 0;
                overflow: hidden;
            }
            .nav-bc-link {
                color: var(--nav-text-muted);
                text-decoration: none;
                white-space: nowrap;
                transition: color 0.15s;
                flex-shrink: 0;
            }
            .nav-bc-link:hover { color: var(--nav-accent); }
            .nav-bc-sep { color: rgba(255,255,255,0.18); user-select: none; flex-shrink: 0; }
            .nav-bc-current {
                color: #CBD5E1;
                font-weight: 500;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            /* ── Page layout ── */
            .container {
                max-width: 1280px;
                margin: 0 auto;
                padding: 2rem;
                position: relative;
                z-index: 1;
            }

            /* ── Page header ── */
            .lang-header {
                margin-bottom: 2rem;
                padding-bottom: 1.5rem;
                border-bottom: 1px solid var(--border-default);
                position: relative;
            }

            /* Accent line under header */
            .lang-header::after {
                content: '';
                position: absolute;
                bottom: -1px; left: 0; width: 120px;
                height: 1px;
                background: linear-gradient(90deg, var(--color-primary), transparent);
            }

            .lang-header h1 {
                font-family: 'Fira Code', monospace;
                font-size: 1.75rem;
                font-weight: 700;
                background: linear-gradient(120deg, #F1F5F9 0%, #38BDF8 50%, #A78BFA 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 0.375rem;
                line-height: 1.2;
            }
            .lang-header-sub {
                font-size: 0.875rem;
                color: var(--text-muted);
            }

            /* ── Stats bar ── */
            .stats-bar {
                display: flex;
                gap: 1rem;
                margin-bottom: 2rem;
                flex-wrap: wrap;
            }
            .stat-pill {
                background: var(--bg-surface);
                border: 1px solid var(--border-default);
                border-radius: 12px;
                padding: 1rem 1.5rem;
                text-align: center;
                min-width: 120px;
                flex: 1;
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                transition: border-color 0.22s, box-shadow 0.22s, transform 0.22s;
                animation: fadeInUp 0.45s cubic-bezier(0.22,1,0.36,1) both;
            }
            .stat-pill:nth-child(1) { animation-delay: 0.04s; }
            .stat-pill:nth-child(2) { animation-delay: 0.09s; }
            .stat-pill:nth-child(3) { animation-delay: 0.14s; }
            .stat-pill:hover {
                border-color: var(--border-hover);
                box-shadow: 0 0 18px var(--glow-primary);
                transform: translateY(-2px);
            }
            .stat-pill-value {
                font-family: 'Fira Code', monospace;
                font-size: 1.625rem;
                font-weight: 700;
                color: var(--color-primary);
                text-shadow: 0 0 16px rgba(56,189,248,0.28);
                line-height: 1;
                margin-bottom: 0.375rem;
            }
            .stat-pill-label {
                font-size: 0.6875rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.10em;
                color: var(--text-muted);
            }

            /* ── Tabs ── */
            .tabs {
                display: flex;
                gap: 0.25rem;
                border-bottom: 1px solid var(--border-default);
                margin-bottom: 1.5rem;
            }
            .tab {
                padding: 0.75rem 1.5rem;
                background: transparent;
                border: none;
                border-bottom: 2px solid transparent;
                margin-bottom: -1px;
                cursor: pointer;
                font-family: 'Inter', sans-serif;
                font-size: 0.875rem;
                font-weight: 500;
                color: var(--text-muted);
                transition: color 0.18s, border-color 0.18s, background 0.18s;
                border-radius: 6px 6px 0 0;
            }
            .tab:hover {
                color: var(--text-secondary);
                background: rgba(255,255,255,0.03);
            }
            .tab.active {
                color: var(--color-primary);
                border-bottom-color: var(--color-primary);
                text-shadow: 0 0 10px rgba(56,189,248,0.25);
            }
            .tab-content { display: none; }
            .tab-content.active { display: block; }

            /* ── Report cards grid ── */
            .reports-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(255px, 1fr));
                gap: 0.875rem;
            }

            .report-card {
                background: var(--bg-surface);
                border: 1px solid var(--border-default);
                border-radius: 12px;
                padding: 1.125rem 1.25rem;
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                transition: border-color 0.22s, box-shadow 0.22s, transform 0.22s;
                animation: fadeInUp 0.45s cubic-bezier(0.22,1,0.36,1) both;
            }
            .report-card:hover {
                border-color: rgba(56,189,248,0.28);
                box-shadow: 0 0 20px rgba(56,189,248,0.07), 0 6px 24px rgba(0,0,0,0.25);
                transform: translateY(-2px);
            }

            .report-date {
                font-family: 'Fira Code', monospace;
                font-size: 0.9375rem;
                font-weight: 600;
                color: var(--text-primary);
                margin-bottom: 0.875rem;
            }

            .report-links { display: flex; gap: 0.5rem; flex-wrap: wrap; }

            .format-link {
                display: inline-flex;
                align-items: center;
                padding: 0.3rem 0.75rem;
                border-radius: 6px;
                text-decoration: none;
                font-size: 0.6875rem;
                font-weight: 700;
                font-family: 'Fira Code', monospace;
                border: 1px solid transparent;
                letter-spacing: 0.04em;
                transition: transform 0.18s, box-shadow 0.18s, background 0.18s;
                cursor: pointer;
            }
            .format-link:hover { transform: translateY(-1px); }

            .format-html {
                background: rgba(56,189,248,0.12);
                color: #38BDF8;
                border-color: rgba(56,189,248,0.22);
            }
            .format-html:hover {
                background: rgba(56,189,248,0.20);
                box-shadow: 0 0 10px rgba(56,189,248,0.22);
            }
            .format-json {
                background: rgba(52,211,153,0.12);
                color: #34D399;
                border-color: rgba(52,211,153,0.22);
            }
            .format-json:hover {
                background: rgba(52,211,153,0.20);
                box-shadow: 0 0 10px rgba(52,211,153,0.22);
            }
            .format-md {
                background: rgba(251,191,36,0.12);
                color: #FBBF24;
                border-color: rgba(251,191,36,0.22);
            }
            .format-md:hover {
                background: rgba(251,191,36,0.20);
                box-shadow: 0 0 10px rgba(251,191,36,0.20);
            }
            .format-csv {
                background: rgba(167,139,250,0.12);
                color: #A78BFA;
                border-color: rgba(167,139,250,0.22);
            }
            .format-csv:hover {
                background: rgba(167,139,250,0.20);
                box-shadow: 0 0 10px rgba(167,139,250,0.20);
            }

            /* ── Empty state ── */
            .empty-state {
                text-align: center;
                padding: 3rem 1rem;
                color: var(--text-muted);
                font-size: 0.9375rem;
                border: 1px dashed var(--border-default);
                border-radius: 14px;
            }

            /* ── Footer ── */
            .footer {
                margin-top: 3rem;
                padding-top: 1.5rem;
                border-top: 1px solid var(--border-default);
                text-align: center;
                font-size: 0.8125rem;
                color: var(--text-muted);
            }
            .footer a:hover { color: var(--color-primary); }

            /* ── Responsive ── */
            @media (max-width: 768px) {
                .top-nav-inner { padding: 0 1rem; gap: 0.75rem; }
                .nav-divider    { display: none; }
                .container      { padding: 1.25rem; }
                .reports-grid   { grid-template-columns: 1fr; }
                .stats-bar      { gap: 0.75rem; }
                .tabs           { overflow-x: auto; -webkit-overflow-scrolling: touch; }
            }
        </style>"""

# ── SVG icons ──────────────────────────────────────────────────────────────────

_ICON_HOME = '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'
_ICON_ARROW = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>'
_ICON_CALENDAR = '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>'


# ── JS partagé (tabs + hash) ───────────────────────────────────────────────────

_TABS_JS = """
    <script>
        function showTab(event, tabId) {
            const btn = event.currentTarget;
            const container = btn.closest('.tab-section');
            container.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            container.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btn.classList.add('active');
            history.replaceState(null, '', '#' + tabId);
        }

        // Activate tab from URL hash on load
        (function() {
            const hash = window.location.hash.slice(1);
            if (hash) {
                const btn = document.querySelector('[data-tab="' + hash + '"]');
                if (btn) btn.click();
            }
        })();
    </script>"""


class IndexGenerator:
    """Génère les pages d'index statiques pour GitHub Pages.

    Produit :
      - docs/index.html               : dashboard global (language cards)
      - docs/{language}/index.html    : page par langage (tabs daily/weekly/monthly)
    """

    def __init__(self, docs_dir: str = "./docs"):
        self.docs_dir = Path(docs_dir)

    # ── Scan ──────────────────────────────────────────────────────────────────

    def _scan_reports(self) -> Dict[str, Dict[str, List[Dict]]]:
        """Scanne docs/ et retourne {language: {daily: [...], weekly: [...], monthly: [...]}}."""
        reports = defaultdict(lambda: {"daily": [], "weekly": [], "monthly": []})

        if not self.docs_dir.exists():
            return reports

        for language_dir in self.docs_dir.iterdir():
            if not language_dir.is_dir() or language_dir.name.startswith('.'):
                continue
            language = language_dir.name

            for year_dir in language_dir.iterdir():
                if not year_dir.is_dir() or not year_dir.name.isdigit():
                    continue

                # Daily
                for date_dir in year_dir.iterdir():
                    if not date_dir.is_dir() or date_dir.name in ("weekly", "monthly"):
                        continue
                    report_info = {"date": date_dir.name, "year": year_dir.name, "files": {}}
                    for ext in ("html", "json", "md", "csv"):
                        f = date_dir / f"report.{ext}"
                        if f.exists():
                            report_info["files"][ext] = str(f.relative_to(self.docs_dir)).replace("\\", "/")
                    if report_info["files"]:
                        reports[language]["daily"].append(report_info)

                # Weekly
                weekly_dir = year_dir / "weekly"
                if weekly_dir.exists():
                    for html_file in weekly_dir.glob("*.html"):
                        reports[language]["weekly"].append({
                            "period": html_file.stem,
                            "year": year_dir.name,
                            "files": {"html": str(html_file.relative_to(self.docs_dir)).replace("\\", "/")}
                        })

                # Monthly
                monthly_dir = year_dir / "monthly"
                if monthly_dir.exists():
                    for html_file in monthly_dir.glob("*.html"):
                        reports[language]["monthly"].append({
                            "period": html_file.stem,
                            "year": year_dir.name,
                            "files": {"html": str(html_file.relative_to(self.docs_dir)).replace("\\", "/")}
                        })

        for lang in reports:
            reports[lang]["daily"].sort(key=lambda x: x["date"], reverse=True)
            reports[lang]["weekly"].sort(key=lambda x: x["period"], reverse=True)
            reports[lang]["monthly"].sort(key=lambda x: x["period"], reverse=True)

        return dict(reports)

    # ── Main index (dashboard global) ─────────────────────────────────────────

    def _generate_main_index(self, reports: Dict[str, Dict[str, List[Dict]]]) -> str:
        """Génère docs/index.html — dashboard global avec une card par langage."""
        total_languages = len(reports)
        total_daily = sum(len(r["daily"]) for r in reports.values())
        all_dates = [rep["date"] for r in reports.values() for rep in r["daily"]]
        latest_date = max(all_dates) if all_dates else "N/A"
        current_year = datetime.now().year

        parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '    <title>GitHub Trending — Dashboard</title>',
            _SHARED_HEAD,
            _TOKENS_CSS,
            _SIDEBAR_CSS,
            '</head>',
            '<body>',
            '<div class="layout">',
            '',
            '  <!-- Sidebar -->',
            '  <aside class="sidebar" aria-label="Language navigation">',
            '    <div class="sidebar-header">',
            '      <a href="index.html" class="sidebar-logo">GitHub Trends</a>',
            '      <div class="sidebar-subtitle">Repository Analytics</div>',
            '    </div>',
            '    <div class="sidebar-search">',
            '      <input type="text" class="search-input" placeholder="Search language…"',
            '             id="searchInput" onkeyup="filterNav()" aria-label="Filter languages">',
            '    </div>',
            '    <div class="sidebar-section-label">Languages</div>',
            '    <nav class="sidebar-nav" id="sidebarNav">',
        ]

        for language in sorted(reports):
            lang_display = display_language(language)
            count = len(reports[language]["daily"])
            parts.append(
                f'      <a class="sidebar-nav-item" href="{language}/index.html">'
                f'<span>{lang_display}</span>'
                f'<span class="nav-count">{count}</span></a>'
            )

        parts += [
            '    </nav>',
            '  </aside>',
            '',
            '  <!-- Main content -->',
            '  <main class="main-content">',
            '    <div class="page-header">',
            '      <h1>GitHub Trending Reports</h1>',
            f'     <div class="page-header-sub">Updated {latest_date} &mdash; {total_languages} languages tracked</div>',
            '    </div>',
            '    <div class="content">',
            '',
            '      <!-- Global stats -->',
            '      <div class="stats-bar">',
            f'       <div class="stat-card"><div class="stat-card-value">{total_languages}</div><div class="stat-card-label">Languages</div></div>',
            f'       <div class="stat-card"><div class="stat-card-value">{total_daily}</div><div class="stat-card-label">Daily Reports</div></div>',
            f'       <div class="stat-card"><div class="stat-card-value">{latest_date}</div><div class="stat-card-label">Latest Update</div></div>',
            '      </div>',
            '',
            '      <!-- Language cards -->',
            '      <h2 class="section-title">Languages</h2>',
            '      <div class="lang-grid" id="langGrid">',
        ]

        for language in sorted(reports):
            lang_reports = reports[language]
            lang_display = display_language(language)
            daily_count = len(lang_reports["daily"])
            weekly_count = len(lang_reports["weekly"])
            monthly_count = len(lang_reports["monthly"])
            latest = lang_reports["daily"][0]["date"] if lang_reports["daily"] else "—"

            parts.append(
                f'        <a class="lang-card" href="{language}/index.html" aria-label="View {lang_display} reports">'
                f'<div class="lang-card-header">'
                f'<span class="lang-card-name">{lang_display}</span>'
                f'<span class="lang-card-badge">{daily_count} daily</span>'
                f'</div>'
                f'<div class="lang-card-stats">'
                f'<div class="lang-stat"><span class="lang-stat-value">{weekly_count}</span><span class="lang-stat-label">Weekly</span></div>'
                f'<div class="lang-stat"><span class="lang-stat-value">{monthly_count}</span><span class="lang-stat-label">Monthly</span></div>'
                f'</div>'
                f'<div class="lang-card-footer">{_ICON_CALENDAR} Latest: {latest}</div>'
                f'<span class="lang-card-cta">View reports {_ICON_ARROW}</span>'
                f'</a>'
            )

        parts += [
            '      </div>',  # .lang-grid
            '    </div>',    # .content
            f'   <div class="footer"><p>&copy; {current_year} GitHub Trending Scraper &mdash; Generated automatically</p></div>',
            '  </main>',
            '</div>',
            '',
            '<script>',
            '  function filterNav() {',
            '    const q = document.getElementById("searchInput").value.toLowerCase();',
            '    document.querySelectorAll(".sidebar-nav-item").forEach(el => {',
            '      el.style.display = el.textContent.toLowerCase().includes(q) ? "" : "none";',
            '    });',
            '    document.querySelectorAll(".lang-card").forEach(el => {',
            '      el.style.display = el.getAttribute("aria-label").toLowerCase().includes(q) ? "" : "none";',
            '    });',
            '  }',
            '</script>',
            '</body>',
            '</html>',
        ]

        return "\n".join(parts)

    # ── Language page ──────────────────────────────────────────────────────────

    def _generate_language_page(self, language: str, lang_reports: Dict[str, List[Dict]]) -> str:
        """Génère docs/{language}/index.html — page dédiée à un langage.

        Les chemins de fichiers sont relativisés par rapport à docs/{language}/.
        """
        lang_display = display_language(language)
        daily_reports = lang_reports.get("daily", [])
        weekly_reports = lang_reports.get("weekly", [])
        monthly_reports = lang_reports.get("monthly", [])
        current_year = datetime.now().year
        latest = daily_reports[0]["date"] if daily_reports else "—"

        def rel(path: str) -> str:
            """Retire le préfixe '{language}/' pour les chemins relatifs depuis docs/{language}/."""
            prefix = f"{language}/"
            return path[len(prefix):] if path.startswith(prefix) else path

        parts = [
            '<!DOCTYPE html>',
            '<html lang="en">',
            '<head>',
            '    <meta charset="UTF-8">',
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'    <title>{lang_display} Trending Reports | GitHub Trends</title>',
            _SHARED_HEAD,
            _TOKENS_CSS,
            _LANG_PAGE_CSS,
            '</head>',
            '<body>',
            '',
            '<!-- Top navbar -->',
            '<nav class="top-nav" aria-label="Site navigation">',
            '  <div class="top-nav-inner">',
            f'    <a href="../index.html" class="nav-logo" aria-label="Back to dashboard">{_ICON_HOME} GitHub Trends</a>',
            '    <div class="nav-divider" aria-hidden="true"></div>',
            '    <div class="nav-breadcrumbs" aria-label="Breadcrumb">',
            '      <a href="../index.html" class="nav-bc-link">Home</a>',
            '      <span class="nav-bc-sep" aria-hidden="true">/</span>',
            f'      <span class="nav-bc-current" aria-current="page">{lang_display}</span>',
            '    </div>',
            '  </div>',
            '</nav>',
            '',
            '<div class="container">',
            '',
            '  <!-- Page header -->',
            '  <div class="lang-header">',
            f'    <h1>{lang_display} Trending Repositories</h1>',
            f'    <p class="lang-header-sub">Latest: {latest} &mdash; All-time tracking</p>',
            '  </div>',
            '',
            '  <!-- Stats -->',
            '  <div class="stats-bar">',
            f'    <div class="stat-pill"><div class="stat-pill-value">{len(daily_reports)}</div><div class="stat-pill-label">Daily Reports</div></div>',
            f'    <div class="stat-pill"><div class="stat-pill-value">{len(weekly_reports)}</div><div class="stat-pill-label">Weekly Reports</div></div>',
            f'    <div class="stat-pill"><div class="stat-pill-value">{len(monthly_reports)}</div><div class="stat-pill-label">Monthly Reports</div></div>',
            '  </div>',
            '',
            '  <!-- Tabs -->',
            '  <div class="tab-section">',
            '    <div class="tabs" role="tablist">',
            f'      <button class="tab active" role="tab" data-tab="daily" onclick="showTab(event, \'daily\')" aria-selected="true">Daily ({len(daily_reports)})</button>',
            f'      <button class="tab" role="tab" data-tab="weekly" onclick="showTab(event, \'weekly\')" aria-selected="false">Weekly ({len(weekly_reports)})</button>',
            f'      <button class="tab" role="tab" data-tab="monthly" onclick="showTab(event, \'monthly\')" aria-selected="false">Monthly ({len(monthly_reports)})</button>',
            '    </div>',
            '',
            '    <!-- Daily tab -->',
            '    <div id="daily" class="tab-content active" role="tabpanel">',
        ]

        if daily_reports:
            parts.append('      <div class="reports-grid">')
            for report in daily_reports:
                parts.append('        <div class="report-card">')
                parts.append(f'          <div class="report-date">{report["date"]}</div>')
                parts.append('          <div class="report-links">')
                for ext, label in [("html", "View"), ("json", "JSON"), ("md", "MD"), ("csv", "CSV")]:
                    if ext in report.get("files", {}):
                        dl = ' download' if ext in ("json", "csv") else ''
                        css = f"format-link format-{ext}"
                        parts.append(f'            <a href="{rel(report["files"][ext])}" class="{css}"{dl}>{label}</a>')
                parts.append('          </div>')
                parts.append('        </div>')
            parts.append('      </div>')
        else:
            parts.append('      <div class="empty-state">No daily reports yet.</div>')

        parts += [
            '    </div>',  # #daily
            '',
            '    <!-- Weekly tab -->',
            '    <div id="weekly" class="tab-content" role="tabpanel">',
        ]

        if weekly_reports:
            parts.append('      <div class="reports-grid">')
            for report in weekly_reports:
                parts.append('        <div class="report-card">')
                parts.append(f'          <div class="report-date">{report["period"]}</div>')
                parts.append('          <div class="report-links">')
                if "html" in report.get("files", {}):
                    parts.append(f'            <a href="{rel(report["files"]["html"])}" class="format-link format-html">View Report</a>')
                parts.append('          </div>')
                parts.append('        </div>')
            parts.append('      </div>')
        else:
            parts.append('      <div class="empty-state">No weekly reports yet.</div>')

        parts += [
            '    </div>',  # #weekly
            '',
            '    <!-- Monthly tab -->',
            '    <div id="monthly" class="tab-content" role="tabpanel">',
        ]

        if monthly_reports:
            parts.append('      <div class="reports-grid">')
            for report in monthly_reports:
                parts.append('        <div class="report-card">')
                parts.append(f'          <div class="report-date">{report["period"]}</div>')
                parts.append('          <div class="report-links">')
                if "html" in report.get("files", {}):
                    parts.append(f'            <a href="{rel(report["files"]["html"])}" class="format-link format-html">View Report</a>')
                parts.append('          </div>')
                parts.append('        </div>')
            parts.append('      </div>')
        else:
            parts.append('      <div class="empty-state">No monthly reports yet.</div>')

        parts += [
            '    </div>',  # #monthly
            '  </div>',   # .tab-section
            '',
            f'  <div class="footer"><p>&copy; {current_year} GitHub Trending Scraper &mdash; <a href="../index.html" style="color:inherit">← Dashboard</a></p></div>',
            '</div>',     # .container
            _TABS_JS,
            '</body>',
            '</html>',
        ]

        return "\n".join(parts)

    # ── Entry point ────────────────────────────────────────────────────────────

    def generate(self) -> None:
        """Génère index.html global + une page par langage."""
        logger.info("Scanning reports in %s…", self.docs_dir)
        reports = self._scan_reports()

        if not reports:
            logger.warning("Aucun rapport trouvé dans %s", self.docs_dir)

        # 1. Main index
        logger.info("Generating docs/index.html…")
        main_html = self._generate_main_index(reports)
        index_path = self.docs_dir / "index.html"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(main_html)

        # 2. Per-language pages
        for language, lang_reports in sorted(reports.items()):
            logger.info("Generating docs/%s/index.html…", language)
            lang_html = self._generate_language_page(language, lang_reports)
            lang_dir = self.docs_dir / language
            lang_dir.mkdir(parents=True, exist_ok=True)
            with open(lang_dir / "index.html", "w", encoding="utf-8") as f:
                f.write(lang_html)

        logger.info(
            "Done: 1 main index + %d language pages generated.",
            len(reports)
        )
