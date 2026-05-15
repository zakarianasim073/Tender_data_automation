from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from ..database.session import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    event = Column(String, index=True)
    actor = Column(String, index=True)
    details = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class License(Base):
    __tablename__ = "licenses"
    key = Column(String, primary_key=True, index=True)
    expiry = Column(DateTime, nullable=False)
    hw_id = Column(String, default="ANY")
    plan = Column(String, default="pro")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
