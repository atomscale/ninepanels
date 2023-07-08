from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, LargeBinary
from sqlalchemy.orm import relationship

from .database import Base

class Entry(Base):
    __tablename__ = "entries"