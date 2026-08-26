# Task Master Backend
TaskMaster Backend is a RESTful API built in Python/FastAPI that powers a personal productivity web application. It handles tasks, notes, habits, calendar settings, and user profiles — all scoped to the authenticated user via Supabase JWTs.

## Overview
The backend uses FastAPI as the web framework, SQLAlchemy as the ORM, Alembic for database migrations, psycopg2-binary to connect to a PostgreSQL database hosted on Supabase, and Pydantic for data validation. Every endpoint requires a valid Supabase-issued JWT, which is verified server-side using either HS256 (symmetric) or ES256/RS256 (asymmetric JWKS) depending on the project configuration.

I built this backend to power a task manager web application, and have expanded it over time to add multi-user auth, notes, habit tracking, and account management on top of the original task/tag foundation.

## Features

### Authentication
- **JWT Verification**: All endpoints require a `Bearer` token in the `Authorization` header.
- **Algorithm support**: HS256 (via `SUPABASE_JWT_SECRET`) and asymmetric ES256/RS256 (via the Supabase JWKS endpoint).
- **User isolation**: Every data row is tied to the authenticated user's UUID, so users can never access each other's data.

### Task Management
- **Full CRUD**: Create, read, update, and delete tasks.
- **Toggle completion**: PATCH endpoint to flip completed status (records `completed_date` automatically).
- **Bulk create**: POST an array of tasks at once (`/save-tasks-list`), used by the AI task-plan flow.
- **Task hierarchy**: `parent_task_id` FK for parent-child task decomposition.
- **Task properties**: title, description, category, completed, priority (1–5), due date/time, estimated time (hours), parent task reference, created date, completed date.

### Tag Management
- **Full CRUD**: Create, read, update, and delete tags (per-user).
- **Tag properties**: unique name and optional color.
- **Cross-entity tagging**: Tags can be applied to tasks, notes, and habits via many-to-many join tables.

### Notes Management
- **Full CRUD**: Create, read, update, and delete notes.
- **Note properties**: title, content (rich text), created date, updated date, associated tags.
- **Time tracking**: Note-editing time is tracked via open/close session events (`note_sessions`), not a running counter. Endpoints to start/end a session and to read totals (per-note, all-notes, or over a date range).
- **Stale-session reaping**: `POST /note-session/reap` force-closes any of the user's own sessions left open past a staleness window (crashed tab, force-quit) at zero duration, so a crash doesn't inflate a note's tracked time.

### Habit Tracking
- **Full CRUD**: Create, read, update, and delete habits.
- **Toggle today**: PATCH to mark a habit complete/incomplete for today — updates `current_streak` and `max_streak`.
- **Toggle by date**: PATCH to retroactively toggle any past date — recalculates streaks from scratch.
- **Streak verification**: POST `/verify-streaks` resets `current_streak` to 0 for habits whose last log is older than yesterday.
- **History**: GET 30-day logged/not-logged history for a habit.
- **Habit properties**: title, current streak, max streak, estimated time (hours), associated tags.

### Calendar Settings
- **Get/upsert**: Retrieve or update the authenticated user's calendar display preferences (title, start date, end date).

### Profile
- **Get/upsert**: Retrieve or save the authenticated user's profile data — display name, avatar, theme accent, page style, rest days, day-start/shutoff times, dashboard layout order/sizes, app mode, and other UI preferences.

### Drawing
- **Get/upsert/delete**: A single freeform doodle canvas per user, stored as an image data URL (`GET /get-drawing`, `POST /save-drawing`, `DELETE /delete-drawing`).

### Daily Debrief
- **GET `/daily-debrief`**: Computes a same-day summary for the authenticated user — overdue tasks, tasks due today, tasks completed today, notes worked on today, habit status, workload capacity (committed vs. available minutes, rest-day awareness), and a prioritized "focus next" list. Purely rule-based (no external AI call); accepts the caller's local date/time as query params so a server/client timezone mismatch can't misclassify tasks as overdue.

### Account Management
- **Update password**: POST `/update-password` — enforces a NIST-aligned password policy (12-char minimum, common-password blacklist, no email-in-password). Blocked for OAuth accounts (Google, GitHub, etc.).
- **Delete account**: DELETE `/delete-account` — removes all user data (tasks, notes, tags, habits, profile, drawing, calendar settings) from the database and hard-deletes the Supabase auth record via the Admin API.
- **Claim data**: POST `/claim-data` — one-time migration that assigns any orphaned rows (pre-auth data) to the newly signed-in user.

## Tech Stack
- **Language:** Python
- **Framework:** FastAPI
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Database:** PostgreSQL (hosted on Supabase)
- **Database Driver:** psycopg2-binary
- **Auth:** Supabase JWT (PyJWT + cryptography for ES256/RS256)
- **Data Validation:** Pydantic v2
- **HTTP Client:** httpx (for Supabase Admin API calls)
- **Middleware:** CORS (localhost:3000 + Vercel production URL, configurable via `ALLOWED_ORIGINS`)

## Project Structure
```
taskmaster-backend/
├── Dockerfile
├── alembic.ini
├── requirements.txt
├── alembic/                         # Database migration scripts
│   ├── env.py
│   └── versions/                    # Migration history (tasks, notes, habits, auth, etc.)
└── app/                             # Main application
    ├── main.py                      # FastAPI app, CORS config, router registration
    ├── core/
    │   ├── auth.py                  # JWT verification dependency (HS256 + JWKS)
    │   └── http_utils.py            # require_found() helper (404 on None)
    ├── crud/                        # Data access layer
    │   ├── base.py                  # Shared CRUD helpers
    │   ├── calendar_crud.py
    │   ├── debrief_crud.py
    │   ├── drawing_crud.py
    │   ├── habit_crud.py
    │   ├── note_crud.py
    │   ├── note_session_crud.py
    │   ├── profile_crud.py
    │   ├── tag_crud.py
    │   └── task_crud.py
    ├── database/
    │   └── database.py              # SQLAlchemy engine, session, Base, connection check
    ├── models/                      # SQLAlchemy ORM models
    │   ├── calendar_settings_model.py
    │   ├── drawing_model.py
    │   ├── habit_model.py
    │   ├── habit_log_model.py
    │   ├── habit_tag_model.py       # habits ↔ tags join table
    │   ├── note_model.py
    │   ├── note_session_model.py    # note open/close time-tracking events
    │   ├── note_tag_model.py        # notes ↔ tags join table
    │   ├── profile_model.py
    │   ├── tag_model.py
    │   ├── task_model.py
    │   └── task_tag_model.py        # tasks ↔ tags join table
    ├── routers/                     # FastAPI route handlers
    │   ├── calendar_router.py
    │   ├── debrief_router.py        # Daily debrief summary
    │   ├── drawing_router.py        # Doodle canvas
    │   ├── habits_router.py
    │   ├── notes_router.py          # Notes CRUD + note-session time tracking
    │   ├── profile_router.py
    │   ├── tags_router.py
    │   ├── tasks_router.py
    │   └── user_router.py           # Password update + account deletion
    └── schemas/                     # Pydantic request/response models
        ├── calendar_schema.py
        ├── debrief_schema.py
        ├── drawing_schema.py
        ├── habit_schema.py
        ├── note_schema.py
        ├── note_session_schema.py
        ├── profile_schema.py
        ├── tag_schema.py
        └── task_schema.py
```

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- A Supabase project with a PostgreSQL database
- pip (Python package installer)

### Installation Steps
1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd taskmaster-backend
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   venv\Scripts\activate   # Windows
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the root directory:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   SUPABASE_URL=https://<project-id>.supabase.co
   SUPABASE_JWT_SECRET=<jwt-secret>
   SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
   ```
   All values are available in the Supabase dashboard under **Project Settings → API**.

5. **Run database migrations:**
   ```
   alembic upgrade head
   ```

6. **Run the application:**
   ```
   python -m uvicorn app.main:app --reload
   ```
   The server will start at `http://localhost:8000`.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string (Session-mode pooler URL recommended) |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_JWT_SECRET` | Yes | JWT secret for HS256 token verification |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes (account mgmt) | Service-role key for Admin API calls (password update, account deletion) |
| `SUPABASE_JWKS_URL` | No | Override JWKS endpoint URL (defaults to `{SUPABASE_URL}/auth/v1/.well-known/jwks.json`) |
| `ALLOWED_ORIGINS` | No | Comma-separated list of allowed CORS origins (defaults to `http://localhost:3000,https://kanso-web-app.vercel.app`) |

## API Endpoints

All endpoints require `Authorization: Bearer <supabase-jwt>`. Interactive docs available at `http://localhost:8000/docs`.

### Tasks
| Method | Path | Description |
|---|---|---|
| `GET` | `/get-tasks` | Return all tasks for the authenticated user |
| `POST` | `/create-task` | Create a new task |
| `PUT` | `/update-task/{task_id}` | Replace all fields of a task |
| `PATCH` | `/update-task-status/{task_id}` | Toggle completion status |
| `DELETE` | `/del-task/{task_id}` | Delete a task |
| `POST` | `/save-tasks-list` | Bulk-insert an array of tasks |
| `POST` | `/claim-data` | Assign orphaned rows to the current user (one-time migration) |

### Tags
| Method | Path | Description |
|---|---|---|
| `GET` | `/get-tags` | Return all tags for the authenticated user |
| `POST` | `/create-tags` | Create a new tag |
| `PUT` | `/update-tag/{tag_id}` | Update a tag's name and color |
| `DELETE` | `/del-tag/{tag_id}` | Delete a tag |

### Notes
| Method | Path | Description |
|---|---|---|
| `GET` | `/get-notes` | Return all notes for the authenticated user |
| `POST` | `/create-note` | Create a new note |
| `PUT` | `/update-note/{note_id}` | Update a note's title, content, and tags |
| `DELETE` | `/del-note/{note_id}` | Delete a note |
| `POST` | `/note-session/start` | Start an editing session for a note |
| `PUT` | `/note-session/end/{session_id}` | Close an open editing session |
| `GET` | `/note-session/total/{note_id}` | Total seconds spent on a note (closed sessions) |
| `GET` | `/note-session/totals` | Total seconds spent per note, across all notes |
| `GET` | `/note-session/totals-range?start_date=&end_date=` | Total seconds spent per note within a date range |
| `POST` | `/note-session/reap` | Force-close the user's own stale open sessions |

### Habits
| Method | Path | Description |
|---|---|---|
| `GET` | `/get-habits` | Return all habits with today's completion state |
| `POST` | `/create-habit` | Create a new habit |
| `PUT` | `/update-habit/{habit_id}` | Update a habit's title and tags |
| `DELETE` | `/del-habit/{habit_id}` | Delete a habit and all its logs |
| `PATCH` | `/toggle-habit/{habit_id}` | Toggle today's completion (updates streaks) |
| `PATCH` | `/toggle-habit-date/{habit_id}` | Toggle completion for a specific past date |
| `POST` | `/verify-streaks` | Reset streaks for habits not completed yesterday |
| `GET` | `/habit-history/{habit_id}` | Return 30-day completion history |

### Calendar Settings
| Method | Path | Description |
|---|---|---|
| `GET` | `/get-calendar-settings` | Return the user's calendar settings |
| `PATCH` | `/update-calendar-settings` | Update calendar settings |

### Profile
| Method | Path | Description |
|---|---|---|
| `GET` | `/get-profile` | Return the user's profile |
| `POST` | `/save-profile` | Upsert the user's profile |

### Drawing
| Method | Path | Description |
|---|---|---|
| `GET` | `/get-drawing` | Return the user's saved doodle canvas |
| `POST` | `/save-drawing` | Upsert the doodle canvas |
| `DELETE` | `/delete-drawing` | Delete the doodle canvas |

### Daily Debrief
| Method | Path | Description |
|---|---|---|
| `GET` | `/daily-debrief?local_date=&local_time=` | Return the day's task/habit/workload summary and focus-next recommendations |

### Account Management
| Method | Path | Description |
|---|---|---|
| `POST` | `/update-password` | Update password (email accounts only) |
| `DELETE` | `/delete-account` | Delete all user data (tasks, notes, tags, habits, profile, drawing, calendar settings) and the Supabase auth record |

### Root
| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Welcome message |

## Author
[Luis Fernando Villalon] — Built as a learning project for backend development with FastAPI, extended to include multi-user auth, habit tracking, and account management.
