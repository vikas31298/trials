from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RateCard(Base):
    __tablename__ = 'ratecards'
    __table_args__ = {'schema': 'resourcifyschema'}    
    id = Column(Integer, primary_key=True, autoincrement=True)
    rate_card_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    rate_type = Column(String, nullable=False)
    card_type = Column(String, nullable=False)
    role_wise_rate = Column(JSON, nullable=True)
    external_references = Column(String, nullable=True)
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}