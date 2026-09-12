# Mood Journal — User Guide

Welcome to **Mood Journal**! This guide covers everything you need to know about using the application, understanding your mood heatmap, mastering the streak system, and getting the most out of automatic sentiment tracking.

---

## 📖 Table of Contents

1. [Introduction & Philosophy](#-introduction--philosophy)
2. [Quickstart Tour](#-quickstart-tour)
3. [Writing & Submitting Daily Entries](#-writing--submitting-daily-entries)
   - [Character Counter & Limits](#character-counter--limits)
   - [Updating Today's Entry](#updating-todays-entry)
4. [Understanding the Mood Heatmap](#-understanding-the-mood-heatmap)
   - [Grid Layout (53 Weeks × 7 Days)](#grid-layout-53-weeks--7-days)
   - [The 5 Sentiment Buckets](#the-5-sentiment-buckets)
   - [Legend & Visual Clues](#legend--visual-clues)
5. [Inspecting Past Entries](#-inspecting-past-entries)
   - [Hover Tooltip](#hover-tooltip)
   - [Detailed Modal Dialog](#detailed-modal-dialog)
6. [Streak Tracking & Habit Building](#-streak-tracking--habit-building)
   - [Current Streak vs. Longest Streak](#current-streak-vs-longest-streak)
   - [Streak Grace Window (Yesterday/Today)](#streak-grace-window-yesterdaytoday)
7. [Tips for Writing for Sentiment Analysis](#-tips-for-writing-for-sentiment-analysis)
   - [How the Sentiment Engine Evaluates Text](#how-the-sentiment-engine-evaluates-text)
   - [Real-world Examples & Scores](#real-world-examples--scores)
8. [Privacy, Data Security & Storage](#-privacy-data-security--storage)
9. [Keyboard Shortcuts & Accessibility](#-keyboard-shortcuts--accessibility)
10. [Frequently Asked Questions (FAQ)](#-frequently-asked-questions-faq)

---

## 🌿 Introduction & Philosophy

Traditional mood tracking apps often feel like a chore:
- They force you to rate yourself on arbitrary 1–5 star scales or select from dozens of emoji faces.
- They fail to capture nuanced feelings or context (e.g., feeling stressed by work but thrilled about seeing friends).
- Over time, rating friction leads to abandoned habits.

**Mood Journal solves this with zero-friction reflection:**
- **No manual ratings**: Just write how your day went.
- **Natural language understanding**: An integrated natural language processing (NLP) engine reads your entry and measures emotional polarity.
- **Visual reflection**: Your mood history is transformed into an interactive 371-day GitHub-style calendar heatmap, revealing emotional rhythms across seasons, weeks, and months.

---

## ⚡ Quickstart Tour

When you open Mood Journal, you are greeted by three main areas:

```
┌────────────────────────────────────────────────────────────────────────┐
│  🌿 Mood Journal                      [ Today: Sep 12, 2026 ]          │
├────────────────────────────────────────────────────────────────────────┤
│  [ 🔥 5 Days ] Current Streak   [ 🏆 12 Days ] Longest   [ 📅 34 Total]│
├────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Today's Journal Entry                [ 😊 Positive (+0.42) ]     │  │
│  │ ┌──────────────────────────────────────────────────────────────┐ │  │
│  │ │ Had a productive morning coding, then took a refreshing walk!│ │  │
│  │ └──────────────────────────────────────────────────────────────┘ │  │
│  │ 62 / 1000 characters                               [ Update Mood ]│ │
│  └──────────────────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ 371-Day Mood History                         [ Rolling 53 Weeks ]│  │
│  │ Jan    Feb    Mar    Apr    May    Jun    Jul    Aug    Sep        │  │
│  │ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓  │  │
│  │ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓ ▓  │  │
│  │ Hover or tap any square to inspect details.                      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Header & Stats Row**: Displays today's date, your current consecutive daily streak, your all-time longest streak, and your total recorded entries.
2. **Journaling Area**: An open textarea with a live character count where you log your daily thoughts.
3. **Calendar Heatmap**: A 53-week interactive visualization displaying your emotional trajectory over the past year.

---

## ✍️ Writing & Submitting Daily Entries

### Basic Submission
1. Click into the **Today's Journal Entry** textarea.
2. Write between **1 and 1,000 characters** describing your day, thoughts, feelings, accomplishments, or frustrations.
3. As soon as you type at least 1 valid character, the **Log Mood** button becomes enabled.
4. Click **Log Mood** (or press Enter).
5. The button displays a spinner with **Analyzing Mood...** while the backend scores your entry.
6. Once complete:
   - A success banner appears showing your calculated mood bucket and score.
   - The corresponding square on today's date in the heatmap instantly lights up with the mood color.
   - Your current streak increments.
   - The status pill in the top-right of the card updates to show today's mood.

### Character Counter & Limits
The character counter in the bottom-right of the input box provides real-time feedback:
- **0 – 899 characters**: Muted gray text (`0 / 1000`).
- **900 – 999 characters**: Orange warning (`920 / 1000`) indicating you are nearing the maximum limit.
- **1,000 characters**: Bold red indicator (`1000 / 1000`).
- **> 1,000 characters**: The submit button is automatically disabled to prevent truncated submissions.

### Updating Today's Entry
Mood Journal is designed for **one entry per calendar day** to keep your heatmap clean and meaningful:
- If you revisit the app later in the day, the textarea will already be pre-filled with what you wrote earlier.
- The button text changes from **Log Mood** to **Update Mood**.
- You can add more thoughts, modify what you wrote, or rewrite the entry.
- Submitting will update today's entry and re-score the sentiment, updating the cell color on the heatmap without creating a duplicate day.

---

## 🎨 Understanding the Mood Heatmap

### Grid Layout (53 Weeks × 7 Days)
The heatmap displays **371 days** (53 columns of 7-day weeks):
- **Columns**: Each column represents one full week, ordered from left (52 weeks ago) to right (the current week).
- **Rows**: Each row represents a day of the week, starting with **Sunday** at the top and ending with **Saturday** at the bottom:
  - Row 0: Sunday
  - Row 1: Monday
  - Row 2: Tuesday
  - Row 3: Wednesday
  - Row 4: Thursday
  - Row 5: Friday
  - Row 6: Saturday
- **Month Headers**: Positioned above the week columns where each new calendar month begins.
- **Today's Cell**: Highlighted with an illuminated cyan border so you can always locate the current day at a glance.
- **Future Days**: Cells in the current week that fall after today are rendered semi-transparent and non-interactive.

### The 5 Sentiment Buckets

Entries are evaluated on a continuous polarity scale from **-1.0 (very negative)** to **+1.0 (very positive)** and mapped to five intuitive color buckets:

| Score Range | Bucket Name | Heatmap Color | Emoji | Description |
|---|---|---|---|---|
| `-1.0` to `-0.50` | **Very Negative** | Dark Red (`#dc2626`) | 💔 | Difficult days, intense grief, extreme frustration, burnout |
| `-0.50` to `-0.10` | **Negative** | Coral Red (`#f87171`) | 🙁 | Challenging moments, low energy, mild sadness, minor setbacks |
| `-0.10` to `+0.10` | **Neutral** | Slate Gray (`#94a3b8`) | 😐 | Objective reflections, routine days, mixed emotions |
| `+0.10` to `+0.50` | **Positive** | Light Green (`#4ade80`) | 😊 | Pleasant experiences, calm satisfaction, good progress |
| `+0.50` to `+1.00` | **Very Positive** | Emerald Green (`#15803d`) | 🌟 | Breakthroughs, deep gratitude, joyful celebrations, excitement |
| *No entry* | **Empty** | Dark Navy (`#1e293b`) | 📝 | Day was not recorded |

### Legend & Visual Clues
The legend at the bottom of the heatmap displays the spectrum from negative to positive along with the empty cell indicator.

---

## 🔍 Inspecting Past Entries

### Hover Tooltip
Hover your mouse over any recorded square on desktop to trigger the quick floating tooltip:
- Shows the full formatted date (e.g. `Friday, August 14, 2026`).
- Shows the mood bucket badge with its associated score (e.g. `Positive (+0.38)`).
- Shows a preview snippet of the journal entry text.

### Detailed Modal Dialog
Click or tap on any cell in the heatmap to open the full **Entry Detail Modal**:
- **Full Journal Text**: Read the complete entry without truncation.
- **Precise Score & Bucket**: Displays exact numeric sentiment polarity.
- **Relative Date Indicator**: Shows whether the day was "Today", "Yesterday", or "N days ago".
- **Edit Shortcut**: If you click on today's entry, an **Edit Today's Entry** button appears in the modal footer. Clicking it closes the dialog and focuses the journal textarea.
- **Closing**: Press the `Esc` key, click the `×` button, click **Close**, or click outside the dialog.

---

## 🔥 Streak Tracking & Habit Building

### Current Streak vs. Longest Streak
- **Current Streak**: The number of consecutive days you have consistently logged an entry up to the present day.
- **Longest Streak**: The maximum unbroken streak you have ever achieved in your journaling history.

### Streak Grace Window (Yesterday/Today)
To accommodate different schedules, the current streak calculator includes a thoughtful grace period:
- If you **have already logged today**, your streak counts backwards from today.
- If you **have not yet logged today**, but you **logged yesterday**, your current streak is preserved! It will not drop to zero until today ends without a submission.
- Once you log today's entry, the streak increments by 1.

> [!TIP]
> **Timezone Consideration**: In v1, dates are evaluated using standard UTC time. For best results, log your entry consistently around the same time each day (e.g. evening reflection).

---

## 💡 Tips for Writing for Sentiment Analysis

### How the Sentiment Engine Evaluates Text
Mood Journal uses the **VADER (Valence Aware Dictionary and sEntiment Reasoner)** lexicon, an established NLP model specifically tuned for natural expressive writing.

It evaluates:
1. **Lexical Polarity**: Words with emotional weight (e.g., `great`, `peaceful`, `exhausted`, `disaster`).
2. **Punctuation Intensity**: Exclamation marks amplify polarity (`"Good day!"` scores higher than `"Good day."`).
3. **Capitalization**: All-caps words intensify sentiment (`"REALLY happy"` scores higher than `"really happy"`).
4. **Degree Modifiers**: Words like `extremely`, `very`, `hardly`, or `barely` scale polarity up or down.
5. **Contrastive Conjunctions**: The word `but` shifts emphasis to the subsequent clause:
   - *"The meeting was long, but we made great progress!"* &rarr; Overall **Positive**.
   - *"The food was good, but the service was terrible."* &rarr; Overall **Negative**.

### Real-world Examples & Scores (English)

| What You Write | Approximate Score | Bucket | Why |
|---|---|---|---|
| *"Woke up early, drank some tea, and read a novel. Very quiet, peaceful morning."* | `+0.68` | **Very Positive** 🌟 | Positive vocabulary (`peaceful`, `tea`, `quiet`) amplified by `Very`. |
| *"Finished my tasks on time. Everything went according to plan."* | `+0.25` | **Positive** 😊 | Mild positive satisfaction and accomplishment. |
| *"Routine Tuesday. Grocery shopping, washed the car, paid electricity bill."* | `0.00` | **Neutral** 😐 | Factual, routine activities without strong emotional valence. |
| *"Stuck in traffic for 2 hours and spilled my lunch. Really annoying day."* | `-0.48` | **Negative** 🙁 | Negative terms (`stuck`, `annoying`) intensified by `Really`. |
| *"Devastated by bad news from home. Feeling completely exhausted and hopeless."* | `-0.82` | **Very Negative** 💔 | Strong negative emotional words (`devastated`, `hopeless`). |

### 🇵🇰 Roman Urdu Journaling Guide

Mood Journal natively understands **Roman Urdu** (Urdu written in the Latin alphabet) as well as mixed **code-switching** ("Urdish"):

| Roman Urdu Entry | Approximate Score | Bucket | Why It Works |
|---|---|---|---|
| *"Aaj ka din bohot behtareen aur khushgawar guzra! Sab kaam ho gaye."* | `+0.86` | **Very Positive** 🌟 | High-valence words (`behtareen`, `khushgawar`) boosted by `bohot`. |
| *"Zabardast kaam hua aaj, doston ke sath maza aa gaya!"* | `+0.83` | **Very Positive** 🌟 | Expressive celebration words (`zabardast`, `maza`). |
| *"Subah utha, chai pi aur kaam shuru kiya."* | `0.00` | **Neutral** 😐 | Everyday routine without emotional charge. |
| *"Tabiyat kharab hai aur sar me bohot dard hai."* | `-0.79` | **Very Negative** 💔 | Negative physical/emotional states (`kharab`, `dard`, `bohot`). |
| *"Aaj bilkul acha din nahi tha, bohot udaas hoon."* | `-0.77` | **Very Negative** 💔 | Postfix negation (`acha din nahi`) properly inverts positive valence. |
| *"Kaam mushkil tha lekin team ne zabardast support kiya."* | `+0.87` | **Positive** 😊 | Contrastive conjunction (`lekin`) gives priority to positive outcome. |
| *"Meeting boring thi lekin overall din theek tha."* | `+0.39` | **Positive** 😊 | Mixed code-switching with mild positive resolution. |

---

## 🔒 Privacy, Data Security & Storage

- **Zero Third-party Tracking**: No analytics scripts, no third-party cookies, and no ad trackers.
- **Stateless Serverless Execution**: Serverless functions process your request in memory and terminate immediately after responding.
- **Encrypted Persistent Storage**: Entries are persisted in an Upstash Redis database using TLS encryption over HTTPS REST endpoints.
- **Offline / Local Storage**: In local development mode without Redis credentials, entries are stored in a local `data/entries.json` file on your machine.

---

## ⌨️ Keyboard Shortcuts & Accessibility

- **`Tab` / `Shift+Tab`**: Smooth keyboard navigation between textarea, buttons, and heatmap cells.
- **`Enter` (on focused cell)**: Opens the detail modal for that date.
- **`Escape`**: Closes the entry detail modal from anywhere.
- **Screen Reader Support**: Live character count announces via `aria-live="polite"`. The heatmap grid provides semantic `role="grid"` and accessible cell attributes.

---

## ❓ Frequently Asked Questions (FAQ)

### Can I delete or edit entries from previous days?
In v1, historical entries are read-only to maintain the integrity of your visual habit record. You can edit and update **today's** entry as many times as you like.

### What happens if I don't journal for a day?
The square for that day remains an empty dark cell (`No Entry`), and your current streak will reset to 0 (or 1 on the day you resume). Your **Longest Streak** record remains intact forever.

### Can I journal multiple times on the same day?
Yes! When you submit a second time on the same date, the system updates your existing entry and recalculates your score rather than creating duplicates.

### Does the app work on mobile devices?
Yes. The UI is fully responsive. The heatmap includes touch momentum scrolling, allowing you to easily pan across all 53 weeks on any smartphone or tablet screen.

---

*Enjoy journaling with Mood Journal! Build self-awareness, one entry at a time.*
