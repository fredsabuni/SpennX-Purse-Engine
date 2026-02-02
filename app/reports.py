"""
Weekly Performance Report Module

Handles data aggregation and calculation for weekly transaction performance reports.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any
from app.models import TransactionCache
from app.currency_rates import convert_to_usd
from app.formatters import format_currency, format_percentage


def get_week_boundaries(week_start_date: str) -> tuple[datetime, datetime]:
    """
    Get week boundaries from a start date string.
    
    Args:
        week_start_date: Date string in YYYY-MM-DD format (should be a Monday)
    
    Returns:
        Tuple of (week_start, week_end) datetime objects
    """
    week_start = datetime.strptime(week_start_date, "%Y-%m-%d")
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    
    return week_start, week_end


def calculate_week_metrics(db: Session, start: datetime, end: datetime) -> Dict[str, Any]:
    """
    Calculate all metrics for a given week.
    
    Args:
        db: Database session
        start: Week start datetime
        end: Week end datetime
    
    Returns:
        Dictionary containing all week metrics
    """
    # Base query for the week
    base_query = db.query(TransactionCache).filter(
        and_(
            TransactionCache.created_at >= start,
            TransactionCache.created_at <= end
        )
    )
    
    # Get all transactions
    all_transactions = base_query.all()
    total_transactions = len(all_transactions)
    
    # Initialize counters
    success_count = 0
    failed_count = 0
    pending_count = 0
    declined_count = 0
    reversed_count = 0
    processing_swap_count = 0
    other_count = 0
    
    total_volume_usd = Decimal(0)
    total_revenue_usd = Decimal(0)
    currency_breakdown = {}
    
    # Process each transaction
    for txn in all_transactions:
        # Count by status
        if txn.status == "success":
            success_count += 1
        elif txn.status == "failed":
            failed_count += 1
        elif txn.status == "pending":
            pending_count += 1
        elif txn.status == "declined":
            declined_count += 1
        elif txn.status == "reversed":
            reversed_count += 1
        elif txn.status == "processing_swap":
            processing_swap_count += 1
        else:
            other_count += 1
        
        # Calculate volumes (only for successful transactions)
        if txn.status == "success":
            amount = txn.human_readable_amount or Decimal(0)
            charge = txn.human_readable_charge or Decimal(0)
            currency = txn.currency or "USD"
            
            # Get rate from recipient JSON
            rate_from_json = None
            if txn.recipient and isinstance(txn.recipient, dict) and 'rate' in txn.recipient:
                try:
                    rate_from_json = Decimal(str(txn.recipient['rate'])) if txn.recipient['rate'] else None
                except:
                    rate_from_json = None
            
            # Convert to USD
            amount_usd = convert_to_usd(amount, currency, rate_from_json)
            charge_usd = convert_to_usd(charge, currency, rate_from_json)
            
            total_volume_usd += amount_usd
            total_revenue_usd += charge_usd
            
            # Track currency breakdown
            if currency not in currency_breakdown:
                currency_breakdown[currency] = {
                    "transaction_count": 0,
                    "volume_usd": Decimal(0)
                }
            
            currency_breakdown[currency]["transaction_count"] += 1
            currency_breakdown[currency]["volume_usd"] += amount_usd
    
    # Calculate percentages
    success_percentage = (success_count / total_transactions * 100) if total_transactions > 0 else 0
    failed_percentage = (failed_count / total_transactions * 100) if total_transactions > 0 else 0
    pending_percentage = (pending_count / total_transactions * 100) if total_transactions > 0 else 0
    declined_percentage = (declined_count / total_transactions * 100) if total_transactions > 0 else 0
    
    # Calculate averages
    avg_transaction_size_usd = total_volume_usd / success_count if success_count > 0 else Decimal(0)
    avg_fee_per_transaction_usd = total_revenue_usd / success_count if success_count > 0 else Decimal(0)
    
    # Calculate fees-to-value ratio
    fees_to_value_ratio = (total_revenue_usd / total_volume_usd * 100) if total_volume_usd > 0 else Decimal(0)
    
    # Sort currency breakdown by volume
    currency_breakdown_list = [
        {
            "currency": currency,
            "transaction_count": data["transaction_count"],
            "volume_usd": str(data["volume_usd"]),
            "percentage": float(data["volume_usd"] / total_volume_usd * 100) if total_volume_usd > 0 else 0
        }
        for currency, data in currency_breakdown.items()
    ]
    currency_breakdown_list.sort(key=lambda x: Decimal(x["volume_usd"]), reverse=True)
    
    return {
        "total_transactions": total_transactions,
        "success_count": success_count,
        "failed_count": failed_count,
        "pending_count": pending_count,
        "declined_count": declined_count,
        "reversed_count": reversed_count,
        "processing_swap_count": processing_swap_count,
        "other_count": other_count,
        "success_percentage": round(success_percentage, 2),
        "failed_percentage": round(failed_percentage, 2),
        "pending_percentage": round(pending_percentage, 2),
        "declined_percentage": round(declined_percentage, 2),
        "success_rate": round(success_percentage, 2),
        "total_volume_usd": str(total_volume_usd),
        "avg_transaction_size_usd": str(avg_transaction_size_usd),
        "total_revenue_usd": str(total_revenue_usd),
        "avg_fee_per_transaction_usd": str(avg_fee_per_transaction_usd),
        "fees_to_value_ratio": float(fees_to_value_ratio),
        "currency_breakdown": currency_breakdown_list[:5]  # Top 5 currencies
    }


def calculate_week_over_week_changes(current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate week-over-week changes between two weeks.
    
    Args:
        current: Current week metrics
        previous: Previous week metrics
    
    Returns:
        Dictionary containing percentage changes
    """
    def calculate_change(current_val, previous_val):
        """Calculate percentage change"""
        if previous_val == 0:
            return 100.0 if current_val > 0 else 0.0
        return ((current_val - previous_val) / previous_val * 100)
    
    # Convert string values to Decimal for calculation
    current_volume = Decimal(current["total_volume_usd"])
    previous_volume = Decimal(previous["total_volume_usd"])
    
    current_revenue = Decimal(current["total_revenue_usd"])
    previous_revenue = Decimal(previous["total_revenue_usd"])
    
    current_avg_size = Decimal(current["avg_transaction_size_usd"])
    previous_avg_size = Decimal(previous["avg_transaction_size_usd"])
    
    return {
        "transaction_volume_change_pct": round(
            calculate_change(current["total_transactions"], previous["total_transactions"]), 
            2
        ),
        "transaction_volume_change_absolute": current["total_transactions"] - previous["total_transactions"],
        "success_rate_change_pct": round(
            current["success_rate"] - previous["success_rate"], 
            2
        ),
        "revenue_change_pct": round(
            calculate_change(float(current_revenue), float(previous_revenue)), 
            2
        ),
        "revenue_change_absolute_usd": str(current_revenue - previous_revenue),
        "avg_transaction_size_change_pct": round(
            calculate_change(float(current_avg_size), float(previous_avg_size)), 
            2
        )
    }


def generate_weekly_performance_report(
    db: Session, 
    week_start_date: str
) -> Dict[str, Any]:
    """
    Generate complete weekly performance report.
    
    Args:
        db: Database session
        week_start_date: Week start date in YYYY-MM-DD format (Monday)
    
    Returns:
        Complete report data structure
    """
    # Get current week boundaries
    current_start, current_end = get_week_boundaries(week_start_date)
    
    # Get previous week boundaries
    previous_start = current_start - timedelta(days=7)
    previous_end = current_start - timedelta(seconds=1)
    
    # Calculate metrics for both weeks
    current_week = calculate_week_metrics(db, current_start, current_end)
    previous_week = calculate_week_metrics(db, previous_start, previous_end)
    
    # Calculate week-over-week changes
    week_over_week_changes = calculate_week_over_week_changes(current_week, previous_week)
    
    # Get week number
    week_number = current_start.isocalendar()[1]
    
    return {
        "period": {
            "start_date": current_start.strftime("%Y-%m-%d"),
            "end_date": current_end.strftime("%Y-%m-%d"),
            "week_number": week_number
        },
        "current_week": current_week,
        "previous_week": previous_week,
        "week_over_week_changes": week_over_week_changes
    }
