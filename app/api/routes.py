from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging

from ..database import get_db, SessionLocal
from ..models import Audit
from ..schemas import AuditCreate, AuditResponse
from ..services.lighthouse_service import run_lighthouse_audit
from ..services.security_service import run_security_checks

logger = logging.getLogger(__name__)

router = APIRouter()

async def process_audit(audit_id: int, url: str):
    logger.info(f"Starting audit process for ID {audit_id}, URL: {url}")

    db = SessionLocal()
    try:
        audit = db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            logger.error(f"Audit ID {audit_id} not found in database.")
            return

        # Run lighthouse and security checks concurrently
        # Run lighthouse and security checks concurrently
        import asyncio
        lighthouse_task = asyncio.create_task(run_lighthouse_audit(url))
        security_task = asyncio.create_task(run_security_checks(url))

        lighthouse_results, security_results = await asyncio.gather(lighthouse_task, security_task)

        # Update database with results
        audit.status = "completed"
        audit.performance = lighthouse_results.get("performance")
        audit.accessibility = lighthouse_results.get("accessibility")
        audit.best_practices = lighthouse_results.get("best_practices")
        audit.seo = lighthouse_results.get("seo")
        audit.first_contentful_paint = lighthouse_results.get("first_contentful_paint")
        audit.largest_contentful_paint = lighthouse_results.get("largest_contentful_paint")
        audit.cumulative_layout_shift = lighthouse_results.get("cumulative_layout_shift")

        audit.security_checks = security_results
        db.commit()
        logger.info(f"Audit {audit_id} completed successfully.")

    except Exception as e:
        logger.error(f"Audit {audit_id} failed: {e}")
        # Audit might not have been loaded if DB failed earlier, safely try to fetch
        if 'audit' in locals() and audit:
            audit.status = "failed"
            audit.error_message = str(e)
            db.commit()
    finally:
        db.close()

@router.post("/audits", response_model=AuditResponse, status_code=202)
def create_audit(
    audit_in: AuditCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    url_str = str(audit_in.url)

    # Create initial pending audit record
    new_audit = Audit(url=url_str, status="pending")
    db.add(new_audit)
    db.commit()
    db.refresh(new_audit)

    # Add background task
    background_tasks.add_task(process_audit, new_audit.id, url_str)

    return new_audit

@router.get("/audits", response_model=List[AuditResponse])
def get_audits(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    audits = db.query(Audit).offset(skip).limit(limit).all()
    return audits

@router.get("/audits/{audit_id}", response_model=AuditResponse)
def get_audit(audit_id: int, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return audit
