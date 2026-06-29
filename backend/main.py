"""
main.py — The starting point of our FastAPI backend.

This is the file you run to start the server. It:
  1. Creates the FastAPI app.
  2. Sets up CORS so our React frontend can talk to this backend.
  3. Creates all database tables (if they don't exist yet).
  4. Registers all our routers (auth, listings, transactions, etc.).
  5. Provides a root endpoint for health checks.

TO START THE SERVER:
  cd backend
  pip install -r requirements.txt
  uvicorn main:app --reload

Then open your browser to:
  http://localhost:8000        → welcome message
  http://localhost:8000/docs  → interactive API explorer (Swagger UI)
  http://localhost:8000/redoc → alternative API docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base

# Import all models so SQLAlchemy knows about them when creating tables
import models  # noqa: F401 — this import registers models with Base

# Import all our route modules
from routers import auth, listings, transactions, withdrawals, users, dashboard


# -----------------------------------------------------------------
# 1. Create the FastAPI application instance.
#    The title and description appear in the /docs page.
# -----------------------------------------------------------------
app = FastAPI(
    title       = "FlipEarn API",
    description = """
## Welcome to the FlipEarn Backend API

FlipEarn is a marketplace where people can **buy and sell social media accounts and channels**.

### Who uses this API?
- **Sellers** — list their YouTube/Instagram/TikTok accounts for sale
- **Buyers** — browse and purchase accounts
- **Admins** — review listings, manage users, approve withdrawals

### How authentication works
1. Register via `POST /api/auth/register`
2. Log in via `POST /api/auth/login` → you get a **JWT token**
3. Include the token in the `Authorization: Bearer <token>` header on every protected request
4. Use the **Authorize** button above (🔒) to set your token in this docs page
    """,
    version     = "1.0.0",
)


# -----------------------------------------------------------------
# 2. CORS — Cross-Origin Resource Sharing.
#    Without this, your browser would BLOCK the React frontend
#    (running on localhost:5173) from calling this API (localhost:8000).
#    This setting says: "React is allowed to call us."
# -----------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins  = [
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",   # Create React App dev server
        "https://socialflip.vercel.app",  # production frontend
    ],
    allow_credentials = True,      # allow cookies and auth headers
    allow_methods     = ["*"],     # allow GET, POST, PUT, DELETE, etc.
    allow_headers     = ["*"],     # allow Authorization, Content-Type, etc.
)


# -----------------------------------------------------------------
# 3. Create database tables.
#    This runs once at startup. If tables already exist, it skips them.
#    In production you'd use Alembic migrations instead, but this
#    is perfect for development and demos.
# -----------------------------------------------------------------
@app.on_event("startup")
def create_tables():
    """Create all database tables when the server starts."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created (or already exist).")


# -----------------------------------------------------------------
# 4. Register all routers.
#    Each router handles a group of related endpoints.
#    Adding a router here "plugs in" all its endpoints to the app.
# -----------------------------------------------------------------
app.include_router(auth.router)
app.include_router(listings.router)
app.include_router(transactions.router)
app.include_router(withdrawals.router)
app.include_router(users.router)
app.include_router(dashboard.router)


# -----------------------------------------------------------------
# 5. Root endpoint — quick health check.
#    If someone visits http://localhost:8000 or hits this in a
#    monitoring tool, they'll know the server is up and running.
# -----------------------------------------------------------------
@app.get("/", tags=["Health"])
def root():
    """Server health check — returns a welcome message if the server is running."""
    return {
        "message":    "FlipEarn API is up and running! 🚀",
        "docs":       "/docs",
        "api_prefix": "/api",
        "version":    "1.0.0",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Simple health check for load balancers and monitoring tools."""
    return {"status": "ok"}
