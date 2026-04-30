# Quick Start Guide

Get the Hardware Rental Management System running in 5 minutes!

## Option 1: Quick Setup (Copy & Paste)

### Terminal 1: Start Backend

```bash
cd /AI-booksy

# Install dependencies (first time only)
pip install -r requirements.txt

# Run backend
python -m uvicorn backend.main:app --reload
```

✅ Backend running at: **http://localhost:8000**

### Terminal 2: Start Frontend

```bash
cd /home/antonina/AI-booksy/frontend

# Install dependencies (first time only)
npm install

# Run frontend
npm run dev
```

✅ Frontend running at: **http://localhost:5173**

## Step 1: Access the Application

Open your browser and go to: **http://localhost:5173**

## Step 2: Login

Use the default admin credentials:
- **Email**: admin@booksy.com
- **Password**: admin123

## Step 3: Explore Features

### For Admin:
1. Go to **Admin** tab
2. **Create new users** - Add test users to the system
3. **Manage Hardware** - Add, delete, or repair hardware items
4. **Toggle repair status** - Mark items as needing repair

### For Users:
1. **Dashboard** - Browse all available hardware
   - Filter by status
   - Sort by name, brand, date, or status
   - Use **semantic search** for natural language queries (e.g., "I need a phone")
   
2. **Rent Hardware** - Click "Rent Now" on available items
3. **My Rentals** - View rental history and return items

## Step 4: Test API (Optional)

### Interactive API Docs
Go to: **http://localhost:8000/docs**

### Sample Requests

**Login:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@booksy.com","password":"admin123"}'
```

**List Hardware:**
```bash
curl -X GET "http://localhost:8000/dashboard/hardware" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Running Tests

```bash
cd /home/antonina/AI-booksy
pytest tests/ -v
```

Expected output:
- ✅ 10+ authentication tests
- ✅ 8+ rental business logic tests  
- ✅ 7+ admin functionality tests
- ✅ 6+ data seeding tests

## Troubleshooting

### Backend won't start
```bash
# Make sure port 8000 is free
lsof -i :8000

# Or use a different port
python -m uvicorn backend.main:app --port 9000 --reload
```

### Frontend won't start
```bash
cd frontend
npm install  # Reinstall node_modules
npm run dev  # Try again
```

### Database issues
```bash
# Delete and recreate database
rm backend/app.db
python -m uvicorn backend.main:app --reload
```

### Can't login
1. Check that backend is running (`http://localhost:8000/docs`)
2. Verify email is `admin@booksy.com`
3. Verify password is `admin123`

## Next Steps

1. **Create test users** in Admin panel
2. **Add sample hardware** to the inventory
3. **Rent as different users** to test concurrent rental prevention
4. **Use semantic search** to find items by description

## File Structure Reference

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app entry point |
| `backend/models.py` | Database models (Hardware, User, Rental) |
| `backend/routes/` | API endpoints |
| `frontend/src/views/` | Vue page components |
| `frontend/src/api/` | Backend API client |
| `tests/` | Unit and integration tests |
| `.env` | Configuration (API keys, secrets) |

## Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=sqlite:///./app.db

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_EXPIRATION_HOURS=1

# Gemini API (optional, fallback to keyword search)
GEMINI_API_KEY=your-gemini-api-key-here

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Environment
ENVIRONMENT=development
```

## Key Features Implemented

✅ **Three Pillars Complete:**
1. ✅ Management Engine - Admin and user controls
2. ✅ Rental Engine - Business logic with guards
3. ✅ AI-Native Layer - Gemini semantic search

✅ **Database:**
- Automatic data cleaning (duplicate IDs, invalid dates)
- Status normalization
- Invalid row detection and logging

✅ **Security:**
- JWT authentication
- Password hashing (bcrypt)
- Role-based access control
- Protected API endpoints

✅ **Testing:**
- 31+ test cases
- Business logic guards
- Data integrity
- Concurrent rental prevention

✅ **UI/UX:**
- Booksy-inspired design
- Responsive layout
- Real-time updates
- Clear error messages

## Support

For issues or questions, check the main [README.md](./README.md) for detailed information.
