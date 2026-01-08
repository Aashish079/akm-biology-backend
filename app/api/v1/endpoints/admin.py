from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models import user as models
from app.schemas import user as schemas
from app.core import security
from app.services.email import send_welcome_email, send_rejection_email

router = APIRouter()

@router.get("/verifications", response_model=List[schemas.UserResponse])
async def get_pending_verifications(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_admin),
) -> Any:
    # return users where payment proof is pending
    # This join might need optimization but works for small scale
    query = select(models.User).join(models.PaymentProof).where(
        models.PaymentProof.status == models.PaymentStatus.PENDING
    ).options(selectinload(models.User.payment_proof))
    result = await db.execute(query)
    users = result.scalars().all()
    return users

@router.post("/verify/{user_id}")
async def verify_student(
    user_id: UUID,
    background_tasks: BackgroundTasks,
    action: str = "approve", # approve or reject
    reason: str = "",
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_admin),
) -> Any:
    if action not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'.")

    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    result_proof = await db.execute(select(models.PaymentProof).where(models.PaymentProof.user_id == user_id))
    payment_proof = result_proof.scalars().first()
    if not payment_proof:
        raise HTTPException(status_code=404, detail="Payment proof not found")
        
    if payment_proof.status != models.PaymentStatus.PENDING:
        raise HTTPException(
            status_code=400, 
            detail=f"This user has already been processed. Current status: {payment_proof.status}"
        )

    if action == "approve":
        # Generate Creds
        temp_password = security.generate_temp_password()
        hashed = security.get_password_hash(temp_password)
        
        # Update User
        user.hashed_password = hashed
        user.is_active = True
        user.must_change_password = True
        
        # Update Proof
        payment_proof.status = models.PaymentStatus.APPROVED
        
        db.add(user)
        db.add(payment_proof)
        await db.commit()
        
        # Send Email
        background_tasks.add_task(send_welcome_email, user.email, temp_password)
        return {"message": "User approved and email sent."}
        
    elif action == "reject":
        payment_proof.status = models.PaymentStatus.REJECTED
        # Optionally we could delete the user or keep them inactive
        # For now, we keep them inactive
        
        db.add(payment_proof)
        await db.commit()
        
        background_tasks.add_task(send_rejection_email, user.email, reason)
        return {"message": "User rejected and email sent."}

@router.post("/test-email")
async def test_email(email: str = "sandesh@example.com"):
    try:
        await send_welcome_email(email, "TEST_PASSWORD_123")
        return {"message": f"Test email sent to {email}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
