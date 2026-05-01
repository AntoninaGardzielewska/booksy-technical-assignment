# Hardware Rental Management System

A full-stack web application for managing hardware rentals with admin controls, user rentals, and AI-powered semantic search.

## Live Demo

**URL**: (https://booksy-technical-assignment.vercel.app/admin)

**Demo credentials**:
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@booksy.com | Admin123 |
| User | user@booksy.com | User123 |

> Additional users can only be created through the admin dashboard — there is no public registration.

---

## Features

### Management Engine (Admin & Users)
- **Admin Command Center**: Manage hardware items and create user accounts
- **Login System**: Secure JWT-based authentication
- **Smart Dashboard**: List hardware with sorting and filtering

### Rental Engine (Business Logic)
- **Rent/Return Flow**: Users can rent available gear and return it
- **Business Logic Guards**: Prevents renting unavailable or repair items; concurrent rental prevention (first user wins)
- **Rental Tracking**: Complete history of rentals per user

### AI-Native Layer
- **Gemini Semantic Search**: Natural language hardware search (e.g., "I need something to test a mobile app on")
- **Fallback Keyword Search**: Works without API key if needed

---

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: Vue.js 3 with Vite
- **Database**: SQLite (file-based, portable)
- **Authentication**: JWT tokens with bcrypt password hashing
- **AI**: Google Gemini API for semantic search

---

## Project Structure

```
AI-booksy/
├── backend/                 # FastAPI backend
│   ├── app.db              # SQLite database
│   ├── config.py           # Configuration management
│   ├── database.py         # Database connection
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── security.py         # JWT and password utilities
│   ├── dependencies.py     # Dependency injection
│   ├── seeder.py           # Database seeding with data cleaning
│   ├── main.py             # FastAPI application
│   └── routes/             # API endpoints
│       ├── auth.py         # Authentication
│       ├── admin.py        # Admin management
│       ├── dashboard.py    # User dashboard and rentals
│       └── search.py       # Semantic search
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── api/            # API client and services
│   │   ├── stores/         # Pinia state management
│   │   ├── router/         # Vue Router configuration
│   │   ├── views/          # Vue components (pages)
│   │   ├── App.vue         # Root component
│   │   ├── main.js         # Vue app entry point
│   │   └── style.css       # Global styles
│   ├── index.html          # HTML entry point
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
├── tests/                  # Backend tests
│   ├── conftest.py         # Pytest configuration
│   ├── test_auth.py        # Authentication tests
│   ├── test_rentals.py     # Rental business logic tests
│   ├── test_admin.py       # Admin functionality tests
│   └── test_seeding.py     # Data cleaning tests
├── data/
│   └── initial_data.json   # Initial hardware data
├── .env                    # Environment variables (create from .env.example)
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 16+
- pip and npm

### Backend Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
cp .env .env.local  # Or create your own .env
```

Edit `.env` and set:
- `GEMINI_API_KEY`: Your Google Gemini API key (optional, will use fallback search)
- `JWT_SECRET_KEY`: Change to a secure random string for production
- `DATABASE_URL`: Default is `sqlite:///./app.db`
- `ADMIN_INITIAL_EMAIL`: Email address for the default admin account
- `ADMIN_INITIAL_PASSWORD`: Password for the default admin account

3. **Run the backend:**
```bash
python -m uvicorn backend.main:app --reload
```

Backend will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Install Node dependencies:**
```bash
cd frontend
npm install
```

2. **Run the development server:**
```bash
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

## Database

### Initial Data
The database is automatically seeded with data from `data/initial_data.json` on first startup.

### Data Cleaning
The seeder automatically:
- Fixes duplicate IDs by reassigning them to the first available value
- Validates and converts dates to DD-MM-YYYY format and logs a warning for dates in the future
- Normalizes status values to: `Available`, `In Use`, `Repair`
- Drops rows with missing or unrecoverable required fields (e.g. missing name or brand), and logs a warning for each skipped record

### Reset Database
To reset the database (useful during development):
```bash
# From Python shell
from backend.database import reset_db
reset_db()
```

---

## Testing

Run backend tests with pytest:
```bash
pytest tests/ -v
```

### Test Coverage

**Business Logic Tests:**
- ✅ Cannot rent unavailable hardware
- ✅ Cannot rent hardware in repair
- ✅ Concurrent rental prevention (first user wins)
- ✅ Cannot return hardware not rented by the current user
- ✅ Rental history tracking

**Admin Tests:**
- ✅ Admin can create users
- ✅ Admin can add/delete hardware
- ✅ Admin can toggle repair status
- ✅ Regular users cannot access admin features

**Data Cleaning Tests:**
- ✅ Handles duplicate IDs
- ✅ Fixes invalid dates
- ✅ Normalizes status values
- ✅ Drops invalid rows with logging

**Authentication Tests:**
- ✅ Login success/failure
- ✅ JWT token generation
- ✅ Inactive user blocking
- ✅ Password hashing and verification

---

## API Endpoints

### Authentication
- `POST /auth/login` — User login

### Admin Only
- `POST /admin/users` — Create new user
- `GET /admin/users` — List all users
- `POST /admin/hardware` — Add hardware
- `DELETE /admin/hardware/{id}` — Delete hardware
- `PATCH /admin/hardware/{id}/toggle-repair` — Toggle repair status

### User
- `GET /dashboard/hardware` — List hardware (with filtering/sorting)
- `POST /dashboard/hardware/{id}/rent` — Rent hardware
- `POST /dashboard/hardware/{id}/return` — Return hardware
- `GET /dashboard/user-rentals` — Get current user's rentals
- `POST /search/semantic` — Semantic search for hardware

---

## UI/UX Design

The interface is inspired by Booksy's clean, modern design with:
- Primary color scheme (`#218cac`) for interactive elements
- Navigation bar in dark (`#1b1d21`) for strong contrast
- Light grey (`#f0f0f0`) for sorting controls and secondary UI
- White backgrounds with a minimal, content-first layout
- Clear status indicators and actionable feedback

---

## Implementation Status & Trade-offs

### ✅ Fully Implemented

- **Admin Command Center**: Admins can add and delete hardware, toggle repair status, and create new user accounts. The add forms are hidden by default and expand on button click to keep the UI clean.
- **Login System**: JWT-based authentication with bcrypt password hashing and inactive user blocking.
- **Smart Dashboard**: Hardware list with sorting and filtering by name, brand, status, and purchase date. Filters and search are combined — filters narrow the result set first, then semantic search runs within those results.
- **Rental Engine**: Full rent/return flow with business logic guards — users cannot rent unavailable or repair items, and concurrent rental attempts are handled with a first-come-first-served lock (the first request wins, the second gets a clear error).
- **Rental History**: Complete per-user rental tracking.
- **AI Semantic Search**: Natural language search powered by Google Gemini. The system first checks for direct matches, then uses Gemini for intent-based matching, and falls back to keyword search when no API key is present or when the query is cleared.
- **Data Seeding & Cleaning**: The seeder validates and normalises the initial dataset on startup, handling duplicate IDs, malformed dates, invalid statuses, and missing required fields.
- **Test Suite**: 15+ tests covering authentication, business logic, admin features, and data cleaning.

### ⚡ Shortcuts & Hacks

**Invalid seed data handling — drop and log**

The initial dataset contains records with missing required fields (e.g. a missing brand or a null purchase date). Rather than attempting to infer or repair every edge case, the seeder drops any record it cannot cleanly import and writes a warning to the logger.

- **Why this was acceptable**: For an MVP with a fixed, known seed file, silent rejection with clear logging is a safe and honest strategy. A system admin reviewing the logs will know exactly which records were skipped and why.
- **What I'd do in production**: Depending on the use case, I would do: (a) a data quarantine table where invalid records land for manual review, (b) a migration UI that flags problems and asks an admin to resolve them before import, or (c) automated repair rules with an audit trail (e.g. "brand set to 'Unknown' because field was empty"). The right choice depends on how frequently data is ingested and from which sources.

**Admin credentials via environment variables (vs. a setup wizard)**

The initial admin account is created from `ADMIN_INITIAL_EMAIL` and `ADMIN_INITIAL_PASSWORD` in `.env`. This is better than hardcoding credentials (the AI's original suggestion), but it still means the password lives in a plain-text file on disk.

- **Why this was acceptable**: For a local or review environment, env vars are the standard pragmatic choice and keep credentials out of version control.
- **Future improvement**: In production, use a one-time setup flow (first-run wizard) or inject credentials via a secrets manager (AWS Secrets Manager, HashiCorp Vault, or Railway/Fly.io secret injection), and force a password change on first login.

**Future-dated hardware is imported silently and can be rented**

The seed data includes a Logitech MX Master 3 with a purchase date of 2027-10-10. The seeder's `validate_and_fix_date` only checks that the date string can be parsed into a known format — it does not check whether the date is in the future. The item passes through with a warning, but there is no guard in the rent endpoint that blocks renting items whose purchase date hasn't arrived yet.

- **Why this was acceptable**: The item has `Available` status so it behaves normally in every other way. For an MVP with a known, fixed dataset the risk is minimal and bounded.
- **Future improvement**: Add a future-date check inside `clean_hardware_data` that logs a warning and either drops the item or sets its status to `Pending`. Add a corresponding guard in the rent endpoint (`purchase_date > today` → reject with a clear error message).

**No user or hardware edit endpoints**

Users and hardware items can be created and deleted, but there are no edit endpoints — you cannot update a user's email, change hardware notes, or rename an item without deleting and re-adding it.

- **Why this was acceptable**: The core requirement was add/delete/toggle-repair. Full CRUD was a natural next step that didn't fit within the available time.
- **Future improvement**: Add `PATCH /admin/users/{id}` and `PATCH /admin/hardware/{id}` endpoints with partial update support (Pydantic's `model.model_copy(update=...)` pattern works well here), and expose the corresponding forms in the admin panel.

### ⚠️ Partial / Missing

- **User management**: No ability to deactivate, edit, or delete existing users from the UI.
- **No Docker setup**: The app must be run manually in two separate terminals (backend + frontend).

### 🔮 Next Steps — 24h Roadmap

If I had one more day, my top four priorities would be:

1. **Seeder and initial data management improvements** — Add a future-date check to the seeder, introduce a proper data quarantine flow for unrecoverable records, and expose a simple admin UI for reviewing and resolving import warnings. 

2. **Docker Compose setup** — A single `docker-compose up` that spins up the backend, frontend dev server, and any future services (e.g. a Postgres instance) in one command. This is the biggest quality-of-life improvement for anyone reviewing or deploying the project.

3. **Full user and hardware edit support** — Add `PATCH` endpoints for both resources and the corresponding admin UI forms. This removes the main gap in the Management Engine and makes the system genuinely usable day-to-day.


---

## AI Development Log

### Tooling

- **Claude in VS Code** (the AI chat panel built into VS Code via GitHub Copilot / Claude integration) — used throughout for code generation, refactoring suggestions, and writing tests.
- **Google Gemini API** — integrated as the semantic search backend.
- The AI log can be found in './AI_log.md'


### Data Strategy

The initial seed dataset had several intentional problems: duplicate IDs, a future purchase date (2027), an unknown status value, a missing brand, a null purchase date, and a non-standard date format. The AI helped scaffold the seeder quickly, but I audited each cleaning rule manually to make sure edge cases were handled correctly rather than silently ignored.

One known gap remains: the Logitech MX Master 3 has a purchase date of 2027-10-10. The seeder's date validator only checks that the string is parseable — it has no concept of "future date" — so this item is imported with no warning and no special handling. There is also no rental-time guard blocking a user from renting it. In a production system this would need either a seeder-level check (log a warning, set a `Pending` status) or a rent-endpoint guard (`purchase_date > today` → reject). For this MVP it was left as a documented, known edge case.

### Prompt Trail

The full prompt history that shaped the architecture and design of the system is available in `prompts.md` at the root of this repository. It covers the initial specification sessions, the iterative UI refinement, the search and filter implementation, and the final documentation pass.

### The Correction

The AI's initial approach to bootstrapping the admin account was to hardcode a default email and password directly in the seeder (`admin@booksy.com` / `admin123`). This is a classic security anti-pattern — hardcoded credentials end up in version control and are easy to miss in a security review.

I caught this immediately and redirected: the admin credentials should come from environment variables (`ADMIN_INITIAL_EMAIL`, `ADMIN_INITIAL_PASSWORD`). This way the credentials are never in the codebase, are straightforward to rotate. 

---

## Production Deployment

1. **Update `.env`:**
   - Change `JWT_SECRET_KEY` to a secure random string
   - Set `ENVIRONMENT=production`
   - Add production `CORS_ORIGINS`
   - Configure `GEMINI_API_KEY`
   - Set `ADMIN_INITIAL_EMAIL` and `ADMIN_INITIAL_PASSWORD`

2. **Build frontend:**
   ```bash
   cd frontend
   npm run build
   ```

3. **Run backend:**
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

---

## Troubleshooting

### Gemini API not working
The app will fall back to keyword search if:
- `GEMINI_API_KEY` is not set
- The API key is invalid
- The network request fails

### Database errors
- Delete `backend/app.db` and restart to reset the database
- Check file permissions in the working directory

### CORS errors
- Update `CORS_ORIGINS` in `.env` with your frontend URL
- Ensure the frontend `VITE_API_URL` matches the backend URL

### Port already in use
- Backend default: 8000
- Frontend default: 5173
- Change ports with `--port 9000` (uvicorn) or `--port 3000` (vite)

---

## License

MIT License — feel free to use for any purpose.