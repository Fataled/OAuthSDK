from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from database import Base
import uuid
from datetime import datetime

#Remember keywords like unique = constraints
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_admin = Column(Boolean, default=False)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    picture = Column(String)
    hashed_password = Column(String, nullable=True)
    totp_secret = Column(String, nullable=True)
    mfa_enabled = Column(Boolean, nullable=True)
    reset_password_token = Column(String, nullable=True)
    reset_password_expiry = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
