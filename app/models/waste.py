from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, Enum, Boolean
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

class WasteForm(enum.Enum):
    HEAT = "heat"
    MATERIAL = "material"

class Waste(Base):
    __tablename__ = "wastes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    waste_type = Column(Enum(WasteType), nullable=False)
    waste_form = Column(Enum(WasteForm), nullable=False)  # Indicates if waste is "heat" or "material"
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    location = Column(String(255), nullable=False)  # Human-readable address
    available_from = Column(DateTime, nullable=True)
    available_to = Column(DateTime, nullable=True)
    requires_special_handling = Column(Boolean, default=False, nullable=False)
    special_handling_notes = Column(Text, nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)  # False when matched
    latitude = Column(Float, nullable=True)         # Geographical latitude
    longitude = Column(Float, nullable=True)        # Geographical longitude
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Foreign Keys
    producer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    producer = relationship("User", back_populates="wastes")
    matches = relationship("WasteMatch", back_populates="waste")
    
    # AI-related fields
    embedding = Column(String, nullable=True)  # Store the embedding vector as a JSON string
    keywords = Column(String, nullable=True)   # Store extracted keywords as a comma-separated string
    category = Column(String, nullable=True)     # AI-categorized waste type
