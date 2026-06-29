"""
models.py — The blueprints for our database tables.

Think of each class here as a table in a spreadsheet.
Each attribute (column) is one column in that spreadsheet.
SQLAlchemy reads these classes and creates the actual tables
in our SQLite database when the app starts.

We have 4 tables:
  1. User        — people who use FlipEarn (buyers and sellers)
  2. Listing     — social media accounts/channels listed for sale
  3. Transaction — records of successful purchases
  4. Withdrawal  — when a seller wants to cash out their earnings
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from database import Base


# -----------------------------------------------------------------
# Helper: get current UTC time. Used as a default for created_at.
# -----------------------------------------------------------------
def now_utc():
    return datetime.now(timezone.utc)


# -----------------------------------------------------------------
# ENUM: Status options we'll reuse across multiple tables.
# Using enums prevents typos — you can't accidentally set
# status to "actve" instead of "active".
# -----------------------------------------------------------------

class ListingStatus(str, enum.Enum):
    active   = "active"     # visible on the marketplace
    sold     = "sold"       # already purchased
    pending  = "pending"    # under review before going live
    rejected = "rejected"   # admin rejected it

class TransactionStatus(str, enum.Enum):
    pending   = "pending"   # payment initiated
    completed = "completed" # money moved successfully
    failed    = "failed"    # something went wrong
    refunded  = "refunded"  # buyer got money back

class WithdrawalStatus(str, enum.Enum):
    pending   = "pending"   # seller requested, waiting for admin
    approved  = "approved"  # admin said yes, payout in progress
    rejected  = "rejected"  # admin said no
    completed = "completed" # money sent to seller


# =================================================================
# TABLE 1: User
# Every person who signs up on FlipEarn gets a row in this table.
# =================================================================
class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, index=True)
    username     = Column(String, unique=True, index=True, nullable=False)
    email        = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)   # NEVER store plain passwords
    full_name    = Column(String, nullable=True)
    role         = Column(String, default="user")    # "user" or "admin"
    is_active    = Column(Boolean, default=True)     # False = banned account
    is_verified  = Column(Boolean, default=False)    # email verified?
    created_at   = Column(DateTime(timezone=True), default=now_utc)

    # ---- Relationships ----
    # One user can have many listings (they're a seller)
    listings     = relationship("Listing", back_populates="seller", foreign_keys="Listing.seller_id")
    # One user can make many purchases (they're a buyer)
    purchases    = relationship("Transaction", back_populates="buyer", foreign_keys="Transaction.buyer_id")
    # One user can request many withdrawals
    withdrawals  = relationship("Withdrawal", back_populates="user")

    def __repr__(self):
        return f"<User id={self.id} username={self.username} role={self.role}>"


# =================================================================
# TABLE 2: Listing
# Each social media account/channel listed for sale is one row here.
# =================================================================
class Listing(Base):
    __tablename__ = "listings"

    id              = Column(Integer, primary_key=True, index=True)
    title           = Column(String, nullable=False)          # e.g. "Tech YouTube Channel"
    description     = Column(String, nullable=True)           # seller's pitch
    niche           = Column(String, nullable=False)          # e.g. "Tech", "Fitness"
    platform        = Column(String, nullable=False)          # YouTube, Instagram, TikTok, etc.
    account_username = Column(String, nullable=False)         # the @handle of the account
    followers_count = Column(Integer, default=0)              # how many followers/subscribers
    monthly_revenue = Column(Float, default=0.0)              # how much it earns per month ($)
    asking_price    = Column(Float, nullable=False)           # what the seller wants ($)
    status          = Column(String, default=ListingStatus.pending) # pending/active/sold/rejected
    proof_url       = Column(String, nullable=True)           # screenshot or analytics link
    created_at      = Column(DateTime(timezone=True), default=now_utc)

    # ---- Foreign Keys ----
    # Which user is selling this account?
    seller_id       = Column(Integer, ForeignKey("users.id"), nullable=False)

    # ---- Relationships ----
    seller          = relationship("User", back_populates="listings", foreign_keys=[seller_id])
    transaction     = relationship("Transaction", back_populates="listing", uselist=False)

    def __repr__(self):
        return f"<Listing id={self.id} title={self.title} status={self.status}>"


# =================================================================
# TABLE 3: Transaction
# When a buyer purchases a listing, we record it here.
# This is our audit trail — we never delete these rows.
# =================================================================
class Transaction(Base):
    __tablename__ = "transactions"

    id          = Column(Integer, primary_key=True, index=True)
    amount      = Column(Float, nullable=False)               # price paid ($)
    status      = Column(String, default=TransactionStatus.pending)
    created_at  = Column(DateTime(timezone=True), default=now_utc)

    # ---- Foreign Keys ----
    listing_id  = Column(Integer, ForeignKey("listings.id"), nullable=False)
    buyer_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    seller_id   = Column(Integer, ForeignKey("users.id"), nullable=False)  # denormalized for speed

    # ---- Relationships ----
    listing     = relationship("Listing", back_populates="transaction")
    buyer       = relationship("User", back_populates="purchases", foreign_keys=[buyer_id])
    seller      = relationship("User", foreign_keys=[seller_id])

    def __repr__(self):
        return f"<Transaction id={self.id} amount=${self.amount} status={self.status}>"


# =================================================================
# TABLE 4: Withdrawal
# When a seller earns money from a sale, they request a payout here.
# Admin reviews and approves/rejects each request.
# =================================================================
class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id             = Column(Integer, primary_key=True, index=True)
    amount         = Column(Float, nullable=False)            # how much they want to withdraw ($)
    status         = Column(String, default=WithdrawalStatus.pending)
    payment_method = Column(String, nullable=False)           # e.g. "bank_transfer", "paypal"
    payment_details = Column(String, nullable=True)           # e.g. PayPal email or bank account
    admin_note     = Column(String, nullable=True)            # reason for approval/rejection
    created_at     = Column(DateTime(timezone=True), default=now_utc)

    # ---- Foreign Keys ----
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False)

    # ---- Relationships ----
    user           = relationship("User", back_populates="withdrawals")

    def __repr__(self):
        return f"<Withdrawal id={self.id} amount=${self.amount} status={self.status}>"
