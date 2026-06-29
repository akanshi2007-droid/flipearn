"""
routers/listings.py — All endpoints for marketplace listings.

A "listing" is a social media account/channel being sold on FlipEarn.
This file handles:
  GET    /api/listings            — browse all active listings (public)
  GET    /api/listings/{id}       — view a single listing (public)
  POST   /api/listings            — seller creates a new listing (login required)
  PUT    /api/listings/{id}       — seller edits their listing (login required)
  DELETE /api/listings/{id}       — seller removes their listing (login required)
  PUT    /api/listings/{id}/approve — admin approves a pending listing
  PUT    /api/listings/{id}/reject  — admin rejects a pending listing
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import models, schemas
from auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/listings", tags=["Listings"])


# =================================================================
# PUBLIC ENDPOINTS — no login needed
# =================================================================

@router.get("", response_model=List[schemas.ListingResponse])
def browse_listings(
    platform: Optional[str] = Query(None, description="Filter by platform, e.g. YouTube"),
    niche:    Optional[str] = Query(None, description="Filter by niche, e.g. Fitness"),
    min_price: Optional[float] = Query(None, description="Minimum asking price"),
    max_price: Optional[float] = Query(None, description="Maximum asking price"),
    skip: int = Query(0,  ge=0,   description="How many listings to skip (for pagination)"),
    limit: int = Query(20, ge=1, le=100, description="How many listings to return at once"),
    db: Session = Depends(get_db)
):
    """
    BROWSE ALL ACTIVE LISTINGS

    Returns listings that are approved and currently available for purchase.
    Supports filtering by platform, niche, and price range.
    Supports pagination with skip + limit (like "give me listings 21-40").
    """
    query = db.query(models.Listing).filter(
        models.Listing.status == models.ListingStatus.active
    )

    # Apply optional filters if the frontend passed them
    if platform:
        query = query.filter(models.Listing.platform.ilike(f"%{platform}%"))
    if niche:
        query = query.filter(models.Listing.niche.ilike(f"%{niche}%"))
    if min_price is not None:
        query = query.filter(models.Listing.asking_price >= min_price)
    if max_price is not None:
        query = query.filter(models.Listing.asking_price <= max_price)

    listings = query.order_by(models.Listing.created_at.desc()).offset(skip).limit(limit).all()

    # Attach the seller's username to each listing for display
    result = []
    for listing in listings:
        data = schemas.ListingResponse.model_validate(listing)
        data.seller_username = listing.seller.username if listing.seller else None
        result.append(data)

    return result


@router.get("/{listing_id}", response_model=schemas.ListingResponse)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    """
    VIEW A SINGLE LISTING

    Fetch all details about one specific listing by its ID.
    Returns 404 if the listing doesn't exist.
    """
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()

    if not listing:
        raise HTTPException(status_code=404, detail=f"No listing found with ID {listing_id}.")

    data = schemas.ListingResponse.model_validate(listing)
    data.seller_username = listing.seller.username if listing.seller else None
    return data


# =================================================================
# SELLER ENDPOINTS — login required
# =================================================================

@router.post("", response_model=schemas.ListingResponse, status_code=201)
def create_listing(
    listing_data: schemas.ListingCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    CREATE A NEW LISTING

    A logged-in user lists their social media account for sale.
    New listings start as "pending" — an admin must approve them before
    they appear publicly in the marketplace.
    """
    new_listing = models.Listing(
        **listing_data.model_dump(),   # unpack all the fields from the request
        seller_id = current_user.id,
        status    = models.ListingStatus.pending,  # starts as pending, not active
    )
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)

    data = schemas.ListingResponse.model_validate(new_listing)
    data.seller_username = current_user.username
    return data


@router.put("/{listing_id}", response_model=schemas.ListingResponse)
def update_listing(
    listing_id: int,
    updates: schemas.ListingUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    UPDATE A LISTING

    The seller can edit their own listing (title, price, description, etc.).
    Admins can also edit any listing (e.g. to update status).
    You cannot edit someone else's listing.
    """
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found.")

    # Only the seller or an admin can edit this listing
    if listing.seller_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only edit your own listings."
        )

    # Only update fields that were actually sent (exclude unset fields)
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(listing, field, value)

    db.commit()
    db.refresh(listing)

    data = schemas.ListingResponse.model_validate(listing)
    data.seller_username = listing.seller.username if listing.seller else None
    return data


@router.delete("/{listing_id}", status_code=204)
def delete_listing(
    listing_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    DELETE A LISTING

    The seller can remove their own listing from the marketplace.
    You can't delete a listing that has already been sold (has a completed transaction).
    """
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found.")

    if listing.seller_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only delete your own listings.")

    if listing.status == models.ListingStatus.sold:
        raise HTTPException(status_code=400, detail="Cannot delete a listing that has already been sold.")

    db.delete(listing)
    db.commit()
    # 204 means "success, nothing to return"


# =================================================================
# ADMIN ENDPOINTS — admin role required
# =================================================================

@router.get("/admin/pending", response_model=List[schemas.ListingResponse])
def get_pending_listings(
    skip: int = 0,
    limit: int = 20,
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    LIST ALL PENDING LISTINGS (Admin only)

    Admins use this to review new listings before they go live.
    """
    listings = db.query(models.Listing).filter(
        models.Listing.status == models.ListingStatus.pending
    ).offset(skip).limit(limit).all()

    result = []
    for listing in listings:
        data = schemas.ListingResponse.model_validate(listing)
        data.seller_username = listing.seller.username if listing.seller else None
        result.append(data)

    return result


@router.put("/{listing_id}/approve", response_model=schemas.ListingResponse)
def approve_listing(
    listing_id: int,
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    APPROVE A LISTING (Admin only)

    Makes a pending listing visible to buyers on the marketplace.
    """
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found.")

    if listing.status != models.ListingStatus.pending:
        raise HTTPException(status_code=400, detail=f"Listing is '{listing.status}', not pending.")

    listing.status = models.ListingStatus.active
    db.commit()
    db.refresh(listing)

    data = schemas.ListingResponse.model_validate(listing)
    data.seller_username = listing.seller.username if listing.seller else None
    return data


@router.put("/{listing_id}/reject", response_model=schemas.ListingResponse)
def reject_listing(
    listing_id: int,
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    REJECT A LISTING (Admin only)

    Marks a listing as rejected — it won't appear publicly.
    """
    listing = db.query(models.Listing).filter(models.Listing.id == listing_id).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found.")

    listing.status = models.ListingStatus.rejected
    db.commit()
    db.refresh(listing)

    data = schemas.ListingResponse.model_validate(listing)
    data.seller_username = listing.seller.username if listing.seller else None
    return data
