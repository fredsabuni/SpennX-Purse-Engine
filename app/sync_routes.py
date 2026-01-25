"""
Transaction Sync API Routes

Provides endpoints to trigger manual transaction syncs and check sync status.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.database import get_db
from app.transaction_sync import get_sync_service
from app.scheduler import get_scheduler

router = APIRouter(prefix="/api/sync", tags=["Transaction Sync"])


class SyncResponse(BaseModel):
    """Response model for sync operations"""
    success: bool
    message: str
    sync_type: str
    started_at: str
    completed_at: Optional[str] = None
    elapsed_seconds: Optional[float] = None
    inserted: Optional[int] = None
    updated: Optional[int] = None
    total: Optional[int] = None
    date: Optional[str] = None


class SchedulerStatus(BaseModel):
    """Response model for scheduler status"""
    is_running: bool
    jobs: list[dict]


@router.post("/full", response_model=SyncResponse)
async def trigger_full_sync(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger a full sync of all transactions from the external API.
    
    This will fetch all pages of transactions and sync them to the cache database.
    Use this endpoint for initial setup or when you need to refresh all cached data.
    
    **Note:** This operation may take some time depending on the number of transactions.
    """
    try:
        sync_service = get_sync_service()
        result = await sync_service.full_sync(db)
        
        return SyncResponse(
            success=True,
            message="Full sync completed successfully",
            **result
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Full sync failed: {str(e)}"
        )


@router.post("/daily", response_model=SyncResponse)
async def trigger_daily_sync(
    target_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Trigger a daily sync for a specific date (defaults to today).
    
    This endpoint fetches transactions for a specific day and syncs them to the cache.
    The scheduler automatically calls this every 30 minutes for today's date.
    
    **Parameters:**
    - **target_date**: Optional date in YYYY-MM-DD format (defaults to today)
    
    **Example:** `/api/sync/daily?target_date=2026-01-25`
    """
    try:
        sync_service = get_sync_service()
        
        # Parse target date if provided
        parsed_date = None
        if target_date:
            try:
                parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        
        result = await sync_service.daily_sync(db, target_date=parsed_date)
        
        return SyncResponse(
            success=True,
            message=f"Daily sync completed successfully for {result['date']}",
            **result
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Daily sync failed: {str(e)}"
        )


@router.get("/scheduler/status", response_model=SchedulerStatus)
async def get_scheduler_status():
    """
    Get the status of the background scheduler.
    
    Returns information about whether the scheduler is running and what jobs are scheduled.
    """
    scheduler = get_scheduler()
    jobs = []
    
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger)
        })
    
    return SchedulerStatus(
        is_running=scheduler.is_running,
        jobs=jobs
    )


@router.post("/scheduler/start")
async def start_scheduler():
    """
    Start the background scheduler for automatic daily syncs.
    
    The scheduler will run a daily sync every 30 minutes automatically.
    """
    try:
        scheduler = get_scheduler()
        scheduler.start()
        return {
            "success": True,
            "message": "Scheduler started successfully. Daily sync will run every 30 minutes."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start scheduler: {str(e)}"
        )


@router.post("/scheduler/stop")
async def stop_scheduler():
    """
    Stop the background scheduler.
    
    This will prevent automatic daily syncs from running until the scheduler is started again.
    """
    try:
        scheduler = get_scheduler()
        scheduler.stop()
        return {
            "success": True,
            "message": "Scheduler stopped successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop scheduler: {str(e)}"
        )
