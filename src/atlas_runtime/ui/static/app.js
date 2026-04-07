function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function renderFiles(files) {
  const list = document.getElementById('file-tree');
  list.innerHTML = '';
  for (const file of files.slice(0, 24)) {
    const item = document.createElement('li');
    item.className = file.kind;
    item.textContent = `${file.kind === 'dir' ? '▸' : '•'} ${file.path}`;
    list.appendChild(item);
  }
}

function renderEvents(events) {
  const mount = document.getElementById('event-stream');
  mount.innerHTML = '';
  for (const event of events.slice().reverse()) {
    const row = document.createElement('article');
    row.className = 'event';
    row.innerHTML = `
      <div class="event-meta">
        <span class="event-type">${event.type}</span>
        <span>${event.agent || 'runtime'} · ${event.ts}</span>
      </div>
      <pre>${JSON.stringify(event.payload || {}, null, 2)}</pre>
    `;
    mount.appendChild(row);
  }
}

function renderAgents(agents) {
  const mount = document.getElementById('agent-list');
  mount.innerHTML = '';
  for (const agent of agents) {
    const row = document.createElement('article');
    row.className = 'agent-row';
    row.innerHTML = `
      <header>
        <strong>${agent.name}</strong>
        <small>${agent.status}</small>
      </header>
      <small>${agent.delivered} delivered / ${agent.tasks} total</small>
    `;
    mount.appendChild(row);
  }
}

function renderTasks(tasks) {
  const mount = document.getElementById('task-list');
  mount.innerHTML = '';
  for (const task of tasks) {
    const row = document.createElement('article');
    row.className = 'task-row';
    row.innerHTML = `
      <header>
        <strong>${task.id}</strong>
        <small>${task.status}</small>
      </header>
      <div>${task.title}</div>
      <small>${task.owner}${task.depends_on?.length ? ` · deps: ${task.depends_on.join(', ')}` : ''}</small>
    `;
    mount.appendChild(row);
  }
}

async function fetchStatus() {
  const response = await fetch('/api/status');
  const data = await response.json();
  setText('workspace-path', data.workspace);
  setText('metric-score', data.metrics.score);
  setText('metric-status', data.metrics.status);
  setText('metric-delivered', data.metrics.delivered);
  setText('metric-gap', `${data.metrics.gap_progress_pct}%`);
  setText('metric-events', data.metrics.event_count);
  setText('doctor-pill', data.doctor.status);
  document.getElementById('doctor-pill').style.background = data.doctor.status === 'PASS' ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)';
  document.getElementById('doctor-pill').style.color = data.doctor.status === 'PASS' ? '#86efac' : '#fca5a5';
  document.getElementById('doctor-json').textContent = JSON.stringify(data.doctor, null, 2);
  document.getElementById('replay-json').textContent = JSON.stringify(data.replay, null, 2);
  document.getElementById('gap-json').textContent = JSON.stringify(data.gap_meter, null, 2);

  const gaps = document.getElementById('open-gaps');
  gaps.innerHTML = '';
  for (const gap of data.verify.open_gaps) {
    const item = document.createElement('li');
    item.textContent = gap;
    gaps.appendChild(item);
  }

  renderFiles(data.files);
  renderEvents(data.events);
  renderAgents(data.agents);
  renderTasks(data.tasks);
}

async function runDemo() {
  const response = await fetch('/api/run-demo', { method: 'POST' });
  await response.json();
  await fetchStatus();
}

document.getElementById('refresh').addEventListener('click', fetchStatus);
document.getElementById('run-demo').addEventListener('click', runDemo);
fetchStatus();
