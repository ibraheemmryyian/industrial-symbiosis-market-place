from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
from datetime import datetime

class MatchStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"

class WasteMatch(Base):
    __tablename__ = "waste_matches"

    id = Column(Integer, primary_key=True, index=True)
    waste_id = Column(Integer, ForeignKey("wastes.id"))
    consumer_id = Column(Integer, ForeignKey("users.id"))
    match_score = Column(Float, nullable=False)  # AI-generated matching score
    status = Column(Enum(MatchStatus), default=MatchStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    waste = relationship("Waste", back_populates="matches")
    consumer = relationship("User", back_populates="matches")
    
    # AI-related fields
    match_reason = Column(String)  # Explanation of why this match was made
    sustainability_score = Column(Float)  # Environmental impact score 