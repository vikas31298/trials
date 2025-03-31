from sqlalchemy import Column, Integer, Numeric, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {'schema': 'resourcifyschema'}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    default_hourly_rate = Column(Numeric(10, 2), nullable=True)
    default_hourly_cost = Column(Numeric(10, 2), nullable=True)
    
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
