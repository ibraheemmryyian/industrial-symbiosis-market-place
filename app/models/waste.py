from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
from datetime import datetime

class WasteType(enum.Enum):
    CHEMICAL = "chemical"
    METAL = "metal"
    PLASTIC = "plastic"
    ORGANIC = "organic"
    ELECTRONIC = "electronic"
    OTHER = "other"

class Waste(Base):
    __tablename__ = "wastes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    waste_type = Column(Enum(WasteType), nullable=False)
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    location = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    producer_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    producer = relationship("User", back_populates="wastes")
    matches = relationship("WasteMatch", back_populates="waste")
    
    # AI-related fields
    embedding = Column(String)  # Store the embedding vector as a string
    keywords = Column(String)  # Store extracted keywords
    category = Column(String)  # AI-categorized waste type 