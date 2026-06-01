import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings

# Create engine - supports SQLite locally and PostgreSQL/MySQL in production on Alibaba Cloud
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AnomalyRecord(Base):
    __tablename__ = "anomalies"

    id = Column(String, primary_key=True, index=True)
    instance_id = Column(String, index=True, nullable=False)
    service_type = Column(String, default="ECS")
    metric_name = Column(String, nullable=False)
    severity = Column(String, default="warning")
    current_value = Column(Float, nullable=False)
    baseline_value = Column(Float, nullable=False)
    root_cause = Column(Text, nullable=False)
    impact_description = Column(Text, nullable=False)
    remediation_action = Column(Text, nullable=False)
    estimated_monthly_savings = Column(Float, nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow)


class ProposedFixRecord(Base):
    __tablename__ = "proposed_fixes"

    id = Column(String, primary_key=True, index=True)
    anomaly_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    files_to_modify = Column(Text, nullable=False)  # Stored as comma-separated string
    diff_content = Column(Text, nullable=False)
    pr_url = Column(String, nullable=True)
    pr_number = Column(Integer, nullable=True)
    status = Column(String, default="pending")  # pending, approved, rejected, deploying, deployed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)


class ConfigurationSetting(Base):
    __tablename__ = "configuration_settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """Initializes all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for retrieving database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
