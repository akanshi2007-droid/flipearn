"""
routers/auth.py — Sign up and log in endpoints.

These two endpoints are the "front door" of our app:
  POST /api/auth/register — create a new account
  POST /api/auth/login    — get a JWT token to access protected routes

Anyone can call these without being logged in.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models, schemas, auth as auth_utils

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    """
    CREATE A NEW ACCOUNT

    Steps:
      1. Check the username isn't already taken.
      2. Check the email isn't already taken.
      3. Hash the password (never store plain text).
      4. Save the new user to the database.
      5. Return the new user's info (without the password).
    """
    # Step 1: Is the username already taken?
    existing_username = db.query(models.User).filter(
        models.User.username == user_data.username
    ).first()
    if existing_username:
        raise HTTPException(
            status_code=400,
            detail=f"Username '{user_data.username}' is already taken. Please choose another."
        )

    # Step 2: Is the email already registered?
    existing_email = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists. Try logging in instead."
        )

    # Step 3 & 4: Hash password and save user
    new_user = models.User(
        username      = user_data.username,
        email         = user_data.email,
        password_hash = auth_utils.hash_password(user_data.password),
        full_name     = user_data.full_name,
        role          = "user",   # new users are always regular users, not admins
        is_active     = True,
        is_verified   = False,    # email verification would happen separately
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # reload the object from DB so we get the auto-generated id

    return new_user


@router.post("/login", response_model=schemas.TokenResponse)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    LOG IN AND GET A TOKEN

    Steps:
      1. Find the user by email.
      2. Verify the password against the stored hash.
      3. Create a JWT token containing the user's id and role.
      4. Return the token — the frontend stores this and sends it on every request.
    """
    # Step 1: Look up the user
    user = db.query(models.User).filter(models.User.email == credentials.email).first()

    # Step 2: Verify password
    # We use a vague error message on purpose — never tell attackers WHICH part was wrong
    if not user or not auth_utils.verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password."
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Your account has been suspended.")

    # Step 3: Create the JWT token
    # "sub" (subject) is a standard JWT claim — we store the user_id here
    token = auth_utils.create_access_token(data={"sub": str(user.id), "role": user.role})

    # Step 4: Return everything the frontend needs
    return schemas.TokenResponse(
        access_token = token,
        token_type   = "bearer",
        user_id      = user.id,
        username     = user.username,
        role         = user.role,
    )


@router.get("/me", response_model=schemas.UserResponse)
def get_my_profile(current_user: models.User = Depends(auth_utils.get_current_user)):
    """
    GET MY OWN PROFILE

    This is a quick way for the frontend to check:
      "Am I still logged in? Who am I?"

    Requires: valid JWT token in the Authorization header.
    """
    return current_user
