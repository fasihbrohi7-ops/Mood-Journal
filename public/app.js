/**
 * Mood Journal — Frontend Application
 * Handles API interaction, 53x7 GitHub-style heatmap generation,
 * live character count, sentiment updates, streak counters, and popover modals.
 */

(() => {
  'use strict';

  // State
  const state = {
    entriesMap: new Map(), // dateStr -> { score, bucket, text? }
    currentStreak: 0,
    longestStreak: 0,
    totalEntries: 0,
    todayStr: '',
    selectedDate: null,
    isSubmitting: false,
  };

  // DOM Elements
  const elements = {
    todayDateBadge: document.getElementById('todayDateBadge'),
    currentStreak: document.getElementById('currentStreak'),
    longestStreak: document.getElementById('longestStreak'),
    totalEntriesCount: document.getElementById('totalEntriesCount'),
    todayMoodIndicator: document.getElementById('todayMoodIndicator'),
    todayMoodPill: document.getElementById('todayMoodPill'),
    entryForm: document.getElementById('entryForm'),
    entryText: document.getElementById('entryText'),
    charCount: document.getElementById('charCount'),
    charCounter: document.getElementById('charCounter'),
    submitBtn: document.getElementById('submitBtn'),
    btnSpinner: document.getElementById('btnSpinner'),
    btnText: document.getElementById('btnText'),
    formMessage: document.getElementById('formMessage'),
    monthLabels: document.getElementById('monthLabels'),
    heatmapGrid: document.getElementById('heatmapGrid'),
    quickTooltip: document.getElementById('quickTooltip'),
    detailModal: document.getElementById('detailModal'),
    modalDateTitle: document.getElementById('modalDateTitle'),
    modalRelativeDate: document.getElementById('modalRelativeDate'),
    modalScoreBadge: document.getElementById('modalScoreBadge'),
    modalBucketBadge: document.getElementById('modalBucketBadge'),
    modalEntryText: document.getElementById('modalEntryText'),
    modalEditBtn: document.getElementById('modalEditBtn'),
    closeModalBtn: document.getElementById('closeModalBtn'),
    modalCloseFooterBtn: document.getElementById('modalCloseFooterBtn'),
  };

  // Formatting helpers
  const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const MONTHS_FULL = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  const DAYS_FULL = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  function formatDateISO(d) {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  function formatDisplayDate(dateStr) {
    const [y, m, d] = dateStr.split('-').map(Number);
    const date = new Date(y, m - 1, d);
    const dayName = DAYS_FULL[date.getDay()];
    const monthName = MONTHS_FULL[date.getMonth()];
    return `${dayName}, ${monthName} ${d}, ${y}`;
  }

  function formatRelativeDate(dateStr) {
    if (dateStr === state.todayStr) return 'Today';
    const [y, m, d] = dateStr.split('-').map(Number);
    const target = new Date(y, m - 1, d);
    const [ty, tm, td] = state.todayStr.split('-').map(Number);
    const today = new Date(ty, tm - 1, td);
    const diffDays = Math.round((today - target) / (1000 * 60 * 60 * 24));
    if (diffDays === 1) return 'Yesterday';
    if (diffDays > 1) return `${diffDays} days ago`;
    return dateStr;
  }

  function formatBucketName(bucket) {
    switch (bucket) {
      case 'very_positive': return 'Very Positive';
      case 'positive': return 'Positive';
      case 'neutral': return 'Neutral';
      case 'negative': return 'Negative';
      case 'very_negative': return 'Very Negative';
      default: return 'No Entry';
    }
  }

  function getBucketEmoji(bucket) {
    switch (bucket) {
      case 'very_positive': return '🌟';
      case 'positive': return '😊';
      case 'neutral': return '😐';
      case 'negative': return '🙁';
      case 'very_negative': return '💔';
      default: return '📝';
    }
  }

  // --- API Client ---
  async function apiFetch(endpoint, options = {}) {
    const response = await fetch(endpoint, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      },
      ...options
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.error || `HTTP ${response.status} Error`);
    }
    return data;
  }

  async function loadInitialData() {
    try {
      const now = new Date();
      state.todayStr = formatDateISO(now);
      
      const [ty, tm, td] = state.todayStr.split('-').map(Number);
      const displayToday = new Date(ty, tm - 1, td);
      elements.todayDateBadge.textContent = `Today: ${MONTHS[displayToday.getMonth()]} ${displayToday.getDate()}, ${displayToday.getFullYear()}`;

      // Fetch entries & streaks in parallel
      const [entriesRes, streakRes] = await Promise.all([
        apiFetch('/api/entries?days=371').catch(err => {
          console.error('Failed to fetch entries:', err);
          return { entries: [] };
        }),
        apiFetch('/api/streak').catch(err => {
          console.error('Failed to fetch streak:', err);
          return { current_streak: 0, longest_streak: 0 };
        })
      ]);

      // Populate entries
      state.entriesMap.clear();
      (entriesRes.entries || []).forEach(e => {
        state.entriesMap.set(e.date, e);
      });
      state.totalEntries = state.entriesMap.size;

      // Update streaks
      state.currentStreak = streakRes.current_streak || 0;
      state.longestStreak = streakRes.longest_streak || 0;
      updateStatsUI();

      // Check today's entry
      if (state.entriesMap.has(state.todayStr)) {
        await checkTodayEntry();
      }

      // Render 53x7 Heatmap
      renderHeatmap();

    } catch (err) {
      console.error('Initialization error:', err);
      showMessage(err.message || 'Failed to connect to backend.', 'error');
    }
  }

  async function checkTodayEntry() {
    try {
      const entry = await apiFetch(`/api/entry/${state.todayStr}`);
      state.entriesMap.set(state.todayStr, entry);
      
      // Pre-fill textarea
      elements.entryText.value = entry.text || '';
      updateCharCount();
      
      // Update button text to "Update Mood"
      elements.btnText.textContent = "Update Mood";
      
      // Show today's mood pill
      const bucket = entry.bucket || 'neutral';
      elements.todayMoodIndicator.classList.remove('hidden');
      elements.todayMoodPill.className = `mood-pill ${bucket}`;
      elements.todayMoodPill.textContent = `${getBucketEmoji(bucket)} ${formatBucketName(bucket)} (${entry.score >= 0 ? '+' : ''}${entry.score})`;
    } catch (err) {
      console.warn('Could not load today entry details:', err);
    }
  }

  function updateStatsUI() {
    elements.currentStreak.textContent = state.currentStreak;
    elements.longestStreak.textContent = state.longestStreak;
    elements.totalEntriesCount.textContent = state.totalEntries;
  }

  // --- Heatmap Construction (53 Weeks x 7 Days = 371 Days) ---
  function renderHeatmap() {
    const gridEl = elements.heatmapGrid;
    const monthLabelsEl = elements.monthLabels;
    gridEl.innerHTML = '';
    monthLabelsEl.innerHTML = '';

    const today = new Date();
    const todayISO = state.todayStr;

    // We align the calendar ending on the Saturday of the current week
    const currentDayOfWeek = today.getDay(); // 0 = Sun, 6 = Sat
    const gridEndDate = new Date(today);
    gridEndDate.setDate(today.getDate() + (6 - currentDayOfWeek));

    // 53 weeks = 371 days
    const totalDays = 53 * 7;
    const gridStartDate = new Date(gridEndDate);
    gridStartDate.setDate(gridEndDate.getDate() - (totalDays - 1));

    // Month headers positioning
    // We create month header spans mapped across the 53 columns
    const monthColumns = new Map(); // colIndex -> MonthName
    let prevMonth = -1;

    // Generate days in column-first order (weeks 0 to 52, days 0 to 6)
    for (let w = 0; w < 53; w++) {
      for (let d = 0; d < 7; d++) {
        const cellDate = new Date(gridStartDate);
        cellDate.setDate(gridStartDate.getDate() + (w * 7 + d));
        const cellISO = formatDateISO(cellDate);

        // Check if month changes on Sunday (d === 0) or first day of month falls in this week
        const cellMonth = cellDate.getMonth();
        if (d === 0) {
          if (cellMonth !== prevMonth) {
            monthColumns.set(w, MONTHS[cellMonth]);
            prevMonth = cellMonth;
          }
        }

        const cell = document.createElement('div');
        cell.className = 'heat-cell';
        cell.dataset.date = cellISO;

        const isFuture = cellISO > todayISO;
        const isToday = cellISO === todayISO;

        if (isToday) {
          cell.classList.add('today-cell');
        }

        if (isFuture) {
          cell.classList.add('future');
          cell.style.opacity = '0.25';
          cell.style.cursor = 'default';
        } else {
          const entry = state.entriesMap.get(cellISO);
          if (entry && entry.bucket) {
            cell.classList.add(entry.bucket);
            cell.dataset.bucket = entry.bucket;
            cell.dataset.score = entry.score;
          } else {
            cell.classList.add('empty');
          }

          // Attach interaction listeners
          cell.addEventListener('mouseenter', handleCellHover);
          cell.addEventListener('mouseleave', handleCellLeave);
          cell.addEventListener('click', () => handleCellClick(cellISO));
        }

        gridEl.appendChild(cell);
      }
    }

    // Build Month Labels header row
    // Prepend empty placeholder for day labels column (32px)
    const spacer = document.createElement('div');
    monthLabelsEl.appendChild(spacer);

    for (let w = 0; w < 53; w++) {
      const monthCol = document.createElement('div');
      monthCol.className = 'month-col';
      if (monthColumns.has(w)) {
        monthCol.textContent = monthColumns.get(w);
      }
      monthLabelsEl.appendChild(monthCol);
    }
  }

  // --- Quick Tooltip Handling ---
  function handleCellHover(e) {
    const cell = e.currentTarget;
    const dateISO = cell.dataset.date;
    if (!dateISO) return;

    const entry = state.entriesMap.get(dateISO);
    const tooltip = elements.quickTooltip;
    const dateFormatted = formatDisplayDate(dateISO);

    let html = `<div class="tooltip-date">${dateFormatted}</div>`;

    if (entry) {
      const scoreStr = (entry.score >= 0 ? '+' : '') + entry.score;
      const bucketName = formatBucketName(entry.bucket);
      const emoji = getBucketEmoji(entry.bucket);
      html += `
        <div class="tooltip-meta">
          <span class="tooltip-badge" style="background: var(--mood-${entry.bucket}); color: #fff;">${bucketName}</span>
          <span style="font-family: monospace; font-size: 0.725rem; color: #94a3b8;">${scoreStr}</span>
        </div>
      `;
      if (entry.text) {
        html += `<div class="tooltip-text">${escapeHtml(entry.text)}</div>`;
      } else {
        html += `<div class="tooltip-text" style="font-style: italic;">Click to view journal entry</div>`;
      }
    } else {
      html += `<div class="tooltip-text" style="color: #64748b;">No entry recorded for this day.</div>`;
    }

    tooltip.innerHTML = html;
    tooltip.classList.remove('hidden');

    const rect = cell.getBoundingClientRect();
    const tooltipX = rect.left + rect.width / 2;
    const tooltipY = rect.top - 6;

    tooltip.style.left = `${tooltipX}px`;
    tooltip.style.top = `${tooltipY}px`;
  }

  function handleCellLeave() {
    elements.quickTooltip.classList.add('hidden');
  }

  // --- Modal Popover Handling ---
  async function handleCellClick(dateISO) {
    elements.quickTooltip.classList.add('hidden');
    state.selectedDate = dateISO;

    const entry = state.entriesMap.get(dateISO);
    elements.modalDateTitle.textContent = formatDisplayDate(dateISO);
    elements.modalRelativeDate.textContent = formatRelativeDate(dateISO);

    // If today, show "Edit" button
    if (dateISO === state.todayStr) {
      elements.modalEditBtn.classList.remove('hidden');
    } else {
      elements.modalEditBtn.classList.add('hidden');
    }

    if (!entry) {
      elements.modalScoreBadge.textContent = 'Score: N/A';
      elements.modalBucketBadge.textContent = 'No Entry';
      elements.modalBucketBadge.className = 'modal-badge modal-bucket-badge';
      elements.modalBucketBadge.style.backgroundColor = 'var(--cell-empty)';
      elements.modalBucketBadge.style.color = 'var(--text-muted)';
      elements.modalEntryText.textContent = dateISO === state.todayStr
        ? 'You have not written a journal entry for today yet. Use the form above to log your thoughts!'
        : 'No journal entry was logged for this day.';
      openModal();
      return;
    }

    // Load full entry details if text is not already cached
    let fullText = entry.text;
    if (!fullText) {
      try {
        elements.modalEntryText.textContent = 'Loading entry...';
        openModal();
        const fullEntry = await apiFetch(`/api/entry/${dateISO}`);
        fullText = fullEntry.text || '';
        entry.text = fullText;
        state.entriesMap.set(dateISO, entry);
      } catch (err) {
        fullText = 'Could not load entry details.';
      }
    } else {
      openModal();
    }

    const scoreStr = (entry.score >= 0 ? '+' : '') + entry.score;
    elements.modalScoreBadge.textContent = `Score: ${scoreStr}`;
    elements.modalBucketBadge.textContent = `${getBucketEmoji(entry.bucket)} ${formatBucketName(entry.bucket)}`;
    elements.modalBucketBadge.className = `modal-badge modal-bucket-badge`;
    elements.modalBucketBadge.style.backgroundColor = `var(--mood-${entry.bucket})`;
    elements.modalBucketBadge.style.color = '#ffffff';
    elements.modalEntryText.textContent = fullText;
  }

  function openModal() {
    elements.detailModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    elements.detailModal.classList.add('hidden');
    document.body.style.overflow = '';
  }

  // --- Form & Input Handling ---
  function updateCharCount() {
    const len = elements.entryText.value.length;
    elements.charCount.textContent = len;

    elements.charCounter.classList.remove('warning', 'limit');
    if (len >= 1000) {
      elements.charCounter.classList.add('limit');
    } else if (len >= 900) {
      elements.charCounter.classList.add('warning');
    }

    const trimmed = elements.entryText.value.trim();
    const isValid = trimmed.length >= 1 && trimmed.length <= 1000;
    elements.submitBtn.disabled = !isValid || state.isSubmitting;
  }

  async function handleFormSubmit(e) {
    e.preventDefault();
    if (state.isSubmitting) return;

    const rawText = elements.entryText.value;
    const trimmed = rawText.trim();
    if (!trimmed || trimmed.length > 1000) {
      showMessage('Please enter between 1 and 1,000 characters.', 'error');
      return;
    }

    setSubmitting(true);
    hideMessage();

    try {
      const result = await apiFetch('/api/entry', {
        method: 'POST',
        body: JSON.stringify({ text: trimmed })
      });

      // Update local state
      state.entriesMap.set(result.date, {
        date: result.date,
        text: result.text,
        score: result.score,
        bucket: result.bucket
      });

      // Update cell directly in heatmap
      const cell = elements.heatmapGrid.querySelector(`[data-date="${result.date}"]`);
      if (cell) {
        cell.className = `heat-cell ${result.bucket} today-cell`;
        cell.dataset.bucket = result.bucket;
        cell.dataset.score = result.score;
      }

      // Re-fetch streaks
      const streakRes = await apiFetch('/api/streak').catch(() => ({
        current_streak: state.currentStreak,
        longest_streak: state.longestStreak
      }));
      state.currentStreak = streakRes.current_streak;
      state.longestStreak = streakRes.longest_streak;
      state.totalEntries = state.entriesMap.size;
      updateStatsUI();

      // Update today pill indicator
      const bucket = result.bucket;
      elements.todayMoodIndicator.classList.remove('hidden');
      elements.todayMoodPill.className = `mood-pill ${bucket}`;
      elements.todayMoodPill.textContent = `${getBucketEmoji(bucket)} ${formatBucketName(bucket)} (${result.score >= 0 ? '+' : ''}${result.score})`;

      elements.btnText.textContent = 'Update Mood';
      showMessage(`Mood recorded: ${formatBucketName(bucket)} (Score: ${result.score >= 0 ? '+' : ''}${result.score})`, 'success');

    } catch (err) {
      console.error('Submission error:', err);
      showMessage(err.message || 'Failed to save entry. Please try again.', 'error');
    } finally {
      setSubmitting(false);
    }
  }

  function setSubmitting(loading) {
    state.isSubmitting = loading;
    elements.submitBtn.disabled = loading || elements.entryText.value.trim().length === 0;
    if (loading) {
      elements.btnSpinner.classList.remove('hidden');
      elements.btnText.textContent = 'Analyzing Mood...';
    } else {
      elements.btnSpinner.classList.add('hidden');
      elements.btnText.textContent = state.entriesMap.has(state.todayStr) ? 'Update Mood' : 'Log Mood';
    }
  }

  function showMessage(text, type = 'error') {
    elements.formMessage.textContent = text;
    elements.formMessage.className = `form-message ${type}`;
    elements.formMessage.classList.remove('hidden');
  }

  function hideMessage() {
    elements.formMessage.classList.add('hidden');
    elements.formMessage.textContent = '';
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // --- Event Listeners ---
  elements.entryText.addEventListener('input', updateCharCount);
  elements.entryForm.addEventListener('submit', handleFormSubmit);

  elements.closeModalBtn.addEventListener('click', closeModal);
  elements.modalCloseFooterBtn.addEventListener('click', closeModal);
  elements.detailModal.addEventListener('click', (e) => {
    if (e.target === elements.detailModal) closeModal();
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !elements.detailModal.classList.contains('hidden')) {
      closeModal();
    }
  });

  elements.modalEditBtn.addEventListener('click', () => {
    closeModal();
    elements.entryText.focus();
    elements.entryText.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });

  // Initialize
  document.addEventListener('DOMContentLoaded', loadInitialData);
})();
