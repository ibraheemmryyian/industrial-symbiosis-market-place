from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ARRAY, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
from datetime import datetime

class UserType(enum.Enum):
    PRODUCER = "producer"
    CONSUMER = "consumer"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=True)
    user_type = Column(Enum(UserType), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Matching preferences
    interested_categories = Column(ARRAY(String), default=[], nullable=False)
    interested_keywords = Column(ARRAY(String), default=[], nullable=False)
    preferred_waste_form = Column(String, nullable=True)  # 'material' or 'heat'
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Relationships
    wastes = relationship("Waste", back_populates="producer")
    matches = relationship("WasteMatch", back_populates="consumer")
