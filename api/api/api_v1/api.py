from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.services.ai_service import AIService
from app.models.match import MatchStatus
from app.models.waste import Waste
from app.models.user import User
from sqlalchemy.orm import Session
from app.db.session import get_db

router = APIRouter()
ai_service = AIService()

@router.post("/matches/find", response_model=List[dict])
async def find_matches(waste_id: int, db: Session = Depends(get_db)):
    """
    Find potential matches for a given waste posting.
    Returns list of potential matches sorted by match score.
    """
    try:
        # Get waste details from database
        waste = db.query(Waste).filter(Waste.id == waste_id).first()
        if not waste:
            raise HTTPException(status_code=404, detail="Waste not found")

        # Get all potential consumers (users looking for this type of waste)
        consumers = db.query(User).filter(
            User.interested_categories.contains([waste.category])
        ).all()

        # Prepare consumer preferences for matching
        consumer_prefs = []
        for consumer in consumers:
            consumer_prefs.append({
                "id": consumer.id,
                "category": waste.category,
                "keywords": consumer.interested_keywords,
                "waste_form": consumer.preferred_waste_form,
                "latitude": consumer.latitude,
                "longitude": consumer.longitude
            })

        # Prepare waste info for matching
        waste_info = {
            "description": waste.description,
            "waste_form": waste.form,
            "latitude": waste.latitude,
            "longitude": waste.longitude
        }

        # Find matches using AI service
        matches = ai_service.find_matches(waste_info, consumer_prefs)

        # Return matches with scores and consumer details
        return [{
            "consumer_id": consumer_id,
            "score": score,
            "consumer": db.query(User).filter(User.id == consumer_id).first().dict(),
            "waste": waste.dict()
        } for score, consumer_id in matches]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
