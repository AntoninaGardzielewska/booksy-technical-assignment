# API Documentation

Complete REST API specification for the Hardware Rental Management System.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: (Configure in deployment)

## Authentication

All protected endpoints require a valid JWT token in the `Authorization` header:

```
Authorization: Bearer <jwt_token>
```

Obtain a token by calling `/auth/login` endpoint.

---

## Endpoints

### Authentication

#### POST `/auth/login`
User login - returns JWT token and user info.

**Request:**
```json
{
  "email": "admin@booksy.com",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@booksy.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-04-26T10:00:00"
  }
}
```

**Status Codes:**
- `200 OK` - Login successful
- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - User account inactive

---

### Admin Management

#### POST `/admin/users`
Create a new user account.

**Required Role**: `admin`

**Request:**
```json
{
  "email": "newuser@booksy.com",
  "password": "securepassword123",
  "role": "user"
}
```

**Response (201):**
```json
{
  "id": 2,
  "email": "newuser@booksy.com",
  "role": "user",
  "is_active": true,
  "created_at": "2026-04-26T11:00:00"
}
```

**Status Codes:**
- `201 Created` - User created
- `400 Bad Request` - Email already exists
- `403 Forbidden` - Admin access required

---

#### GET `/admin/users`
List all users in the system.

**Required Role**: `admin`

**Response (200):**
```json
[
  {
    "id": 1,
    "email": "admin@booksy.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-04-26T10:00:00"
  },
  {
    "id": 2,
    "email": "user@booksy.com",
    "role": "user",
    "is_active": true,
    "created_at": "2026-04-26T11:00:00"
  }
]
```

---

#### POST `/admin/hardware`
Add a new hardware item to inventory.

**Required Role**: `admin`

**Request:**
```json
{
  "name": "iPhone 13 Pro Max",
  "brand": "Apple",
  "purchase_date": "23-11-2021",
  "status": "Available",
  "notes": "Perfect condition"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "iPhone 13 Pro Max",
  "brand": "Apple",
  "purchase_date": "23-11-2021",
  "status": "Available",
  "notes": "Perfect condition",
  "assigned_to": null
}
```

**Validation:**
- `name`: 1-255 characters, required
- `brand`: 1-255 characters, required
- `purchase_date`: DD-MM-YYYY format, required
- `status`: Available, In Use, or Repair
- `notes`: 0-500 characters, optional

---

#### DELETE `/admin/hardware/{hardware_id}`
Delete a hardware item.

**Required Role**: `admin`

**Response (204):** No content

**Status Codes:**
- `204 No Content` - Deleted successfully
- `400 Bad Request` - Item is currently in use
- `404 Not Found` - Hardware not found
- `403 Forbidden` - Admin access required

---

#### PATCH `/admin/hardware/{hardware_id}/toggle-repair`
Toggle repair status (Available ↔ Repair).

**Required Role**: `admin`

**Response (200):**
```json
{
  "id": 1,
  "name": "iPhone 13 Pro Max",
  "brand": "Apple",
  "purchase_date": "23-11-2021",
  "status": "Repair",
  "notes": "Screen damaged",
  "assigned_to": null
}
```

---

### Dashboard & Rentals

#### GET `/dashboard/hardware`
List all hardware with filtering, sorting, and pagination.

**Query Parameters:**
- `skip` (int, default: 0) - Pagination offset
- `limit` (int, default: 20, max: 100) - Items per page
- `status_filter` (string) - Filter by status (Available, In Use, Repair)
- `sort_by` (string) - Sort field: name, brand, purchase_date, status

**Example:**
```
GET /dashboard/hardware?skip=0&limit=20&status_filter=Available&sort_by=name
```

**Response (200):**
```json
{
  "items": [
    {
      "id": 1,
      "name": "iPhone 13 Pro Max",
      "brand": "Apple",
      "purchase_date": "23-11-2021",
      "status": "Available",
      "notes": "Perfect condition",
      "assigned_to": null
    }
  ],
  "total": 15,
  "skip": 0,
  "limit": 20
}
```

**Required Role**: `user` or `admin`

---

#### POST `/dashboard/hardware/{hardware_id}/rent`
Rent a hardware item.

**Required Role**: `user`

**Business Logic:**
- Item must have status "Available"
- Only one user can rent the same item (first user wins)
- User is automatically assigned to the item

**Response (201):**
```json
{
  "id": 1,
  "hardware_id": 1,
  "user_id": 2,
  "rented_at": "2026-04-26T12:00:00",
  "returned_at": null,
  "hardware": {...},
  "user": {...}
}
```

**Status Codes:**
- `201 Created` - Rental successful
- `400 Bad Request` - Item not available (in use or repair)
- `404 Not Found` - Hardware not found

---

#### POST `/dashboard/hardware/{hardware_id}/return`
Return a rented hardware item.

**Required Role**: `user`

**Business Logic:**
- User must have an active rental for this item
- Updates item status to "Available"
- Records return timestamp

**Response (200):**
```json
{
  "id": 1,
  "hardware_id": 1,
  "user_id": 2,
  "rented_at": "2026-04-26T12:00:00",
  "returned_at": "2026-04-26T14:30:00",
  "hardware": {...},
  "user": {...}
}
```

**Status Codes:**
- `200 OK` - Return successful
- `404 Not Found` - No active rental found
- `403 Forbidden` - User trying to return someone else's rental

---

#### GET `/dashboard/user-rentals`
Get all rentals (active and returned) for the current user.

**Required Role**: `user`

**Response (200):**
```json
[
  {
    "id": 1,
    "hardware_id": 1,
    "user_id": 2,
    "rented_at": "2026-04-26T12:00:00",
    "returned_at": "2026-04-26T14:30:00",
    "hardware": {...},
    "user": {...}
  }
]
```

---

### Semantic Search

#### POST `/search/semantic`
Search for hardware using natural language (powered by Gemini API).

**Required Role**: `user` or `admin`

**Request:**
```json
{
  "query": "I need something to test a mobile app on"
}
```

**Response (200):**
```json
{
  "results": [
    {
      "id": 1,
      "name": "iPhone 13 Pro Max",
      "brand": "Apple",
      "purchase_date": "23-11-2021",
      "status": "Available",
      "notes": null,
      "assigned_to": null
    },
    {
      "id": 4,
      "name": "Samsung Galaxy S21",
      "brand": "Samsung",
      "purchase_date": "23-11-2021",
      "status": "Available",
      "notes": null,
      "assigned_to": null
    }
  ],
  "query": "I need something to test a mobile app on"
}
```

**Features:**
- Falls back to keyword search if Gemini API is unavailable
- Matches hardware based on semantic relevance
- Returns all available and unavailable items

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Descriptive error message",
  "status_code": 400
}
```

**Common Status Codes:**
- `400 Bad Request` - Invalid input or business logic violation
- `401 Unauthorized` - Invalid or missing authentication token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Rate Limiting

Currently not implemented. Can be added using middleware for production.

---

## CORS Configuration

The API supports CORS for these origins (configurable in `.env`):
- `http://localhost:3000`
- `http://localhost:5173`

Add additional origins to `CORS_ORIGINS` environment variable.

---

## Authentication Flow

1. **Login** → POST `/auth/login`
2. **Store JWT** → Save `access_token` from response
3. **Make requests** → Add `Authorization: Bearer <token>` header
4. **Token expires** → Re-login when token expires (default: 1 hour)

---

## Status Transitions

Valid status transitions:

```
Available ↔ Repair
    ↓
In Use → Available (via return)
```

- Only admins can toggle between Available and Repair
- Rental automatically changes Available → In Use
- Return automatically changes In Use → Available
- Cannot rent items in Repair status

---

## Data Types

### Hardware Status (Enum)
- `Available` - Ready to rent
- `In Use` - Currently rented
- `Repair` - Under maintenance

### User Role (Enum)
- `admin` - Can manage users and hardware
- `user` - Can view and rent hardware

### Date Format
- All dates: `DD-MM-YYYY` (e.g., `23-11-2021`)
- All timestamps: ISO 8601 with UTC timezone

---

## Examples

### Complete Login & Rent Flow

```bash
# 1. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@booksy.com","password":"password123"}'

# Response includes: access_token

# 2. List available hardware
curl -X GET "http://localhost:8000/dashboard/hardware?status_filter=Available" \
  -H "Authorization: Bearer <access_token>"

# 3. Rent an item
curl -X POST http://localhost:8000/dashboard/hardware/1/rent \
  -H "Authorization: Bearer <access_token>"

# 4. Get user rentals
curl -X GET http://localhost:8000/dashboard/user-rentals \
  -H "Authorization: Bearer <access_token>"

# 5. Return item
curl -X POST http://localhost:8000/dashboard/hardware/1/return \
  -H "Authorization: Bearer <access_token>"
```

---

## Testing Endpoints

Interactive API documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Test all endpoints directly in the browser with auto-generated UI.
