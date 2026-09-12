# Mood Journal 🌿

A lightweight, zero-friction daily journaling web app with automated sentiment analysis and a rolling 371-day (53 weeks × 7 days) GitHub-style calendar heatmap.

Built with **Python (Flask)** on the backend, **Vanilla HTML/CSS/JS** on the frontend, persistent storage via **Upstash Redis REST API**, and deployed to **Vercel Serverless**.

![Mood Journal Preview](https://raw.githubusercontent.com/placeholder/mood-journal.png)

---

## ✨ Features

- **Effortless Journaling**: No manual mood pickers, sliders, or tagging. Just write a short entry (1–1,000 characters) and submit.
- **Automated Sentiment Analysis**: Analyzes text polarity using `vaderSentiment` (-1.0 to +1.0) and automatically maps it into 5 mood buckets:
  - 💔 **Very Negative** (-1.0 to -0.5) — Dark Red
  - 🙁 **Negative** (-0.5 to -0.1) — Coral Red
  - 😐 **Neutral** (-0.1 to 0.1) — Slate Gray
  - 😊 **Positive** (0.1 to 0.5) — Light Green
  - 🌟 **Very Positive** (0.5 to 1.0) — Emerald Green
- **371-Day Visual Heatmap**: A rolling 53-week × 7-day contribution graph with month labels and day-of-week rows.
- **Interactive Inspector**: Hover to preview sentiment score, date, and entry snippet. Click any day to open the full journal entry popover modal.
- **Habit Streaks**: Live calculation of current consecutive daily streak and historical longest streak.
- **Single Entry per Day**: Prevents duplicates. If you submit again on the same day, your entry and mood score are seamlessly updated.
- **Serverless & Local Ready**: Works out-of-the-box locally with an automatic JSON datastore fallback; switches transparently to Upstash Redis REST in production.

---

## 🛠 Tech Stack

| Layer | Technology | Description |
|---|---|---|
| **Backend** | Python 3.11+, Flask | Serverless API routes on Vercel |
| **Sentiment** | `vaderSentiment` | Fast, pure-Python lexicon-based polarity scoring |
| **Datastore** | Upstash Redis (REST) | HTTP-based serverless datastore (with local JSON fallback) |
| **Frontend** | Vanilla HTML5 / CSS3 / ES6+ JS | Zero frameworks, zero build step, responsive design |
| **Deployment** | Vercel | Unified static frontend & serverless Python API |

---

## 🚀 Getting Started

### 1. Clone & Install Dependencies

```bash
cd Mood-Journal
pip install -r requirements.txt
```

### 2. Run Locally

You can launch the development server immediately without setting any environment variables (it will use an automatic local fallback store in `data/entries.json`):

```bash
python api/index.py
```

Open your browser at **[http://localhost:5000](http://localhost:5000)**.

---

## 🧪 Running Automated Tests

Run the full pytest test suite covering API endpoints, input validation, sentiment bucketing, streak calculation, and static asset routing:

```bash
pytest tests/ -v
```

---

## 🌐 Deploying to Vercel

### Step 1: Create an Upstash Redis Database
1. Go to [Upstash Console](https://console.upstash.com/) (free tier).
2. Create a new Redis database.
3. Copy the `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` from the database dashboard (REST API section).

### Step 2: Configure Environment Variables
Create `.env.local` locally for testing with Redis:
```ini
UPSTASH_REDIS_REST_URL=https://your-upstash-redis-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_upstash_redis_token
```

### Step 3: Deploy with Vercel CLI or Web Dashboard
With Vercel CLI:
```bash
npm install -g vercel
vercel
```
Add the environment variables in the Vercel Dashboard under **Project Settings → Environment Variables**:
- `UPSTASH_REDIS_REST_URL`
- `UPSTASH_REDIS_REST_TOKEN`

`vercel.json` is already configured to route `/api/*` to `api/index.py` and static assets from `public/`.

---

## 📡 API Reference

### `POST /api/entry`
Create or update today's journal entry.
- **Body**: `{"text": "Had a productive day finishing our project!"}`
- **Validation**: 1 to 1,000 characters (trimmed).
- **Response**:
  ```json
  {
    "date": "2026-09-12",
    "text": "Had a productive day finishing our project!",
    "score": 0.42,
    "bucket": "positive"
  }
  ```

### `GET /api/entries?days=371`
Fetch entries for the heatmap grid (omits full text for bandwidth efficiency).
- **Response**:
  ```json
  {
    "entries": [
      { "date": "2026-09-12", "score": 0.42, "bucket": "positive" }
    ]
  }
  ```

### `GET /api/entry/<date>`
Fetch full entry details for a specific date (`YYYY-MM-DD`).
- **Response**:
  ```json
  {
    "date": "2026-09-12",
    "text": "Had a productive day finishing our project!",
    "score": 0.42,
    "bucket": "positive"
  }
  ```

### `GET /api/streak`
Get the current and historical longest journaling streaks.
- **Response**:
  ```json
  {
    "current_streak": 4,
    "longest_streak": 12
  }
  ```

---

## 📄 License
MIT License.
