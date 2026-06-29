"""
routers/users.py — User profile management.

After a user signs up (handled in auth.py), they might want to:
  - View their own profile
  - Update their profile info
  - See a list of their own listings

Admins can also:
  - See all users
  - Ban/unban a user

Endpoints:
  GET  /api/users/me               — get my own profile (same as /auth/me)
  PUT  /api/users/me               — update my profile
  GET  /api/users/me/listings      — my listings as a seller
  GET  /api/users                  — list all users (admin only)
  PUT  /api/users/{id}/ban         — ban a user (admin only)
  PUT  /api/users/{id}/unban       — unban a user (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas
from auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=schemas.UserResponse)
def get_my_profile(current_user: models.User = Depends(get_current_user)):
    """
    GET MY PROFILE

    Returns the logged-in user's own profile info.
    """
    return current_user


@router.put("/me", response_model=schemas.UserResponse)
def update_my_profile(
    updates: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    UPDATE MY PROFILE

    Users can update their full_name or email.
    If they change email, we check the new email isn't already taken.
    """
    if updates.email and updates.email != current_user.email:
        # Check new email isn't already used by someone else
        existing = db.query(models.User).filter(models.User.email == updates.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="This email is already in use by another account.")

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/listings", response_model=List[schemas.ListingResponse])
def my_listings(
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    MY LISTINGS (as a seller)

    Returns all listings this user has created, including pending/sold ones.
    Unlike the public browse endpoint, this shows ALL statuses.
    """
    listings = db.query(models.Listing).filter(
        models.Listing.seller_id == current_user.id
    ).order_by(models.Listing.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for listing in listings:
        data = schemas.ListingResponse.model_validate(listing)
        data.seller_username = current_user.username
        result.append(data)

    return result


# =================================================================
# ADMIN ENDPOINTS
# =================================================================

@router.get("", response_model=List[schemas.UserResponse])
def list_all_users(
    skip: int = 0,
    limit: int = 50,
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    LIST ALL USERS (Admin only)

    Admins can see all registered users on the platform.
    """
    return db.query(models.User).order_by(
        models.User.created_at.desc()
    ).offset(skip).limit(limit).all()


@router.put("/{user_id}/ban", response_model=schemas.UserResponse)
def ban_user(
    user_id: int,
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    BAN A USER (Admin only)

    Banning sets is_active=False.
    The user will be blocked from logging in or taking any actions.
    Admins cannot ban other admins.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user.role == "admin":
        raise HTTPException(status_code=403, detail="You cannot ban another admin.")

    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot ban yourself.")

    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}/unban", response_model=schemas.UserResponse)
def unban_user(
    user_id: int,
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    UNBAN A USER (Admin only)

    Restores access for a previously banned user.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    user.is_active = True
    db.commit()
    db.refresh(user)
    return user
