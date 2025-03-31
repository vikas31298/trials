from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Date, Interval
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import date, timedelta
from pydantic import BaseModel
from typing import Optional, List

Base = declarative_base()

class Person(Base):
    __tablename__ = "person"
    __table_args__ = {'schema': 'resourcifyschema'}
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    team = Column(String, nullable=True)
    skills = Column(String, nullable=True)
    people_tags = Column(String, nullable=True)
    manager = Column(String, nullable=True)
    links = Column(String, nullable=True)
    external_references = Column(String, nullable=True)
    default_role = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    employment_type = Column(String)
    start_date = Column(Date)
    end_date = Column(Date, nullable=True)
    work_days = Column(String)
    no_of_hours_per_day = Column(Interval)
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


