"""
routers/withdrawals.py — Sellers cashing out their earnings.

When a seller's listing gets sold, the money shows up on FlipEarn's platform.
To get actual money in their bank/PayPal, they need to submit a withdrawal request.

Flow:
  Seller submits request → Admin reviews → Admin approves → Money is sent → Completed

Endpoints:
  POST /api/withdrawals                 — seller requests a payout
  GET  /api/withdrawals                 — seller sees their own requests
  GET  /api/withdrawals/admin/all       — admin sees all requests
  PUT  /api/withdrawals/{id}/review     — admin approves or rejects
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas
from auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/withdrawals", tags=["Withdrawals"])


def get_seller_balance(user_id: int, db: Session) -> float:
    """
    Calculate how much a seller has earned but not yet withdrawn.

    Earned = sum of all completed sales
    Withdrawn = sum of all approved/completed withdrawals
    Available = Earned - Withdrawn
    """
    # Total earned from all completed sales
    sales = db.query(models.Transaction).filter(
        models.Transaction.seller_id == user_id,
        models.Transaction.status == models.TransactionStatus.completed
    ).all()
    total_earned = sum(s.amount for s in sales)

    # Total already requested for withdrawal (approved or completed)
    past_withdrawals = db.query(models.Withdrawal).filter(
        models.Withdrawal.user_id == user_id,
        models.Withdrawal.status.in_([
            models.WithdrawalStatus.approved,
            models.WithdrawalStatus.completed
        ])
    ).all()
    total_withdrawn = sum(w.amount for w in past_withdrawals)

    return round(total_earned - total_withdrawn, 2)


@router.post("", response_model=schemas.WithdrawalResponse, status_code=201)
def request_withdrawal(
    withdrawal_data: schemas.WithdrawalCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    REQUEST A PAYOUT

    The seller specifies how much they want to withdraw and via what method.
    We check their available balance first — they can't withdraw more than they've earned.
    The request starts as "pending" for admin to review.
    """
    available_balance = get_seller_balance(current_user.id, db)

    if withdrawal_data.amount > available_balance:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. You have ${available_balance:.2f} available to withdraw."
        )

    new_withdrawal = models.Withdrawal(
        user_id         = current_user.id,
        amount          = withdrawal_data.amount,
        payment_method  = withdrawal_data.payment_method,
        payment_details = withdrawal_data.payment_details,
        status          = models.WithdrawalStatus.pending,
    )
    db.add(new_withdrawal)
    db.commit()
    db.refresh(new_withdrawal)
    return new_withdrawal


@router.get("/balance")
def get_my_balance(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    CHECK MY AVAILABLE BALANCE

    Returns how much the seller has earned and how much they can still withdraw.
    """
    balance = get_seller_balance(current_user.id, db)
    return {
        "user_id":           current_user.id,
        "available_balance": balance,
        "currency":          "USD"
    }


@router.get("", response_model=List[schemas.WithdrawalResponse])
def my_withdrawals(
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    MY WITHDRAWAL HISTORY

    Returns all withdrawal requests made by the current user, newest first.
    """
    return db.query(models.Withdrawal).filter(
        models.Withdrawal.user_id == current_user.id
    ).order_by(models.Withdrawal.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/admin/all", response_model=List[schemas.WithdrawalResponse])
def all_withdrawals(
    status_filter: str = None,
    skip: int = 0,
    limit: int = 50,
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    ALL WITHDRAWAL REQUESTS (Admin only)

    Admin can see all requests. Optionally filter by status:
      ?status_filter=pending    → only show requests awaiting review
      ?status_filter=approved   → already approved
      ?status_filter=completed  → paid out
    """
    query = db.query(models.Withdrawal)

    if status_filter:
        query = query.filter(models.Withdrawal.status == status_filter)

    return query.order_by(models.Withdrawal.created_at.desc()).offset(skip).limit(limit).all()


@router.put("/{withdrawal_id}/review", response_model=schemas.WithdrawalResponse)
def review_withdrawal(
    withdrawal_id: int,
    review: schemas.WithdrawalUpdate,
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    APPROVE OR REJECT A WITHDRAWAL (Admin only)

    Admin reviews the request and either:
      - "approved"  → money will be sent
      - "rejected"  → request denied (admin should add a note explaining why)
      - "completed" → money has been sent out

    The admin can also add a note that the seller will see.
    """
    withdrawal = db.query(models.Withdrawal).filter(
        models.Withdrawal.id == withdrawal_id
    ).first()

    if not withdrawal:
        raise HTTPException(status_code=404, detail="Withdrawal request not found.")

    if withdrawal.status != models.WithdrawalStatus.pending:
        raise HTTPException(
            status_code=400,
            detail=f"This withdrawal is already '{withdrawal.status}' and can't be reviewed again."
        )

    allowed_statuses = ["approved", "rejected", "completed"]
    if review.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Status must be one of: {', '.join(allowed_statuses)}"
        )

    withdrawal.status     = review.status
    withdrawal.admin_note = review.admin_note

    db.commit()
    db.refresh(withdrawal)
    return withdrawal
