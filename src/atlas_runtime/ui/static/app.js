async function fetchStatus() {
  const response = await fetch('/api/status');
  const data = await response.json();
  document.getElementById('workspace').textContent = data.workspace;
  document.getElementById('doctor').textContent = JSON.stringify(data.doctor, null, 2);
  document.getElementById('verify').textContent = JSON.stringify(data.verify, null, 2);
  document.getElementById('gap-meter').textContent = JSON.stringify(data.gap_meter, null, 2);
  document.getElementById('replay').textContent = JSON.stringify(data.replay, null, 2);
  const list = document.getElementById('open-gaps');
  list.innerHTML = '';
  for (const gap of data.verify.open_gaps) {
    const item = document.createElement('li');
    item.textContent = gap;
    list.appendChild(item);
  }
}

async function runDemo() {
  const response = await fetch('/api/run-demo', { method: 'POST' });
  await response.json();
  await fetchStatus();
}

document.getElementById('refresh').addEventListener('click', fetchStatus);
document.getElementById('run-demo').addEventListener('click', runDemo);
fetchStatus();
