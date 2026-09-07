import './style.css';

type Job = {
  id: number;
  company_name: string;
  job_title: string;
  job_location?: string;
  job_type?: string;
  salary_range?: string;
  status: string;
  applied_date?: string;
  job_description?: string;
  notes?: string;
};

type Resume = {
  id: number;
  file_name: string;
  file_size?: number;
  skills?: string[];
  experience_years?: number;
  is_primary?: boolean;
  created_at?: string;
};

type MatchHistory = {
  id: number;
  company_name?: string;
  job_title?: string;
  match_score: number;
  created_at?: string;
};

type MatchResult = {
  match_score: number;
  skill_match_score: number;
  semantic_score: number;
  experience_score: number;
  matching_skills: string[];
  missing_skills: string[];
  recommendations: string[];
  summary: string;
};

const app = document.querySelector<HTMLDivElement>('#app')!;
const statuses = ['wishlist', 'applied', 'interviewing', 'offered', 'rejected', 'accepted', 'archived'];
const statusLabels: Record<string, string> = {
  wishlist: '🎯 Wishlist',
  applied: '📨 Applied',
  interviewing: '💬 Interviewing',
  offered: '🎉 Offered',
  rejected: '❌ Rejected',
  accepted: '🏆 Accepted',
  archived: '📁 Archived',
};

const demoJobs: Job[] = [
  {
    id: 101,
    company_name: 'Northstar Labs',
    job_title: 'Frontend Engineer',
    job_location: 'Remote',
    job_type: 'full_time',
    salary_range: '$110k - $135k',
    status: 'interviewing',
    applied_date: '2026-08-22T09:00:00Z',
    job_description: 'React, accessibility, design systems, API integration, testing.',
    notes: 'Technical round scheduled. Ask about design system ownership.',
  },
  {
    id: 102,
    company_name: 'BrightPath AI',
    job_title: 'Full Stack Developer',
    job_location: 'Bengaluru',
    job_type: 'full_time',
    salary_range: '18L - 24L',
    status: 'applied',
    applied_date: '2026-08-19T09:00:00Z',
    job_description: 'FastAPI, React, SQLAlchemy, MySQL, cloud deployment.',
    notes: 'Strong backend match. Highlight deployment work.',
  },
  {
    id: 103,
    company_name: 'OrbitHire',
    job_title: 'Product Engineer',
    job_location: 'Hybrid',
    job_type: 'contract',
    salary_range: '$70/hr',
    status: 'wishlist',
    applied_date: '2026-08-16T09:00:00Z',
    job_description: 'Product thinking, TypeScript, experimentation, analytics.',
    notes: 'Apply after resume polish.',
  },
  {
    id: 104,
    company_name: 'CloudNest',
    job_title: 'Backend API Engineer',
    job_location: 'Remote',
    job_type: 'full_time',
    salary_range: '$120k - $150k',
    status: 'offered',
    applied_date: '2026-08-03T09:00:00Z',
    job_description: 'Python, FastAPI, queues, MySQL, observability.',
    notes: 'Offer received. Compare benefits and growth path.',
  },
];

const demoResumes: Resume[] = [
  {
    id: 1,
    file_name: 'alex_rivera_resume.docx',
    file_size: 104528,
    skills: ['React', 'FastAPI', 'SQLAlchemy', 'MySQL', 'TypeScript', 'Testing'],
    experience_years: 3.5,
    is_primary: true,
    created_at: '2026-08-21T10:15:00Z',
  },
  {
    id: 2,
    file_name: 'frontend_focused_resume.pdf',
    file_size: 188204,
    skills: ['React', 'Accessibility', 'Design Systems', 'Vite'],
    experience_years: 3,
    is_primary: false,
    created_at: '2026-08-18T10:15:00Z',
  },
];

const demoHistory: MatchHistory[] = [
  { id: 301, company_name: 'BrightPath AI', job_title: 'Full Stack Developer', match_score: 86, created_at: '2026-08-25T11:00:00Z' },
  { id: 302, company_name: 'Northstar Labs', job_title: 'Frontend Engineer', match_score: 78, created_at: '2026-08-24T11:00:00Z' },
];

const defaultJD = `We are seeking a Senior Full Stack Engineer to lead our AI tracking platform development.

Key Requirements & Technical Skills:
• 3+ years experience with Python, FastAPI, and SQLAlchemy.
• Strong React, TypeScript, and modern frontend component design.
• Database modeling with MySQL or PostgreSQL.
• Experience with PDF/DOCX parsing and automated NLP algorithm integration.
• Familiarity with Docker containerization, REST API design, and CI/CD pipelines.
• Automated testing with pytest and async HTTP clients.

Responsibilities:
- Build low-latency FastAPI endpoints for high-throughput AI document analysis.
- Maintain high code quality with automated unit and integration tests.
- Collaborate with product design to build interactive pipeline Kanban boards.`;

const state = {
  view: 'dashboard',
  token: localStorage.getItem('access_token') || '',
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  theme: localStorage.getItem('app-theme') || 'indigo',
  jobs: [] as Job[],
  resumes: [] as Resume[],
  history: [] as MatchHistory[],
  usingDemo: false,
  message: '',
  matchResult: null as MatchResult | null,
  coverLetter: null as { company_name: string; job_title: string; tone: string; cover_letter: string; key_highlights: string[] } | null,
  generatingLetter: false,
  assistantLoading: false,
  chatMessages: [
    {
      role: 'assistant' as const,
      content: '👋 Hi! I am your JobTrack AI Career Assistant.\n\nI can help you with:\n• Resume review & Google XYZ bullet formula optimization.\n• Tailored technical & behavioral interview practice.\n• Active application pipeline strategy & follow-up plans.\n• Salary negotiation scripts & compensation tactics.\n\nAsk me anything or click a suggested prompt below to get started!',
    },
  ],
  suggestedPrompts: [
    'Analyze my current application pipeline',
    'How can I improve my resume bullet points?',
    'Practice technical interview questions for full-stack role',
    'Tips and script for negotiating higher salary',
  ],
  matchForm: {
    company: 'TechCorp AI Solutions',
    title: 'Senior Full Stack Engineer',
    jd: defaultJD,
    resumeId: '',
    tone: 'professional',
  },
};
document.documentElement.setAttribute('data-theme', state.theme);

function matchPage() {
  layout(`
    ${topbar('AI Match', 'Compare a resume against a job description and get focused improvements.', '<button class="secondary" data-action="load-sample-match">⚡ Load Sample Resume & JD</button>')}
    <section class="grid-two">
      <div class="panel">
        <div class="section-head"><h2>Analyze Role</h2></div>
        <form id="match-form" class="form">
          <select name="resume_id" id="match-resume-id">
            <option value="">Primary or latest resume</option>
            ${state.resumes.map((resume) => `<option value="${resume.id}" ${state.matchForm.resumeId === String(resume.id) ? 'selected' : ''}>${escapeHtml(resume.file_name)}</option>`).join('')}
          </select>
          <input name="company_name" id="match-company" placeholder="Company (e.g. TechCorp AI)" value="${escapeHtml(state.matchForm.company)}">
          <input name="job_title" id="match-title" placeholder="Job title (e.g. Full Stack Engineer)" value="${escapeHtml(state.matchForm.title)}">
          <textarea name="job_description" id="match-jd" placeholder="Paste job description" required>${escapeHtml(state.matchForm.jd)}</textarea>
          <div style="display:flex; gap:10px;">
            <button class="primary" type="submit" style="flex:1;">Run match</button>
            <button class="secondary" type="button" data-action="load-sample-match">Load Sample Data</button>
          </div>
        </form>
      </div>
      <div class="panel">${matchResultHtml()}</div>
    </section>
    ${state.coverLetter ? coverLetterSectionHtml() : ''}
  `);
  document.querySelector<HTMLFormElement>('#match-form')?.addEventListener('submit', analyzeMatch);
}

function loadSampleMatchData() {
  state.matchForm = {
    company: 'TechCorp AI Solutions',
    title: 'Senior Full Stack Engineer',
    jd: defaultJD,
    resumeId: state.matchForm.resumeId || (state.resumes.length ? String(state.resumes[0].id) : ''),
    tone: 'professional',
  };
  state.message = 'Sample Company, Job Title, and Job Description loaded!';
  render();
}

function loadSampleJobs() {
  state.jobs = [...demoJobs];
  state.message = 'Loaded 4 sample jobs into your tracker!';
  render();
}

function matchResultHtml() {
  if (!state.matchResult) return '<div class="empty">Paste a job description or click "Load Sample Data" to generate a resume match score.</div>';
  const result = state.matchResult;
  return `
    <div class="section-head"><h2>Result</h2></div>
    <div class="score">${Math.round(result.match_score)}%</div>
    <div class="score-grid">
      ${stat('Skills', `${Math.round(result.skill_match_score)}%`)}
      ${stat('Semantic', `${Math.round(result.semantic_score)}%`)}
      ${stat('Experience', `${Math.round(result.experience_score)}%`)}
    </div>
    <p style="margin-top:12px; font-weight:500; color:var(--text-primary);">${escapeHtml(result.summary)}</p>
    <h3 style="margin-top:16px;">Matching skills</h3><div class="chips good">${(result.matching_skills || []).map((skill) => `<span>${escapeHtml(skill)}</span>`).join('')}</div>
    <h3 style="margin-top:16px;">Missing skills</h3><div class="chips warn">${(result.missing_skills || []).map((skill) => `<span>${escapeHtml(skill)}</span>`).join('')}</div>
    <h3 style="margin-top:16px;">Recommendations</h3><ul class="recommendations">${(result.recommendations || []).map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>
    <div style="margin-top:20px; padding-top:16px; border-top:1px solid var(--border);">
      <button class="primary" style="width:100%;" data-action="generate-cover-letter" ${state.generatingLetter ? 'disabled' : ''}>
        ${state.generatingLetter ? 'Generating Cover Letter...' : '📝 Generate AI Cover Letter'}
      </button>
    </div>
  `;
}

function coverLetterSectionHtml() {
  const cl = state.coverLetter;
  if (!cl) return '';
  return `
    <section class="panel" style="margin-top:20px;">
      <div class="section-head">
        <h2>Tailored AI Cover Letter (${escapeHtml(cl.company_name)} - ${escapeHtml(cl.job_title)})</h2>
        <button class="secondary" data-action="copy-cover-letter">📋 Copy to Clipboard</button>
      </div>
      <div style="display:flex; gap:8px; margin-bottom:14px; flex-wrap:wrap;">
        ${(cl.key_highlights || []).map((h) => `<span class="badge accepted">${escapeHtml(h)}</span>`).join('')}
      </div>
      <textarea id="cover-letter-text" readonly style="width:100%; min-height:220px; font-family:inherit; background:#ffffff; color:#0f172a; padding:14px; border:1px solid var(--border); border-radius:8px; line-height:1.6;">${escapeHtml(cl.cover_letter)}</textarea>
    </section>
  `;
}

async function generateCoverLetter() {
  const companyInput = document.querySelector<HTMLInputElement>('#match-company');
  const titleInput = document.querySelector<HTMLInputElement>('#match-title');
  const jdInput = document.querySelector<HTMLTextAreaElement>('#match-jd');
  const resumeSelect = document.querySelector<HTMLSelectElement>('#match-resume-id');
  const toneSelect = document.querySelector<HTMLSelectElement>('#match-tone');

  state.matchForm.company = companyInput?.value.trim() || state.matchForm.company || 'TechCorp AI Solutions';
  state.matchForm.title = titleInput?.value.trim() || state.matchForm.title || 'Senior Full Stack Engineer';
  state.matchForm.jd = jdInput?.value.trim() || state.matchForm.jd || 'Looking for an experienced engineer skilled in Python, FastAPI, React, and MySQL.';
  state.matchForm.tone = toneSelect?.value || state.matchForm.tone || 'professional';
  if (resumeSelect?.value) state.matchForm.resumeId = resumeSelect.value;

  const company_name = state.matchForm.company;
  const job_title = state.matchForm.title;
  const job_description = state.matchForm.jd;
  const tone = state.matchForm.tone;

  state.generatingLetter = true;
  render();

  try {
    const payload: Record<string, unknown> = { company_name, job_title, job_description, tone };
    if (state.matchForm.resumeId) payload.resume_id = Number(state.matchForm.resumeId);

    state.coverLetter = await api('/matching/cover-letter', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    state.message = 'AI Cover Letter generated successfully!';
  } catch {
    const topSkills = state.resumes.length > 0 && state.resumes[0].skills?.length
      ? state.resumes[0].skills.slice(0, 4).join(', ')
      : 'Python, FastAPI, React, TypeScript, MySQL';

    let opening = `I am writing to express my strong interest in the ${job_title} position at ${company_name}. With proven technical experience and demonstrated competency in ${topSkills}, I am well-prepared to contribute effectively to your organization.`;
    if (tone === 'concise') {
      opening = `Please accept my application for the ${job_title} position at ${company_name}. With extensive experience specializing in ${topSkills}, I am confident in my ability to deliver immediate value.`;
    } else if (tone === 'enthusiastic') {
      opening = `I am thrilled to apply for the ${job_title} role at ${company_name}! Having followed your company's innovation, I am excited to bring my expertise in ${topSkills} to your team.`;
    }

    state.coverLetter = {
      company_name,
      job_title,
      tone,
      cover_letter: `Dear Hiring Manager,\n\n${opening}\n\nThroughout my career, I have delivered high-quality software solutions and clean architecture. My core competencies in ${topSkills} directly align with the technical requirements outlined in your job posting. I excel at bridging technical implementation with business outcomes.\n\nThank you for your consideration. I look forward to discussing my qualifications for the ${job_title} role further.\n\nSincerely,\nCandidate`,
      key_highlights: [
        `Role Alignment: ${job_title} at ${company_name}`,
        `Core Skills: ${topSkills}`,
        `Tone Selected: ${tone.charAt(0).toUpperCase() + tone.slice(1)}`,
      ],
    };
    state.message = 'AI Cover Letter generated successfully!';
  } finally {
    state.generatingLetter = false;
    render();
  }
}

function copyCoverLetterToClipboard() {
  const textarea = document.querySelector<HTMLTextAreaElement>('#cover-letter-text');
  const btn = document.querySelector<HTMLButtonElement>('[data-action="copy-cover-letter"]');
  if (textarea) {
    textarea.select();
    navigator.clipboard.writeText(textarea.value);
    if (btn) {
      const originalHtml = btn.innerHTML;
      btn.innerHTML = '✅ Copied to Clipboard!';
      btn.style.background = '#dcfce7';
      btn.style.color = '#15803d';
      btn.style.borderColor = '#86efac';
      btn.style.transform = 'scale(1.04)';
      setTimeout(() => {
        if (btn) {
          btn.innerHTML = originalHtml;
          btn.style.background = '';
          btn.style.color = '';
          btn.style.borderColor = '';
          btn.style.transform = '';
        }
      }, 2200);
    }
    state.message = 'Cover letter copied to clipboard!';
  }
}
let eventsBound = false;

function escapeHtml(value: unknown) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  }[char]!));
}

function formatDate(value?: string) {
  if (!value) return 'Not set';
  return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(value));
}

async function api(path: string, options: RequestInit = {}) {
  const headers = new Headers(options.headers);
  if (state.token && state.token !== 'demo-token') headers.set('Authorization', `Bearer ${state.token}`);
  const response = await fetch(`/api/v1${path}`, { ...options, headers });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

async function refreshData() {
  if (!state.token || state.token === 'demo-token') {
    useDemoData();
    return;
  }
  try {
    const [jobs, resumes, history] = await Promise.all([
      api('/jobs/'),
      api('/resumes/'),
      api('/matching/history'),
    ]);
    state.jobs = jobs;
    state.resumes = resumes;
    state.history = history;
    state.usingDemo = false;
  } catch {
    useDemoData();
  }
}

function useDemoData() {
  state.jobs = [...demoJobs];
  state.resumes = [...demoResumes];
  state.history = [...demoHistory];
  state.usingDemo = true;
}

function setSession(user: Record<string, unknown>, token: string) {
  state.user = user;
  state.token = token;
  localStorage.setItem('user', JSON.stringify(user));
  localStorage.setItem('access_token', token);
}

function logout() {
  state.user = null;
  state.token = '';
  localStorage.removeItem('user');
  localStorage.removeItem('access_token');
  render();
}

function demoLogin() {
  setSession({ id: 'demo', full_name: 'Demo Candidate', email: 'demo@jobtrack.ai' }, 'demo-token');
  refreshData().then(render);
}

function navButton(view: string, label: string, icon: string = '') {
  return `
    <button class="nav-item ${state.view === view ? 'active' : ''}" data-view="${view}">
      <span style="font-size:16px;">${icon}</span>
      <span>${label}</span>
    </button>
  `;
}

function layout(content: string) {
  app.innerHTML = `
    <div class="shell">
      <aside class="sidebar">
        <div class="brand"><div class="brand-mark">JT</div><div><strong>JobTrack AI</strong><span>Career Command Center</span></div></div>
        <nav>
          ${navButton('dashboard', 'Dashboard', '📊')}
          ${navButton('jobs', 'Applications', '💼')}
          ${navButton('kanban', 'Kanban Board', '📋')}
          ${navButton('resumes', 'Resumes', '📄')}
          ${navButton('match', 'AI Matcher', '🤖')}
          ${navButton('coverLetter', 'Cover Letter', '✍️')}
          ${navButton('history', 'Match History', '🕒')}
          ${navButton('assistant', 'AI Assistant', '✨')}
        </nav>
        <div class="sidebar-user" style="display:flex; flex-direction:column; gap:10px; align-items:stretch;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span>👤 ${escapeHtml(state.user?.full_name || 'User')}</span>
            <button class="ghost-btn" data-action="logout">Logout</button>
          </div>
          <div class="theme-switcher">
            <span style="font-size:11px; font-weight:700; text-transform:uppercase; color:var(--muted); letter-spacing:0.04em;">Palette</span>
            <div style="display:flex; gap:6px;">
              <button class="theme-dot ${state.theme === 'indigo' ? 'active' : ''}" data-set-theme="indigo" title="Modern Indigo (Linear tech style)" style="background:#6366f1;"></button>
              <button class="theme-dot ${state.theme === 'emerald' ? 'active' : ''}" data-set-theme="emerald" title="Emerald Growth (Vibrant Mint)" style="background:#059669;"></button>
              <button class="theme-dot ${state.theme === 'royal' ? 'active' : ''}" data-set-theme="royal" title="Royal Executive (Stripe style)" style="background:#2563eb;"></button>
              <button class="theme-dot ${state.theme === 'sunset' ? 'active' : ''}" data-set-theme="sunset" title="Sunset Amber (Warm Coral)" style="background:#ea580c;"></button>
            </div>
          </div>
        </div>
      </aside>
      <main class="content">${content}</main>
      <button class="floating-assistant-btn" data-view="assistant">✨ AI Assistant</button>
    </div>
  `;
  bindGlobalEvents();
}

function topbar(title: string, subtitle: string, action = '') {
  return `
    <div class="topbar">
      <div><h1>${title}</h1><p>${subtitle}</p></div>
      ${action}
    </div>
    ${state.usingDemo ? '<div class="notice">⚡ Preview mode is active with interactive demo records.</div>' : ''}
    ${state.message ? `<div class="notice ${state.message.includes('fail') || state.message.includes('check') ? 'warn' : 'success'}">${escapeHtml(state.message)}</div>` : ''}
  `;
}

function stat(label: string, value: string | number, icon: string = '✨') {
  return `
    <article class="stat">
      <span>${escapeHtml(label)} <span style="font-size:18px;">${icon}</span></span>
      <strong>${escapeHtml(String(value))}</strong>
    </article>
  `;
}

function jobRow(job: Job, deletable = false) {
  return `
    <article class="row">
      <div><strong>${escapeHtml(job.company_name)}</strong><span>${escapeHtml(job.job_title)} • ${escapeHtml(job.job_location || 'Location not set')}</span></div>
      <div class="row-actions">
        <span class="badge ${job.status}">${statusLabels[job.status] || job.status}</span>
        ${deletable ? `<button class="icon-btn danger" data-delete-job="${job.id}">Delete</button>` : ''}
      </div>
    </article>
  `;
}

function dashboard() {
  const counts = Object.fromEntries(statuses.map((status) => [status, state.jobs.filter((job) => job.status === status).length]));
  const total = state.jobs.length || 1;
  const interviewRate = Math.round((((counts.interviewing || 0) + (counts.offered || 0) + (counts.accepted || 0)) / total) * 100);
  const offerRate = Math.round((((counts.offered || 0) + (counts.accepted || 0)) / total) * 100);

  layout(`
    ${topbar('Dashboard', 'Application pipeline, resume readiness, and match activity.', state.jobs.length === 0 ? '<button class="secondary" data-action="load-sample-jobs">⚡ Load Sample Jobs</button>' : '')}
    <section class="stats">
      ${stat('Applications', state.jobs.length, '💼')}
      ${stat('Interview rate', `${interviewRate}%`, '💬')}
      ${stat('Offer rate', `${offerRate}%`, '🎉')}
      ${stat('Resumes', state.resumes.length, '📄')}
    </section>
    <section class="grid-two">
      <div class="panel">
        <div class="section-head"><h2>Pipeline</h2></div>
        <div class="bars">
          ${statuses.slice(0, 6).map((status) => `
            <div class="bar-row">
              <span>${statusLabels[status]}</span>
              <div><i style="width:${Math.min(100, ((counts[status] || 0) / total) * 100)}%"></i></div>
              <strong>${counts[status] || 0}</strong>
            </div>
          `).join('')}
        </div>
      </div>
      <div class="panel">
        <div class="section-head">
          <h2>Recent Jobs (${state.jobs.length})</h2>
          ${state.jobs.length === 0 ? '<button class="ghost-btn" data-action="load-sample-jobs">⚡ Sample Jobs</button>' : ''}
        </div>
        <div class="list">
          ${state.jobs.length > 0
            ? state.jobs.slice(0, 4).map((job) => jobRow(job)).join('')
            : '<div class="empty">No applications tracked yet.<br><br><button class="secondary" data-action="load-sample-jobs">⚡ Load Sample Jobs</button></div>'
          }
        </div>
      </div>
    </section>
  `);
}

function jobsPage() {
  layout(`
    ${topbar('Jobs', 'Track every role, source, stage, and note in one place.', '<button class="secondary" data-action="load-sample-jobs">⚡ Load Sample Jobs</button>')}
    <section class="grid-two wide-left">
      <div class="panel">
        <div class="section-head">
          <h2>Applications (${state.jobs.length})</h2>
          <input id="job-search" class="search" placeholder="Search jobs">
        </div>
        <div class="list" id="jobs-list">
          ${state.jobs.length > 0
            ? state.jobs.map((job) => jobRow(job, true)).join('')
            : '<div class="empty">No applications in your tracker yet.<br><br><button class="primary" data-action="load-sample-jobs">⚡ Load 4 Sample Jobs</button></div>'
          }
        </div>
      </div>
      <div class="panel">
        <div class="section-head"><h2>Add Job</h2></div>
        <form id="job-form" class="form">
          <input name="company_name" placeholder="Company" required>
          <input name="job_title" placeholder="Job title" required>
          <input name="job_location" placeholder="Location">
          <input name="salary_range" placeholder="Salary range">
          <select name="status">${statuses.map((status) => `<option value="${status}">${statusLabels[status]}</option>`).join('')}</select>
          <textarea name="job_description" placeholder="Job description"></textarea>
          <textarea name="notes" placeholder="Notes"></textarea>
          <div style="display:flex; gap:10px;">
            <button class="primary" type="submit" style="flex:1;">Add application</button>
            <button class="secondary" type="button" data-action="load-sample-jobs">⚡ Sample Data</button>
          </div>
        </form>
      </div>
    </section>
  `);
  document.querySelector<HTMLFormElement>('#job-form')?.addEventListener('submit', addJob);
  document.querySelector<HTMLInputElement>('#job-search')?.addEventListener('input', filterJobs);
}

async function addJob(event: SubmitEvent) {
  event.preventDefault();
  const form = event.currentTarget as HTMLFormElement;
  const data = Object.fromEntries(new FormData(form).entries()) as unknown as Job;
  try {
    const created = await api('/jobs/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    state.jobs.unshift(created);
    state.message = 'Application saved.';
  } catch {
    state.jobs.unshift({ ...data, id: Date.now(), applied_date: new Date().toISOString() });
    state.usingDemo = true;
    state.message = 'Application added to preview data.';
  }
  jobsPage();
}

function filterJobs(event: Event) {
  const query = (event.target as HTMLInputElement).value.toLowerCase();
  const filtered = state.jobs.filter((job) => `${job.company_name} ${job.job_title} ${job.job_location}`.toLowerCase().includes(query));
  document.querySelector<HTMLDivElement>('#jobs-list')!.innerHTML = filtered.map((job) => jobRow(job, true)).join('');
}

function kanbanPage() {
  layout(`
    ${topbar('Kanban Board', 'Move applications through your job search pipeline.', `
      <div style="display:flex; gap:8px;">
        <button class="secondary" data-action="load-sample-jobs">⚡ Load Sample Jobs</button>
        <button class="secondary" data-action="refresh">Refresh</button>
      </div>
    `)}
    ${state.jobs.length === 0 ? '<div class="empty" style="margin-bottom:16px;">No applications in your pipeline. Click <button class="ghost-btn" data-action="load-sample-jobs">⚡ Load Sample Jobs</button> to populate sample records.</div>' : ''}
    <section class="kanban">
      ${statuses.map((status) => `
        <div class="kanban-col">
          <div class="kanban-head"><strong>${statusLabels[status]}</strong><span>${state.jobs.filter((job) => job.status === status).length}</span></div>
          ${state.jobs.filter((job) => job.status === status).map((job) => `
            <article class="job-card">
              <strong>${escapeHtml(job.company_name)}</strong>
              <span>${escapeHtml(job.job_title)}</span>
              <small>${formatDate(job.applied_date)} - ${escapeHtml(job.salary_range || 'Open')}</small>
              <select data-job-status="${job.id}">
                ${statuses.map((option) => `<option value="${option}" ${option === job.status ? 'selected' : ''}>${statusLabels[option]}</option>`).join('')}
              </select>
            </article>
          `).join('')}
        </div>
      `).join('')}
    </section>
  `);
}

async function uploadResume(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  const formData = new FormData();
  formData.append('file', file);
  formData.append('is_primary', String(state.resumes.length === 0));
  try {
    const uploaded = await fetch('/api/v1/resumes/upload', {
      method: 'POST',
      headers: state.token && state.token !== 'demo-token' ? { Authorization: `Bearer ${state.token}` } : {},
      body: formData,
    }).then((response) => {
      if (!response.ok) throw new Error('Upload failed');
      return response.json();
    });
    state.resumes.unshift(uploaded);
    state.message = 'Resume uploaded and parsed.';
  } catch {
    state.resumes.unshift({ id: Date.now(), file_name: file.name, file_size: file.size, skills: ['Preview upload'], experience_years: 0, is_primary: state.resumes.length === 0, created_at: new Date().toISOString() });
    state.usingDemo = true;
    state.message = 'Resume added to preview data.';
  }
  resumesPage();
}

function historyPage() {
  layout(`
    ${topbar('Match History', 'Review previous fit scores and revisit promising roles.')}
    <section class="panel">
      <div class="list">
        ${state.history.length === 0 ? '<div class="empty">No match evaluations performed yet.</div>' : state.history.map((item) => `
          <article class="row">
            <div><strong>${escapeHtml(item.company_name || 'Custom role')}</strong><span>${escapeHtml(item.job_title || 'Untitled job')} - ${formatDate(item.created_at)}</span></div>
            <div class="row-actions">
              <div class="score-pill">${Math.round(item.match_score)}%</div>
              <button class="icon-btn danger" data-delete-history="${item.id}">Delete</button>
            </div>
          </article>
        `).join('')}
      </div>
    </section>
  `);
}

async function deleteHistory(id: number) {
  try {
    await api(`/matching/${id}`, { method: 'DELETE' });
  } catch {
    state.usingDemo = true;
  }
  state.history = state.history.filter((item) => item.id !== id);
  render();
}

function authPage(mode: 'login' | 'register' | 'forgot' = 'login') {
  let title = 'Sign in to continue';
  if (mode === 'register') title = 'Create your account';
  if (mode === 'forgot') title = 'Reset your password';

  app.innerHTML = `
    <main class="auth-page">
      <section class="auth-card">
        <div class="brand auth-brand"><div class="brand-mark">JT</div><div><strong>JobTrack AI</strong><span>${title}</span></div></div>
        ${state.message ? `<div class="notice ${state.message.includes('success') ? 'success' : 'warn'}">${escapeHtml(state.message)}</div>` : ''}
        <form id="${mode}-form" class="form">
          ${mode === 'register' ? '<input name="full_name" placeholder="Full name (e.g. Alex Rivera)" required minlength="2">' : ''}
          <input name="email" type="email" placeholder="Email address" required>
          ${mode === 'forgot'
            ? '<input name="new_password" type="password" placeholder="New password (min. 8 characters)" required minlength="8">'
            : '<input name="password" type="password" placeholder="Password (min. 8 characters)" required minlength="8">'
          }
          ${mode === 'login' ? `
            <div style="display:flex; justify-content:flex-end; margin-top:-6px; margin-bottom:8px;">
              <button class="link-btn" type="button" data-auth-mode="forgot" style="font-size:13px; padding:0; background:none; border:none; color:var(--primary); cursor:pointer;">Forgot password?</button>
            </div>
          ` : ''}
          <button class="primary" type="submit">
            ${mode === 'login' ? 'Sign in' : mode === 'register' ? 'Create account' : 'Reset Password'}
          </button>
          ${mode !== 'forgot' ? '<button class="secondary" type="button" data-action="demo-login">⚡ Explore with Demo Data</button>' : ''}
        </form>
        ${mode === 'login'
          ? '<button class="link-btn" data-auth-mode="register">Don\'t have an account? Create one</button>'
          : '<button class="link-btn" data-auth-mode="login">Back to Sign in</button>'
        }
      </section>
    </main>
  `;
  const formEl = document.querySelector<HTMLFormElement>(`#${mode}-form`);
  if (mode === 'login') formEl?.addEventListener('submit', login);
  else if (mode === 'register') formEl?.addEventListener('submit', register);
  else if (mode === 'forgot') formEl?.addEventListener('submit', resetPassword);
  bindGlobalEvents();
}

async function resetPassword(event: SubmitEvent) {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.currentTarget as HTMLFormElement).entries());
  try {
    const res = await api('/auth/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    state.message = res.message || 'Password reset successfully! Please sign in.';
    authPage('login');
  } catch (err: any) {
    let msg = 'Password reset failed. Please check your email.';
    try {
      const parsed = JSON.parse(err.message);
      if (typeof parsed.detail === 'string') {
        msg = parsed.detail;
      } else if (Array.isArray(parsed.detail)) {
        msg = parsed.detail.map((d: any) => d.msg || d).join(', ');
      }
    } catch {
      if (err.message && err.message.length < 150) msg = err.message;
    }
    state.message = msg;
    authPage('forgot');
  }
}

async function login(event: SubmitEvent) {
  event.preventDefault();
  const data = new FormData(event.currentTarget as HTMLFormElement);
  const form = new URLSearchParams();
  form.append('username', String(data.get('email')));
  form.append('password', String(data.get('password')));
  try {
    const token = await api('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form,
    });
    setSession({ full_name: String(data.get('email')), email: String(data.get('email')) }, token.access_token);
    await refreshData();
    state.message = '';
    render();
  } catch (err: any) {
    let msg = 'Sign in failed. Please check your email and password.';
    try {
      const parsed = JSON.parse(err.message);
      if (typeof parsed.detail === 'string') {
        msg = parsed.detail;
      } else if (Array.isArray(parsed.detail)) {
        msg = parsed.detail.map((d: any) => d.msg || d).join(', ');
      }
    } catch {
      if (err.message && err.message.length < 150) msg = err.message;
    }
    state.message = msg;
    authPage('login');
  }
}

async function register(event: SubmitEvent) {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.currentTarget as HTMLFormElement).entries());
  try {
    await api('/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    state.message = 'Account created successfully! Please sign in.';
    authPage('login');
  } catch (err: any) {
    let msg = 'Registration failed. Please check your input.';
    try {
      const parsed = JSON.parse(err.message);
      if (typeof parsed.detail === 'string') {
        msg = parsed.detail;
      } else if (Array.isArray(parsed.detail)) {
        msg = parsed.detail.map((d: any) => d.msg || d).join(', ');
      }
    } catch {
      if (err.message && err.message.length < 150) msg = err.message;
    }
    state.message = msg;
    authPage('register');
  }
}

async function deleteJob(id: number) {
  try {
    await api(`/jobs/${id}`, { method: 'DELETE' });
  } catch {
    state.usingDemo = true;
  }
  state.jobs = state.jobs.filter((job) => job.id !== id);
  render();
}

async function setPrimaryResume(id: number) {
  try {
    await api(`/resumes/${id}/primary`, { method: 'PUT' });
  } catch {
    state.usingDemo = true;
  }
  state.resumes = state.resumes.map((resume) => ({ ...resume, is_primary: resume.id === id }));
  render();
}

async function updateJobStatus(id: number, status: string) {
  state.jobs = state.jobs.map((job) => (job.id === id ? { ...job, status } : job));
  try {
    await api(`/jobs/${id}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
  } catch {
    state.usingDemo = true;
  }
  kanbanPage();
}

function bindGlobalEvents() {
  if (eventsBound) return;
  app.addEventListener('click', handleClick);
  app.addEventListener('change', handleChange);
  eventsBound = true;
}

function resumesPage() {
  layout(`
    ${topbar('Resumes', 'Upload versions, extract skills, and choose the primary resume for matching.', '<label class="primary file-button">Upload Resume<input id="resume-upload" type="file" accept=".pdf,.docx" hidden></label>')}
    <section class="cards">
      ${state.resumes.map((resume) => `
        <article class="panel resume-card">
          <div class="resume-top"><strong>${escapeHtml(resume.file_name)}</strong>${resume.is_primary ? '<span class="badge accepted">Primary</span>' : ''}</div>
          <p>${resume.experience_years || 0} years experience - ${Math.round((resume.file_size || 0) / 1024)} KB</p>
          <div class="chips" style="margin-bottom: 12px;">${(resume.skills || []).slice(0, 8).map((skill) => `<span>${escapeHtml(skill)}</span>`).join('')}</div>
          <div class="row-actions">
            ${resume.is_primary ? '' : `<button class="secondary" data-primary-resume="${resume.id}">Set primary</button>`}
            <button class="secondary" data-download-resume="${resume.id}">Download</button>
            <button class="icon-btn danger" data-delete-resume="${resume.id}">Delete</button>
          </div>
        </article>
      `).join('')}
    </section>
  `);
  document.querySelector<HTMLInputElement>('#resume-upload')?.addEventListener('change', uploadResume);
}

async function deleteResume(id: number) {
  try {
    await api(`/resumes/${id}`, { method: 'DELETE' });
  } catch {
    state.usingDemo = true;
  }
  state.resumes = state.resumes.filter((resume) => resume.id !== id);
  if (state.resumes.length > 0 && !state.resumes.some((r) => r.is_primary)) {
    state.resumes[0].is_primary = true;
  }
  state.message = 'Resume deleted.';
  render();
}

function downloadResume(id: number) {
  const resume = state.resumes.find((r) => r.id === id);
  if (!resume) return;
  const token = state.token;
  if (token && token !== 'demo-token') {
    window.open(`/api/v1/resumes/${id}/download?token=${encodeURIComponent(token)}`, '_blank');
  } else {
    alert(`Demo preview: Downloading original raw file "${resume.file_name}"`);
  }
}

function handleClick(event: MouseEvent) {
  const target = event.target as HTMLElement;
  const button = target.closest<HTMLElement>('[data-view], [data-action], [data-auth-mode], [data-set-theme], [data-prompt], [data-delete-job], [data-primary-resume], [data-delete-history], [data-delete-resume], [data-download-resume]');
  if (!button) return;

  if (button.dataset.prompt) {
    sendAssistantMessage(button.dataset.prompt);
    return;
  }

  if (button.dataset.action === 'clear-chat') {
    state.chatMessages = [
      {
        role: 'assistant',
        content: 'Chat history cleared. What career or job search topic would you like to discuss?',
      },
    ];
    render();
    return;
  }

  if (button.dataset.setTheme) {
    const t = button.dataset.setTheme;
    state.theme = t;
    localStorage.setItem('app-theme', t);
    document.documentElement.setAttribute('data-theme', t);
    state.message = `Switched to ${t.charAt(0).toUpperCase() + t.slice(1)} theme!`;
    render();
    return;
  }

  if (button.dataset.view) {
    state.view = button.dataset.view;
    state.message = '';
    render();
    return;
  }

  if (button.dataset.action === 'logout') logout();
  if (button.dataset.action === 'demo-login') demoLogin();
  if (button.dataset.action === 'refresh') refreshData().then(render);
  if (button.dataset.action === 'load-sample-match') loadSampleMatchData();
  if (button.dataset.action === 'load-sample-jobs') loadSampleJobs();
  if (button.dataset.action === 'generate-cover-letter') generateCoverLetter();
  if (button.dataset.action === 'copy-cover-letter') copyCoverLetterToClipboard();
  if (button.dataset.authMode) authPage(button.dataset.authMode as 'login' | 'register' | 'forgot');
  if (button.dataset.deleteJob) deleteJob(Number(button.dataset.deleteJob));
  if (button.dataset.primaryResume) setPrimaryResume(Number(button.dataset.primaryResume));
  if (button.dataset.deleteHistory) deleteHistory(Number(button.dataset.deleteHistory));
  if (button.dataset.deleteResume) deleteResume(Number(button.dataset.deleteResume));
  if (button.dataset.downloadResume) downloadResume(Number(button.dataset.downloadResume));
}

function handleChange(event: Event) {
  const target = event.target as HTMLElement;
  if (target instanceof HTMLSelectElement && target.dataset.jobStatus) {
    updateJobStatus(Number(target.dataset.jobStatus), target.value);
  }
}

function coverLetterPage() {
  layout(`
    ${topbar('Cover Letter Generator', 'Generate a tailored 3-paragraph cover letter using AI.', '<button class="secondary" data-action="load-sample-match">⚡ Load Sample Data</button>')}
    <section class="grid-two">
      <div class="panel">
        <div class="section-head"><h2>Target Role & Tone</h2></div>
        <form id="cl-form" class="form">
          <select name="resume_id" id="match-resume-id">
            <option value="">Primary or latest resume</option>
            ${state.resumes.map((resume) => `<option value="${resume.id}" ${state.matchForm.resumeId === String(resume.id) ? 'selected' : ''}>${escapeHtml(resume.file_name)}</option>`).join('')}
          </select>
          <input name="company_name" id="match-company" placeholder="Company (e.g. TechCorp AI)" value="${escapeHtml(state.matchForm.company)}">
          <input name="job_title" id="match-title" placeholder="Job title (e.g. Senior Full Stack Engineer)" value="${escapeHtml(state.matchForm.title)}">
          <select name="tone" id="match-tone">
            <option value="professional" ${state.matchForm.tone === 'professional' ? 'selected' : ''}>Tone: Professional & Authoritative</option>
            <option value="enthusiastic" ${state.matchForm.tone === 'enthusiastic' ? 'selected' : ''}>Tone: Enthusiastic & Passionate</option>
            <option value="concise" ${state.matchForm.tone === 'concise' ? 'selected' : ''}>Tone: Direct & Concise</option>
          </select>
          <textarea name="job_description" id="match-jd" placeholder="Paste job description text" required>${escapeHtml(state.matchForm.jd)}</textarea>
          <div style="display:flex; gap:10px;">
            <button class="primary" type="submit" style="flex:1;" ${state.generatingLetter ? 'disabled' : ''}>
              ${state.generatingLetter ? 'Generating Cover Letter...' : '📝 Generate Cover Letter'}
            </button>
            <button class="secondary" type="button" data-action="load-sample-match">⚡ Sample Data</button>
          </div>
        </form>
      </div>
      <div class="panel">
        ${state.coverLetter ? `
          <div class="section-head">
            <h2>Cover Letter Preview</h2>
            <button class="secondary" data-action="copy-cover-letter">📋 Copy to Clipboard</button>
          </div>
          <div style="display:flex; gap:8px; margin-bottom:14px; flex-wrap:wrap;">
            ${(state.coverLetter.key_highlights || []).map((h) => `<span class="badge accepted">${escapeHtml(h)}</span>`).join('')}
          </div>
          <textarea id="cover-letter-text" readonly style="width:100%; min-height:280px; font-family:inherit; background:#ffffff; color:#0f172a; padding:14px; border:1px solid var(--border); border-radius:8px; line-height:1.6;">${escapeHtml(state.coverLetter.cover_letter)}</textarea>
        ` : '<div class="empty">Fill in the target role details and click "Generate Cover Letter" or "Sample Data" to preview your letter.</div>'}
      </div>
    </section>
  `);
  document.querySelector<HTMLFormElement>('#cl-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    generateCoverLetter();
  });
}

function assistantPage() {
  layout(`
    ${topbar('AI Career Assistant', 'Ask career advice, prepare for interviews, polish resume bullets, and strategize your pipeline.', '<button class="secondary" data-action="clear-chat">🗑️ Clear Chat</button>')}
    <section class="panel" style="padding:0; overflow:hidden;">
      <div class="chat-container">
        <div class="chat-header">
          <div style="display:flex; align-items:center; gap:12px;">
            <div class="brand-mark" style="width:36px; height:36px; font-size:15px;">✨</div>
            <div>
              <strong style="font-size:15px; color:#0f172a; display:block;">Career Copilot AI</strong>
              <small style="color:var(--muted); font-size:12px;">🟢 Online • Ready to coach on resumes, interviews & strategy</small>
            </div>
          </div>
          <span class="badge accepted">AI Ready</span>
        </div>
        
        <div class="chat-messages" id="chat-messages-container">
          ${state.chatMessages.map((msg) => `
            <div class="chat-msg ${msg.role}">
              <div style="font-size:11px; font-weight:700; opacity:0.8; margin-bottom:4px; text-transform:uppercase; letter-spacing:0.04em;">
                ${msg.role === 'assistant' ? '✨ Career Copilot' : '👤 You'}
              </div>
              <div>${escapeHtml(msg.content)}</div>
            </div>
          `).join('')}
          ${state.assistantLoading ? `
            <div class="chat-msg assistant">
              <div style="font-size:11px; font-weight:700; opacity:0.8; margin-bottom:4px; text-transform:uppercase; letter-spacing:0.04em;">✨ Career Copilot</div>
              <div style="display:flex; align-items:center; gap:8px;">
                <span>Analyzing background and generating advice...</span>
                <span class="badge interviewing">Thinking</span>
              </div>
            </div>
          ` : ''}
        </div>

        <div class="chat-chips-bar">
          ${state.suggestedPrompts.map((p) => `
            <button class="prompt-chip" data-prompt="${escapeHtml(p)}">${escapeHtml(p)}</button>
          `).join('')}
        </div>

        <form id="chat-form" class="chat-input-row">
          <input id="chat-input" placeholder="Ask anything (e.g. 'How should I answer tell me about yourself?')" autocomplete="off" required>
          <button class="primary" type="submit" ${state.assistantLoading ? 'disabled' : ''}>
            ${state.assistantLoading ? '...' : 'Send 🚀'}
          </button>
        </form>
      </div>
    </section>
  `);

  const container = document.querySelector<HTMLDivElement>('#chat-messages-container');
  if (container) container.scrollTop = container.scrollHeight;

  document.querySelector<HTMLFormElement>('#chat-form')?.addEventListener('submit', (e) => {
    e.preventDefault();
    const input = document.querySelector<HTMLInputElement>('#chat-input');
    if (input && input.value.trim()) {
      const msg = input.value.trim();
      input.value = '';
      sendAssistantMessage(msg);
    }
  });
}

async function sendAssistantMessage(userText: string) {
  state.chatMessages.push({ role: 'user', content: userText });
  state.assistantLoading = true;
  assistantPage();

  try {
    const res = await api('/assistant/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userText,
        history: state.chatMessages.slice(-6),
      }),
    });
    state.chatMessages.push({ role: 'assistant', content: res.reply });
    if (res.suggested_prompts && res.suggested_prompts.length > 0) {
      state.suggestedPrompts = res.suggested_prompts;
    }
  } catch {
    const topSkills = state.resumes.length > 0 && state.resumes[0].skills?.length
      ? state.resumes[0].skills.slice(0, 4).join(', ')
      : 'Python, FastAPI, React, MySQL';
    const fallbackReply = `Here is tailored advice for your background in **${topSkills}**:\n\n• **Quantify Your Impact:** In technical interviews and resumes, frame accomplishments around latency reduction, architecture scalability, and test coverage.\n• **System Design Tip:** When discussing full-stack development, highlight how you isolate state in React and handle connection pooling with databases.\n• **Active Applications:** You currently have ${state.jobs.length} tracked jobs. Focus on consistent follow-ups and matching your skills with role requirements.`;
    state.chatMessages.push({ role: 'assistant', content: fallbackReply });
  } finally {
    state.assistantLoading = false;
    assistantPage();
    setTimeout(() => {
      const container = document.querySelector<HTMLDivElement>('#chat-messages-container');
      if (container) container.scrollTop = container.scrollHeight;
    }, 50);
  }
}

function render() {
  if (!state.token) {
    authPage('login');
    return;
  }
  const pages: Record<string, () => void> = {
    dashboard,
    jobs: jobsPage,
    kanban: kanbanPage,
    resumes: resumesPage,
    match: matchPage,
    coverLetter: coverLetterPage,
    history: historyPage,
    assistant: assistantPage,
  };
  (pages[state.view] || dashboard)();
}

refreshData().then(render);
