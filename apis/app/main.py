import os
from fastapi import FastAPI, HTTPException, Request, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from urllib.parse import urlparse

from .config import ALLOWED_HOSTS
from .database import get_db  


from .projects.ProjectController import router as project_router
from .person.PersonController import router as person_router
from .client.ClientController import router as client_router
from .ratecard.RateCardController import router as rate_card_router
from .schedule.ScheduleController import router as schedule_router
from .roles.RolesController import router as roles_router
from .holiday.HolidayController import router as holiday_router


from .reports.ResourceUtilization import router as resource_report_router


from .analytics.SQLChatController import router as sql_chat_router

app = FastAPI()
router = APIRouter()

@router.get("/")
async def get_pmi_topics():
    return JSONResponse(
            content={"message": "Successfully fetched topics", "status": 200},
            status_code=200
        )
    


app.include_router(router)
app.include_router(project_router)
app.include_router(person_router)
app.include_router(client_router)
app.include_router(rate_card_router)
app.include_router(roles_router)
app.include_router(schedule_router)
app.include_router(holiday_router)
app.include_router(resource_report_router)



app.include_router(sql_chat_router)


# Run using:
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
# uvicorn app.main:app --reload
