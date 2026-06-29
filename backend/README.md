# FlipEarn — Backend API

A REST API built with **FastAPI** for the FlipEarn marketplace — a platform where people can buy and sell social media accounts and channels (YouTube, Instagram, TikTok, etc.).

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| FastAPI | Web framework for building the API |
| SQLAlchemy | ORM — talks to the database using Python classes |
| SQLite | Database — stores all data in a local file (`flipearn.db`) |
| Pydantic | Validates incoming and outgoing data |
| Passlib + bcrypt | Hashes passwords securely before storing |
| python-jose | Creates and verifies JWT tokens for authentication |
| Uvicorn | ASGI server — runs the FastAPI app |

---

## Project Structure

```
backend/
├── main.py            # App entry point — starts the server, registers all routes
├── database.py        # Database connection and session setup
├── models.py          # Database tables (User, Listing, Transaction, Withdrawal)
├── schemas.py         # Data shapes for requests and responses (validation)
├── auth.py            # Password hashing and JWT token logic
├── requirements.txt   # All Python dependencies
└── routers/
    ├── auth.py        # Sign up and log in endpoints
    ├── listings.py    # Create, browse, approve, reject listings
    ├── transactions.py# Buy a listing, view purchase history
    ├── withdrawals.py # Seller payout requests, admin review
    ├── users.py       # User profile management, admin user control
    └── dashboard.py   # Live stats for the admin dashboard
```

---

## Getting Started

### 1. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the server

```bash
uvicorn main:app --reload
```

The server runs at `http://localhost:8000`

### 3. Open the interactive API docs

```
http://localhost:8000/docs
```

This gives you a full UI to test every endpoint — no Postman needed.

---

## Database Tables

| Table | What it stores |
|-------|---------------|
| `users` | Everyone who registers (buyers, sellers, admins) |
| `listings` | Social media accounts listed for sale |
| `transactions` | Every purchase ever made on the platform |
| `withdrawals` | Seller payout requests |

---

## API Endpoints

### Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | Create a new account | No |
| POST | `/api/auth/login` | Log in and get a JWT token | No |
| GET | `/api/auth/me` | Get your own profile | Yes |

### Listings
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/listings` | Browse all active listings | No |
| GET | `/api/listings/{id}` | View one listing | No |
| POST | `/api/listings` | Create a new listing | Yes |
| PUT | `/api/listings/{id}` | Edit your listing | Yes |
| DELETE | `/api/listings/{id}` | Remove your listing | Yes |
| GET | `/api/listings/admin/pending` | View pending listings | Admin |
| PUT | `/api/listings/{id}/approve` | Approve a listing | Admin |
| PUT | `/api/listings/{id}/reject` | Reject a listing | Admin |

### Transactions
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/transactions` | Purchase a listing | Yes |
| GET | `/api/transactions` | My purchase history | Yes |
| GET | `/api/transactions/sales` | My sales history | Yes |
| GET | `/api/transactions/{id}` | One transaction detail | Yes |
| GET | `/api/transactions/admin/all` | All transactions | Admin |

### Withdrawals
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/withdrawals/balance` | Check available balance | Yes |
| POST | `/api/withdrawals` | Request a payout | Yes |
| GET | `/api/withdrawals` | My withdrawal history | Yes |
| GET | `/api/withdrawals/admin/all` | All withdrawal requests | Admin |
| PUT | `/api/withdrawals/{id}/review` | Approve or reject a payout | Admin |

### Users
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/users/me` | Get my profile | Yes |
| PUT | `/api/users/me` | Update my profile | Yes |
| GET | `/api/users/me/listings` | My listings as a seller | Yes |
| GET | `/api/users` | List all users | Admin |
| PUT | `/api/users/{id}/ban` | Ban a user | Admin |
| PUT | `/api/users/{id}/unban` | Unban a user | Admin |

### Dashboard
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/dashboard/stats` | Live stats (users, revenue, listings) | Admin |

---

## How Authentication Works

1. **Register** via `POST /api/auth/register`
2. **Login** via `POST /api/auth/login` — you get back a JWT token
3. For protected routes, click **Authorize 🔒** in the docs and paste your token
4. The token lasts **7 days** — after that, log in again to get a new one

---

## User Roles

| Role | What they can do |
|------|----------------|
| `user` | Register, list accounts for sale, browse, buy, request withdrawals |
| `admin` | Everything above + approve/reject listings, manage users, review payouts, see dashboard |

To make a user an admin, run this once:

```bash
python3 -c "
from database import SessionLocal
from models import User
db = SessionLocal()
user = db.query(User).filter(User.email == 'your@email.com').first()
user.role = 'admin'
db.commit()
print('Done')
db.close()
"
```

---

## How a Listing Works (Full Flow)

```
Seller creates listing  →  status: pending
       ↓
Admin reviews it        →  status: active (or rejected)
       ↓
Buyer purchases it      →  status: sold  +  Transaction created
       ↓
Seller requests payout  →  Withdrawal: pending
       ↓
Admin approves payout   →  Withdrawal: approved → completed
```
