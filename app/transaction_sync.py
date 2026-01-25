"""
Transaction Cache Sync Module

This module handles synchronization of transaction data from the external SpennX API
to the local cache database. It supports both full syncs and daily incremental syncs.
"""

import httpx
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import insert
from app.database import get_db
from app.models import TransactionCache
from app.config import settings

logger = logging.getLogger(__name__)


class TransactionSyncService:
    """Service for syncing transactions from external API to cache database"""
    
    BASE_URL = "https://app.spennx.com/api/v1/globaltransactions"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
    
    async def fetch_transactions(
        self, 
        day: Optional[str] = None,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Fetch transactions from the external API
        
        Args:
            day: Optional date filter in format YYYY-MM-DD
            page: Page number for pagination
            
        Returns:
            Dict containing data, links, and meta information
        """
        params = {"page": page}
        if day:
            params["day"] = day
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    self.BASE_URL,
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"HTTP error fetching transactions: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error fetching transactions: {e}")
                raise
    
    async def fetch_all_pages(self, day: Optional[str] = None) -> List[Dict]:
        """
        Fetch all pages of transactions
        
        Args:
            day: Optional date filter in format YYYY-MM-DD
            
        Returns:
            List of all transaction records
        """
        all_transactions = []
        current_page = 1
        
        while True:
            logger.info(f"Fetching page {current_page} for day={day or 'all'}")
            response = await self.fetch_transactions(day=day, page=current_page)
            
            transactions = response.get("data", [])
            all_transactions.extend(transactions)
            
            # Check if there are more pages
            meta = response.get("meta", {})
            current_page = meta.get("current_page", current_page)
            last_page = meta.get("last_page", current_page)
            
            logger.info(f"Fetched {len(transactions)} transactions from page {current_page}/{last_page}")
            
            if current_page >= last_page:
                break
            
            current_page += 1
        
        logger.info(f"Total transactions fetched: {len(all_transactions)}")
        return all_transactions
    
    def sync_to_database(self, transactions: List[Dict], db: Session) -> Dict[str, int]:
        """
        Sync transactions to the database using upsert logic
        
        Args:
            transactions: List of transaction dictionaries
            db: Database session
            
        Returns:
            Dict with counts of inserted and updated records
        """
        inserted_count = 0
        updated_count = 0
        
        for txn_data in transactions:
            try:
                # Extract recipient as JSON if it exists
                recipient = txn_data.get("recipient")
                
                # Parse created_at timestamp
                created_at_str = txn_data.get("created_at")
                created_at = None
                if created_at_str:
                    try:
                        # Parse ISO format: "2026-01-23T21:56:04.000000Z"
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    except Exception as e:
                        logger.warning(f"Failed to parse created_at '{created_at_str}': {e}")
                
                # Prepare the data for upsert
                txn_dict = {
                    "id": txn_data.get("id"),
                    "amount": txn_data.get("amount"),
                    "human_readable_amount": txn_data.get("human_readable_amount"),
                    "charge": txn_data.get("charge"),
                    "human_readable_charge": txn_data.get("human_readable_charge"),
                    "status": txn_data.get("status"),
                    "decline_reason": txn_data.get("decline_reason"),
                    "mode": txn_data.get("mode"),
                    "type": txn_data.get("type"),
                    "description": txn_data.get("description"),
                    "external_id": txn_data.get("external_id"),
                    "currency": txn_data.get("currency"),
                    "created_at": created_at,
                    "recipient": recipient,
                    # Wallet swap fields
                    "from_wallet": txn_data.get("from_wallet"),
                    "to_wallet": txn_data.get("to_wallet"),
                    "debit_id": txn_data.get("debit_id"),
                    "credit_id": txn_data.get("credit_id"),
                    "rate": txn_data.get("rate"),
                }
                
                # MySQL INSERT ... ON DUPLICATE KEY UPDATE
                stmt = insert(TransactionCache).values(**txn_dict)
                
                # Update all fields except id and cached_at on duplicate
                update_dict = {
                    key: stmt.inserted[key] 
                    for key in txn_dict.keys() 
                    if key != "id"
                }
                
                stmt = stmt.on_duplicate_key_update(**update_dict)
                
                result = db.execute(stmt)
                
                # Check if it was an insert or update based on rowcount
                # rowcount = 1 for insert, 2 for update in MySQL
                if result.rowcount == 1:
                    inserted_count += 1
                elif result.rowcount == 2:
                    updated_count += 1
                
            except Exception as e:
                logger.error(f"Error syncing transaction {txn_data.get('id')}: {e}")
                continue
        
        db.commit()
        logger.info(f"Sync complete: {inserted_count} inserted, {updated_count} updated")
        
        return {
            "inserted": inserted_count,
            "updated": updated_count,
            "total": len(transactions)
        }
    
    async def full_sync(self, db: Session) -> Dict[str, Any]:
        """
        Perform a full sync of all transactions
        
        Args:
            db: Database session
            
        Returns:
            Dict with sync statistics
        """
        logger.info("Starting full transaction sync...")
        start_time = datetime.now()
        
        transactions = await self.fetch_all_pages()
        sync_stats = self.sync_to_database(transactions, db)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        result = {
            "sync_type": "full",
            "started_at": start_time.isoformat(),
            "completed_at": datetime.now().isoformat(),
            "elapsed_seconds": elapsed,
            **sync_stats
        }
        
        logger.info(f"Full sync completed in {elapsed:.2f}s: {result}")
        return result
    
    async def daily_sync(self, db: Session, target_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Perform a daily sync for a specific date
        
        Args:
            db: Database session
            target_date: Date to sync (defaults to today)
            
        Returns:
            Dict with sync statistics
        """
        if target_date is None:
            target_date = date.today()
        
        # Format as DD-MM-YYYY for the API
        day_str = target_date.strftime("%d-%m-%Y")
        logger.info(f"Starting daily transaction sync for {day_str}...")
        start_time = datetime.now()
        
        transactions = await self.fetch_all_pages(day=day_str)
        sync_stats = self.sync_to_database(transactions, db)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        result = {
            "sync_type": "daily",
            "date": day_str,
            "started_at": start_time.isoformat(),
            "completed_at": datetime.now().isoformat(),
            "elapsed_seconds": elapsed,
            **sync_stats
        }
        
        logger.info(f"Daily sync for {day_str} completed in {elapsed:.2f}s: {result}")
        return result


# Singleton instance
_sync_service: Optional[TransactionSyncService] = None


def get_sync_service() -> TransactionSyncService:
    """Get or create the transaction sync service singleton"""
    global _sync_service
    if _sync_service is None:
        _sync_service = TransactionSyncService(settings.global_transaction_api_key)
    return _sync_service
