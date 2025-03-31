from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict
from app.database import get_db  
from .RolesModels import Role    

router = APIRouter()

def role_as_dict(role: Role) -> Dict:
    """Convert a Role model instance to a dictionary."""
    return role.as_dict()

# GET all roles
@router.get("/roles")
def get_all_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    return {
        "status": 200,
        "roles": [role_as_dict(role) for role in roles]
    }

@router.get("/roles/{role_id}")
def get_role_by_id(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return {
        "status": 200,
        "role": role_as_dict(role)
    }

# POST: Add a new role
@router.post("/roles")
def add_role(data: dict = Body(...), db: Session = Depends(get_db)):
    
    if "title" not in data:
        raise HTTPException(status_code=400, detail="Missing required field: title")
    try:
        new_role = Role(
            title=data.get("title"),
            default_hourly_rate=data.get("default_hourly_rate"),
            default_hourly_cost=data.get("default_hourly_cost")
        )
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        return {
            "status": 200,
            "message": "Role added successfully",
            "role": role_as_dict(new_role)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.put("/roles/{role_id}")
def update_role(role_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    try:
        
        update_fields = ["title", "default_hourly_rate", "default_hourly_cost"]
        for field in update_fields:
            if field in data:
                setattr(role, field, data[field])
        db.commit()
        db.refresh(role)
        return {
            "status": 200,
            "message": "Role updated successfully",
            "role": role_as_dict(role)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    try:
        db.delete(role)
        db.commit()
        return {
            "status": 200,
            "message": "Role deleted successfully"
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
