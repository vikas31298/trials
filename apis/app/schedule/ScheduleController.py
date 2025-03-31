from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from datetime import date

from app.database import get_db  
from .ScheduleModel import Schedule
from ..person.PersonModels import Person
from ..projects.ProjectModels import Project

router = APIRouter(prefix="/schedule", tags=["Projects"])


@router.post("/add", response_model=dict)
def create_schedule(schedule: dict, db: Session = Depends(get_db)):
    try:
        new_schedule = Schedule(**schedule)
        db.add(new_schedule)
        db.commit()
        db.refresh(new_schedule)
        return {"status": 201, "message": "Schedule created successfully!", "data": new_schedule.as_dict()}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/getdetails/{schedule_id}")
def get_schedule(schedule_id: int, db: Session = Depends(get_db)):
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return {"status": 200, "message": "Schedule retrieved successfully!", "data": schedule.as_dict()}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/update/{schedule_id}")
def update_schedule(schedule_id: int, schedule_data: dict, db: Session = Depends(get_db)):
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        for key, value in schedule_data.items():
            setattr(schedule, key, value)

        db.commit()
        db.refresh(schedule)
        return {"status": 200, "message": "Schedule updated successfully!", "data": schedule.as_dict()}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/delete/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        db.delete(schedule)
        db.commit()
        return {"status": 200, "message": "Schedule deleted successfully!"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



@router.get("/getresources/{projectid}")
def get_project_details(projectid: int, db: Session = Depends(get_db)):
    try:
        resources = db.query(Schedule).filter(Schedule.projectid == projectid).all()
        if not resources:
            raise HTTPException(status_code=404, detail="No resources are allocated to this project")
        
        result = []
        for resource in resources:
            resource_details = db.query(Person).filter(Person.id == resource.personid).first()
            resource_dict = resource.as_dict() 
            resource_dict['resource'] = resource_details.as_dict() if resource_details else {}
            result.append(resource_dict)
        
        return {
            "status": 200,
            "message": "Project details retrieved successfully!",
            "data": result
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
    
@router.get("/getprojects/{resourceid}")
def get_project_details(resourceid: int, db: Session = Depends(get_db)):
    try:
        allocations = db.query(Schedule).filter(Schedule.personid == resourceid).all()
        if not allocations:
            raise HTTPException(status_code=404, detail="No project allocations are found for this resource")
        
        result = []
        for allocation in allocations:
            project_details = db.query(Project).filter(Project.id == allocation.projectid).first()
            project_dict = project_details.as_dict() 
            project_dict['project'] = project_details.as_dict() if project_details else {}
            result.append(project_details)
        
        return {
            "status": 200,
            "message": "Resource details retrieved successfully!",
            "data": result
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")