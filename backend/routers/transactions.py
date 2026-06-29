"""
routers/transactions.py — Buying a listing (purchase flow).

When a buyer clicks "Buy Now", this is what happens on the backend:
  1. Verify the listing is still available.
  2. Create a transaction record (pending).
  3. Mark the listing as "sold" so no one else can buy it.
  4. Mark the transaction as "completed".

Endpoints:
  POST /api/transactions               — buyer purchases a listing
  GET  /api/transactions               — buyer sees their purchase history
  GET  /api/transactions/{id}          — detail of one transaction
  GET  /api/transactions/admin/all     — admin sees all transactions
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas
from auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.post("", response_model=schemas.TransactionResponse, status_code=201)
def purchase_listing(
    purchase: schemas.TransactionCreate,
    buyer: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    BUY A LISTING

    This is the main purchase flow. The buyer sends the listing_id,
    and we:
      1. Check the listing exists and is active (not already sold).
      2. Make sure the buyer isn't trying to buy their own listing.
      3. Create a Transaction record and mark it completed.
      4. Mark the listing as "sold" so no one else can buy it.

    NOTE: In a real app, you'd integrate a payment gateway (Stripe, Razorpay)
    here before marking the transaction as completed. For now, we simulate it.
    """
    # Step 1: Find the listing
    listing = db.query(models.Listing).filter(
        models.Listing.id == purchase.listing_id
    ).first()

    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found.")

    if listing.status != models.ListingStatus.active:
        raise HTTPException(
            status_code=400,
            detail=f"This listing is not available for purchase (status: {listing.status})."
        )

    # Step 2: Can't buy your own listing
    if listing.seller_id == buyer.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot purchase your own listing."
        )

    # Step 3: Create the transaction
    transaction = models.Transaction(
        listing_id = listing.id,
        buyer_id   = buyer.id,
        seller_id  = listing.seller_id,  # copy seller_id for easy querying later
        amount     = listing.asking_price,
        status     = models.TransactionStatus.completed,  # simulated instant payment
    )
    db.add(transaction)

    # Step 4: Mark listing as sold so no one else can buy it
    listing.status = models.ListingStatus.sold

    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("", response_model=List[schemas.TransactionResponse])
def my_purchases(
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    MY PURCHASE HISTORY

    Returns all transactions where the current user is the buyer.
    Ordered newest first.
    """
    transactions = db.query(models.Transaction).filter(
        models.Transaction.buyer_id == current_user.id
    ).order_by(models.Transaction.created_at.desc()).offset(skip).limit(limit).all()

    return transactions


@router.get("/sales", response_model=List[schemas.TransactionResponse])
def my_sales(
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    MY SALES HISTORY

    Returns all transactions where the current user is the seller.
    Sellers use this to see how much they've earned.
    """
    transactions = db.query(models.Transaction).filter(
        models.Transaction.seller_id == current_user.id
    ).order_by(models.Transaction.created_at.desc()).offset(skip).limit(limit).all()

    return transactions


@router.get("/admin/all", response_model=List[schemas.TransactionResponse])
def all_transactions(
    skip: int = 0,
    limit: int = 50,
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    ALL TRANSACTIONS (Admin only)

    Admins can see every transaction ever made on the platform.
    Used for monitoring, dispute resolution, and revenue tracking.
    """
    return db.query(models.Transaction).order_by(
        models.Transaction.created_at.desc()
    ).offset(skip).limit(limit).all()


@router.get("/{transaction_id}", response_model=schemas.TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET ONE TRANSACTION

    View details of a specific transaction.
    You can only see transactions you were part of (as buyer or seller).
    Admins can see any transaction.
    """
    transaction = db.query(models.Transaction).filter(
        models.Transaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    # Regular users can only see their own transactions
    is_involved = (transaction.buyer_id == current_user.id or
                   transaction.seller_id == current_user.id)

    if not is_involved and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this transaction."
        )

    return transaction
