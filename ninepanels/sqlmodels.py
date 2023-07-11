from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, LargeBinary
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    panels = relationship('Panel', back_populates="user")

    MAX_PANELS = 3

    def add_panel(self, panel):
        """ a regular setter method, panel is the Panel instance being added"""

        if len(self.panels) >= self.MAX_PANELS:
            raise ValueError(f"number of panels for a user cannot be greater than {self.MAX_PANELS}")
        else:
            self.panels.append(panel)

class Panel(Base):
    __tablename__ = "panels"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates="panels")

    entries = relationship('Entry', back_populates="panel")

class Entry(Base):
    __tablename__ = "entries"
    id = Column(Integer, primary_key=True)
    is_complete = Column(Boolean)
    timestamp = Column(DateTime)
    panel_id = Column(Integer, ForeignKey('panels.id'))
    panel = relationship('Panel', back_populates="entries")





