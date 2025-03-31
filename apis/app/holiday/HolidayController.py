
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from datetime import date

from app.database import get_db  
from .HolidayModels import Holiday, HolidayCalendar

router = APIRouter(prefix="/holidays", tags=["Holidays"])


@router.get("/getholidaycalenders")
def get_all_holidaycalendars(db: Session = Depends(get_db)):
    calendars = db.query(HolidayCalendar).all()
    return {
        "status": 200,
        "holidaycalendars": [calendar.as_dict() for calendar in calendars]
    }

@router.get("/holidaycalendars/{calendarid}")
def get_holidaycalendar(calendarid: int, db: Session = Depends(get_db)):
    calendar = db.query(HolidayCalendar).filter(HolidayCalendar.id == calendarid).first()
    if not calendar:
        raise HTTPException(status_code=404, detail="HolidayCalendar not found")
    
    # Retrieve all holidays linked to this holiday calendar
    holidays = db.query(Holiday).filter(Holiday.holiday_calendar_id == calendarid).all()
    
    # Convert holiday objects to dictionaries, ensuring no recursive calls
    holiday_dicts = []
    for holiday in holidays:
        holiday_data = holiday.as_dict()
        # If holiday.as_dict() includes a reference back to the calendar, remove it:
        # holiday_data.pop("holidaycalendar", None)
        holiday_dicts.append(holiday_data)
    
    # Convert the calendar object to a dictionary, ensuring no recursive calls
    calendar_data = calendar.as_dict()
    # If calendar.as_dict() includes a reference to holidays, remove it:
    # calendar_data.pop("holidays", None)
    
    return {
        "status": 200,
        "holidaycalendar": calendar_data,
        "holidays": holiday_dicts
    }


@router.post("/holidaycalenders")
def create_holidaycalendar(data: dict = Body(...), db: Session = Depends(get_db)):
    # Validate required fields
    required_fields = ["calendar_name", "country", "year"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )
    try:
        new_calendar = HolidayCalendar(
            calendar_name = data.get("calendar_name"),
            country = data.get("country"),
            zone = data.get("zone"),
            year = data.get("year")
        )
        db.add(new_calendar)
        db.commit()
        db.refresh(new_calendar)
        return {
            "status": 200,
            "message": "HolidayCalendar created successfully",
            "holidaycalendar": new_calendar.as_dict()
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/holidaycalendars/{calendar_id}")
def update_holidaycalendar(calendar_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    calendar = db.query(HolidayCalendar).filter(HolidayCalendar.id == calendar_id).first()
    if not calendar:
        raise HTTPException(status_code=404, detail="HolidayCalendar not found")
    try:
        update_fields = ["calendar_name", "country", "zone", "year"]
        for field in update_fields:
            if field in data:
                setattr(calendar, field, data[field])
        db.commit()
        db.refresh(calendar)
        return {
            "status": 200,
            "message": "HolidayCalendar updated successfully",
            "holidaycalendar": calendar.as_dict()
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/holidaycalendars/{calendar_id}")
def delete_holidaycalendar(calendar_id: int, db: Session = Depends(get_db)):
    calendar = db.query(HolidayCalendar).filter(HolidayCalendar.id == calendar_id).first()
    if not calendar:
        raise HTTPException(status_code=404, detail="HolidayCalendar not found")
    try:
        db.delete(calendar)
        db.commit()
        return {
            "status": 200,
            "message": "HolidayCalendar deleted successfully"
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


