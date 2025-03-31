from pydantic import BaseModel
from typing import Optional, List
from datetime import date, timedelta

from sqlalchemy import Column, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class Schedule(Base):
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




