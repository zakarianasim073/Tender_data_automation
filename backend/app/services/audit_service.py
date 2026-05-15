from datetime import datetime
from sqlalchemy.orm import Session
from ..models.database_models import AuditLog
import logging

logger = logging.getLogger("audit")

def build_audit(db: Session, event: str, actor: str, details: dict):
    try:
        db_audit = AuditLog(
            event=event,
            actor=actor,
            details=details
        )
        db.add(db_audit)
        db.commit()
        db.refresh(db_audit)
        return db_audit
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")
        # Fallback to local logging if DB fails
        return {"error": str(e), "event": event}
