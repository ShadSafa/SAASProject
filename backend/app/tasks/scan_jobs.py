"""
Celery scan job tasks.

Phase 3 Plan 4 provides the placeholder execute_scan task so that the API
routes can dispatch scan jobs. Full implementation (Apify calls, viral scoring,
result storage) is wired in Plans 03-03 through 03-06.
"""
import logging
from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.scan_jobs.execute_scan", bind=True, max_retries=3)
def execute_scan(self, scan_id: int) -> dict:
    """
    Execute a viral content scan.

    Dispatched by POST /scans/trigger and POST /scans/analyze-url.
    Full implementation added in Plans 03-03 (Apify) and 03-05 (OpenAI analysis).

    Args:
        scan_id: Primary key of the Scan record to process.

    Returns:
        dict with scan_id and status.
    """
    logger.info(f"execute_scan received scan_id={scan_id} (stub — full implementation in 03-03/03-05)")
    # Placeholder: full implementation will update Scan.status to running/completed/failed
    # and populate ViralPost records via Apify + viral scoring.
    return {"scan_id": scan_id, "status": "pending"}
