from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import enum
import uuid
from app.core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    role = Column(String, default=UserRole.STUDENT)
    is_active = Column(Boolean, default=False) # Inactive until approved
    must_change_password = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    payment_proof = relationship("PaymentProof", back_populates="user", uselist=False)

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    location = Column(String)
    
    user = relationship("User", back_populates="student_profile")

class PaymentProof(Base):
    __tablename__ = "payment_proofs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    file_path = Column(String)
    status = Column(String, default=PaymentStatus.PENDING)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="payment_proof")
