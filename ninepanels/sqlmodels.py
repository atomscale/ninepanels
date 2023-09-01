from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Index
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
    password_reset_tokens = relationship('PasswordResetToken', back_populates="user")

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

class BlacklistedAccessToken(Base):
    __tablename__ = "blacklisted_access_tokens"
    id = Column(Integer, primary_key=True)
    access_token = Column(String, unique=True)
    blacklisted_at = Column(DateTime)

Index('access_token_index', BlacklistedAccessToken.access_token)

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True)
    password_reset_token = Column(String, unique=True, nullable=False)
    issued_at = Column(DateTime, nullable=False)
    expiry = Column(DateTime, nullable=False)
    is_valid = Column(Boolean, default=True)
    invalidated_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship('User', back_populates="password_reset_tokens")
