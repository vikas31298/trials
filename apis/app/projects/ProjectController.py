
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from datetime import date

from app.database import get_db  
from .ProjectModels import Project as ProjectModel, ProjectPersonAllocation
from ..schedule import ScheduleModel
from ..person.PersonModels import Person
from ..ratecard.RateCardModels import RateCard

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/getprojects/")
def get_word_counts( db: Session = Depends(get_db)):
    try:
        projects = db.query(ProjectModel).all()
        return {
            "status": 200,
            "message": "Projects retrieved successfully",
            "data": [project.as_dict() for project in projects]
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    finally:
        db.close()


@router.get("/getproject/{projectid}")
def get_project_details(projectid: int, db: Session = Depends(get_db)):
    try:
        # Use filter() instead of filter_by() and retrieve a single project instance
        project = db.query(ProjectModel).filter(ProjectModel.id == projectid).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Ensure that your ProjectModel has an as_dict() method or convert using a Pydantic schema
        return {
            "status": 200,
            "message": "Project details retrieved successfully!",
            "data": project.as_dict()
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/addproject")
def add_project(data: dict = Body(...),   db: Session = Depends(get_db)):
    try:
        
        name = data.get("name")
        # website = data.get("website", "")
        holiday_group = data.get("holiday_group", 0)
        currency = data.get("currency", "USD")
        default_pricing_model = data.get("default_pricing_model")
        default_rate_card = data.get("default_rate_card")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        status = data.get("status")
        tags = data.get("tags")
        primary_team = data.get("primary_team")

        # Validate required fields
        if not all([name, start_date, end_date, status]):
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Convert date strings to `date` objects if needed
        try:
            start_date = date.fromisoformat(start_date) if isinstance(start_date, str) else start_date
            end_date = date.fromisoformat(end_date) if isinstance(end_date, str) else end_date
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

        # Create a new project instance
        new_project = ProjectModel(
            name=name,
            holiday_group=holiday_group,
            currency=currency,
            default_pricing_model=default_pricing_model,
            default_rate_card=default_rate_card,
            start_date=start_date,
            end_date=end_date,
            status=status,
            tags=tags,
            primary_team=primary_team
        )

        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        return {
            "status": 200,
            "message": "Project added successfully",
            "project": new_project.as_dict()  # Using your model's `as_dict()` method
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/addprojects")
def add_projects(data: List[dict] = Body(...), db: Session = Depends(get_db)):
    if len(data) > 100:
        raise HTTPException(status_code=400, detail="Maximum of 100 projects allowed per bulk addition")
    
    required_fields = ["name", "start_date", "end_date", "status"]
    new_projects = []
    
    # Iterate over each project dictionary
    for idx, proj_data in enumerate(data, start=1):
        # Validate required fields
        missing_fields = [field for field in required_fields if field not in proj_data or not proj_data[field]]
        if missing_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Project {idx}: Missing required fields: {', '.join(missing_fields)}"
            )
        
        # Extract and assign values, with defaults if needed
        name = proj_data.get("name")
        holiday_group = proj_data.get("holiday_group", 0)
        currency = proj_data.get("currency", "USD")
        default_pricing_model = proj_data.get("default_pricing_model")
        default_rate_card = proj_data.get("default_rate_card")
        start_date = proj_data.get("start_date")
        end_date = proj_data.get("end_date")
        status = proj_data.get("status")
        tags = proj_data.get("tags")
        primary_team = proj_data.get("primary_team")
        
        # Convert date strings to date objects if necessary
        try:
            start_date = date.fromisoformat(start_date) if isinstance(start_date, str) else start_date
            end_date = date.fromisoformat(end_date) if isinstance(end_date, str) else end_date
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Project {idx}: Invalid date format. Use YYYY-MM-DD.")
        
        # Create a new project instance
        new_project = ProjectModel(
            name=name,
            holiday_group=holiday_group,
            currency=currency,
            default_pricing_model=default_pricing_model,
            default_rate_card=default_rate_card,
            start_date=start_date,
            end_date=end_date,
            status=status,
            tags=tags,
            primary_team=primary_team
        )
        db.add(new_project)
        new_projects.append(new_project)
    
    try:
        db.commit()
        for project in new_projects:
            db.refresh(project)
        return {
            "status": 200,
            "message": f"{len(new_projects)} projects added successfully",
            "projects": [project.as_dict() for project in new_projects]
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



@router.put("/updateproject/{project_id}")
def update_project(project_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    try:
        project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        update_fields = [
            "name",  "holiday_group", "currency", 
            "default_pricing_model", "default_rate_card", 
            "start_date", "end_date", "status", "tags", "primary_team"
        ]
        for field in update_fields:
            if field in data:
                setattr(project, field, data[field])
        
        db.commit()
        db.refresh(project)
        
        return {
            "status": 200,
            "message": "Project updated successfully",
            "project": project.as_dict()
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



    
    

@router.get("/getprojectrevenue/{projectid}")
def get_project_details(projectid: int, db: Session = Depends(get_db)):
    try:
        project = db.query(ProjectModel).filter(ProjectModel.id == projectid).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        
        ratecard = db.query(RateCard).filter(ScheduleModel.projectid == projectid).all()

        
        resources = db.query(ScheduleModel).filter(ScheduleModel.projectid == projectid).all()
        
        return {
            "status": 200,
            "message": "Project details retrieved successfully!",
            "data": project.as_dict()
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")