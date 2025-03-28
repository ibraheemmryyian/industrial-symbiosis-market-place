from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text
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
    waste_id = Column(Integer, ForeignKey("wastes.id"), nullable=False)
    consumer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_score = Column(Float, nullable=False)  # AI-generated matching score
    status = Column(Enum(MatchStatus), default=MatchStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    waste = relationship("Waste", back_populates="matches")
    consumer = relationship("User", back_populates="matches")
    
    # Match details
    matched_quantity = Column(Float, nullable=True)  # Actual quantity matched (can be less than total)
    matched_unit = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)  # General notes about the match
    
    # Communication
    producer_notes = Column(Text, nullable=True)
    consumer_notes = Column(Text, nullable=True)
    
    # Feedback
    producer_rating = Column(Integer, nullable=True)  # 1-5 rating
    consumer_rating = Column(Integer, nullable=True)  # 1-5 rating
    producer_feedback = Column(Text, nullable=True)
    consumer_feedback = Column(Text, nullable=True)
    
    # AI-related fields
    match_reason = Column(String, nullable=True)  # Explanation of why this match was made
    sustainability_score = Column(Float, nullable=True)  # Environmental impact score
