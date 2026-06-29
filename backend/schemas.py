"""
schemas.py — The shapes of data coming IN and going OUT of our API.

Think of schemas as contracts:
  - "Request" schemas define what the frontend must send us.
  - "Response" schemas define what we send back to the frontend.

We use Pydantic for this. Pydantic automatically:
  - Validates the data (e.g. email must look like an email)
  - Converts types (e.g. turns "42" into the integer 42)
  - Gives a clear error message if something is wrong

Why keep schemas separate from models?
  → Our database models (models.py) define what's stored in the DB.
  → Schemas define what travels over the network.
  → They're not always the same! (e.g. we NEVER send password_hash to the frontend)
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


# =================================================================
# AUTH SCHEMAS — for signing up and logging in
# =================================================================

class UserRegister(BaseModel):
    """What the frontend sends when a new user signs up."""
    username:  str       = Field(..., min_length=3, max_length=30, description="Unique username, 3-30 chars")
    email:     EmailStr  = Field(..., description="Valid email address")
    password:  str       = Field(..., min_length=6, description="Password, at least 6 characters")
    full_name: Optional[str] = Field(None, max_length=100)

    @field_validator("username")
    @classmethod
    def username_no_spaces(cls, v):
        """Usernames can't have spaces — @john doe is not valid."""
        if " " in v:
            raise ValueError("Username cannot contain spaces")
        return v.lower()  # store usernames in lowercase


class UserLogin(BaseModel):
    """What the frontend sends when a user tries to log in."""
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    """What we send back after a successful login."""
    access_token: str    # the JWT token the frontend will store and send with every request
    token_type:   str = "bearer"
    user_id:      int
    username:     str
    role:         str


# =================================================================
# USER SCHEMAS
# =================================================================

class UserResponse(BaseModel):
    """Safe user data we can send to the frontend (NO password hash!)."""
    id:          int
    username:    str
    email:       str
    full_name:   Optional[str]
    role:        str
    is_active:   bool
    is_verified: bool
    created_at:  datetime

    model_config = {"from_attributes": True}  # lets Pydantic read SQLAlchemy objects


class UserUpdate(BaseModel):
    """What a user sends when they want to edit their profile."""
    full_name: Optional[str] = None
    email:     Optional[EmailStr] = None


# =================================================================
# LISTING SCHEMAS
# =================================================================

class ListingCreate(BaseModel):
    """What a seller sends when they list a new account for sale."""
    title:            str   = Field(..., min_length=5, max_length=150)
    description:      Optional[str] = Field(None, max_length=2000)
    niche:            str   = Field(..., description="e.g. Tech, Fitness, Fashion")
    platform:         str   = Field(..., description="e.g. YouTube, Instagram, TikTok")
    account_username: str   = Field(..., description="The @handle of the account being sold")
    followers_count:  int   = Field(..., ge=0, description="Number of followers/subscribers")
    monthly_revenue:  float = Field(0.0, ge=0, description="Average monthly earnings in USD")
    asking_price:     float = Field(..., gt=0, description="Price in USD — must be greater than 0")
    proof_url:        Optional[str] = Field(None, description="Link to analytics screenshot")


class ListingUpdate(BaseModel):
    """Seller or admin can update a listing — all fields are optional."""
    title:            Optional[str]   = None
    description:      Optional[str]   = None
    asking_price:     Optional[float] = Field(None, gt=0)
    status:           Optional[str]   = None
    proof_url:        Optional[str]   = None


class ListingResponse(BaseModel):
    """Full listing data sent to the frontend."""
    id:               int
    title:            str
    description:      Optional[str]
    niche:            str
    platform:         str
    account_username: str
    followers_count:  int
    monthly_revenue:  float
    asking_price:     float
    status:           str
    proof_url:        Optional[str]
    created_at:       datetime
    seller_id:        int
    seller_username:  Optional[str] = None  # we'll add this when responding

    model_config = {"from_attributes": True}


# =================================================================
# TRANSACTION SCHEMAS
# =================================================================

class TransactionCreate(BaseModel):
    """What the frontend sends when a buyer wants to purchase a listing."""
    listing_id: int = Field(..., description="ID of the listing being purchased")


class TransactionResponse(BaseModel):
    """Transaction details sent back to frontend."""
    id:         int
    amount:     float
    status:     str
    created_at: datetime
    listing_id: int
    buyer_id:   int
    seller_id:  int

    model_config = {"from_attributes": True}


# =================================================================
# WITHDRAWAL SCHEMAS
# =================================================================

class WithdrawalCreate(BaseModel):
    """What a seller sends when requesting a payout."""
    amount:          float  = Field(..., gt=0, description="Amount to withdraw in USD")
    payment_method:  str    = Field(..., description="e.g. bank_transfer, paypal, crypto")
    payment_details: Optional[str] = Field(None, description="PayPal email or bank details")


class WithdrawalUpdate(BaseModel):
    """Admin uses this to approve or reject a withdrawal."""
    status:     str            # "approved", "rejected", or "completed"
    admin_note: Optional[str] = None


class WithdrawalResponse(BaseModel):
    """Withdrawal details sent back to frontend."""
    id:              int
    amount:          float
    status:          str
    payment_method:  str
    payment_details: Optional[str]
    admin_note:      Optional[str]
    created_at:      datetime
    user_id:         int

    model_config = {"from_attributes": True}


# =================================================================
# DASHBOARD SCHEMA
# =================================================================

class DashboardStats(BaseModel):
    """Summary numbers shown at the top of the admin dashboard."""
    total_listings:    int
    active_listings:   int
    total_users:       int
    total_revenue:     float   # sum of all completed transactions
    pending_listings:  int     # awaiting admin review
    pending_withdrawals: int   # awaiting admin approval
