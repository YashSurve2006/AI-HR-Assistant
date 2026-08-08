/* ================================================================
   AI HR Assistant — script.js
   Vanilla JS • fetch() for all API calls • Chart.js for charts
   ================================================================ */

'use strict';

const API = '';
const MAX_MSG_LENGTH = 2000;

/* ── Helpers ─────────────────────────────────────────────────────── */
function el(id) { return document.getElementById(id); }
function show(id) { const e = el(id); if (e) e.classList.remove('hidden'); }
function hide(id) { const e = el(id); if (e) e.classList.add('hidden'); }
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ================================================================
   All DOM-dependent code runs after DOMContentLoaded
   ================================================================ */
document.addEventListener('DOMContentLoaded', function () {

  /* ── Navbar / Hamburger ────────────────────────────────────────── */
  const hamburger = el('hamburger');
  const navLinks  = el('nav-links');

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => navLinks.classList.toggle('open'));

    // Close mobile menu when a link is clicked
    navLinks.querySelectorAll('.nav-link').forEach(link => {
      link.addEventListener('click', () => navLinks.classList.remove('open'));
    });
  }

  // Active link highlight on scroll
  const sections = document.querySelectorAll('.section');
  const navItems  = document.querySelectorAll('.nav-link');
  if (sections.length && navItems.length) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          navItems.forEach(a => {
            a.classList.toggle('active', a.dataset.section === entry.target.id);
          });
        }
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    sections.forEach(s => io.observe(s));
  }

  /* ── Health Check ──────────────────────────────────────────────── */
  async function checkHealth() {
    try {
      const r = await fetch(`${API}/api/health`);
      if (r.ok) {
        el('status-dot').className    = 'status-dot ok';
        el('status-text').textContent = 'Backend Online';
      } else throw new Error('not ok');
    } catch {
      el('status-dot').className    = 'status-dot error';
      el('status-text').textContent = 'Backend Offline';
    }
  }

  /* ── Chart registry ────────────────────────────────────────────── */
  const chartInstances = {};

  function destroyChart(id) {
    if (chartInstances[id]) {
      chartInstances[id].destroy();
      delete chartInstances[id];
    }
  }

  /* ── Theme Toggle & Persistence ────────────────────────────────── */
  const themeToggle = el('theme-toggle');
  const themeIcon = el('theme-icon');

  function updateChartThemes(isDark) {
    const textColor = isDark ? '#cbd5e1' : '#767586'; 
    const gridColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)';
    
    Chart.defaults.color = textColor;
    Chart.defaults.font.family = 'Inter';

    Object.values(chartInstances).forEach(chart => {
      if (chart.options.scales) {
        if (chart.options.scales.x) {
          if (!chart.options.scales.x.ticks) chart.options.scales.x.ticks = {};
          chart.options.scales.x.ticks.color = textColor;
          if (!chart.options.scales.x.grid) chart.options.scales.x.grid = {};
          chart.options.scales.x.grid.color = gridColor;
        }
        if (chart.options.scales.y) {
          if (!chart.options.scales.y.ticks) chart.options.scales.y.ticks = {};
          chart.options.scales.y.ticks.color = textColor;
          if (!chart.options.scales.y.grid) chart.options.scales.y.grid = {};
          chart.options.scales.y.grid.color = gridColor;
        }
      }
      if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
        chart.options.plugins.legend.labels.color = textColor;
      }
      chart.update();
    });
  }

  function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    if (themeIcon) {
      themeIcon.textContent = theme === 'dark' ? 'light_mode' : 'dark_mode';
    }
    updateChartThemes(theme === 'dark');
  }

  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    setTheme(savedTheme);
  } else {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    setTheme(prefersDark ? 'dark' : 'light');
  }

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      setTheme(currentTheme === 'dark' ? 'light' : 'dark');
    });
  }

  /* ── Dashboard ─────────────────────────────────────────────────── */
  async function loadDashboard() {
    try {
      const r    = await fetch(`${API}/api/dashboard`);
      const data = await r.json();
      if (!data.success) return;

      const s = data.summary;
      const setEl = (id, val) => { const e = el(id); if (e) e.textContent = val; };
      
      setEl('stat-total-jobs', s.total_jobs);
      setEl('stat-total-feedback', s.total_feedback);
      setEl('stat-avg-rating', Number(s.average_rating).toFixed(2));
      setEl('stat-positive-pct', s.positive_percentage + '%');

      renderSentimentChart(data.sentiment);
      renderRatingChart(data.rating_distribution);
      renderJobDeptChart('jobDeptChart',     data.job_distribution);
      renderJobDeptChart('jobDeptChartJobs', data.job_distribution);
      renderJobLocChart(data.location_distribution);

      // Employee Insights section
      setEl('ins-positive', s.positive);
      setEl('ins-negative', s.negative);
      setEl('ins-neutral', s.neutral);
      setEl('ins-positive-pct', s.positive_percentage + '% of total');
      setEl('ins-negative-pct', s.negative_percentage + '% of total');
      setEl('ins-neutral-pct', s.neutral_percentage + '% of total');

      renderDeptSentimentChart(data.department_sentiment);
    } catch (e) {
      console.error('Dashboard load error:', e);
    }
  }

  function renderSentimentChart(sentiment) {
    destroyChart('sentimentChart');
    const ctx = el('sentimentChart').getContext('2d');
    chartInstances['sentimentChart'] = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: sentiment.labels,
        datasets: [{
          data: sentiment.values,
          backgroundColor: ['#d1fae5', '#fee2e2', '#e0e7ff'],
          borderColor:     ['#10b981', '#ef4444', '#6366f1'],
          borderWidth: 2,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { font: { family: 'Inter', size: 12 }, padding: 16 } }
        },
        cutout: '68%'
      }
    });
  }

  function renderRatingChart(dist) {
    destroyChart('ratingChart');
    const ctx = el('ratingChart').getContext('2d');
    chartInstances['ratingChart'] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: dist.map(d => `${d.rating} Star${d.rating > 1 ? 's' : ''}`),
        datasets: [{
          label: 'Feedback Count',
          data: dist.map(d => d.count),
          backgroundColor: 'rgba(99,102,241,0.7)',
          borderColor: '#6366f1',
          borderWidth: 2,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, ticks: { precision: 0, font: { family: 'Inter' } }, grid: { color: 'rgba(0,0,0,.04)' } },
          x: { grid: { display: false }, ticks: { font: { family: 'Inter' } } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }

  function renderJobDeptChart(canvasId, dist) {
    destroyChart(canvasId);
    const cvs = el(canvasId);
    if (!cvs) return;
    const ctx = cvs.getContext('2d');
    const colors = ['#6366f1','#14b8a6','#f59e0b','#ef4444','#10b981','#8b5cf6','#f97316','#06b6d4'];
    chartInstances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: dist.map(d => d.department),
        datasets: [{
          label: 'Open Positions',
          data: dist.map(d => d.count),
          backgroundColor: dist.map((_, i) => colors[i % colors.length] + 'bb'),
          borderColor:     dist.map((_, i) => colors[i % colors.length]),
          borderWidth: 2,
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { beginAtZero: true, ticks: { precision: 0, font: { family: 'Inter' } }, grid: { color: 'rgba(0,0,0,.04)' } },
          y: { grid: { display: false }, ticks: { font: { family: 'Inter', size: 11 } } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }

  function renderJobLocChart(dist) {
    destroyChart('jobLocChart');
    const ctx = el('jobLocChart').getContext('2d');
    chartInstances['jobLocChart'] = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: dist.map(d => d.location),
        datasets: [{
          data: dist.map(d => d.count),
          backgroundColor: ['#6366f1bb','#14b8a6bb','#f59e0bbb','#ef4444bb','#10b981bb'],
          borderWidth: 2,
          borderColor: '#fff',
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { font: { family: 'Inter', size: 12 }, padding: 12 } }
        },
        cutout: '60%'
      }
    });
  }

  function renderDeptSentimentChart(deptData) {
    destroyChart('deptSentimentChart');
    const ctx = el('deptSentimentChart').getContext('2d');
    chartInstances['deptSentimentChart'] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: deptData.map(d => d.department),
        datasets: [
          { label: 'Positive', data: deptData.map(d => d.positive), backgroundColor: '#10b981bb', borderColor: '#10b981', borderWidth: 1.5, borderRadius: 4 },
          { label: 'Negative', data: deptData.map(d => d.negative), backgroundColor: '#ef4444bb', borderColor: '#ef4444', borderWidth: 1.5, borderRadius: 4 },
          { label: 'Neutral',  data: deptData.map(d => d.neutral),  backgroundColor: '#e0e7ffbb', borderColor: '#6366f1', borderWidth: 1.5, borderRadius: 4 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { grid: { display: false }, ticks: { font: { family: 'Inter', size: 11 } } },
          y: { beginAtZero: true, ticks: { precision: 0, font: { family: 'Inter' } }, grid: { color: 'rgba(0,0,0,.04)' } }
        },
        plugins: {
          legend: { position: 'bottom', labels: { font: { family: 'Inter', size: 12 }, padding: 12 } }
        }
      }
    });
  }

  /* ── Feedback List ─────────────────────────────────────────────── */
  async function loadFeedback() {
    const list = el('feedback-list');
    try {
      const r    = await fetch(`${API}/api/feedback/sentiment`);
      const data = await r.json();
      if (!data.success) {
        list.innerHTML = '<p class="loading-placeholder">Could not load feedback.</p>';
        return;
      }
      list.innerHTML = '';
      data.feedback.slice(0, 10).forEach(fb => {
        const sntClass = fb.sentiment === 'Positive' ? 'snt-positive'
                       : fb.sentiment === 'Negative' ? 'snt-negative'
                       : 'snt-neutral';
        const item = document.createElement('div');
        item.className = 'feedback-item';
        // Use escapeHtml to prevent XSS from feedback text
        item.innerHTML = `
          <p class="feedback-name">${escapeHtml(fb.employee_name)}</p>
          <p class="feedback-dept">${escapeHtml(fb.department)} &bull; Rating: ${fb.rating}/5</p>
          <p class="feedback-text">${escapeHtml(fb.feedback)}</p>
          <span class="feedback-sentiment ${sntClass}">${fb.sentiment} (${fb.polarity})</span>
        `;
        list.appendChild(item);
      });
    } catch (e) {
      list.innerHTML = '<p class="loading-placeholder">Could not load feedback. Make sure the backend is running.</p>';
    }
  }

  /* ── HR Chatbot ────────────────────────────────────────────────── */
  const chatMessages = el('chat-messages');
  const chatInput    = el('chat-input');
  const chatSend     = el('chat-send');
  
  // Generate a random session ID on load for context tracking
  const sessionId    = 'sess_' + Math.random().toString(36).substring(2, 9);

  function appendChatMsg(role, text, meta) {
    const div = document.createElement('div');
    div.className = `chat-msg chat-msg--${role}`;
    
    let metaHtml = '';
    if (meta && role === 'ai') {
      const confText = meta.confidence !== undefined ? `${(meta.confidence * 100).toFixed(0)}%` : '';
      const level = meta.confidence_level || 'low';
      let color = 'var(--text-muted)';
      if (level === 'high') color = 'var(--green)';
      else if (level === 'medium') color = 'var(--orange)';
      
      metaHtml = `<div style="margin-top:8px; display:flex; gap:8px; font-size:11px; align-items:center;">`;
      if (confText) {
          metaHtml += `<span style="padding:2px 6px; border-radius:4px; background:rgba(0,0,0,0.05); color:${color}; font-weight:600;">Conf: ${confText} (${level})</span>`;
      }
      if (meta.source) {
          metaHtml += `<span style="color:var(--text-muted)">Source: ${meta.source}</span>`;
      }
      metaHtml += `</div>`;
      if (meta.matched_question) {
          metaHtml += `<div style="margin-top:4px; font-size:11px; color:var(--text-muted); font-style:italic;">Matched: "${escapeHtml(meta.matched_question)}"</div>`;
      }
    }
    
    div.innerHTML = `
      <div class="chat-bubble">
        <p>${escapeHtml(text)}</p>
        ${metaHtml}
      </div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function showTyping() {
    // Remove any existing indicator first
    const existing = el('typing-indicator');
    if (existing) existing.remove();

    const div = document.createElement('div');
    div.className = 'chat-msg chat-msg--ai';
    div.id = 'typing-indicator';
    div.innerHTML = `<div class="typing-bubble">
      <span style="font-size:13px;font-weight:500;color:var(--text-muted)">AI is thinking</span>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function hideTyping() {
    const t = el('typing-indicator');
    if (t) t.remove();
  }

  async function sendChatMessage() {
    const rawMsg = chatInput.value.trim();
    if (!rawMsg) return;

    // Guard: max message length
    const msg = rawMsg.slice(0, MAX_MSG_LENGTH);

    chatInput.value   = '';
    chatSend.disabled = true;
    appendChatMsg('user', msg);
    showTyping();

    try {
      const r    = await fetch(`${API}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg, session_id: sessionId })
      });
      const data = await r.json();
      hideTyping();
      if (data.success) {
        appendChatMsg('ai', data.answer, data);
      } else {
        appendChatMsg('ai', 'Sorry, I encountered an issue. Please try again.', null);
      }
    } catch {
      hideTyping();
      appendChatMsg('ai', 'Could not reach the server. Please make sure the backend is running on port 5000.');
    } finally {
      chatSend.disabled = false;
      chatInput.focus();
    }
  }

  chatSend.addEventListener('click', sendChatMessage);
  chatInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  });

  /* ── Resume Analyzer ───────────────────────────────────────────── */
  const uploadZone   = el('upload-zone');
  const fileInput    = el('resume-file-input');
  const browseBtn    = el('browse-btn');
  const analyzeBtn   = el('analyze-btn');
  const recommendBtn = el('recommend-btn');
  let selectedFile   = null;

  // BUG FIX: stopPropagation on browseBtn so click doesn't bubble
  // up to uploadZone and open the file picker twice
  browseBtn.addEventListener('click', e => {
    e.stopPropagation();
    fileInput.click();
  });

  uploadZone.addEventListener('click', () => fileInput.click());

  // Drag-and-drop
  ['dragover', 'dragenter'].forEach(evt => {
    uploadZone.addEventListener(evt, e => {
      e.preventDefault();
      e.stopPropagation();
      uploadZone.classList.add('drag-over');
    });
  });
  ['dragleave', 'drop'].forEach(evt => {
    uploadZone.addEventListener(evt, e => {
      e.preventDefault();
      e.stopPropagation();
      uploadZone.classList.remove('drag-over');
    });
  });
  uploadZone.addEventListener('drop', e => {
    const f = e.dataTransfer.files[0];
    if (f) setFile(f);
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) setFile(fileInput.files[0]);
  });

  function setFile(file) {
    const hint = el('upload-hint');
    // Validate extension
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      hint.textContent = 'Only PDF files are accepted. Please choose a .pdf file.';
      hint.style.color = 'var(--red)';
      selectedFile = null;
      analyzeBtn.disabled   = true;
      recommendBtn.disabled = true;
      return;
    }
    // Validate size (10 MB)
    if (file.size > 10 * 1024 * 1024) {
      hint.textContent = 'File is too large. Maximum size is 10 MB.';
      hint.style.color = 'var(--red)';
      selectedFile = null;
      analyzeBtn.disabled   = true;
      recommendBtn.disabled = true;
      return;
    }
    selectedFile = file;
    hint.textContent = `Selected: ${escapeHtml(file.name)} (${(file.size / 1024).toFixed(1)} KB)`;
    hint.style.color = 'var(--green)';
    analyzeBtn.disabled   = false;
    recommendBtn.disabled = false;
    // Clear previous results when a new file is chosen
    hide('resume-results');
    hide('recommendations-area');
    // Reset score ring to 0 — must match SVG stroke-dasharray="314.16"
    el('score-ring-fill').style.strokeDashoffset = '314.16';
    el('score-number').textContent = '0';
  }

  /* ── Resume Analyze ────────────────────────────────────────────── */
  analyzeBtn.addEventListener('click', analyzeResume);

  async function analyzeResume() {
    if (!selectedFile) return;
    show('resume-loading');
    hide('resume-results');
    analyzeBtn.disabled = true;

    const fd = new FormData();
    fd.append('file', selectedFile);

    try {
      const r    = await fetch(`${API}/api/resume/analyze`, { method: 'POST', body: fd });
      const data = await r.json();

      if (!data.success) {
        showError('Resume Error', data.error || 'Could not analyze the resume.');
        return;
      }
      renderAnalysisResults(data);
      show('resume-results');
      // Scroll to results
      el('resume-results').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } catch {
      showError('Connection Error', 'Could not reach the backend. Make sure Flask is running on port 5000.');
    } finally {
      hide('resume-loading');
      analyzeBtn.disabled = false;
    }
  }

  function renderAnalysisResults(data) {
    // Circumference = 2 * PI * r(50) = 314.159... — rounded to 314.16 to match SVG attribute
    const circumference = 314.16;
    const score  = Math.max(0, Math.min(100, data.score));
    const offset = circumference * (1 - score / 100);

    el('score-number').textContent    = score;
    el('score-filename').textContent  = data.filename || '';
    // Use double rAF to ensure CSS transition fires
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        el('score-ring-fill').style.strokeDashoffset = offset.toFixed(2);
      });
    });

    // Score breakdown bars
    const bd     = data.score_breakdown || {};
    const maxMap = { skills: 25, experience: 25, education: 20, projects: 15, content_quality: 15 };
    const lblMap = { skills: 'Skills', experience: 'Experience', education: 'Education', projects: 'Projects', content_quality: 'Content Quality' };
    const barsEl = el('breakdown-bars');
    barsEl.innerHTML = '';
    Object.entries(bd).forEach(([key, val]) => {
      const max = maxMap[key] || 25;
      const pct = Math.min(100, Math.round((val / max) * 100));
      barsEl.innerHTML += `
        <div class="breakdown-item">
          <div class="breakdown-label">
            <span>${lblMap[key] || key}</span>
            <span>${val}/${max}</span>
          </div>
          <div class="breakdown-bar-bg">
            <div class="breakdown-bar-fill" style="width:${pct}%"></div>
          </div>
        </div>`;
    });

    // Skills cloud
    const cloud = el('skills-cloud');
    cloud.innerHTML = '';
    el('skill-count').textContent = data.skill_count || 0;
    const skills = Array.isArray(data.skills) ? data.skills : [];
    if (skills.length === 0) {
      cloud.innerHTML = '<span style="color:var(--text-muted);font-size:13px;">No recognizable technical skills found in this resume.</span>';
    } else {
      skills.forEach(s => {
        const chip = document.createElement('span');
        chip.className   = 'skill-chip';
        chip.textContent = s;
        cloud.appendChild(chip);
      });
    }
    el('text-length-info').textContent = `Extracted text: ${data.text_length || 0} characters`;
  }

  /* ── Job Recommendations ───────────────────────────────────────── */
  recommendBtn.addEventListener('click', recommendJobs);

  async function recommendJobs() {
    if (!selectedFile) return;
    show('resume-loading');
    hide('recommendations-area');
    recommendBtn.disabled = true;

    const fd = new FormData();
    fd.append('file', selectedFile);

    try {
      const r    = await fetch(`${API}/api/resume/recommend`, { method: 'POST', body: fd });
      const data = await r.json();

      if (!data.success) {
        showError('Recommendation Error', data.error || 'Could not generate recommendations.');
        return;
      }
      renderRecommendations(data.recommendations);
      show('recommendations-area');
      el('recommendations-area').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } catch {
      showError('Connection Error', 'Could not reach the backend. Make sure Flask is running on port 5000.');
    } finally {
      hide('resume-loading');
      recommendBtn.disabled = false;
    }
  }

  function renderRecommendations(recs) {
    const grid = el('jobs-grid');
    grid.innerHTML = '';
    if (!recs || recs.length === 0) {
      grid.innerHTML = '<p style="color:var(--text-muted)">No matching jobs found for this resume.</p>';
      return;
    }
    recs.forEach(rec => {
      const simPct      = (Number(rec.similarity) * 100).toFixed(1);
      const matchPct    = Number(rec.match_percentage) || 0;
      const matchedHtml = (rec.matched_skills || []).map(s => `<span class="job-skill-matched">${escapeHtml(s)}</span>`).join('');
      const missingHtml = (rec.missing_skills  || []).map(s => `<span class="job-skill-missing">${escapeHtml(s)}</span>`).join('');

      let linksHtml = '';
      if (rec.platform_links) {
        linksHtml += `<div class="platform-links">
          <span style="width:100%; font-size:11px; font-weight:600; color:var(--text-label); margin-bottom:4px; display:block;">Find this role online</span>`;
        for (const [platform, url] of Object.entries(rec.platform_links)) {
          let btnClass = `btn-${platform.toLowerCase()}`;
          let pName = platform.charAt(0).toUpperCase() + platform.slice(1);
          linksHtml += `<a href="${url}" target="_blank" rel="noopener noreferrer" class="platform-btn ${btnClass}">${pName}</a>`;
        }
        linksHtml += `</div>`;
      }

      const card = document.createElement('div');
      card.className = 'job-rec-card glass-card';
      card.innerHTML = `
        <p class="job-rec-title">${escapeHtml(rec.title)}</p>
        <p class="job-rec-meta">${escapeHtml(rec.department)} &bull; ${escapeHtml(rec.location)}</p>
        <span class="job-rec-sim">
          <span class="material-symbols-outlined" style="font-size:14px">graphic_eq</span>
          NLP Similarity: ${simPct}%
        </span>
        <div class="job-rec-match-bar">
          <div class="job-rec-match-fill" style="width:${matchPct}%"></div>
        </div>
        <p class="job-rec-pct">${matchPct}% skill match</p>
        ${matchedHtml.length ? `<p class="job-skills-title">Matched Skills</p><div class="job-skills-row">${matchedHtml}</div>` : ''}
        ${missingHtml.length ? `<p class="job-skills-title" style="margin-top:8px">Skill Gap (Missing)</p><div class="job-skills-row">${missingHtml}</div>` : ''}
        ${linksHtml}
      `;
      grid.appendChild(card);
    });
  }

  /* ── Error Helper ──────────────────────────────────────────────── */
  function showError(title, message) {
    // Non-blocking inline error — avoids alert() blocking the thread
    const existing = el('inline-error');
    if (existing) existing.remove();
    const div = document.createElement('div');
    div.id        = 'inline-error';
    div.className = 'inline-error';
    div.innerHTML = `<strong>${escapeHtml(title)}:</strong> ${escapeHtml(message)}
      <button onclick="this.parentElement.remove()" class="error-close">&times;</button>`;
    el('section-resume').insertBefore(div, el('upload-zone'));
  }

  /* ── Job Directory ─────────────────────────────────────────────── */
  let allJobs = [];

  async function loadJobsDirectory() {
    try {
      const r = await fetch(`${API}/api/jobs`);
      const data = await r.json();
      if (data.success) {
        allJobs = data.jobs;
        populateJobFilters(allJobs);
        renderJobDirectory(allJobs);
      }
    } catch (e) {
      console.error('Failed to load job directory', e);
    }
  }

  function populateJobFilters(jobs) {
    const depts = [...new Set(jobs.map(j => j.department))].filter(Boolean).sort();
    const locs = [...new Set(jobs.map(j => j.location))].filter(Boolean).sort();
    const exps = [...new Set(jobs.map(j => j.experience_level))].filter(Boolean).sort();

    const fDept = el('filter-dept');
    const fLoc = el('filter-loc');
    const fExp = el('filter-exp');
    
    if(fDept) depts.forEach(d => fDept.innerHTML += `<option value="${d}">${d}</option>`);
    if(fLoc) locs.forEach(l => fLoc.innerHTML += `<option value="${l}">${l}</option>`);
    if(fExp) exps.forEach(e => fExp.innerHTML += `<option value="${e}">${e}</option>`);
  }

  function renderJobDirectory(jobsToRender) {
    const grid = el('jobs-directory-grid');
    if (!grid) return;
    grid.innerHTML = '';
    
    if (jobsToRender.length === 0) {
      grid.innerHTML = '<div style="grid-column: 1/-1; color:var(--text-muted);">No jobs found matching criteria.</div>';
      return;
    }
    
    jobsToRender.forEach(job => {
      const card = document.createElement('div');
      card.className = 'job-card glass-card';
      
      const titleEnc = encodeURIComponent(job.title || '');
      const locEnc = encodeURIComponent(job.location || '');
      const naukriTitle = (job.title || '').replace(/ /g, '-').toLowerCase();
      const naukriLoc = (job.location || '').replace(/ /g, '-').toLowerCase();
      
      let platformHtml = `<div class="platform-links">
          <span style="width:100%; font-size:11px; font-weight:600; color:var(--text-label); margin-bottom:4px; display:block;">Search Live Jobs</span>
          <a href="https://www.linkedin.com/jobs/search/?keywords=${titleEnc}%20${locEnc}" target="_blank" class="platform-btn btn-linkedin">LinkedIn</a>
          <a href="https://in.indeed.com/jobs?q=${titleEnc}&l=${locEnc}" target="_blank" class="platform-btn btn-indeed">Indeed</a>
          <a href="https://www.naukri.com/${naukriTitle}-jobs-in-${naukriLoc}" target="_blank" class="platform-btn btn-naukri">Naukri</a>
          <a href="https://wellfound.com/jobs?search=${titleEnc}" target="_blank" class="platform-btn btn-wellfound">Wellfound</a>
      `;
      if ((job.title || '').toLowerCase().includes('intern')) {
          platformHtml += `<a href="https://internshala.com/internships/${naukriTitle}-internship-in-${naukriLoc}/" target="_blank" class="platform-btn btn-internshala">Internshala</a>`;
      }
      platformHtml += `</div>`;
      
      card.innerHTML = `
        <div class="job-card-title">${escapeHtml(job.title)}</div>
        <div class="job-card-meta">${escapeHtml(job.department)} &bull; ${escapeHtml(job.location)} &bull; ${escapeHtml(job.experience_level || job.experience)}</div>
        <div class="job-card-desc">${escapeHtml(job.description).substring(0, 110)}...</div>
        ${platformHtml}
      `;
      grid.appendChild(card);
    });
  }

  function filterJobs() {
    const q = (el('job-search-input')?.value || '').toLowerCase();
    const d = el('filter-dept')?.value;
    const l = el('filter-loc')?.value;
    const e = el('filter-exp')?.value;
    
    const filtered = allJobs.filter(job => {
      const matchQ = (job.title || '').toLowerCase().includes(q) || (job.description || '').toLowerCase().includes(q);
      const matchD = d ? job.department === d : true;
      const matchL = l ? job.location === l : true;
      const matchE = e ? job.experience_level === e : true;
      return matchQ && matchD && matchL && matchE;
    });
    renderJobDirectory(filtered);
  }

  el('job-search-input')?.addEventListener('input', filterJobs);
  el('filter-dept')?.addEventListener('change', filterJobs);
  el('filter-loc')?.addEventListener('change', filterJobs);
  el('filter-exp')?.addEventListener('change', filterJobs);

  /* ── Init ──────────────────────────────────────────────────────── */
  async function init() {
    await checkHealth();
    await Promise.all([loadDashboard(), loadFeedback(), loadJobsDirectory()]);
    const currentTheme = document.documentElement.getAttribute('data-theme');
    updateChartThemes(currentTheme === 'dark');
  }

  init();

}); // end DOMContentLoaded
