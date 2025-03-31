from pydantic import BaseModel
from typing import Optional, List
from datetime import date, timedelta
from sqlalchemy import Column, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
  
class Project(Base):
    __tablename__ = 'projects'
    __table_args__ = {'schema': 'resourcifyschema'}
    id = Column(Integer, primary_key=True, autoincrement=True)
    clientid = Column(Integer)
    name = Column(Text, nullable=False)  # Using Text to match SQL "text"
    holiday_group_id = Column(Integer, default=0)
    currency = Column(Text, default='USD')
    default_pricing_model = Column(Text)  # Adjust as needed
    default_ratecard_id = Column(Text)        # Adjust as needed
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(Text, nullable=False)
    tags = Column(Text)
    primary_team = Column(Text)
    clientid= Column(Integer, default=0)
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}



class ProjectPersonAllocation(Base):
    __tablename__ = "project_person_allocation"
    __table_args__ = {'schema': 'resourcifyschema'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    personid = Column(Integer)
    projectid = Column(Integer)
    start_date = Column(Date)
    end_date = Column(Date)
    dailyhours = Column(Integer)
    
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}




class Skill(BaseModel):
    id: int
    skill_name: str


class Holiday(BaseModel):
    id: int
    occasion: str
    date: date
    duration: str
    holiday_calendar_id: int
    type: str

class HolidayCalendar(BaseModel):
    id: int
    calendar_name: str
    country: str
    zone: Optional[str]
    year: int
