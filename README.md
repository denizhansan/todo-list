# To-Do List Web Application

A full-stack, locally-runnable To-Do List web application built as a beginner
DevOps learning project. It is designed from the ground up to be easy to
containerize with **Docker**, orchestrate with **Docker Compose** and
**Kubernetes**, and wire into a **Jenkins CI/CD pipeline** later, without
requiring major refactoring.

## 1. Project Overview

This application lets users create, edit, delete, complete, search, filter,
and sort to-do tasks through a clean, responsive browser-based UI. The
backend is a REST API built with FastAPI and PyMongo, backed by a MongoDB
database. The frontend is built with plain HTML, CSS, and vanilla
JavaScript — no frameworks, no build step — so it can run directly in any
browser via `http://localhost`.

The codebase is intentionally modular: configuration, database access,
data models, and route handlers are each in their own file, which keeps
the project easy to reason about, test, and later split into separate
containers/services.

## 2. Technologies Used

| Layer        | Technology                          |
|--------------|--------------------------------------|
| Backend      | Python 3.12, FastAPI, Uvicorn        |
| Database     | MongoDB                              |
| DB Driver    | PyMongo                              |
| Validation   | Pydantic v2                          |
| Frontend     | HTML5, CSS3, Vanilla JavaScript (Fetch API) |
| Config       | python-dotenv (.env files)           |
| Package mgmt | pip + virtual environment (venv)     |
| Future infra | Docker, Docker Compose, Kubernetes, Jenkins |

## 3. Folder Structure

```text
todo-app/
│
├── backend/
│   ├── main.py            # FastAPI app entrypoint, CORS, lifespan, health check
│   ├── database.py        # PyMongo connection + all DB access logic
│   ├── models.py          # Pydantic request/response schemas
│   ├── routes.py          # /tasks API route handlers
│   ├── config.py          # Environment-based settings
│   └── requirements.txt   # Python dependencies
│
├── frontend/
│   ├── index.html         # App markup
│   ├── style.css          # Responsive, modern minimal styling
│   └── script.js          # Fetch API calls, UI state, DOM rendering
│
├── README.md
├── .gitignore
└── .env                    # Environment variables (DB URI, names, CORS)
```

## 4. Prerequisites

- Python 3.12 installed
- MongoDB installed locally (Community Edition) **or** access to a MongoDB
  instance (e.g., MongoDB Atlas)
- A modern web browser (Chrome, Firefox, Edge, etc.)

## 5. Installation

### 5.1 Clone / download the project

```bash
cd todo-app
```

### 5.2 Create a virtual environment

From inside the `backend/` folder (recommended), or from the project root —
just be consistent with where you run the server from.

**macOS / Linux:**

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**

```powershell
cd backend
py -3.12 -m venv venv
venv\Scripts\Activate.ps1
```

You should see `(venv)` appear in your terminal prompt once activated.

### 5.3 Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 6. Installing and Starting MongoDB Locally

### Option A: Native install

1. Download MongoDB Community Server from the official MongoDB website for
   your operating system.
2. Install it following the platform-specific installer instructions.
3. Start the MongoDB service:

   - **Windows:** MongoDB usually installs as a service and starts
     automatically. You can also start it manually via
     `net start MongoDB`.
   - **macOS (Homebrew):**
     ```bash
     brew tap mongodb/brew
     brew install mongodb-community
     brew services start mongodb-community
     ```
   - **Linux (systemd-based):**
     ```bash
     sudo systemctl start mongod
     sudo systemctl enable mongod
     ```

4. Verify MongoDB is running on its default port `27017`:

   ```bash
   mongosh --eval "db.runCommand({ ping: 1 })"
   ```

### Option B: Run MongoDB via Docker (optional, quick start)

If you already have Docker installed and just want a quick local Mongo
instance without a native install:

```bash
docker run -d --name todo-mongo -p 27017:27017 mongo:7
```

Either option works as long as MongoDB is reachable at the URI configured
in `.env` (`mongodb://localhost:27017` by default).

## 7. Configuration (.env)

The `.env` file at the project root (or copied into `backend/`) contains:

```env
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=todo_app
COLLECTION_NAME=tasks
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost,http://localhost:3000,http://localhost:5500,http://127.0.0.1,http://127.0.0.1:3000,http://127.0.0.1:5500
```

Make sure this `.env` file is accessible from wherever you run
`uvicorn` (typically inside `backend/`, since `config.py` calls
`load_dotenv()` which looks for `.env` in the current working directory
or its parents). If needed, copy `.env` into the `backend/` folder, or
run uvicorn from the project root.

## 8. Running the FastAPI Backend

From inside `backend/` (with the virtual environment activated):

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see output indicating the server is running, e.g.:

```text
Uvicorn running on http://0.0.0.0:8000
```

Verify it's working by visiting:

- API root: http://localhost:8000/
- Health check: http://localhost:8000/health
- Interactive API docs (Swagger UI): http://localhost:8000/docs
- Alternative API docs (ReDoc): http://localhost:8000/redoc

## 9. Opening the Frontend in the Browser

The frontend is static (no build step required). You have two simple
options:

### Option A: Open directly

Double-click `frontend/index.html`, or open it via your browser's
`File > Open` menu.

### Option B: Serve via a simple local web server (recommended)

Serving over HTTP (instead of `file://`) avoids some browser quirks and
better matches how it will run once containerized.

```bash
cd frontend
python -m http.server 5500
```

Then open: http://localhost:5500

> The backend's CORS settings already allow common local origins like
> `http://localhost:5500` and `http://127.0.0.1:5500`. If you serve the
> frontend on a different port, add that origin to `ALLOWED_ORIGINS` in
> `.env` and restart the backend.

## 10. API Documentation

| Method | Endpoint                     | Description                          |
|--------|-------------------------------|---------------------------------------|
| GET    | `/tasks`                      | List tasks (supports `status`, `search`, `sort` query params) |
| GET    | `/tasks/{id}`                 | Get a single task by id              |
| POST   | `/tasks`                      | Create a new task                    |
| PUT    | `/tasks/{id}`                 | Update an existing task (partial)    |
| DELETE | `/tasks/{id}`                 | Delete a task                        |
| PATCH  | `/tasks/{id}/complete`        | Mark a task as completed             |
| PATCH  | `/tasks/{id}/uncomplete`      | Mark a task as active                |
| GET    | `/health`                     | Health check (DB connectivity status)|

### Query parameters for `GET /tasks`

- `status` — `active` or `completed` (omit for all tasks)
- `search` — case-insensitive substring match on task title
- `sort` — `newest` (default) or `oldest`, based on `created_at`

### Example: Create a task

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread"}'
```

### Example: Mark a task as completed

```bash
curl -X PATCH http://localhost:8000/tasks/<task_id>/complete
```

Full interactive documentation (auto-generated by FastAPI) is always
available at **http://localhost:8000/docs** while the backend is running.

## 11. Task Data Model

Each task document stored in MongoDB has the following shape:

```json
{
  "_id": "ObjectId",
  "title": "string",
  "description": "string or null",
  "completed": "boolean",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

## 12. Future Improvements

- **Containerization:** Add a `Dockerfile` for the backend (and optionally
  a lightweight Nginx-based `Dockerfile` for the frontend) plus a
  `docker-compose.yml` that wires together `backend`, `frontend`, and
  `mongo` services.
- **Kubernetes manifests:** Deployments, Services, ConfigMaps/Secrets
  (for `.env` values), and a PersistentVolumeClaim for MongoDB data.
- **CI/CD with Jenkins:** Automated linting, testing, image build/push,
  and deployment pipeline triggered on every commit.
- **Authentication:** User accounts and per-user task lists (JWT-based
  auth).
- **Pagination:** Server-side pagination for large task lists.
- **Unit & integration tests:** Pytest-based backend tests with a test
  database; frontend tests with a tool like Playwright.
- **Due dates & priorities:** Extend the task model with optional due
  dates, priority levels, and tags/categories.
- **Dark mode:** Theme toggle on the frontend.
- **WebSocket live updates:** Real-time task list sync across multiple
  open browser tabs/clients.

## 13. Notes on Future Docker/Kubernetes Readiness

This project was structured with containerization in mind:

- Configuration is fully externalized via environment variables (`.env`),
  so a Docker/K8s ConfigMap or Secret can simply override them.
- The backend exposes a `/health` endpoint suitable for Docker
  `HEALTHCHECK` instructions and Kubernetes liveness/readiness probes.
- The backend and frontend are decoupled (separate folders, communicate
  only via HTTP/Fetch), making it straightforward to build them as two
  independent container images.
- Database logic is isolated in `database.py`, so the MongoDB connection
  string is the only thing that needs to change when MongoDB runs as its
  own container/service (e.g., `mongodb://mongo:27017` inside a Docker
  Compose network instead of `mongodb://localhost:27017`).
