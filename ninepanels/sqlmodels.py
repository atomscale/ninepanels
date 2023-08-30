from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)
    hashed_password = Column(String)
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
    created_at = Column(DateTime) # dev None, will be non-nullable
    title = Column(String)
    description = Column(String)
    position = Column(Integer) # dev None, will be non-nullable
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





