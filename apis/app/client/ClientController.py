from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict
from app.database import get_db  
from .ClientModels import Client
from ..projects.ProjectModels import Project

router = APIRouter(prefix="/clients", tags=["Clients"])


def client_as_dict(client: Client) -> dict:
    return {
        "id": client.id,
        "name": client.name,
        "website": client.website,
        "isactive": client.isactive
    }


@router.get("/getallclients")
def get_all_clients(db: Session = Depends(get_db)):
    clients = db.query(Client).all()
    return {
        "status": 200,
        "clients": [client_as_dict(client) for client in clients]
    }

@router.get("/getclient/{clientid}")
def get_client_by_id(clientid: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == clientid).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return {
        "status": 200,
        "client": client_as_dict(client)
    }

@router.post("/addclient")
def add_client(data: dict = Body(...), db: Session = Depends(get_db)):
    if "name" not in data:
        raise HTTPException(status_code=400, detail="Missing required field: name")
    
    try:
        new_client = Client(
            name=data.get("name"),
            website=data.get("website"),
            isactive=bool(data.get("isactive", True))  # Ensure BOOLEAN type
        )
        
        db.add(new_client)
        db.commit()
        db.refresh(new_client)
        
        return {
            "status": 200,
            "message": "Client added successfully",
            "client": client_as_dict(new_client)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



# POST: Bulk Add Clients
@router.post("/addclients")
def add_clients(data: dict = Body(...), db: Session = Depends(get_db)):
    if "clients" not in data or not isinstance(data["clients"], list):
        raise HTTPException(status_code=400, detail="Invalid request format. Expected a list of clients.")

    try:
        new_clients = [
            Client(
                name=client["name"],
                website=client.get("website"),
                isactive=bool(client.get("isactive", True))  # Convert to BOOLEAN
            )
            for client in data["clients"]
        ]
        
        db.bulk_save_objects(new_clients)
        db.commit()
        
        return {
            "status": 200,
            "message": f"{len(new_clients)} clients added successfully",
            "clients": [client_as_dict(client) for client in new_clients]
        }
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# PUT: Update an existing client
@router.put("/updateclient/{client_id}")
def update_client(client_id: int, data: dict = Body(...), db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    try:
        if "name" in data:
            client.name = data["name"]
        db.commit()
        db.refresh(client)
        return {
            "status": 200,
            "message": "Client updated successfully",
            "client": client_as_dict(client)
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# DELETE a client
@router.delete("/deleteclient/{clientid}")
def delete_client(clientid: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == clientid).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    try:
        db.delete(client)
        db.commit()
        return {
            "status": 200,
            "message": "Client deleted successfully"
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



@router.get("/getprojects/{clientid}")
def get_project_details(clientid: int, db: Session = Depends(get_db)):
    try:
        projects = db.query(Project).filter(Project.clientid == clientid).all()
        if not projects:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "status": 200,
            "message": "Project details retrieved successfully!",
            "data": [project.as_dict() for project in projects]
        }
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

