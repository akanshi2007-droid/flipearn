"""
routers/dashboard.py — The admin dashboard summary stats.

This file powers the 4 (or more) big number cards you see at the top
of the admin dashboard:
  - Total Listings
  - Active Listings
  - Total Users
  - Total Revenue

These are aggregate queries — they look at ALL records in the database
and return counts and sums, not individual rows.

Endpoints:
  GET /api/dashboard/stats  — returns all summary numbers (admin only)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
import models, schemas
from auth import get_current_admin

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    GET DASHBOARD SUMMARY STATS (Admin only)

    Runs several aggregate queries to count and sum records.
    All these numbers are real-time — calculated fresh on each request.

    Returns:
      - total_listings:      how many listings exist in total
      - active_listings:     how many are currently on sale
      - pending_listings:    how many need admin review
      - total_users:         how many people have registered
      - total_revenue:       sum of all completed purchases (USD)
      - pending_withdrawals: how many payout requests await admin review
    """

    # Count listings by status
    total_listings = db.query(func.count(models.Listing.id)).scalar()

    active_listings = db.query(func.count(models.Listing.id)).filter(
        models.Listing.status == models.ListingStatus.active
    ).scalar()

    pending_listings = db.query(func.count(models.Listing.id)).filter(
        models.Listing.status == models.ListingStatus.pending
    ).scalar()

    # Count total registered users
    total_users = db.query(func.count(models.User.id)).scalar()

    # Sum all money from completed transactions → total platform revenue
    total_revenue = db.query(func.sum(models.Transaction.amount)).filter(
        models.Transaction.status == models.TransactionStatus.completed
    ).scalar() or 0.0   # use 0.0 if there are no transactions yet

    # Count withdrawal requests waiting for admin review
    pending_withdrawals = db.query(func.count(models.Withdrawal.id)).filter(
        models.Withdrawal.status == models.WithdrawalStatus.pending
    ).scalar()

    return schemas.DashboardStats(
        total_listings      = total_listings,
        active_listings     = active_listings,
        pending_listings    = pending_listings,
        total_users         = total_users,
        total_revenue       = round(total_revenue, 2),
        pending_withdrawals = pending_withdrawals,
    )


# Shortcuts to avoid importing through models
ListingStatus     = models.ListingStatus
TransactionStatus = models.TransactionStatus
WithdrawalStatus  = models.WithdrawalStatus
