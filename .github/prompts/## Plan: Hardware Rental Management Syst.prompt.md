## Plan: Hardware Rental Management System

Build a full-stack web application for managing hardware rentals with admin controls, user rentals, and AI-powered semantic search. Use Python (FastAPI) backend, Vue.js frontend, SQLite database, seeded with provided JSON data.

**Steps**
1. Set up project structure: Create backend (Python/FastAPI), frontend (Vue.js), and database (SQLite) directories.
2. Implement database schema and seed data: Design tables for hardware, users, rentals; import initial_data.json with data cleaning. Handle broken seed data: duplicate IDs - update to first free value; invalid dates - fix to DD-MM-YYYY format; wrong status - normalize to Available, Repair, In Use; drop impossible rows and log warnings.
3. Build Management Engine: Admin command center for hardware management, account creation; login system; smart dashboard with sorting/filtering.
4. Develop Rental Engine: Rent/return API endpoints with business logic guards (e.g., prevent renting unavailable/repair items; ensure no concurrent rentals, first user wins via atomic DB transactions).
5. Integrate AI-Native Layer: Implement semantic search using Gemini API for natural language hardware queries.
6. Develop frontend: Vue.js components for login, dashboard, admin views, rental interface, search. UI should be simple, stylish, exactly like Booksy style.
7. Add authentication and authorization: JWT-based for admin/user roles, with middleware checks on protected endpoints.
8. Implement testing: Write backend test cases focusing on business logic guards and critical features.
9. Polish UI/UX and error handling.

**REST API Endpoints**
- POST /auth/login: User login (returns JWT).
- POST /admin/users: Create new user or admin account (admin only).
- GET /admin/users: See all users and their role user/admin
- POST /admin/hardware: Add new hardware item (admin only).
- DELETE /admin/hardware/{id}: Delete hardware item (admin only).
- PATCH /admin/hardware/{id}/toggle-repair: Toggle repair status (admin only).
- GET /dashboard/hardware: List hardware with filtering/sorting, ability to rent (user/admin).
- POST /dashboard/hardware/{id}/rent: Rent hardware (user).
- POST /dashboard/hardware/{id}/return: Return hardware (user).
- GET /dashboard/user-rentals: List user's rented hardware (user).
- POST /search: Semantic search for hardware using natural language (user/admin).
All endpoints requiring authentication use JWT middleware for role checks (admin/user).

**Backend Test Cases**
- Business Logic Guards: Cannot rent hardware in Repair status; cannot rent already In Use hardware; cannot return hardware not rented by user; prevent concurrent rentals (first user wins via atomic DB update).
- Critical Features: Data import handles duplicates/invalid data correctly; login authenticates users; admin can manage hardware; rent/return updates status and assigns to user.
- Basic Unit Tests: Model validations (e.g., status enum); API response formats; middleware blocks unauthorized access.

**Relevant files**
- [backend/app/main.py](backend/app/main.py) — FastAPI app setup
- [backend/app/models.py](backend/app/models.py) — SQLAlchemy models for hardware, users, rentals
- [backend/app/routes/](backend/app/routes/) — API endpoints for management, rental, search
- [backend/app/middleware.py](backend/app/middleware.py) — JWT authentication middleware
- [frontend/src/](frontend/src/) — Vue components for views
- [data/initial_data.json](data/initial_data.json) — Seed data (already present)
- [tests/](tests/) — Test files

**Verification**
1. Run backend tests: pytest on rental logic, guards, data import.
2. Frontend tests: Vue test utils for components.
3. Manual testing: Login as admin, manage hardware, rent/return, semantic search.
4. API integration tests: Ensure rent/return updates status correctly.

**Decisions**
- Stack: Python/FastAPI backend, Vue.js frontend, SQLite DB (file-based, portable).
- AI: Semantic search with Gemini (requires API key, stored in .env).
- Authentication: JWT for simplicity, with password hashing (bcrypt), JWT expiration (1 hour).
- Data cleaning: Handle duplicates, invalid dates, status normalization; drop invalid rows with logging.
- UI: Exact copy of Booksy style (clean, modern, blue/white theme, simple forms, responsive layout).
- Excluded: Multi-tenancy, advanced reporting (focus on core pillars).

**Database Schema**
- Hardware: id (int, primary), name (str), brand (str), purchase_date (date, DD-MM-YYYY), status (enum: Available, Repair, In Use), notes (str, optional), assigned_to (str, user email, optional).
- Users: id (int, primary), email (str, unique), password_hash (str), role (enum: admin, user).
- Rentals: id (int, primary), hardware_id (int, foreign), user_id (int, foreign), rented_at (datetime), returned_at (datetime, optional).

**Security Considerations**
- Password hashing with bcrypt.
- JWT tokens with expiration and refresh mechanism.
- Input validation and sanitization to prevent injection.
- Rate limiting on API endpoints.
- .env file for secrets, not committed to git (.gitignore).
- CORS enabled for frontend-backend communication.
- HTTPS in production.

**Architectural Issues**
- Separation of concerns: Backend handles API/DB, frontend handles UI.
- No database migrations needed (SQLite, recreate on changes).
- Logging: Use Python logging for data import warnings, API errors.
- Scalability: Suitable for small team, single DB file.
- Error handling: Consistent API responses (JSON with error codes), frontend displays user-friendly messages.
- Concurrency: Atomic DB updates for rentals to prevent race conditions (first user wins).

**Additional Specifications**
- Semantic Search: Use Gemini to generate embeddings for hardware names/brands, store in DB; query with cosine similarity.
- Rental Tracking: Rentals table tracks history; users see only their rentals.
- Frontend: Vue Router for navigation, Pinia for state management, Vite for build.
- Deployment: Backend with uvicorn, frontend built to static files served by backend or separate.
- Build Tools: Poetry for Python deps, npm for Vue.
- Initial Admin: Seed one admin user (e.g., admin@booksy.com).
