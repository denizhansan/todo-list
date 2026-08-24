/* ==========================================================================
   script.js
   Vanilla JavaScript frontend logic for the To-Do List app.
   Communicates with the FastAPI backend exclusively through the Fetch API.
   ========================================================================== */

// Base URL of the backend API. Change this if the backend runs on a
// different host/port (e.g., when later deployed behind Docker/K8s,
// this can be swapped for a relative path or an injected config value).
const API_BASE_URL = "/api";

// ---------------------------------------------------------------------
// State
// ---------------------------------------------------------------------
const state = {
  tasks: [],
  filter: "all", // 'all' | 'active' | 'completed'
  search: "",
  sort: "newest", // 'newest' | 'oldest'
  editingTaskId: null,
  pendingDeleteId: null,
};

// ---------------------------------------------------------------------
// DOM references
// ---------------------------------------------------------------------
const taskForm = document.getElementById("task-form");
const titleInput = document.getElementById("title-input");
const descriptionInput = document.getElementById("description-input");
const submitBtn = document.getElementById("submit-btn");
const cancelEditBtn = document.getElementById("cancel-edit-btn");

const searchInput = document.getElementById("search-input");
const filterButtons = document.querySelectorAll(".filter-btn");
const sortBtn = document.getElementById("sort-btn");

const loadingIndicator = document.getElementById("loading-indicator");
const taskListEl = document.getElementById("task-list");
const emptyStateEl = document.getElementById("empty-state");

const toastContainer = document.getElementById("toast-container");

const confirmModal = document.getElementById("confirm-modal");
const confirmDeleteBtn = document.getElementById("confirm-delete-btn");
const confirmCancelBtn = document.getElementById("confirm-cancel-btn");

// ---------------------------------------------------------------------
// Utility: toast notifications
// ---------------------------------------------------------------------
function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 3000);
}

// ---------------------------------------------------------------------
// Utility: loading indicator
// ---------------------------------------------------------------------
function setLoading(isLoading) {
  loadingIndicator.classList.toggle("hidden", !isLoading);
}

// ---------------------------------------------------------------------
// Utility: date formatting
// ---------------------------------------------------------------------
function formatDate(isoString) {
  const date = new Date(isoString);
  return date.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// ---------------------------------------------------------------------
// API calls
// ---------------------------------------------------------------------
async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  let data = null;
  try {
    data = await response.json();
  } catch (err) {
    // Response had no JSON body (e.g., network failure before reaching server)
  }

  if (!response.ok) {
    const detail = data && data.detail ? data.detail : "Something went wrong.";
    throw new Error(detail);
  }

  return data;
}

async function fetchTasks() {
  const params = new URLSearchParams();
  if (state.filter !== "all") params.append("status", state.filter);
  if (state.search.trim()) params.append("search", state.search.trim());
  params.append("sort", state.sort);

  return apiRequest(`/tasks?${params.toString()}`);
}

async function createTask(title, description) {
  return apiRequest("/tasks", {
    method: "POST",
    body: JSON.stringify({ title, description: description || null }),
  });
}

async function updateTask(id, payload) {
  return apiRequest(`/tasks/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

async function deleteTaskRequest(id) {
  return apiRequest(`/tasks/${id}`, { method: "DELETE" });
}

async function setTaskCompletion(id, completed) {
  const endpoint = completed ? "complete" : "uncomplete";
  return apiRequest(`/tasks/${id}/${endpoint}`, { method: "PATCH" });
}

// ---------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------
function renderTasks() {
  taskListEl.innerHTML = "";

  if (state.tasks.length === 0) {
    emptyStateEl.classList.remove("hidden");
    return;
  }
  emptyStateEl.classList.add("hidden");

  state.tasks.forEach((task) => {
    const li = document.createElement("li");
    li.className = `task-item ${task.completed ? "completed" : ""}`;
    li.dataset.id = task._id;

    li.innerHTML = `
      <input
        type="checkbox"
        class="task-checkbox"
        ${task.completed ? "checked" : ""}
        aria-label="Mark task as ${task.completed ? "active" : "completed"}"
      />
      <div class="task-content">
        <div class="task-title">${escapeHtml(task.title)}</div>
        ${
          task.description
            ? `<div class="task-description">${escapeHtml(task.description)}</div>`
            : ""
        }
        <div class="task-meta">Created: ${formatDate(task.created_at)}</div>
      </div>
      <div class="task-actions">
        <button class="icon-btn edit-btn" title="Edit task">✏️</button>
        <button class="icon-btn delete-btn" title="Delete task">🗑️</button>
      </div>
    `;

    taskListEl.appendChild(li);
  });
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// ---------------------------------------------------------------------
// Core load logic
// ---------------------------------------------------------------------
async function loadTasks() {
  setLoading(true);
  try {
    const tasks = await fetchTasks();
    state.tasks = tasks;
    renderTasks();
  } catch (err) {
    showToast(err.message || "Failed to load tasks.", "error");
  } finally {
    setLoading(false);
  }
}

// ---------------------------------------------------------------------
// Form handling (create + edit)
// ---------------------------------------------------------------------
function enterEditMode(task) {
  state.editingTaskId = task._id;
  titleInput.value = task.title;
  descriptionInput.value = task.description || "";
  submitBtn.textContent = "Update Task";
  cancelEditBtn.classList.remove("hidden");
  titleInput.focus();
}

function exitEditMode() {
  state.editingTaskId = null;
  taskForm.reset();
  submitBtn.textContent = "Add Task";
  cancelEditBtn.classList.add("hidden");
}

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const title = titleInput.value.trim();
  const description = descriptionInput.value.trim();

  if (!title) {
    showToast("Task title is required.", "error");
    return;
  }

  try {
    if (state.editingTaskId) {
      await updateTask(state.editingTaskId, {
        title,
        description: description || null,
      });
      showToast("Task updated successfully.");
      exitEditMode();
    } else {
      await createTask(title, description);
      showToast("Task created successfully.");
      taskForm.reset();
    }
    await loadTasks();
  } catch (err) {
    showToast(err.message || "Failed to save task.", "error");
  }
});

cancelEditBtn.addEventListener("click", () => {
  exitEditMode();
});

// ---------------------------------------------------------------------
// Task list interactions (checkbox, edit, delete)
// ---------------------------------------------------------------------
taskListEl.addEventListener("click", async (event) => {
  const li = event.target.closest(".task-item");
  if (!li) return;
  const taskId = li.dataset.id;
  const task = state.tasks.find((t) => t._id === taskId);
  if (!task) return;

  if (event.target.classList.contains("task-checkbox")) {
    try {
      await setTaskCompletion(taskId, event.target.checked);
      showToast(
        event.target.checked ? "Task marked as completed." : "Task marked as active."
      );
      await loadTasks();
    } catch (err) {
      showToast(err.message || "Failed to update task status.", "error");
    }
    return;
  }

  if (event.target.classList.contains("edit-btn")) {
    enterEditMode(task);
    return;
  }

  if (event.target.classList.contains("delete-btn")) {
    openDeleteConfirmation(taskId);
    return;
  }
});

// ---------------------------------------------------------------------
// Delete confirmation modal
// ---------------------------------------------------------------------
function openDeleteConfirmation(taskId) {
  state.pendingDeleteId = taskId;
  confirmModal.classList.remove("hidden");
}

function closeDeleteConfirmation() {
  state.pendingDeleteId = null;
  confirmModal.classList.add("hidden");
}

confirmCancelBtn.addEventListener("click", closeDeleteConfirmation);

confirmModal.addEventListener("click", (event) => {
  if (event.target === confirmModal) closeDeleteConfirmation();
});

confirmDeleteBtn.addEventListener("click", async () => {
  if (!state.pendingDeleteId) return;
  try {
    await deleteTaskRequest(state.pendingDeleteId);
    showToast("Task deleted successfully.");
    if (state.editingTaskId === state.pendingDeleteId) exitEditMode();
    await loadTasks();
  } catch (err) {
    showToast(err.message || "Failed to delete task.", "error");
  } finally {
    closeDeleteConfirmation();
  }
});

// ---------------------------------------------------------------------
// Search
// ---------------------------------------------------------------------
let searchDebounceTimer = null;
searchInput.addEventListener("input", (event) => {
  state.search = event.target.value;
  clearTimeout(searchDebounceTimer);
  searchDebounceTimer = setTimeout(() => {
    loadTasks();
  }, 300);
});

// ---------------------------------------------------------------------
// Filters
// ---------------------------------------------------------------------
filterButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    filterButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    state.filter = btn.dataset.filter;
    loadTasks();
  });
});

// ---------------------------------------------------------------------
// Sort
// ---------------------------------------------------------------------
sortBtn.addEventListener("click", () => {
  state.sort = state.sort === "newest" ? "oldest" : "newest";
  sortBtn.textContent = state.sort === "newest" ? "Sort: Newest First" : "Sort: Oldest First";
  loadTasks();
});

// ---------------------------------------------------------------------
// Initial load
// ---------------------------------------------------------------------
loadTasks();
// End of script.js