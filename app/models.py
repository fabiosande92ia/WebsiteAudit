from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from datetime import datetime, timezone
from .database import Base

class Audit(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    status = Column(String, default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Lighthouse Metrics
    performance = Column(Float, nullable=True)
    accessibility = Column(Float, nullable=True)
    best_practices = Column(Float, nullable=True)
    seo = Column(Float, nullable=True)
    first_contentful_paint = Column(Float, nullable=True)
    largest_contentful_paint = Column(Float, nullable=True)
    cumulative_layout_shift = Column(Float, nullable=True)

    # Security Metrics (JSON for flexibility)
    security_checks = Column(JSON, nullable=True)

    # Error message if failed
    error_message = Column(String, nullable=True)
