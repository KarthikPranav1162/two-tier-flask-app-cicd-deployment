const API = '';

function qs(id) { return document.getElementById(id); }

function toast(msg, color = '#1a1916') {
  const t = document.createElement('div');
  t.className = 'toast';
  t.textContent = msg;
  t.style.background = color;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2800);
}

const statusLabel = { todo: 'To Do', in_progress: 'In Progress', done: 'Done' };
const statusBadge = { todo: 'badge-todo', in_progress: 'badge-prog', done: 'badge-done' };
const priorityBadge = { low: 'badge-low', medium: 'badge-med', high: 'badge-high' };

async function apiFetch(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });

  if (!res.ok) {
    const text = await res.text(); // get actual error
    console.error("API Error:", text);
    throw new Error(`HTTP ${res.status}`);
  }

  return res.json();
}

async function loadStats() {
  const d = await apiFetch('/api/stats');
  qs('s-total').textContent = d.total;
  qs('s-todo').textContent  = d.todo;
  qs('s-prog').textContent  = d.in_progress;
  qs('s-done').textContent  = d.done;
}

async function loadTasks() {
  const status   = qs('statusFilter').value;
  const priority = qs('priorityFilter').value;
  const search   = qs('searchInput').value.trim();

  let url = '/api/tasks?';
  if (status)   url += `status=${status}&`;
  if (priority) url += `priority=${priority}&`;
  if (search)   url += `search=${encodeURIComponent(search)}&`;

  const data = await apiFetch(url);
  renderTasks(data.tasks);
  loadStats();
}

function renderTasks(tasks) {
  const list = qs('taskList');
  if (!tasks.length) {
    list.innerHTML = `<div class="empty">
      <div class="empty-icon">📋</div>
      <p>No tasks found. Create one!</p>
    </div>`;
    return;
  }

  list.innerHTML = tasks.map(t => `
    <div class="task-card ${t.status === 'done' ? 'done-card' : ''}">
      <div>
        <div class="task-title">${escHtml(t.title)}</div>
        ${t.description ? `<div class="task-desc">${escHtml(t.description)}</div>` : ''}
        <div class="task-meta">
          <span class="badge ${statusBadge[t.status]}">${statusLabel[t.status]}</span>
          <span class="badge ${priorityBadge[t.priority]}">${cap(t.priority)}</span>
          <span class="task-date">${t.created_at}</span>
        </div>
      </div>
      <div class="task-actions">
        <button class="btn btn-ghost btn-sm" onclick="openEdit(${t.id})">Edit</button>
        <button class="btn btn-sm" onclick="deleteTask(${t.id})">Delete</button>
      </div>
    </div>
  `).join('');
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

function openModal() {
  qs('modalTitle').textContent = 'New Task';
  qs('taskId').value = '';
  qs('titleInput').value = '';
  qs('descInput').value = '';
  qs('statusInput').value = 'todo';
  qs('priorityInput').value = 'medium';
  qs('overlay').classList.add('active');
}

async function openEdit(id) {
  const t = await apiFetch(`/api/tasks/${id}`);
  qs('modalTitle').textContent = 'Edit Task';
  qs('taskId').value = t.id;
  qs('titleInput').value = t.title;
  qs('descInput').value = t.description;
  qs('statusInput').value = t.status;
  qs('priorityInput').value = t.priority;
  qs('overlay').classList.add('active');
}

function closeModal() { qs('overlay').classList.remove('active'); }
function handleOverlayClick(e) { if (e.target === qs('overlay')) closeModal(); }

async function saveTask() {
  const title = qs('titleInput').value.trim();
  if (!title) { toast('Title is required', '#c0392b'); return; }

  const body = {
    title,
    description: qs('descInput').value.trim(),
    status: qs('statusInput').value,
    priority: qs('priorityInput').value,
  };

  const id = qs('taskId').value;
  if (id) {
    await apiFetch(`/api/tasks/${id}`, { method: 'PUT', body: JSON.stringify(body) });
    toast('Task updated ✓');
  } else {
    await apiFetch('/api/tasks', { method: 'POST', body: JSON.stringify(body) });
    toast('Task created ✓');
  }

  closeModal();
  loadTasks();
}

async function deleteTask(id) {
  if (!confirm('Delete this task?')) return;
  await apiFetch(`/api/tasks/${id}`, { method: 'DELETE' });
  toast('Task deleted');
  loadTasks();
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') saveTask();
});

loadTasks();