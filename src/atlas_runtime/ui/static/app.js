function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function initials(name) {
  return String(name || 'AT').split(/\s+/).map((part) => part[0]).join('').slice(0, 2).toUpperCase();
}

function prettyPayload(payload) {
  const text = JSON.stringify(payload || {}, null, 2);
  return text.length > 240 ? `${text.slice(0, 240)}...` : text;
}

function renderFiles(files) {
  const list = document.getElementById('file-tree');
  list.innerHTML = '';
  for (const file of files.slice(0, 28)) {
    const item = document.createElement('li');
    item.className = file.kind;
    item.textContent = `${file.kind === 'dir' ? '▸' : '•'} ${file.path}`;
    list.appendChild(item);
  }
  setText('file-count', `${files.length} items`);
}

function renderEvents(events) {
  const mount = document.getElementById('event-stream');
  mount.innerHTML = '';
  for (const event of [...events].reverse()) {
    const row = document.createElement('article');
    row.className = 'event-card';
    const agent = event.agent || 'runtime';
    row.innerHTML = `
      <div class="event-head">
        <div class="event-agent">
          <div class="event-avatar">${initials(agent)}</div>
          <div>
            <div class="event-title">${event.type}</div>
            <div class="event-subtitle">${agent} · ${event.ts || 'n/a'}</div>
          </div>
        </div>
      </div>
      <pre class="event-body">${prettyPayload(event.payload)}</pre>
    `;
    mount.appendChild(row);
  }
}

function renderAgents(agents) {
  const mount = document.getElementById('agent-list');
  mount.innerHTML = '';
  for (const agent of agents) {
    const delivered = Number(agent.delivered || 0);
    const total = Math.max(Number(agent.tasks || 0), 1);
    const progress = Math.round((delivered / total) * 100);
    const row = document.createElement('article');
    row.className = 'agent-row';
    row.innerHTML = `
      <div class="agent-top">
        <div class="agent-name">${agent.name}</div>
        <div class="agent-status">${agent.status}</div>
      </div>
      <div class="agent-progress"><span style="width:${progress}%"></span></div>
      <div class="agent-meta">
        <span>${delivered} delivered</span>
        <span>${agent.tasks} tasks</span>
      </div>
    `;
    mount.appendChild(row);
  }
  setText('agent-count', `${agents.length} owners`);
}

function renderTasks(tasks) {
  const mount = document.getElementById('task-list');
  mount.innerHTML = '';
  for (const task of tasks) {
    const row = document.createElement('article');
    row.className = 'task-card';
    const deps = task.depends_on?.length ? task.depends_on.join(', ') : 'none';
    row.innerHTML = `
      <header>
        <div class="task-id">${task.id}</div>
        <div class="task-status">${task.status}</div>
      </header>
      <div class="task-title">${task.title}</div>
      <div class="task-meta">
        <span class="task-chip">owner: ${task.owner}</span>
        <span class="task-chip">deps: ${deps}</span>
      </div>
    `;
    mount.appendChild(row);
  }
  setText('task-count', `${tasks.length} tasks`);
}

function renderGaps(gaps) {
  const mount = document.getElementById('open-gaps');
  mount.innerHTML = '';
  for (const gap of gaps) {
    const item = document.createElement('li');
    item.textContent = gap;
    mount.appendChild(item);
  }
  setText('gap-count', `${gaps.length} open`);
}

function applyPill(id, status) {
  const el = document.getElementById(id);
  el.textContent = status;
  const pass = status === 'PASS';
  el.style.background = pass ? 'rgba(120,241,181,0.16)' : 'rgba(255,139,139,0.14)';
  el.style.borderColor = pass ? 'rgba(120,241,181,0.15)' : 'rgba(255,139,139,0.18)';
  el.style.color = pass ? '#78f1b5' : '#ff8b8b';
}

async function fetchStatus() {
  const response = await fetch('/api/status');
  const data = await response.json();

  setText('workspace-path', data.workspace);
  setText('workspace-mode', data.workspace.includes('Atlas Autonomous Group') ? 'Atlas Source' : 'Wrapper');
  setText('metric-score', data.metrics.score);
  setText('metric-status', data.metrics.status);
  setText('metric-delivered', data.metrics.delivered);
  setText('metric-gap', `${data.metrics.gap_progress_pct}%`);
  setText('metric-events', data.metrics.event_count);

  setText('quick-doctor', data.doctor.status);
  setText('quick-replay', data.replay.status);
  setText('quick-verify', data.verify.status);
  setText('quick-gaps', `${data.gap_meter.active} active`);

  applyPill('doctor-pill', data.doctor.status);
  applyPill('verify-pill', data.verify.status);

  document.getElementById('doctor-json').textContent = JSON.stringify(data.doctor, null, 2);
  document.getElementById('replay-json').textContent = JSON.stringify(data.replay, null, 2);
  document.getElementById('gap-json').textContent = JSON.stringify(data.gap_meter, null, 2);

  renderGaps(data.verify.open_gaps || []);
  renderFiles(data.files || []);
  renderEvents(data.events || []);
  renderAgents(data.agents || []);
  renderTasks(data.tasks || []);
}

async function runDemo() {
  const button = document.getElementById('run-demo');
  const previous = button.textContent;
  button.disabled = true;
  button.textContent = 'Running...';
  try {
    const response = await fetch('/api/run-demo', { method: 'POST' });
    await response.json();
    await fetchStatus();
  } finally {
    button.disabled = false;
    button.textContent = previous;
  }
}

document.getElementById('refresh').addEventListener('click', fetchStatus);
document.getElementById('run-demo').addEventListener('click', runDemo);
fetchStatus();
setInterval(fetchStatus, 15000);
