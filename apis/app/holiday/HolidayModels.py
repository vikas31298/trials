from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, Date, CheckConstraint

Base = declarative_base()

class HolidayCalendar(Base):
    __tablename__ = "holidaycalendars"
    __table_args__ = {'schema': 'resourcifyschema'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    calendar_name = Column(Text, nullable=False)
    country = Column(Text, nullable=False)
    zone = Column(Text, nullable=True)
    year = Column(Integer, nullable=False)
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Holiday(Base):
    __tablename__ = "holidays"
    __table_args__ = (
        CheckConstraint("duration IN ('Full day', 'Half day')", name="holidays_duration_check"),
        CheckConstraint("type IN ('Standard', 'Custom')", name="holidays_type_check"),
        {'schema': 'resourcifyschema'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    occasion = Column(Text, nullable=False)
    date = Column(Date, nullable=False)
    duration = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    holiday_calendar_id = Column(Integer, nullable=False)

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
