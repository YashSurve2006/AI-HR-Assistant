/* ================================================================
   AI HR Assistant — script.js
   Vanilla JS • fetch() API • Centralized AI Chatbot + Resume NLP
   ================================================================ */

'use strict';

const API = '';
const MAX_MSG_LENGTH = 2000;

/* ── Helpers ─────────────────────────────────────────────────────── */
function el(id) { return document.getElementById(id); }
function show(id) { const e = el(id); if (e) e.classList.remove('hidden'); }
function hide(id) { const e = el(id); if (e) e.classList.add('hidden'); }
function escapeHtml(str) {
  return String(str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* Format markdown text inside chat bubbles */
function formatMarkdown(text) {
  if (!text) return '';
  let formatted = escapeHtml(text);

  // Bold **text**
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Italic *text*
  formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
  // Inline code `code`
  formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
  // Bullet lists
  formatted = formatted.replace(/^•\s+(.*)$/gm, '<li style="margin-left:18px;">$1</li>');
  formatted = formatted.replace(/^-\s+(.*)$/gm, '<li style="margin-left:18px;">$1</li>');
  // Line breaks
  formatted = formatted.replace(/\n\n/g, '</p><p>');
  formatted = formatted.replace(/\n/g, '<br/>');

  return `<p>${formatted}</p>`;
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
    }, { rootMargin: '-30% 0px -60% 0px' });
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
    const textColor = isDark ? '#cbd5e1' : '#64748b'; 
    const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)';
    
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

  /* ================================================================
     AI CHATBOT CONTROLLER (Flagship Feature + In-Chat Resume NLP)
     ================================================================ */
  const chatContainer     = el('chat-container');
  const chatMessages      = el('chat-messages');
  const chatEmptyState    = el('chat-empty-state');
  const quickPromptsGrid  = el('quick-prompts-grid');
  const chatInput         = el('chat-input');
  const chatSend          = el('chat-send');
  const chatFileInput     = el('chat-file-input');
  const chatAttachBtn     = el('chat-attach-btn');
  const dragOverlay       = el('chat-drag-overlay');
  const previewBar        = el('attachment-preview-bar');
  const attachedFilename  = el('attached-filename');
  const attachedFilesize  = el('attached-filesize');
  const removeAttachBtn   = el('remove-attachment-btn');
  const newChatBtn        = el('new-chat-btn');

  let sessionId           = 'sess_' + Math.random().toString(36).substring(2, 9);
  let attachedFile        = null;
  let conversationStarted = false;

  // Auto-grow textarea
  if (chatInput) {
    chatInput.addEventListener('input', function() {
      this.style.height = 'auto';
      this.style.height = (this.scrollHeight) + 'px';
      if (this.scrollHeight > 120) {
        this.style.overflowY = 'auto';
      } else {
        this.style.overflowY = 'hidden';
      }
    });
  }

  /* ── Reset / New Chat ──────────────────────────────────────────── */
  if (newChatBtn) {
    newChatBtn.addEventListener('click', () => {
      sessionId = 'sess_' + Math.random().toString(36).substring(2, 9);
      clearAttachedFile();
      chatMessages.innerHTML = '';
      if (chatEmptyState) {
        chatMessages.appendChild(chatEmptyState);
        show('chat-empty-state');
      }
      conversationStarted = false;
      if (chatInput) {
        chatInput.value = '';
        chatInput.style.height = 'auto';
        chatInput.focus();
      }
    });
  }

  /* ── Quick-Start Message Prompts ───────────────────────────────── */
  if (quickPromptsGrid) {
    quickPromptsGrid.addEventListener('click', (e) => {
      const card = e.target.closest('.quick-prompt-card');
      if (!card) return;
      const promptText = card.getAttribute('data-prompt') || '';
      
      // If user clicked 'Analyze my Resume' or 'Check ATS Score' and no file attached yet, prompt file picker
      if ((promptText.includes('Analyze my Resume') || promptText.includes('Check my ATS Score')) && !attachedFile) {
        if (chatFileInput) chatFileInput.click();
      }
      
      handleUserPrompt(promptText);
    });
  }

  // Policy Chips in empty state
  document.querySelectorAll('.policy-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const promptText = chip.getAttribute('data-prompt') || chip.textContent.replace(/"/g, '');
      handleUserPrompt(promptText);
    });
  });

  function handleUserPrompt(promptText) {
    if (!promptText) return;
    if (chatInput) chatInput.value = promptText;
    sendChatMessage();
  }

  /* ── Attachment Handling ───────────────────────────────────────── */
  if (chatAttachBtn && chatFileInput) {
    chatAttachBtn.addEventListener('click', () => chatFileInput.click());
    
    chatFileInput.addEventListener('change', () => {
      if (chatFileInput.files && chatFileInput.files[0]) {
        handleFileSelection(chatFileInput.files[0]);
      }
    });
  }

  if (removeAttachBtn) {
    removeAttachBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      clearAttachedFile();
    });
  }

  function handleFileSelection(file) {
    if (!file) return;

    // Validate Extension (.pdf, .docx, .doc)
    const name = file.name.toLowerCase();
    const isPdf = name.endsWith('.pdf');
    const isDoc = name.endsWith('.docx') || name.endsWith('.doc');

    if (!isPdf && !isDoc) {
      showChatNotification('Invalid File Type', 'Please upload a PDF or Word document (.docx, .doc).', 'error');
      clearAttachedFile();
      return;
    }

    // Validate Size (10 MB max)
    if (file.size > 10 * 1024 * 1024) {
      showChatNotification('File Too Large', 'Maximum file size is 10 MB.', 'error');
      clearAttachedFile();
      return;
    }

    attachedFile = file;
    if (attachedFilename) attachedFilename.textContent = file.name;
    if (attachedFilesize) attachedFilesize.textContent = (file.size / 1024).toFixed(1) + ' KB';
    show('attachment-preview-bar');
    if (chatInput) chatInput.focus();
  }

  function clearAttachedFile() {
    attachedFile = null;
    if (chatFileInput) chatFileInput.value = '';
    hide('attachment-preview-bar');
  }

  /* ── Drag & Drop on Chat Container ─────────────────────────────── */
  if (chatContainer && dragOverlay) {
    let dragCounter = 0;

    chatContainer.addEventListener('dragenter', (e) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounter++;
      show('chat-drag-overlay');
    });

    chatContainer.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.stopPropagation();
    });

    chatContainer.addEventListener('dragleave', (e) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounter--;
      if (dragCounter <= 0) {
        dragCounter = 0;
        hide('chat-drag-overlay');
      }
    });

    chatContainer.addEventListener('drop', (e) => {
      e.preventDefault();
      e.stopPropagation();
      dragCounter = 0;
      hide('chat-drag-overlay');

      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        handleFileSelection(files[0]);
      }
    });
  }

  /* ── Chat Messages Stream Rendering ────────────────────────────── */
  function appendChatMsg(role, text, meta, fileAttachment) {
    // Hide empty state on first message
    if (!conversationStarted) {
      conversationStarted = true;
      hide('chat-empty-state');
    }

    const div = document.createElement('div');
    div.className = `chat-msg chat-msg--${role}`;

    let attachmentHtml = '';
    if (fileAttachment && role === 'user') {
      attachmentHtml = `
        <div class="user-msg-attachment">
          <span class="material-symbols-outlined">description</span>
          <span>${escapeHtml(fileAttachment.name)} (${(fileAttachment.size / 1024).toFixed(1)} KB)</span>
        </div>`;
    }

    let metaHtml = '';
    if (meta && role === 'ai') {
      const confText = meta.confidence !== undefined ? `${(meta.confidence * 100).toFixed(0)}%` : '';
      const level = meta.confidence_level || 'low';
      let colorClass = level === 'high' ? 'chat-conf high' : (level === 'medium' ? 'chat-conf medium' : 'chat-conf low');

      metaHtml = `<div class="chat-meta" style="margin-top:10px; display:flex; gap:8px; align-items:center; font-size:12px;">`;
      if (confText) {
        metaHtml += `<span class="${colorClass}" style="padding:2px 8px; border-radius:4px; font-weight:600; font-size:11px;">Confidence: ${confText} (${level})</span>`;
      }
      if (meta.source) {
        metaHtml += `<span class="chat-source" style="color:var(--text-label); font-size:11px;">Source: ${escapeHtml(meta.source)}</span>`;
      }
      metaHtml += `</div>`;
    }

    let resumeCardHtml = '';
    if (meta && meta.resume_analysis) {
      resumeCardHtml = renderResumeCardHtml(meta.resume_analysis);
    }

    div.innerHTML = `
      <div class="chat-bubble">
        ${attachmentHtml}
        ${text ? formatMarkdown(text) : ''}
        ${resumeCardHtml}
        ${metaHtml}
      </div>`;

    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Animate SVG score rings if present in the message
    const ringFill = div.querySelector('.rc-score-ring-fill');
    if (ringFill) {
      const targetOffset = ringFill.getAttribute('data-target-offset');
      if (targetOffset) {
        requestAnimationFrame(() => {
          setTimeout(() => {
            ringFill.style.strokeDashoffset = targetOffset;
          }, 50);
        });
      }
    }

    // Attach click listeners to in-chat follow-up buttons
    div.querySelectorAll('.followup-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const query = btn.getAttribute('data-query');
        if (query) {
          if (chatInput) chatInput.value = query;
          sendChatMessage();
        }
      });
    });
  }

  function renderResumeCardHtml(res) {
    const score = Math.max(0, Math.min(100, res.score || 0));
    const circumference = 2 * Math.PI * 26; // r=26 -> 163.36
    const offset = circumference * (1 - score / 100);

    let scoreBadge = 'High Match';
    let badgeClass = 'high';
    if (score < 50) {
      scoreBadge = 'Needs Optimization';
      badgeClass = 'low';
    } else if (score < 75) {
      scoreBadge = 'Good Profile';
      badgeClass = 'medium';
    }

    // Breakdown bars
    const bd = res.score_breakdown || {};
    const maxMap = { skills: 25, experience: 25, education: 20, projects: 15, content_quality: 15 };
    const lblMap = { skills: 'Technical Skills', experience: 'Work Experience', education: 'Academic Credentials', projects: 'Projects & Impact', content_quality: 'Format & Detail' };

    let breakdownHtml = '';
    Object.entries(bd).forEach(([k, v]) => {
      const max = maxMap[k] || 25;
      const pct = Math.min(100, Math.round((v / max) * 100));
      breakdownHtml += `
        <div class="rc-bar-item">
          <div class="rc-bar-label">
            <span>${lblMap[k] || k}</span>
            <span>${v}/${max}</span>
          </div>
          <div class="rc-bar-track">
            <div class="rc-bar-fill" style="width:${pct}%"></div>
          </div>
        </div>`;
    });

    // Skills cloud
    const skills = Array.isArray(res.skills) ? res.skills : [];
    let skillsHtml = skills.map(s => `<span class="rc-skill-tag">${escapeHtml(s)}</span>`).join('');
    if (!skillsHtml) skillsHtml = '<span style="font-size:12px; color:var(--text-muted);">No common technical skills detected.</span>';

    // Strengths & Weaknesses
    const strengths = res.strengths || [];
    const weaknesses = res.weaknesses || [];
    const suggestions = res.suggestions || [];

    let strengthsLi = strengths.map(s => `<li>${escapeHtml(s)}</li>`).join('');
    let weaknessesLi = weaknesses.map(w => `<li>${escapeHtml(w)}</li>`).join('');
    let suggestionsLi = suggestions.map(s => `<li>${escapeHtml(s)}</li>`).join('');

    // Matching Jobs Preview
    const recs = res.recommendations || [];
    let jobsHtml = '';
    if (recs.length > 0) {
      jobsHtml = `<div class="rc-jobs-preview"><div class="rc-section-title">Top Matching Roles (${recs.length})</div>`;
      recs.slice(0, 3).forEach(j => {
        const matchP = j.match_percentage || Math.round((j.similarity || 0.5) * 100);
        
        let platformLinks = '';
        if (j.platform_links) {
          platformLinks = `<div style="display:flex; gap:6px; margin-top:6px;">`;
          for (const [p, url] of Object.entries(j.platform_links)) {
            platformLinks += `<a href="${url}" target="_blank" rel="noopener noreferrer" class="platform-btn btn-${p.toLowerCase()}" style="font-size:10px; padding:3px 8px;">${p}</a>`;
          }
          platformLinks += `</div>`;
        }

        jobsHtml += `
          <div class="rc-job-item">
            <div>
              <div class="rc-job-title">${escapeHtml(j.title)}</div>
              <div class="rc-job-meta">${escapeHtml(j.department)} &bull; ${escapeHtml(j.location)}</div>
              ${platformLinks}
            </div>
            <span class="rc-job-match">${matchP}% Match</span>
          </div>`;
      });
      jobsHtml += `</div>`;
    }

    return `
      <div class="chat-resume-card">
        <div class="rc-header">
          <div class="rc-file-meta">
            <div class="rc-file-icon"><span class="material-symbols-outlined">task</span></div>
            <div>
              <div class="rc-filename">${escapeHtml(res.filename || 'Resume Analysis')}</div>
              <div class="rc-filesize">${res.text_length || 0} characters extracted &bull; ${res.skill_count || 0} skills detected</div>
            </div>
          </div>
          
          <div class="rc-score-gauge">
            <div class="rc-score-ring-wrap">
              <svg class="rc-score-ring" viewBox="0 0 60 60">
                <circle class="rc-score-ring-bg" cx="30" cy="30" r="26"></circle>
                <circle class="rc-score-ring-fill" cx="30" cy="30" r="26" 
                  stroke-dasharray="${circumference.toFixed(2)}" 
                  stroke-dashoffset="${circumference.toFixed(2)}"
                  data-target-offset="${offset.toFixed(2)}">
                </circle>
              </svg>
              <div class="rc-score-center">${score}</div>
            </div>
            <span class="rc-score-badge ${badgeClass}">${scoreBadge}</span>
          </div>
        </div>

        <div class="rc-section-title">ATS Evaluation Breakdown</div>
        <div class="rc-breakdown-grid">${breakdownHtml}</div>

        <div class="rc-section-title">Detected Technical Skills (${skills.length})</div>
        <div class="rc-skills-wrap">${skillsHtml}</div>

        <div class="rc-insights-grid">
          <div class="rc-insight-box strengths">
            <div class="rc-insight-title"><span class="material-symbols-outlined" style="font-size:16px; color:var(--success);">check_circle</span> Key Strengths</div>
            <ul class="rc-insight-list">${strengthsLi}</ul>
          </div>
          <div class="rc-insight-box weaknesses">
            <div class="rc-insight-title"><span class="material-symbols-outlined" style="font-size:16px; color:var(--warning);">warning</span> Growth Areas</div>
            <ul class="rc-insight-list">${weaknessesLi}</ul>
          </div>
        </div>

        ${suggestionsLi ? `
        <div class="rc-suggestions-box">
          <div class="rc-insight-title"><span class="material-symbols-outlined" style="font-size:16px;">lightbulb</span> ATS Score Optimization Suggestions</div>
          <ul>${suggestionsLi}</ul>
        </div>` : ''}

        ${jobsHtml}

        <!-- Interactive Follow-up Chips -->
        <div class="chat-followup-actions">
          <button class="followup-btn" data-query="💼 Find more suitable jobs based on my resume">
            <span class="material-symbols-outlined" style="font-size:14px;">work</span> Matching Jobs
          </button>
          <button class="followup-btn" data-query="🎤 Prepare for an Interview for my skills">
            <span class="material-symbols-outlined" style="font-size:14px;">record_voice_over</span> Interview Questions
          </button>
          <button class="followup-btn" data-query="🚀 How can I improve my ATS score to 90+?">
            <span class="material-symbols-outlined" style="font-size:14px;">trending_up</span> Score Improvement Tips
          </button>
          <button class="followup-btn" data-query="What is the work from home policy?">
            <span class="material-symbols-outlined" style="font-size:14px;">home_work</span> WFH Policy
          </button>
        </div>
      </div>
    `;
  }

  function showTyping() {
    const existing = el('typing-indicator');
    if (existing) existing.remove();

    const div = document.createElement('div');
    div.className = 'chat-msg chat-msg--ai';
    div.id = 'typing-indicator';
    div.innerHTML = `
      <div class="typing-bubble">
        <span style="font-size:13px; font-weight:600; color:var(--text-muted);">AI is processing</span>
        <div class="typing-dots">
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
          <div class="typing-dot"></div>
        </div>
      </div>`;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function hideTyping() {
    const t = el('typing-indicator');
    if (t) t.remove();
  }

  function showChatNotification(title, msg, type = 'info') {
    appendChatMsg('ai', `⚠️ **${title}**: ${msg}`, { source: 'system' });
  }

  /* ── Send Chat Message (Text + Optional File) ──────────────────── */
  async function sendChatMessage() {
    const rawMsg = (chatInput ? chatInput.value.trim() : '');
    const fileToSend = attachedFile;

    if (!rawMsg && !fileToSend) return;

    const msg = rawMsg.slice(0, MAX_MSG_LENGTH);

    // Reset input state
    if (chatInput) {
      chatInput.value = '';
      chatInput.style.height = 'auto';
    }
    if (chatSend) chatSend.disabled = true;

    // Display user message in chat
    appendChatMsg('user', msg, null, fileToSend);
    clearAttachedFile();
    showTyping();

    try {
      let r, data;

      if (fileToSend) {
        // Send multipart form-data with attached file
        const fd = new FormData();
        fd.append('file', fileToSend);
        fd.append('message', msg);
        fd.append('session_id', sessionId);

        r = await fetch(`${API}/api/chat`, {
          method: 'POST',
          body: fd
        });
      } else {
        // Send standard JSON query
        r = await fetch(`${API}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: msg, session_id: sessionId })
        });
      }

      data = await r.json();
      hideTyping();

      if (data.success) {
        appendChatMsg('ai', data.answer, data);
      } else {
        appendChatMsg('ai', data.error || 'I encountered an issue processing your request. Please try again.', data);
      }
    } catch (e) {
      hideTyping();
      appendChatMsg('ai', 'Could not connect to the backend server. Please verify the Flask service is running on port 5000.');
    } finally {
      if (chatSend) chatSend.disabled = false;
      if (chatInput) chatInput.focus();
    }
  }

  if (chatSend) chatSend.addEventListener('click', sendChatMessage);

  if (chatInput) {
    chatInput.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
      }
    });
  }

  /* ================================================================
     DASHBOARD & EMPLOYEE INSIGHTS
     ================================================================ */
  async function loadDashboard() {
    try {
      const r    = await fetch(`${API}/api/dashboard`);
      const data = await r.json();
      if (!data.success) return;

      const s = data.summary;
      const setEl = (id, val) => { const e = el(id); if (e) e.textContent = val; };
      
      setEl('stat-total-jobs', s.total_jobs);
      setEl('ins-positive', s.positive);
      setEl('ins-negative', s.negative);
      setEl('ins-neutral', s.neutral);
      setEl('ins-positive-pct', s.positive_percentage + '% of total');
      setEl('ins-negative-pct', s.negative_percentage + '% of total');
      setEl('ins-neutral-pct', s.neutral_percentage + '% of total');

      renderSentimentChart(data.sentiment);
      renderRatingChart(data.rating_distribution);
      renderJobDeptChart('jobDeptChartJobs', data.job_distribution);
      renderJobLocChart(data.location_distribution);
      renderDeptSentimentChart(data.department_sentiment);
    } catch (e) {
      console.error('Dashboard load error:', e);
    }
  }

  function renderSentimentChart(sentiment) {
    destroyChart('sentimentChart');
    const cvs = el('sentimentChart');
    if (!cvs) return;
    const ctx = cvs.getContext('2d');
    chartInstances['sentimentChart'] = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: sentiment.labels,
        datasets: [{
          data: sentiment.values,
          backgroundColor: ['rgba(16, 185, 129, 0.75)', 'rgba(239, 68, 68, 0.75)', 'rgba(99, 102, 241, 0.75)'],
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
    const cvs = el('ratingChart');
    if (!cvs) return;
    const ctx = cvs.getContext('2d');
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
          backgroundColor: dist.map((_, i) => colors[i % colors.length] + 'cc'),
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
    const cvs = el('jobLocChart');
    if (!cvs) return;
    const ctx = cvs.getContext('2d');
    chartInstances['jobLocChart'] = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: dist.map(d => d.location),
        datasets: [{
          data: dist.map(d => d.count),
          backgroundColor: ['#6366f1cc','#14b8a6cc','#f59e0bcc','#ef4444cc','#10b981cc'],
          borderWidth: 2,
          borderColor: 'transparent',
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
    const cvs = el('deptSentimentChart');
    if (!cvs) return;
    const ctx = cvs.getContext('2d');
    chartInstances['deptSentimentChart'] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: deptData.map(d => d.department),
        datasets: [
          { label: 'Positive', data: deptData.map(d => d.positive), backgroundColor: 'rgba(16, 185, 129, 0.75)', borderColor: '#10b981', borderWidth: 1.5, borderRadius: 4 },
          { label: 'Negative', data: deptData.map(d => d.negative), backgroundColor: 'rgba(239, 68, 68, 0.75)', borderColor: '#ef4444', borderWidth: 1.5, borderRadius: 4 },
          { label: 'Neutral',  data: deptData.map(d => d.neutral),  backgroundColor: 'rgba(99, 102, 241, 0.75)', borderColor: '#6366f1', borderWidth: 1.5, borderRadius: 4 }
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
    if (!list) return;
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
        item.innerHTML = `
          <p class="feedback-name">${escapeHtml(fb.employee_name)}</p>
          <p class="feedback-dept">${escapeHtml(fb.department)} &bull; Rating: ${fb.rating}/5</p>
          <p class="feedback-text">${escapeHtml(fb.feedback)}</p>
          <span class="feedback-sentiment ${sntClass}">${fb.sentiment} (${fb.polarity})</span>
        `;
        list.appendChild(item);
      });
    } catch (e) {
      list.innerHTML = '<p class="loading-placeholder">Could not load feedback stream.</p>';
    }
  }

  /* ================================================================
     JOB DIRECTORY & FILTERING
     ================================================================ */
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
    
    if (fDept) {
      fDept.innerHTML = '<option value="">All Departments</option>';
      depts.forEach(d => fDept.innerHTML += `<option value="${d}">${d}</option>`);
    }
    if (fLoc) {
      fLoc.innerHTML = '<option value="">All Locations</option>';
      locs.forEach(l => fLoc.innerHTML += `<option value="${l}">${l}</option>`);
    }
    if (fExp) {
      fExp.innerHTML = '<option value="">All Experience Levels</option>';
      exps.forEach(e => fExp.innerHTML += `<option value="${e}">${e}</option>`);
    }
  }

  function renderJobDirectory(jobsToRender) {
    const grid = el('jobs-directory-grid');
    if (!grid) return;
    grid.innerHTML = '';
    
    if (jobsToRender.length === 0) {
      grid.innerHTML = '<div style="grid-column: 1/-1; color:var(--text-muted); text-align:center; padding:32px;">No active openings match the selected filters.</div>';
      return;
    }
    
    jobsToRender.forEach(job => {
      const card = document.createElement('div');
      card.className = 'job-card glass-card';
      
      const titleEnc = encodeURIComponent(job.title || '');
      const locEnc = encodeURIComponent(job.location || '');
      const naukriTitle = (job.title || '').replace(/ /g, '-').toLowerCase();
      const naukriLoc = (job.location || '').replace(/ /g, '-').toLowerCase();
      
      const svgs = {
        linkedin: `<svg viewBox="0 0 24 24"><path fill="currentColor" d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>`,
        indeed: `<svg viewBox="0 0 24 24"><path fill="currentColor" d="M6.3 19.3h4.9v-9.3H6.3v9.3zM8.8 4.7c-1.6 0-2.8 1.3-2.8 2.8 0 1.6 1.3 2.8 2.8 2.8s2.8-1.3 2.8-2.8c0-1.6-1.3-2.8-2.8-2.8zm11 5.4c-2 0-3.6.7-4.5 2.1V10h-4.8v9.3h4.9v-5.2c0-1.5.8-2.2 1.9-2.2 1.2 0 1.7.8 1.7 2v5.3h4.8v-5.7c0-2.1-1.3-3.4-4-3.4z"/></svg>`,
        naukri: `<svg viewBox="0 0 24 24"><path fill="currentColor" d="M16.9 14.2c-1-1.2-1.9-2.3-2.8-3.4-.2-.3-.5-.4-.8-.4-.3 0-.6.1-.8.4l-2.6 3.1-1.4-1.6c-.2-.2-.4-.3-.7-.3-.3 0-.5.1-.7.3l-1.9 2.2c-.3.4-.3 1 0 1.4.3.4 1 .4 1.4 0l1.2-1.4 1.4 1.6c.2.2.4.3.7.3.3 0 .5-.1.7-.3l2.6-3.1 2.3 2.8c.2.2.4.3.7.3.5 0 1-.4 1-1 0-.3-.1-.6-.3-.8zM12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm0 18c-4.4 0-8-3.6-8-8s3.6-8 8-8 8 3.6 8 8-3.6 8-8 8z"/></svg>`,
        wellfound: `<svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10zm-3-11v4h2v-4H9zm4 0v4h2v-4h-2zm4 0h-2v4h2v-4z"/></svg>`,
        internshala: `<svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 0L1 6l11 6 11-6L12 0zm0 13.5L2.8 8.5v5L12 18.5 21.2 13.5v-5L12 13.5z"/></svg>`
      };
      
      let platformHtml = `<div class="platform-links">
          <span>Apply on Portals</span>
          <a href="https://www.linkedin.com/jobs/search/?keywords=${titleEnc}%20${locEnc}" target="_blank" class="platform-btn btn-linkedin" title="LinkedIn">${svgs.linkedin}</a>
          <a href="https://in.indeed.com/jobs?q=${titleEnc}&l=${locEnc}" target="_blank" class="platform-btn btn-indeed" title="Indeed">${svgs.indeed}</a>
          <a href="https://www.naukri.com/${naukriTitle}-jobs-in-${naukriLoc}" target="_blank" class="platform-btn btn-naukri" title="Naukri">${svgs.naukri}</a>
          <a href="https://wellfound.com/jobs?search=${titleEnc}" target="_blank" class="platform-btn btn-wellfound" title="Wellfound">${svgs.wellfound}</a>
      `;
      if ((job.title || '').toLowerCase().includes('intern')) {
          platformHtml += `<a href="https://internshala.com/internships/${naukriTitle}-internship-in-${naukriLoc}/" target="_blank" class="platform-btn btn-internshala" title="Internshala">${svgs.internshala}</a>`;
      }
      platformHtml += `</div>`;
      
      card.innerHTML = `
        <div class="job-card-title">${escapeHtml(job.title)}</div>
        <div class="job-card-meta">${escapeHtml(job.department)} &bull; ${escapeHtml(job.location)} &bull; ${escapeHtml(job.experience_level || job.experience || 'Entry')}</div>
        <div class="job-card-desc">${escapeHtml(job.description).substring(0, 120)}...</div>
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
      const matchQ = (job.title || '').toLowerCase().includes(q) || (job.description || '').toLowerCase().includes(q) || (job.required_skills || '').toLowerCase().includes(q);
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

