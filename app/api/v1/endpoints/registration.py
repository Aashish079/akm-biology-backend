from typing import Any
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core import security
from app.api import deps
from app.services.storage import storage_service
from app.services.email import send_registration_received_email
from app.models import user as models

router = APIRouter()

@router.post("/register")
async def register_student(
    background_tasks: BackgroundTasks,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    location: str = Form(...),
    payment_proof: UploadFile = File(...),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    # Check if user exists
    result = await db.execute(select(models.User).where(models.User.email == email))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
        
    # Create User (Inactive)
    user = models.User(
        email=email,
        hashed_password=security.get_password_hash("temp123"), # Not usable until active
        role=models.UserRole.STUDENT,
        is_active=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create Profile
    profile = models.StudentProfile(
        user_id=user.id,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        location=location
    )
    db.add(profile)
    
    # Save File
    file_path = await storage_service.save_file(payment_proof, directory="payment_proofs")
    
    # Create Payment Proof Record
    proof = models.PaymentProof(
        user_id=user.id,
        file_path=file_path,
        status="pending"
    )
    db.add(proof)
    await db.commit()
    
    # Send Registration Received Email
    background_tasks.add_task(send_registration_received_email, email, f"{first_name} {last_name}")
    
    return {"message": "Registration successful. Please wait for admin approval."}
