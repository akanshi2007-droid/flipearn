"""
database.py — The foundation of our backend.

Think of this file like setting up the storage room of a shop.
Before we can store or fetch anything (users, listings, transactions),
we need to tell our app WHERE to save the data and HOW to talk to it.

We're using SQLite here — it's a simple file-based database that lives
right inside our project folder as "flipearn.db". No external server needed.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# -----------------------------------------------------------------
# 1. Tell SQLAlchemy where our database file lives.
#    "sqlite:///./flipearn.db" means: use SQLite, create a file called
#    flipearn.db in the current folder (the backend/ folder).
# -----------------------------------------------------------------
DATABASE_URL = "sqlite:///./flipearn.db"

# -----------------------------------------------------------------
# 2. Create the "engine" — this is the connection to our database.
#    check_same_thread=False is needed only for SQLite so that
#    multiple requests can use the same connection safely.
# -----------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# -----------------------------------------------------------------
# 3. Create a "SessionLocal" factory.
#    Every time we want to talk to the database (read/write data),
#    we open a "session". Think of it like opening a transaction
#    at a bank teller — you do your work, then close the session.
# -----------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,   # We manually commit changes (safer)
    autoflush=False,    # Don't auto-save until we say so
    bind=engine         # Link this session to our database engine
)

# -----------------------------------------------------------------
# 4. Base class for all our models.
#    Every table (User, Listing, Transaction, etc.) will "inherit"
#    from this Base. SQLAlchemy uses it to know what tables to create.
# -----------------------------------------------------------------
Base = declarative_base()


# -----------------------------------------------------------------
# 5. Dependency function for FastAPI routes.
#    FastAPI calls this function automatically before each request.
#    It opens a database session, hands it to the route, and then
#    closes it when the request is done — even if something crashes.
# -----------------------------------------------------------------
def get_db():
    """Open a database session for one request, then close it."""
    db = SessionLocal()
    try:
        yield db           # hand the session to the route
    finally:
        db.close()         # always close, no matter what
