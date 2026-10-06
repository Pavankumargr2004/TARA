"""
SQLAlchemy ORM models for the TARA audit database.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class Threat(Base):
    __tablename__ = "threats"

    id = Column(String, primary_key=True, index=True)
    asset = Column(String, index=True)
    boundary = Column(String)
    stride = Column(String)
    mitre = Column(String)
    description = Column(Text)
    attack_path = Column(JSON)
    csr = Column(Text)
    feasibility = Column(String)
    impact = Column(String)
    risk = Column(Integer)
    status = Column(String, default="Pending Review")
    notes = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ReviewAudit(Base):
    __tablename__ = "review_audit"

    id = Column(Integer, primary_key=True, autoincrement=True)
    threat_id = Column(String, index=True)
    reviewer = Column(String, default="Engineer")
    action = Column(String)          # "Approved" or "Rejected"
    rationale = Column(Text)
    timestamp = Column(DateTime, server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="Cybersecurity Engineer")  # System Architect, Cybersecurity Engineer, Lead Security Auditor, Guest Viewer
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())

