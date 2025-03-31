from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Date, Interval,Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import date, timedelta
from pydantic import BaseModel
from typing import Optional, List

Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"
    __table_args__ = {'schema': 'resourcifyschema'}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    website = Column(Text, nullable=True)
    isactive = Column(Boolean, default=True)