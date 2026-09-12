# Mood Journal — REST API Reference

This document provides complete documentation for the Mood Journal REST API.

---

## 🌐 Overview

- **Base URL (Local)**: `http://localhost:5000/api`
- **Base URL (Production)**: `https://<your-vercel-domain>.vercel.app/api`
- **Default Content-Type**: `application/json`
- **Response Format**: JSON
- **Authentication**: None required in v1 (single-user personal scope)

---

## 📑 Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/entry` | Create or update today's journal entry |
| `GET` | `/api/entries` | Fetch entries for heatmap visualization |
| `GET` | `/api/entry/<date>` | Fetch full entry text and metadata for a date |
| `GET` | `/api/streak` | Get current and historical longest streaks |
| `GET` | `/api/health` | Health check and datastore status |

---

## 1. Create or Update Entry

### `POST /api/entry`
Submits a free-text journal entry for today (or a specified date). The backend automatically calculates sentiment polarity, maps it to a mood bucket, and updates the datastore. If an entry already exists for the target date, it is updated in place (not duplicated).

#### Request Headers
| Header | Value | Required |
|---|---|---|
| `Content-Type` | `application/json` | Yes |

#### Request Body
```json
{
  "text": "Had a productive morning coding, followed by an inspiring walk in the park."
}
```

*Optional parameter for dev / backfill:*
```json
{
  "text": "Yesterday was a great day.",
  "date": "2026-09-11"
}
```

#### Field Specifications
| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| `text` | string | **Yes** | 1 to 1,000 characters after trimming | The free-text journal reflection |
| `date` | string | No | Format `YYYY-MM-DD` | Target date (defaults to current UTC date) |

#### Response `200 OK`
```json
{
  "date": "2026-09-12",
  "text": "Had a productive morning coding, followed by an inspiring walk in the park.",
  "score": 0.76,
  "bucket": "very_positive"
}
```

#### Error Responses
- **`400 Bad Request`**: Invalid JSON, missing text, or text length out of bounds.
  ```json
  {
    "error": "Entry text must be between 1 and 1000 characters."
  }
  ```
- **`500 Internal Server Error`**: Datastore write failure.
  ```json
  {
    "error": "Failed to persist entry: <error details>"
  }
  ```

#### Example `curl`
```bash
curl -X POST http://localhost:5000/api/entry \
  -H "Content-Type: application/json" \
  -d '{"text": "Really enjoyed spending time with family this evening."}'
```

---

## 2. Get Heatmap Entries

### `GET /api/entries`
Fetches all recorded entries for calendar heatmap rendering. Full entry text is deliberately omitted from this bulk response to minimize network payload size and latency.

#### Query Parameters
| Parameter | Type | Default | Description |
|---|---|---|---|
| `days` | integer | `371` | Maximum days in the past to include (1 to 1000) |

#### Response `200 OK`
```json
{
  "entries": [
    {
      "date": "2026-09-12",
      "score": 0.76,
      "bucket": "very_positive"
    },
    {
      "date": "2026-09-11",
      "score": -0.32,
      "bucket": "negative"
    },
    {
      "date": "2026-09-10",
      "score": 0.05,
      "bucket": "neutral"
    }
  ]
}
```

#### Example `curl`
```bash
curl -X GET "http://localhost:5000/api/entries?days=371"
```

---

## 3. Get Single Entry by Date

### `GET /api/entry/<date>`
Retrieves the full journal entry text and sentiment analysis breakdown for a specific calendar date. Used when a user clicks or inspects a day on the heatmap.

#### Path Parameters
| Parameter | Type | Required | Format | Description |
|---|---|---|---|---|
| `date` | string | **Yes** | `YYYY-MM-DD` | Target calendar date |

#### Response `200 OK`
```json
{
  "date": "2026-09-11",
  "text": "Rough day at the office. Traffic was terrible and I arrived late.",
  "score": -0.32,
  "bucket": "negative"
}
```

#### Error Responses
- **`400 Bad Request`**: Date parameter is not in `YYYY-MM-DD` format.
  ```json
  {
    "error": "Invalid date format. Expected YYYY-MM-DD."
  }
  ```
- **`404 Not Found`**: No entry exists for the requested date.
  ```json
  {
    "error": "Entry not found"
  }
  ```

#### Example `curl`
```bash
curl -X GET http://localhost:5000/api/entry/2026-09-11
```

---

## 4. Get Streak Statistics

### `GET /api/streak`
Computes and returns the user's current consecutive daily journaling streak and all-time longest streak.

#### Response `200 OK`
```json
{
  "current_streak": 6,
  "longest_streak": 14
}
```

#### Streak Calculation Rules
- **Current Streak**:
  - If today has an entry, counts backwards consecutively starting from today.
  - If today does not yet have an entry, but yesterday does, counts backwards consecutively starting from yesterday (grace window).
  - If neither today nor yesterday has an entry, returns `0`.
- **Longest Streak**:
  - The maximum sequence of uninterrupted consecutive calendar days in the user's complete history.

#### Example `curl`
```bash
curl -X GET http://localhost:5000/api/streak
```

---

## 5. Health Check

### `GET /api/health`
Returns the operational health status and active datastore backend.

#### Response `200 OK`
```json
{
  "status": "healthy",
  "storage": "upstash_redis",
  "timestamp": "2026-09-12T07:25:00.123456+00:00"
}
```

*Note: In local mode without Upstash configured, `storage` will report `"local_json"`.*

#### Example `curl`
```bash
curl -X GET http://localhost:5000/api/health
```

---

## 📊 Sentiment Buckets Summary

| Bucket Identifier | Score Min | Score Max | Heatmap Display Color |
|---|---|---|---|
| `very_negative` | `-1.00` | `< -0.50` | `#dc2626` (Dark Red) |
| `negative` | `-0.50` | `< -0.10` | `#f87171` (Coral Red) |
| `neutral` | `-0.10` | `+0.10` | `#94a3b8` (Slate Gray) |
| `positive` | `> +0.10` | `+0.50` | `#4ade80` (Light Green) |
| `very_positive` | `> +0.50` | `+1.00` | `#15803d` (Emerald Green) |
