# Mood Journal — Production Deployment Guide

This guide walks you through deploying **Mood Journal** to production using **Vercel** and **Upstash Redis**.

---

## 🎯 Architecture Summary

- **Frontend**: Static HTML5/CSS3/JS served directly via Vercel's global Edge CDN.
- **Backend API**: Ephemeral Python 3.11 serverless functions (`api/index.py`) running on Vercel.
- **Datastore**: Upstash Redis (serverless HTTP/REST datastore with zero cold-connection penalties).

---

## 📋 Prerequisites

Before starting, ensure you have:
1. A [GitHub](https://github.com/) account.
2. A free [Vercel](https://vercel.com/) account.
3. A free [Upstash](https://upstash.com/) account.
4. Git installed locally.

---

## Step 1: Set Up Upstash Redis Datastore

Because Vercel serverless functions are stateless, persistent storage must be external. Upstash provides a generous free tier that supports up to 10,000 commands/day, which is more than enough for personal journaling.

1. Log in to the [Upstash Console](https://console.upstash.com/).
2. Click **Create Database**.
3. Choose:
   - **Name**: `mood-journal-db`
   - **Type**: Regional (select the region closest to you or your Vercel functions, e.g., `us-east-1` or `eu-west-1`).
   - **TLS (SSL)**: Enabled (checked).
   - **Eviction**: None (or standard).
4. Click **Create**.
5. Once created, scroll down to the **REST API** section on your database dashboard.
6. Copy the following two values:
   - `UPSTASH_REDIS_REST_URL` (starts with `https://...`)
   - `UPSTASH_REDIS_REST_TOKEN` (a long secret string)

---

## Step 2: Test Locally with Upstash (Optional)

You can verify that your Upstash credentials work before deploying:

1. In your project root, create a file named `.env.local`:
   ```ini
   UPSTASH_REDIS_REST_URL=https://your-upstash-database.upstash.io
   UPSTASH_REDIS_REST_TOKEN=your_upstash_secret_token
   PORT=5000
   ```
2. Start the local server:
   ```bash
   python api/index.py
   ```
3. You should see in the console:
   ```
   [Storage] Using Upstash Redis REST datastore.
   Starting Mood Journal on http://localhost:5000
   ```
4. Visit `http://localhost:5000/api/health` and verify `"storage": "upstash_redis"`.

---

## Step 3: Push Your Code to GitHub

1. If you haven't already committed your code locally:
   ```bash
   git add .
   git commit -m "Prepare Mood Journal for production deployment"
   ```
2. Create a new repository on GitHub (e.g. `mood-journal`).
3. Link your remote repository and push:
   ```bash
   git remote add origin https://github.com/<your-username>/mood-journal.git
   git branch -M main
   git push -u origin main
   ```

---

## Step 4: Deploy to Vercel

### Method A: Via Vercel Web Dashboard (Recommended)

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard) and click **Add New... &rarr; Project**.
2. Import your `mood-journal` repository from GitHub.
3. Configure the Project:
   - **Framework Preset**: Other (leave default).
   - **Root Directory**: `./` (leave default).
   - **Build Command**: Leave blank (not needed).
   - **Output Directory**: Leave blank (not needed).
4. Expand **Environment Variables** and add:
   - `UPSTASH_REDIS_REST_URL`: *Your copied Upstash REST URL*
   - `UPSTASH_REDIS_REST_TOKEN`: *Your copied Upstash REST token*
5. Click **Deploy**.

Vercel will detect `vercel.json`, build the Python serverless function, package the static frontend from `public/`, and deploy the application in approximately 30–60 seconds.

---

### Method B: Via Vercel CLI

1. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   ```
2. Run the deployment command from the project root:
   ```bash
   vercel
   ```
3. Follow the interactive prompts:
   - Set up and deploy? **Yes**
   - Which scope? **Select your account**
   - Link to existing project? **No**
   - Project name? **mood-journal**
   - In which directory is your code located? **`./`**
4. Set the environment variables:
   ```bash
   vercel env add UPSTASH_REDIS_REST_URL
   vercel env add UPSTASH_REDIS_REST_TOKEN
   ```
5. Trigger a production build:
   ```bash
   vercel --prod
   ```

---

## Step 5: Post-Deployment Smoke Testing

Once deployment completes, open your live Vercel URL (e.g., `https://mood-journal-xyz.vercel.app`) and verify the following:

1. **Check Health Endpoint**:
   Navigate to `https://<your-app>.vercel.app/api/health`.
   It should return:
   ```json
   {
     "status": "healthy",
     "storage": "upstash_redis",
     "timestamp": "..."
   }
   ```
2. **Submit a Test Entry**:
   Type: `"Had a fantastic day deploying my project to the cloud!"` and click **Log Mood**.
   - Verify the submit button shows the loading spinner.
   - Verify the sentiment is evaluated (e.g. `Very Positive 🌟`).
   - Verify today's square in the heatmap turns bright green.
   - Verify your current streak changes to `1 days`.
3. **Inspect the Cell**:
   Hover or click on today's green square. Verify the modal opens and displays the full text.
4. **Refresh the Page**:
   Reload your browser. Verify your entry, heatmap color, and streak persist seamlessly.

---

## 🔧 Troubleshooting

### Problem: `"storage": "local_json"` on Vercel
- **Cause**: The environment variables were not added, or were added under "Preview" instead of "Production".
- **Fix**: Go to Vercel Dashboard &rarr; **Project Settings &rarr; Environment Variables**. Ensure `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` are checked for **Production**, then redeploy under the **Deployments** tab.

### Problem: First request takes 1–2 seconds (Cold Start)
- **Explanation**: In serverless architectures, an idle container spin-up (cold start) may take 1–2 seconds for the initial request. Subsequent requests typically respond in < 150ms.
- **Fix**: Normal behavior for serverless hobby tier. No action needed.

### Problem: Error `400 Bad Request` on Submission
- **Cause**: Text is empty, only contains whitespace, or exceeds 1,000 characters.
- **Fix**: Check the character counter on the frontend; ensure text length is between 1 and 1,000 characters.

---

## 🚀 Continuous Deployment
Every push to your GitHub `main` branch will automatically trigger a new zero-downtime deployment on Vercel.
