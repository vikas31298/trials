from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from app.database import get_db  # Your DB session dependency
from .RateCardModels import RateCard  # Your RateCard model

router = APIRouter()

def ratecard_to_dict(ratecard: RateCard) -> dict:
    return ratecard.as_dict()

@router.get("/ratecards")
def get_all_ratecards(db: Session = Depends(get_db)):
    ratecards = db.query(RateCard).all()
    return {
        "status": 200,
        "ratecards": [ratecard_to_dict(r) for r in ratecards]
    }


@router.get("/ratecards/{ratecard_id}")
def get_ratecard(ratecard_id: int, db: Session = Depends(get_db)):
    ratecard = db.query(RateCard).filter(RateCard.id == ratecard_id).first()
    if not ratecard:
        raise HTTPException(status_code=404, detail="RateCard not found")
    return {
        "status": 200,
        "ratecard": ratecard_to_dict(ratecard)
    }

# POST: Add a new ratecard
@router.post("/ratecards")
def add_ratecard(data: dict = Body(...), db: Session = Depends(get_db)):
    # Validate required fields
    required_fields = ["rate_card_name", "rate_type", "card_type"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )
    try:
        new_ratecard = RateCard(
            rate_card_name = data.get("rate_card_name"),
            description = data.get("description"),
            rate_type = data.get("rate_type"),
            card_type = data.get("card_type"),
            role_wise_rate = data.get("role_wise_rate"),
            external_references = data.get("external_references")
        )
        db.add(new_ratecard)
        db.commit()
        db.refresh(new_ratecard)
        return {
            "status": 200,
            "message": "RateCard added successfully",
            "ratecard": ratecard_to_dict(new_ratecard)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.put("/ratecards/{ratecard_id}")
def update_ratecard(ratecard_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    ratecard = db.query(RateCard).filter(RateCard.id == ratecard_id).first()
    if not ratecard:
        raise HTTPException(status_code=404, detail="RateCard not found")
    try:
        update_fields = [
            "rate_card_name", "description", "rate_type",
            "card_type", "role_wise_rate", "external_references"
        ]
        for field in update_fields:
            if field in data:
                setattr(ratecard, field, data[field])
        db.commit()
        db.refresh(ratecard)
        return {
            "status": 200,
            "message": "RateCard updated successfully",
            "ratecard": ratecard_to_dict(ratecard)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
