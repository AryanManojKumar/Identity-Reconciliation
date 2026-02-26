from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
from database import Base
import enum

class LinkPrecedence(enum.Enum):
    primary = "primary"
    secondary = "secondary"

class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    phoneNumber = Column(String, nullable=True, index=True)
    email = Column(String, nullable=True, index=True)
    linkedId = Column(Integer, nullable=True, index=True)
    linkPrecedence = Column(Enum(LinkPrecedence), nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deletedAt = Column(DateTime, nullable=True)
