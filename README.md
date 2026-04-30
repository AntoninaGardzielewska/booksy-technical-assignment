# Hardware Rental Management System

A full-stack web application for managing hardware rentals with admin controls, user rentals, and AI-powered semantic search.

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

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: Vue.js 3 with Vite
- **Database**: SQLite (file-based, portable)
- **Authentication**: JWT tokens with bcrypt password hashing
- **AI**: Google Gemini API for semantic search

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

## Database

### Initial Data
The database is automatically seeded with data from `data/initial_data.json` on first startup.

### Data Cleaning
The seeder automatically:
- Fixes duplicate IDs by reassigning them
- Validates and converts dates to DD-MM-YYYY format
- Normalizes status values to: Available, In Use, Repair
- Drops rows with invalid or missing required data
- Logs all warnings during import

### Reset Database
To reset the database (useful during development):
```bash
# From Python shell
from backend.database import reset_db
reset_db()
```

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
- ✅ Cannot return hardware not rented by user
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

## API Endpoints

### Authentication
- `POST /auth/login` - User login

### Admin Only
- `POST /admin/users` - Create new user
- `GET /admin/users` - List all users
- `POST /admin/hardware` - Add hardware
- `DELETE /admin/hardware/{id}` - Delete hardware
- `PATCH /admin/hardware/{id}/toggle-repair` - Toggle repair status

### User
- `GET /dashboard/hardware` - List hardware (with filtering/sorting)
- `POST /dashboard/hardware/{id}/rent` - Rent hardware
- `POST /dashboard/hardware/{id}/return` - Return hardware
- `GET /dashboard/user-rentals` - Get user's rentals
- `POST /search/semantic` - Semantic search for hardware

## Demo Credentials

Default admin account created on first run:
- **Email**: admin@booksy.com
- **Password**: admin123

Create additional users through the admin dashboard.

## UI/UX Design

The interface is inspired by Booksy's clean, modern design with:
- Blue color scheme (`#00B4D8`)
- Simple, intuitive navigation
- Responsive grid-based layouts
- Clear status badges and feedback
- Smooth transitions and hover effects

## Production Deployment

1. **Update .env:**
   - Change `JWT_SECRET_KEY` to a secure random string
   - Set `ENVIRONMENT=production`
   - Add production `CORS_ORIGINS`
   - Configure `GEMINI_API_KEY`

2. **Build frontend:**
   ```bash
   cd frontend
   npm run build
   ```

3. **Run backend with uvicorn:**
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

## Troubleshooting

### Gemini API not working
The app will fall back to keyword search if:
- `GEMINI_API_KEY` is not set
- API key is invalid
- Network request fails

### Database errors
- Delete `backend/app.db` and restart to reset
- Check file permissions in the directory
- Ensure SQLite is installed: `pip install sqlite3`

### CORS errors
- Update `CORS_ORIGINS` in `.env` with your frontend URL
- Ensure frontend `VITE_API_URL` matches backend URL

### Port already in use
- Backend default: 8000
- Frontend default: 5173
- Change ports: `--port 9000` (uvicorn) or `--port 3000` (vite)

## Contributing

When making changes:
1. Write tests for new features
2. Follow the existing code structure
3. Keep API responses consistent
4. Document complex logic with comments

## License

MIT License - Feel free to use for any purpose.
