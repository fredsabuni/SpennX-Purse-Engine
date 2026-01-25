"""
Background Scheduler for Transaction Sync

This module sets up and manages the background task scheduler for periodic
transaction synchronization.
"""

import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.transaction_sync import get_sync_service

logger = logging.getLogger(__name__)


async def scheduled_daily_sync():
    """
    Background task that runs every 30 minutes to sync today's transactions
    """
    logger.info("Starting scheduled daily transaction sync...")
    db = SessionLocal()
    try:
        sync_service = get_sync_service()
        result = await sync_service.daily_sync(db)
        logger.info(f"Scheduled sync completed: {result}")
    except Exception as e:
        logger.error(f"Error in scheduled daily sync: {e}", exc_info=True)
    finally:
        db.close()


class TransactionSyncScheduler:
    """Manages the background scheduler for transaction syncs"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._is_running = False
    
    def start(self):
        """Start the background scheduler"""
        if self._is_running:
            logger.warning("Scheduler is already running")
            return
        
        # Schedule daily sync every 30 minutes
        self.scheduler.add_job(
            scheduled_daily_sync,
            trigger=IntervalTrigger(minutes=30),
            id='daily_transaction_sync',
            name='Daily Transaction Sync (Every 30 minutes)',
            replace_existing=True,
            max_instances=1,  # Prevent overlapping runs
            misfire_grace_time=300  # 5 minutes grace period
        )
        
        self.scheduler.start()
        self._is_running = True
        logger.info("Transaction sync scheduler started - daily sync will run every 30 minutes")
    
    def stop(self):
        """Stop the background scheduler"""
        if not self._is_running:
            logger.warning("Scheduler is not running")
            return
        
        self.scheduler.shutdown()
        self._is_running = False
        logger.info("Transaction sync scheduler stopped")
    
    def get_jobs(self):
        """Get list of scheduled jobs"""
        return self.scheduler.get_jobs()
    
    @property
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self._is_running


# Singleton instance
_scheduler: TransactionSyncScheduler = None


def get_scheduler() -> TransactionSyncScheduler:
    """Get or create the scheduler singleton"""
    global _scheduler
    if _scheduler is None:
        _scheduler = TransactionSyncScheduler()
    return _scheduler
