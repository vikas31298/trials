from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
from datetime import date, timedelta

from app.database import get_db  
from .PersonModels import Person 
router = APIRouter(prefix="/person", tags=["Person"])

@router.get("/getallpersons")
def get_all_persons(db: Session = Depends(get_db)):
    persons = db.query(Person).all()
    return {
        "status": 200,
        "total": len(persons),
        "persons": [person.as_dict() for person in persons]
    }

@router.get("/getperson/{personid}")
def get_person_by_id(personid: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == personid).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return {
        "status": 200,
        "person": person.as_dict()
    }

@router.post("/addperson")
def add_person(data: dict = Body(...), db: Session = Depends(get_db)):
    required_fields = [
        "first_name", "last_name", "email",
        "employment_type", "start_date", "work_days", "no_of_hours_per_day"
    ]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )
    try:
        new_person = Person(
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            team=data.get("team"),
            skills=data.get("skills"),
            people_tags=data.get("people_tags"),
            manager=data.get("manager"),
            links=data.get("links"),
            external_references=data.get("external_references"),
            default_role=data.get("default_role"),
            job_title=data.get("job_title"),
            employment_type=data.get("employment_type"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            work_days=data.get("work_days"),
            no_of_hours_per_day=data.get("no_of_hours_per_day")
        )
        db.add(new_person)
        db.commit()
        db.refresh(new_person)
        return {
            "status": 200,
            "message": "Person added successfully",
            "person": new_person.as_dict()
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



@router.post("/addpersons")
def add_persons(data: List[dict] = Body(...), db: Session = Depends(get_db)):
    
    if len(data) > 100:
        raise HTTPException(status_code=400, detail="Maximum of 100 persons allowed per bulk addition")
    
    required_fields = [
        "first_name", "last_name", "email",
        "employment_type", "start_date", "work_days", "no_of_hours_per_day"
    ]
    
    created_persons = []
    
    # Loop through each person in the provided list
    for idx, person_data in enumerate(data, start=1):
        missing_fields = [field for field in required_fields if field not in person_data]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Person {idx}: Missing required fields: {', '.join(missing_fields)}"
            )
        new_person = Person(
            first_name=person_data.get("first_name"),
            last_name=person_data.get("last_name"),
            email=person_data.get("email"),
            team=person_data.get("team"),
            skills=person_data.get("skills"),
            people_tags=person_data.get("people_tags"),
            manager=person_data.get("manager"),
            links=person_data.get("links"),
            external_references=person_data.get("external_references"),
            default_role=person_data.get("default_role"),
            job_title=person_data.get("job_title"),
            employment_type=person_data.get("employment_type"),
            start_date=person_data.get("start_date"),
            end_date=person_data.get("end_date"),
            work_days=person_data.get("work_days"),
            no_of_hours_per_day=person_data.get("no_of_hours_per_day")
        )
        db.add(new_person)
        created_persons.append(new_person)
    
    try:
        db.commit()
        # Refresh each instance to retrieve updated values (like auto-generated IDs)
        for person in created_persons:
            db.refresh(person)
        return {
            "status": 200,
            "message": f"{len(created_persons)} persons added successfully",
            "persons": [person.as_dict() for person in created_persons]
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



@router.put("/update/{personid}")
def update_person(personid: int, data: dict = Body(...), db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == personid).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    try:
        update_fields = [
            "first_name", "last_name", "email", "team", "skills", "people_tags",
            "manager", "links", "external_references", "default_role",
            "job_title", "employment_type", "start_date", "end_date", "work_days",
            "no_of_hours_per_day"
        ]
        for field in update_fields:
            if field in data:
                setattr(person, field, data[field])
        db.commit()
        db.refresh(person)
        return {
            "status": 200,
            "message": "Person updated successfully",
            "person": person.as_dict()
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.delete("/persons/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    try:
        db.delete(person)
        db.commit()
        return {
            "status": 200,
            "message": "Person deleted successfully"
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
