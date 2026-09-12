# Mood Journal 🌿

> **Effortless emotional tracking in English & Roman Urdu powered by sentiment analysis & visual 371-day GitHub-style calendar heatmap.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Language](https://img.shields.io/badge/languages-English%20%7C%20Roman%20Urdu-green.svg)](#-bilingual-support)
[![Flask 3.0+](https://img.shields.io/badge/framework-Flask-black.svg)](https://palletsprojects.com/p/flask/)
[![Deployment](https://img.shields.io/badge/deployed%20on-Vercel-black.svg)](https://vercel.com/)
[![Database](https://img.shields.io/badge/datastore-Upstash%20Redis-red.svg)](https://upstash.com/)
[![Tests](https://img.shields.io/badge/tests-9%20passed-brightgreen.svg)](#-automated-testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Executive Summary

Mood Journal is a lightweight, zero-friction daily reflection web application. Instead of forcing users to manually select arbitrary 1–5 star ratings, pick from confusing emoji pickers, or tag feelings, Mood Journal lets users simply **write how they feel in plain English, Roman Urdu, or mixed code-switching**. 

The app automatically evaluates emotional valence using continuous NLP sentiment scoring and transforms a user's journaling history into an interactive, color-coded **371-day calendar heatmap** (53 weeks × 7 days), inspired by GitHub’s contribution graph.

---

## 📚 Documentation Index

For in-depth guides, visit the documentation directory:

| Document | Description |
|---|---|
| 📖 **[User Guide](docs/USER_GUIDE.md)** | Step-by-step instructions for journaling, Roman Urdu writing guide, understanding heatmap buckets, streak rules, and FAQ. |
| 🏛 **[Technical Architecture](docs/ARCHITECTURE.md)** | System design, Roman Urdu & English NLP engine, Redis schema, dual-mode storage abstraction, and streak algorithm. |
| 📡 **[REST API Reference](docs/API.md)** | Complete OpenAPI-style documentation with endpoints, payloads, HTTP status codes, and `curl` examples. |
| 🚀 **[Production Deployment Guide](docs/DEPLOYMENT.md)** | End-to-end instructions for deploying to Vercel with Upstash Redis, configuring environment variables, and smoke testing. |

---

## ✨ Key Features

- ✍️ **Frictionless Daily Journaling**: Min 1 to max 1,000 characters. No manual sliders or tagging.
- 🇵🇰 **Bilingual English & Roman Urdu Understanding**: Native understanding of Roman Urdu words (*zabardast, behtareen, acha, kharab, udaas, dard, sukoon, thak gaya*), intensifiers (*bohot, intehai*), negations (*nahi, mat*), and code-switching (*"Today was good lekin baad me bohot thak gaya"*).
- 🤖 **Automated Sentiment Analysis**: Evaluates text on a continuous scale from `-1.0` (very negative) to `+1.0` (very positive) using pure-Python VADER NLP.
- 🎨 **Visual 371-Day Heatmap**: 53 columns × 7 rows GitHub-style calendar grid with dynamic month headers and day-of-week indicators.
- 🏷 **5-Bucket Emotional Palette**:
  - 💔 **Very Negative** (`-1.0` to `-0.5`) — Dark Red (`#dc2626`)
  - 🙁 **Negative** (`-0.5` to `-0.1`) — Coral Red (`#f87171`)
  - 😐 **Neutral** (`-0.1` to `+0.1`) — Slate Gray (`#94a3b8`)
  - 😊 **Positive** (`+0.1` to `+0.5`) — Light Green (`#4ade80`)
  - 🌟 **Very Positive** (`+0.5` to `+1.0`) — Emerald Green (`#15803d`)
- 🔍 **Interactive Cell Inspection**: Hover over any past day for a quick tooltip preview; click to open a full popover modal with complete text and numeric scores.
- 🔥 **Habit Streak Tracker**: Live tracking of current consecutive days and all-time longest streak with a built-in grace window.
- 🛡 **One Entry Per Day**: Submitting multiple times in the same day updates the entry and re-scores sentiment in place without creating duplicate records.
- ⚡ **Stateless Serverless + Local Fallback**: Seamlessly runs locally with an automatic JSON file store (`data/entries.json`), and switches to Upstash Redis REST in production.
- 📱 **Fully Responsive**: Mobile-ready layout with smooth horizontal touch-scrolling across all 53 weeks.

---

## 🏗 Architecture & Tech Stack

```
┌──────────────────────────────────────────────────────────┐
│                      Client Layer                        │
│     Vanilla HTML5 / Modern CSS3 (Grid) / Vanilla JS      │
└────────────────────────────┬─────────────────────────────┘
                             │ HTTPS / JSON
                             ▼
┌──────────────────────────────────────────────────────────┐
│                     Vercel Serverless                    │
│      Flask Entrypoint (api/index.py) + VADER NLP         │
└────────────────────────────┬─────────────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│  Upstash Redis REST API │       │ Local JSON File Store   │
│   (Production Cloud)    │       │   (data/entries.json)   │
└─────────────────────────┘       └─────────────────────────┘
```

| Component | Technology | Purpose |
|---|---|---|
| **Backend Framework** | Python 3.11+, Flask | Serverless routing & API handlers |
| **Sentiment Engine** | `vaderSentiment` | Fast, deterministic polarity scoring without cold-start corpus downloads |
| **Production Datastore** | Upstash Redis (REST) | Ephemeral serverless persistence over HTTP |
| **Local Datastore** | File-backed JSON store | Zero-config instant local development |
| **Frontend Framework** | Vanilla HTML5 / CSS3 / ES6+ | High performance, zero build step, instant load |
| **Deployment Platform**| Vercel | Unified static edge hosting & Python serverless functions |

---

## 🚀 Quickstart (Local Development)

### 1. Prerequisites
- Python 3.11 or higher
- Git

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/<your-username>/mood-journal.git
cd mood-journal
pip install -r requirements.txt
```

### 3. Run the Development Server
No environment variables or API keys are required for local development (the app uses a transparent local datastore in `data/entries.json`):

```bash
python api/index.py
```

Visit **[http://localhost:5000](http://localhost:5000)** in your browser.

---

## 🧪 Automated Testing

The project includes an automated test suite verifying all 4 API endpoints, validation logic, sentiment boundaries, streak calculations, and static asset serving:

```bash
python -m pytest tests/ -v
```

### Test Coverage Summary:
- `test_sentiment_buckets`: Verifies all 5 polarity range mappings.
- `test_create_and_update_entry`: Verifies creation, same-day updating, and duplicate prevention.
- `test_validation`: Verifies empty text, whitespace, and 1,000-character constraints.
- `test_get_entries_list`: Verifies 371-day rolling list excludes heavy text blobs.
- `test_get_entry_by_date`: Verifies single entry lookup and 404/400 errors.
- `test_streak_calculation`: Verifies consecutive counting, gaps, and longest streak history.
- `test_health_check`: Verifies `/api/health` status reporting.
- `test_static_routes`: Verifies Flask local serving of frontend assets.

---

## 🌐 Production Deployment on Vercel

1. Create a free Redis database in the [Upstash Console](https://console.upstash.com/).
2. Copy `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` from the database REST API tab.
3. Import your GitHub repository to [Vercel](https://vercel.com/).
4. Add the two environment variables in **Vercel Settings &rarr; Environment Variables**:
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN`
5. Deploy! Vercel automatically routes `/api/*` to `api/index.py` and serves `public/` at the root.

*(See **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** for detailed step-by-step instructions.)*

---

## 📡 API Overview

| Method | Route | Description |
|---|---|---|
| `POST` | `/api/entry` | Submit or update today's journal entry (`1–1000` chars). |
| `GET` | `/api/entries?days=371` | Fetch rolling entries (`date`, `score`, `bucket`) for heatmap. |
| `GET` | `/api/entry/<YYYY-MM-DD>` | Fetch full text and score for a specific date. |
| `GET` | `/api/streak` | Get current and historical longest streaks. |
| `GET` | `/api/health` | Service health and active storage backend. |

*(See **[docs/API.md](docs/API.md)** for full request/response schemas and curl examples.)*

---

## 📂 Repository Structure

```
Mood-Journal/
├── api/
│   └── index.py            # Flask app & Vercel serverless function entrypoint
├── public/
│   ├── index.html          # Semantic SPA layout & accessible components
│   ├── style.css           # Modern design system & 53x7 CSS Grid heatmap
│   └── app.js              # Vanilla JS: API client, heatmap generator, streak logic
├── docs/
│   ├── USER_GUIDE.md       # Comprehensive user manual & journaling tips
│   ├── ARCHITECTURE.md     # Technical design, VADER NLP math, & storage model
│   ├── API.md              # Complete REST API reference
│   └── DEPLOYMENT.md       # Step-by-step production deployment guide
├── tests/
│   └── test_app.py         # Pytest automated test suite
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── requirements.txt        # Production dependencies
├── vercel.json             # Vercel deployment routing configuration
└── README.md               # Main project overview
```

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
