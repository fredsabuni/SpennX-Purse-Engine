from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, cast, String
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from app.database import get_db
from app.models import TransactionCache
from app.schemas import (
    TransactionResponse, DashboardStats, RecipientData, 
    TransactionsLiveView, PeriodStats, TransactionPulse,
    NetIncomeStats, CountryCurrencyVolume, TimeInterval,
    TransactionStatusBreakdown, CurrencyVolumeBreakdown,
    TransactionOverview, DailyTrendData, TransactionTrend,
    TodayTransactionItem, TodayTransactionsSummary,
    WeeklyPerformanceReport, SendWeeklyEmailRequest
)
from app.utils import get_date_range, parse_datetime
from app.currency_rates import convert_to_usd
from app.formatters import format_currency, format_percentage
from app.reports import generate_weekly_performance_report
from app.email_service import generate_html_email, generate_plain_text_email, send_email
from app.scheduler import get_scheduler
import app.sync_routes as sync_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup: Start the transaction sync scheduler
    scheduler = get_scheduler()
    scheduler.start()
    yield
    # Shutdown: Stop the scheduler
    scheduler.stop()


app = FastAPI(
    title="SpennX Live Pulse Dashboard API", 
    version="2.0",
    lifespan=lifespan
)

# Include the transaction sync routes
app.include_router(sync_routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def calculate_period_stats(db: Session, start: datetime, end: datetime, period_name: str) -> PeriodStats:
    """
    Calculate statistics for a given time period.
    Uses human_readable_amount for accurate calculations across different currencies.
    Only counts 'success' status transactions for volume and revenue calculations.
    Converts to USD using rate from recipient JSON or assumes USD if rate not available.
    """
    # Base query for all transactions in period
    base_query = db.query(TransactionCache).filter(
        and_(
            TransactionCache.created_at >= start,
            TransactionCache.created_at <= end
        )
    )
    
    # Query for successful transactions only
    success_query = base_query.filter(TransactionCache.status == "success")
    
    # Total transactions (all statuses)
    total_transactions = base_query.count()
    
    # Successful transactions count
    success_count = success_query.count()
    
    # Calculate USD equivalent volume
    # For each transaction: convert to USD using rate from JSON or predefined rates
    total_volume_usd = Decimal(0)
    total_revenue_usd = Decimal(0)
    
    for txn in success_query.all():
        amount = txn.human_readable_amount or Decimal(0)
        charge = txn.human_readable_charge or Decimal(0)
        currency = txn.currency or "USD"
        
        # Get rate from recipient JSON if available
        rate_from_json = None
        if txn.recipient and isinstance(txn.recipient, dict) and 'rate' in txn.recipient:
            try:
                rate_from_json = Decimal(str(txn.recipient['rate'])) if txn.recipient['rate'] else None
            except:
                rate_from_json = None
        
        # Convert to USD using our conversion function
        total_volume_usd += convert_to_usd(amount, currency, rate_from_json)
        total_revenue_usd += convert_to_usd(charge, currency, rate_from_json)
    
    # Average in USD
    avg_amount = total_volume_usd / success_count if success_count > 0 else Decimal(0)
    avg_revenue = total_revenue_usd / success_count if success_count > 0 else Decimal(0)
    
    # Error rate calculation (failed, declined, reversed)
    error_count = base_query.filter(
        or_(
            TransactionCache.status == "failed",
            TransactionCache.status == "declined",
            TransactionCache.status == "reversed"
        )
    ).count()
    error_rate = (error_count / total_transactions * 100) if total_transactions > 0 else 0.0
    
    return PeriodStats(
        period_name=period_name,
        start_date=start,
        end_date=end,
        total_transactions=success_count,  # Only successful transactions
        total_volume=format_currency(total_volume_usd),
        total_revenue=format_currency(total_revenue_usd),
        avg_transaction_amount=format_currency(avg_amount),
        avg_revenue_per_transaction=format_currency(avg_revenue),
        error_rate=format_percentage(error_rate)
    )

@app.get("/")
def read_root():
    return {
        "message": "SpennX Live Pulse Dashboard API",
        "version": "2.0",
        "endpoints": {
            "live_view": "/api/live-view",
            "transaction_pulse": "/api/transaction-pulse",
            "net_income": "/api/net-income",
            "transactions": "/api/transactions"
        }
    }

@app.get("/api/live-view", response_model=TransactionsLiveView)
def get_transactions_live_view(db: Session = Depends(get_db)):
    """
    Get transactions live view structured by time intervals.
    All calculations use human_readable_amount for accuracy across different currencies.
    """
    intervals = {
        "today": "Today",
        "previous_day": "Previous Day",
        "current_week": "Current Week",
        "previous_week": "Previous Week",
        "current_month": "Current Month",
        "previous_month": "Previous Month",
        "year_to_date": "Year to Date"
    }
    
    stats = {}
    for key, name in intervals.items():
        start, end = get_date_range(key)
        stats[key] = calculate_period_stats(db, start, end, name)
    
    return TransactionsLiveView(**stats)

@app.get("/api/transaction-pulse", response_model=TransactionPulse)
def get_transaction_pulse(db: Session = Depends(get_db)):
    """
    Get real-time transaction pulse metrics.
    Uses human_readable_amount for accurate volume calculations across currencies.
    """
    now = datetime.now()
    
    # Last minute
    one_min_ago = now - timedelta(minutes=1)
    txn_last_min = db.query(func.count(TransactionCache.id)).filter(
        TransactionCache.created_at >= one_min_ago
    ).scalar()
    
    # Last hour
    one_hour_ago = now - timedelta(hours=1)
    txn_last_hour = db.query(func.count(TransactionCache.id)).filter(
        TransactionCache.created_at >= one_hour_ago
    ).scalar()
    
    # Today - calculate USD equivalent using rate from recipient JSON
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_base_query = db.query(TransactionCache).filter(TransactionCache.created_at >= today_start)
    
    # Only count successful transactions for volume
    today_success_query = today_base_query.filter(TransactionCache.status == "success")
    txn_today = today_success_query.count()
    
    # Calculate USD equivalent volume using proper conversion
    volume_today_usd = Decimal(0)
    for txn in today_success_query.all():
        amount = txn.human_readable_amount or Decimal(0)
        currency = txn.currency or "USD"
        
        rate_from_json = None
        if txn.recipient and isinstance(txn.recipient, dict) and 'rate' in txn.recipient:
            try:
                rate_from_json = Decimal(str(txn.recipient['rate'])) if txn.recipient['rate'] else None
            except:
                rate_from_json = None
        
        volume_today_usd += convert_to_usd(amount, currency, rate_from_json)
    
    avg_size = volume_today_usd / txn_today if txn_today > 0 else Decimal(0)
    
    # Error rate today (failed, declined, reversed)
    total_today = today_base_query.count()
    errors_today = today_base_query.filter(
        or_(
            TransactionCache.status == "failed",
            TransactionCache.status == "declined",
            TransactionCache.status == "reversed"
        )
    ).count()
    error_rate = (errors_today / total_today * 100) if total_today > 0 else 0.0
    
    # Active users (unique from_wallet or external_id)
    active_today = db.query(func.count(func.distinct(TransactionCache.from_wallet))).filter(
        TransactionCache.created_at >= today_start,
        TransactionCache.from_wallet.isnot(None)
    ).scalar()
    
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    active_week = db.query(func.count(func.distinct(TransactionCache.from_wallet))).filter(
        TransactionCache.created_at >= week_start,
        TransactionCache.from_wallet.isnot(None)
    ).scalar()
    
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    active_month = db.query(func.count(func.distinct(TransactionCache.from_wallet))).filter(
        TransactionCache.created_at >= month_start,
        TransactionCache.from_wallet.isnot(None)
    ).scalar()
    
    # New users today (simplified - count unique wallets created today)
    new_users = db.query(func.count(func.distinct(TransactionCache.from_wallet))).filter(
        TransactionCache.created_at >= today_start,
        TransactionCache.from_wallet.isnot(None)
    ).scalar()
    
    return TransactionPulse(
        transactions_per_minute=float(txn_last_min),
        transactions_per_hour=float(txn_last_hour),
        transactions_per_day=txn_today,
        transaction_volume_usd=format_currency(volume_today_usd),
        avg_transaction_size=format_currency(avg_size),
        error_rate=format_percentage(error_rate),
        active_users_today=active_today,
        active_users_week=active_week,
        active_users_month=active_month,
        new_users_today=new_users
    )

@app.get("/api/net-income", response_model=NetIncomeStats)
def get_net_income_stats(db: Session = Depends(get_db)):
    """
    Get net income statistics with multi-currency support.
    Uses human_readable_amount for accurate calculations.
    """
    now = datetime.now()
    
    # Income per minute (success only)
    one_min_ago = now - timedelta(minutes=1)
    income_min = db.query(func.sum(TransactionCache.human_readable_charge)).filter(
        TransactionCache.created_at >= one_min_ago,
        TransactionCache.status == "success"
    ).scalar() or Decimal(0)
    
    # Income per hour (success only)
    one_hour_ago = now - timedelta(hours=1)
    income_hour = db.query(func.sum(TransactionCache.human_readable_charge)).filter(
        TransactionCache.created_at >= one_hour_ago,
        TransactionCache.status == "success"
    ).scalar() or Decimal(0)
    
    # Income per day (success only) - convert to USD
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_base_query = db.query(TransactionCache).filter(TransactionCache.created_at >= today_start)
    today_success_query = today_base_query.filter(TransactionCache.status == "success")
    
    # Calculate USD equivalent income and volume using proper conversion
    income_day_usd = Decimal(0)
    total_moved_usd = Decimal(0)
    
    for txn in today_success_query.all():
        amount = txn.human_readable_amount or Decimal(0)
        charge = txn.human_readable_charge or Decimal(0)
        currency = txn.currency or "USD"
        
        rate_from_json = None
        if txn.recipient and isinstance(txn.recipient, dict) and 'rate' in txn.recipient:
            try:
                rate_from_json = Decimal(str(txn.recipient['rate'])) if txn.recipient['rate'] else None
            except:
                rate_from_json = None
        
        income_day_usd += convert_to_usd(charge, currency, rate_from_json)
        total_moved_usd += convert_to_usd(amount, currency, rate_from_json)
    
    success_count_today = today_success_query.count()
    avg_sent = total_moved_usd / success_count_today if success_count_today > 0 else Decimal(0)
    
    # Error rate (failed, declined, reversed)
    total_today = today_base_query.count()
    errors_today = today_base_query.filter(
        or_(
            TransactionCache.status == "failed",
            TransactionCache.status == "declined",
            TransactionCache.status == "reversed"
        )
    ).count()
    error_rate = (errors_today / total_today * 100) if total_today > 0 else 0.0
    
    # Top 5 countries by volume (from recipient JSON) - using human_readable_amount (success only)
    top_countries_raw = db.query(
        cast(TransactionCache.recipient['country'], String).label('country'),
        func.sum(TransactionCache.human_readable_amount).label('volume'),
        func.count(TransactionCache.id).label('count')
    ).filter(
        TransactionCache.created_at >= today_start,
        TransactionCache.status == "success",
        TransactionCache.recipient['country'].isnot(None)
    ).group_by('country').order_by(desc('volume')).limit(5).all()
    
    top_countries = [
        CountryCurrencyVolume(
            country=row.country,
            currency=None,
            volume=format_currency(row.volume or Decimal(0)),
            transaction_count=row.count
        )
        for row in top_countries_raw
    ]
    
    # Top 5 currencies by volume - using human_readable_amount for accurate totals (success only)
    top_currencies_raw = db.query(
        TransactionCache.currency,
        func.sum(TransactionCache.human_readable_amount).label('volume'),
        func.count(TransactionCache.id).label('count')
    ).filter(
        TransactionCache.created_at >= today_start,
        TransactionCache.status == "success"
    ).group_by(TransactionCache.currency).order_by(desc('volume')).limit(5).all()
    
    top_currencies = [
        CountryCurrencyVolume(
            country=None,
            currency=row.currency,
            volume=format_currency(row.volume or Decimal(0)),
            transaction_count=row.count
        )
        for row in top_currencies_raw
    ]
    
    # YTD accumulated revenue (success only)
    ytd_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    ytd_revenue = db.query(func.sum(TransactionCache.human_readable_charge)).filter(
        TransactionCache.created_at >= ytd_start,
        TransactionCache.status == "success"
    ).scalar() or Decimal(0)
    
    return NetIncomeStats(
        income_per_minute=format_currency(income_min),
        income_per_hour=format_currency(income_hour),
        income_per_day=format_currency(income_day_usd),
        total_value_moved_usd=format_currency(total_moved_usd),
        avg_amount_sent=format_currency(avg_sent),
        error_rate=format_percentage(error_rate),
        top_countries=top_countries,
        top_currencies=top_currencies,
        accumulated_revenue_ytd=format_currency(ytd_revenue)
    )

@app.get("/api/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get overall dashboard statistics.
    Converts all amounts to USD using rate from recipient JSON.
    Only counts successful transactions for volume calculations.
    """
    # Get all successful transactions
    success_query = db.query(TransactionCache).filter(TransactionCache.status == "success")
    total_transactions = success_query.count()
    
    # Calculate USD equivalent volume using proper conversion
    total_volume_usd = Decimal(0)
    for txn in success_query.all():
        amount = txn.human_readable_amount or Decimal(0)
        currency = txn.currency or "USD"
        
        rate_from_json = None
        if txn.recipient and isinstance(txn.recipient, dict) and 'rate' in txn.recipient:
            try:
                rate_from_json = Decimal(str(txn.recipient['rate'])) if txn.recipient['rate'] else None
            except:
                rate_from_json = None
        
        total_volume_usd += convert_to_usd(amount, currency, rate_from_json)
    
    # Status counts
    pending_count = db.query(func.count(TransactionCache.id)).filter(TransactionCache.status == "pending").scalar()
    completed_count = db.query(func.count(TransactionCache.id)).filter(TransactionCache.status == "success").scalar()
    failed_count = db.query(func.count(TransactionCache.id)).filter(
        or_(
            TransactionCache.status == "failed",
            TransactionCache.status == "declined",
            TransactionCache.status == "reversed"
        )
    ).scalar()
    
    # Average in USD
    avg_amount = total_volume_usd / total_transactions if total_transactions > 0 else Decimal(0)
    
    return DashboardStats(
        total_transactions=total_transactions,
        total_volume=format_currency(total_volume_usd),
        pending_count=pending_count,
        completed_count=completed_count,
        failed_count=failed_count,
        avg_transaction_amount=format_currency(avg_amount)
    )

@app.get("/api/transactions", response_model=List[TransactionResponse])
def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    interval: Optional[TimeInterval] = None,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of transactions with optional filters.
    
    Filters:
    - status: Filter by transaction status
    - interval: Predefined time intervals (today, current_week, etc.)
    - start_date & end_date: Custom date range (overrides interval if provided)
    
    Date formats accepted:
    - YYYY-MM-DD (e.g., 2024-01-15)
    - YYYY-MM-DD HH:MM:SS (e.g., 2024-01-15 14:30:00)
    """
    query = db.query(TransactionCache)
    
    if status:
        query = query.filter(TransactionCache.status == status)
    
    # Custom date range takes priority over interval
    if start_date or end_date:
        try:
            if start_date:
                start_dt = parse_datetime(start_date)
                query = query.filter(TransactionCache.created_at >= start_dt)
            
            if end_date:
                end_dt = parse_datetime(end_date)
                # If only date provided, set to end of day
                if end_dt.hour == 0 and end_dt.minute == 0 and end_dt.second == 0:
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(TransactionCache.created_at <= end_dt)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    elif interval:
        # Use predefined interval if no custom dates provided
        start, end = get_date_range(interval.value)
        query = query.filter(
            and_(
                TransactionCache.created_at >= start,
                TransactionCache.created_at <= end
            )
        )
    
    transactions = query.order_by(desc(TransactionCache.created_at)).offset(skip).limit(limit).all()
    
    return [
        TransactionResponse(
            **{k: v for k, v in t.__dict__.items() if k not in ['_sa_instance_state', 'recipient', 'human_readable_amount', 'human_readable_charge']},
            recipient=RecipientData(**t.recipient) if t.recipient else None,
            human_readable_amount=format_currency(t.human_readable_amount),
            human_readable_charge=format_currency(t.human_readable_charge)
        )
        for t in transactions
    ]

@app.get("/api/transactions/today", response_model=TodayTransactionsSummary)
def get_today_transactions(
    status: Optional[str] = Query(None, description="Filter by status (success, pending, failed, etc.)"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of transactions to return"),
    db: Session = Depends(get_db)
):
    """
    Get today's transactions with USD conversion for finance team monitoring.
    
    Returns:
    - All transactions from today with specific timestamps
    - Amounts converted to USD
    - Summary statistics (counts by status, total volume, revenue)
    - Sorted by most recent first
    
    Perfect for:
    - Real-time finance team monitoring
    - Today's transaction activity dashboard
    - Live transaction feed with USD values
    
    Filters:
    - status: Filter by specific status (optional)
    - limit: Number of transactions to return (default 100, max 500)
    
    Example:
    /api/transactions/today
    /api/transactions/today?status=success
    /api/transactions/today?limit=200
    """
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Base query for today
    base_query = db.query(TransactionCache).filter(
        TransactionCache.created_at >= today_start
    )
    
    # Apply status filter if provided
    if status:
        base_query = base_query.filter(TransactionCache.status == status)
    
    # Get transactions ordered by most recent first
    transactions = base_query.order_by(desc(TransactionCache.created_at)).limit(limit).all()
    
    # Calculate summary stats
    total_count = 0
    success_count = 0
    pending_count = 0
    failed_count = 0
    total_volume_usd = Decimal(0)
    total_revenue_usd = Decimal(0)
    
    # Build transaction list with USD conversion
    transaction_items = []
    
    for txn in transactions:
        # Get amounts
        amount = txn.human_readable_amount or Decimal(0)
        charge = txn.human_readable_charge or Decimal(0)
        currency = txn.currency or "USD"
        
        # Get rate from recipient JSON
        rate_from_json = None
        if txn.recipient and isinstance(txn.recipient, dict):
            if 'rate' in txn.recipient:
                try:
                    rate_from_json = Decimal(str(txn.recipient['rate'])) if txn.recipient['rate'] else None
                except:
                    rate_from_json = None
        
        # Convert to USD
        amount_usd = convert_to_usd(amount, currency, rate_from_json)
        charge_usd = convert_to_usd(charge, currency, rate_from_json)
        
        # Get recipient info
        recipient_name = None
        recipient_country = None
        if txn.recipient and isinstance(txn.recipient, dict):
            first_name = txn.recipient.get('first_name', '')
            last_name = txn.recipient.get('last_name', '')
            if first_name or last_name:
                recipient_name = f"{first_name} {last_name}".strip()
            recipient_country = txn.recipient.get('country')
        
        # Count by status
        total_count += 1
        if txn.status == "success":
            success_count += 1
            total_volume_usd += amount_usd
            total_revenue_usd += charge_usd
        elif txn.status == "pending":
            pending_count += 1
        elif txn.status in ["failed", "declined", "reversed"]:
            failed_count += 1
        
        # Build transaction item
        transaction_items.append(TodayTransactionItem(
            id=txn.id,
            time=txn.created_at.strftime("%H:%M:%S"),
            created_at=txn.created_at,
            status=txn.status,
            amount=format_currency(amount),
            currency=currency,
            amount_usd=format_currency(amount_usd),
            charge=format_currency(charge),
            charge_usd=format_currency(charge_usd),
            type=txn.type,
            description=txn.description,
            from_wallet=txn.from_wallet,
            to_wallet=txn.to_wallet,
            recipient_name=recipient_name,
            recipient_country=recipient_country
        ))
    
    return TodayTransactionsSummary(
        date=today_start.date().isoformat(),
        total_count=total_count,
        success_count=success_count,
        pending_count=pending_count,
        failed_count=failed_count,
        total_volume_usd=format_currency(total_volume_usd),
        total_revenue_usd=format_currency(total_revenue_usd),
        transactions=transaction_items
    )

@app.get("/api/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """Get a specific transaction by ID"""
    transaction = db.query(TransactionCache).filter(TransactionCache.id == transaction_id).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return TransactionResponse(
        **{k: v for k, v in transaction.__dict__.items() if k not in ['_sa_instance_state', 'recipient', 'human_readable_amount', 'human_readable_charge']},
        recipient=RecipientData(**transaction.recipient) if transaction.recipient else None,
        human_readable_amount=format_currency(transaction.human_readable_amount),
        human_readable_charge=format_currency(transaction.human_readable_charge)
    )

@app.get("/api/analytics/custom-range", response_model=PeriodStats)
def get_custom_range_analytics(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"),
    db: Session = Depends(get_db)
):
    """
    Get analytics for a custom date range.
    
    Returns comprehensive statistics including:
    - Total transactions (successful only)
    - Total volume (USD)
    - Total revenue (USD)
    - Net revenue
    - Average transaction amount
    - Average revenue per transaction
    - Error rate
    
    Date formats accepted:
    - YYYY-MM-DD (e.g., 2024-01-15)
    - YYYY-MM-DD HH:MM:SS (e.g., 2024-01-15 14:30:00)
    
    Example:
    /api/analytics/custom-range?start_date=2024-01-01&end_date=2024-01-31
    """
    try:
        # Parse start date
        start_dt = parse_datetime(start_date)
        
        # Parse end date
        end_dt = parse_datetime(end_date)
        if end_dt.hour == 0 and end_dt.minute == 0 and end_dt.second == 0:
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
        
        # Validate date range
        if start_dt > end_dt:
            raise HTTPException(
                status_code=400,
                detail="start_date must be before or equal to end_date"
            )
        
        # Calculate stats for the custom range
        period_name = f"Custom Range ({start_date} to {end_date})"
        return calculate_period_stats(db, start_dt, end_dt, period_name)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/analytics/status-breakdown", response_model=TransactionStatusBreakdown)
def get_status_breakdown(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"),
    interval: Optional[TimeInterval] = None,
    db: Session = Depends(get_db)
):
    """
    Get transaction status breakdown for pie chart visualization.
    
    Returns count and percentage for each status:
    - success
    - pending
    - failed
    - declined
    - reversed
    - processing_swap
    
    Can filter by:
    - Custom date range (start_date & end_date)
    - Predefined interval (today, current_week, etc.)
    - If no filter provided, returns all-time data
    """
    query = db.query(TransactionCache)
    
    # Apply date filters
    if start_date or end_date:
        try:
            if start_date:
                start_dt = parse_datetime(start_date)
                query = query.filter(TransactionCache.created_at >= start_dt)
            
            if end_date:
                end_dt = parse_datetime(end_date)
                if end_dt.hour == 0 and end_dt.minute == 0 and end_dt.second == 0:
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(TransactionCache.created_at <= end_dt)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
    elif interval:
        start, end = get_date_range(interval.value)
        query = query.filter(
            and_(
                TransactionCache.created_at >= start,
                TransactionCache.created_at <= end
            )
        )
    
    # Get total count
    total_count = query.count()
    
    # Get count by status
    status_counts = db.query(
        TransactionCache.status,
        func.count(TransactionCache.id).label('count')
    ).filter(
        TransactionCache.id.in_(query.with_entities(TransactionCache.id))
    ).group_by(TransactionCache.status).all()
    
    # Build status breakdown
    statuses = {}
    for status, count in status_counts:
        percentage = (count / total_count * 100) if total_count > 0 else 0
        statuses[status] = {
            "count": count,
            "percentage": format_percentage(percentage)
        }
    
    # Ensure all statuses are present (even if 0)
    all_statuses = ["success", "pending", "failed", "declined", "reversed", "processing_swap"]
    for status in all_statuses:
        if status not in statuses:
            statuses[status] = {"count": 0, "percentage": 0.0}
    
    return TransactionStatusBreakdown(
        total_transactions=total_count,
        statuses=statuses
    )

@app.get("/api/analytics/currency-breakdown", response_model=List[CurrencyVolumeBreakdown])
def get_currency_breakdown(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"),
    interval: Optional[TimeInterval] = None,
    status: Optional[str] = Query(None, description="Filter by status (default: success only)"),
    db: Session = Depends(get_db)
):
    """
    Get transaction volume breakdown by currency for bar/line chart visualization.
    
    Returns for each currency:
    - Currency code
    - Transaction count
    - Total volume in original currency
    - Total volume in USD
    - Average transaction size
    - Percentage of total volume
    
    By default, only includes successful transactions.
    Use status parameter to include other statuses.
    
    Perfect for:
    - Bar charts showing volume by currency
    - Line charts showing currency trends over time
    - Currency distribution analysis
    """
    query = db.query(TransactionCache)
    
    # Default to success status only
    if status:
        query = query.filter(TransactionCache.status == status)
    else:
        query = query.filter(TransactionCache.status == "success")
    
    # Apply date filters
    if start_date or end_date:
        try:
            if start_date:
                start_dt = parse_datetime(start_date)
                query = query.filter(TransactionCache.created_at >= start_dt)
            
            if end_date:
                end_dt = parse_datetime(end_date)
                if end_dt.hour == 0 and end_dt.minute == 0 and end_dt.second == 0:
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(TransactionCache.created_at <= end_dt)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
    elif interval:
        start, end = get_date_range(interval.value)
        query = query.filter(
            and_(
                TransactionCache.created_at >= start,
                TransactionCache.created_at <= end
            )
        )
    
    # Get all transactions for this query
    transactions = query.all()
    
    # Calculate totals by currency
    currency_data = {}
    total_volume_usd_all = Decimal(0)
    
    for txn in transactions:
        currency = txn.currency or "USD"
        amount = txn.human_readable_amount or Decimal(0)
        
        # Convert to USD
        rate_from_json = None
        if txn.recipient and isinstance(txn.recipient, dict) and 'rate' in txn.recipient:
            try:
                rate_from_json = Decimal(str(txn.recipient['rate'])) if txn.recipient['rate'] else None
            except:
                rate_from_json = None
        
        amount_usd = convert_to_usd(amount, currency, rate_from_json)
        total_volume_usd_all += amount_usd
        
        if currency not in currency_data:
            currency_data[currency] = {
                "count": 0,
                "total_volume": Decimal(0),
                "total_volume_usd": Decimal(0)
            }
        
        currency_data[currency]["count"] += 1
        currency_data[currency]["total_volume"] += amount
        currency_data[currency]["total_volume_usd"] += amount_usd
    
    # Build response
    result = []
    for currency, data in currency_data.items():
        avg_transaction = data["total_volume"] / data["count"] if data["count"] > 0 else Decimal(0)
        percentage = (data["total_volume_usd"] / total_volume_usd_all * 100) if total_volume_usd_all > 0 else 0
        
        result.append(CurrencyVolumeBreakdown(
            currency=currency,
            transaction_count=data["count"],
            total_volume=format_currency(data["total_volume"]),
            total_volume_usd=format_currency(data["total_volume_usd"]),
            avg_transaction_size=format_currency(avg_transaction),
            percentage_of_total=format_percentage(percentage)
        ))
    
    # Sort by volume (descending)
    result.sort(key=lambda x: x.total_volume_usd, reverse=True)
    
    return result

@app.get("/api/analytics/transaction-overview", response_model=TransactionOverview)
def get_transaction_overview(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"),
    interval: Optional[TimeInterval] = None,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive transaction overview with actual numbers for table display.
    
    Returns:
    - Total transactions by status (with counts and volumes)
    - Success rate
    - Total volume (USD)
    - Total revenue (USD)
    - Average transaction size
    - Status breakdown with percentages
    
    Perfect for:
    - Overview tables showing all transaction metrics
    - Dashboard summary cards
    - Executive reports
    """
    query = db.query(TransactionCache)
    
    # Apply date filters
    if start_date or end_date:
        try:
            if start_date:
                start_dt = parse_datetime(start_date)
                query = query.filter(TransactionCache.created_at >= start_dt)
            
            if end_date:
                end_dt = parse_datetime(end_date)
                if end_dt.hour == 0 and end_dt.minute == 0 and end_dt.second == 0:
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(TransactionCache.created_at <= end_dt)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
    elif interval:
        start, end = get_date_range(interval.value)
        query = query.filter(
            and_(
                TransactionCache.created_at >= start,
                TransactionCache.created_at <= end
            )
        )
    
    # Get all transactions
    all_transactions = query.all()
    total_count = len(all_transactions)
    
    # Calculate metrics by status
    status_metrics = {}
    total_volume_usd = Decimal(0)
    total_revenue_usd = Decimal(0)
    success_count = 0
    
    for txn in all_transactions:
        status = txn.status or "unknown"
        amount = txn.human_readable_amount or Decimal(0)
        charge = txn.human_readable_charge or Decimal(0)
        currency = txn.currency or "USD"
        
        # Convert to USD
        rate_from_json = None
        if txn.recipient and isinstance(txn.recipient, dict) and 'rate' in txn.recipient:
            try:
                rate_from_json = Decimal(str(txn.recipient['rate'])) if txn.recipient['rate'] else None
            except:
                rate_from_json = None
        
        amount_usd = convert_to_usd(amount, currency, rate_from_json)
        charge_usd = convert_to_usd(charge, currency, rate_from_json)
        
        if status not in status_metrics:
            status_metrics[status] = {
                "count": 0,
                "volume_usd": Decimal(0),
                "revenue_usd": Decimal(0)
            }
        
        status_metrics[status]["count"] += 1
        status_metrics[status]["volume_usd"] += amount_usd
        status_metrics[status]["revenue_usd"] += charge_usd
        
        if status == "success":
            success_count += 1
            total_volume_usd += amount_usd
            total_revenue_usd += charge_usd
    
    # Build status breakdown
    status_breakdown = {}
    for status, metrics in status_metrics.items():
        percentage = (metrics["count"] / total_count * 100) if total_count > 0 else 0
        status_breakdown[status] = {
            "count": metrics["count"],
            "volume_usd": format_currency(metrics["volume_usd"]),
            "revenue_usd": format_currency(metrics["revenue_usd"]),
            "percentage": format_percentage(percentage)
        }
    
    # Calculate success rate
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    # Calculate average transaction size (success only)
    avg_transaction_size = total_volume_usd / success_count if success_count > 0 else Decimal(0)
    
    return TransactionOverview(
        total_transactions=total_count,
        success_count=success_count,
        success_rate=format_percentage(success_rate),
        total_volume_usd=format_currency(total_volume_usd),
        total_revenue_usd=format_currency(total_revenue_usd),
        avg_transaction_size=format_currency(avg_transaction_size),
        status_breakdown=status_breakdown
    )

@app.get("/api/transactions/status/{status}", response_model=List[TransactionResponse])
def get_transactions_by_status(
    status: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"),
    db: Session = Depends(get_db)
):
    """
    Get transactions filtered by status with optional date range.
    
    Date formats accepted:
    - YYYY-MM-DD (e.g., 2024-01-15)
    - YYYY-MM-DD HH:MM:SS (e.g., 2024-01-15 14:30:00)
    """
    query = db.query(TransactionCache).filter(TransactionCache.status == status)
    
    # Apply date filters if provided
    if start_date or end_date:
        try:
            if start_date:
                start_dt = parse_datetime(start_date)
                query = query.filter(TransactionCache.created_at >= start_dt)
            
            if end_date:
                end_dt = parse_datetime(end_date)
                if end_dt.hour == 0 and end_dt.minute == 0 and end_dt.second == 0:
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(TransactionCache.created_at <= end_dt)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    transactions = query.order_by(desc(TransactionCache.created_at)).offset(skip).limit(limit).all()
    
    return [
        TransactionResponse(
            **{k: v for k, v in t.__dict__.items() if k not in ['_sa_instance_state', 'recipient', 'human_readable_amount', 'human_readable_charge']},
            recipient=RecipientData(**t.recipient) if t.recipient else None,
            human_readable_amount=format_currency(t.human_readable_amount),
            human_readable_charge=format_currency(t.human_readable_charge)
        )
        for t in transactions
    ]

@app.get("/api/analytics/daily-trend", response_model=TransactionTrend)
def get_daily_transaction_trend(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)"),
    interval: Optional[TimeInterval] = None,
    db: Session = Depends(get_db)
):
    """
    Get daily transaction trends with all amounts converted to USD.
    
    Returns daily breakdown of:
    - Transaction counts by status
    - Total volume in USD
    - Total revenue in USD
    - Average transaction size in USD
    - Success rate
    
    Perfect for line charts showing:
    - Number of successful transactions per day
    - Transaction volume in USD per day
    
    Filters:
    - Custom date range (start_date & end_date)
    - Predefined interval (today, current_week, current_month, etc.)
    - If no filter provided, returns from 2025-07-18 to today
    
    Example:
    /api/analytics/daily-trend?start_date=2024-01-01&end_date=2024-01-31
    /api/analytics/daily-trend?interval=current_month
    /api/analytics/daily-trend  (defaults to 2025-07-18 to today)
    """
    now = datetime.now()
    
    # Determine date range
    if start_date or end_date:
        try:
            if start_date:
                start_dt = parse_datetime(start_date)
            else:
                # Default start date if only end_date provided
                start_dt = datetime(2025, 7, 18, 0, 0, 0)
            
            if end_date:
                end_dt = parse_datetime(end_date)
                if end_dt.hour == 0 and end_dt.minute == 0 and end_dt.second == 0:
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
            else:
                end_dt = now
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    elif interval:
        start_dt, end_dt = get_date_range(interval.value)
    else:
        # Default: from 2025-07-18 to today
        start_dt = datetime(2025, 7, 18, 0, 0, 0)
        end_dt = now
    
    # Validate date range
    if start_dt > end_dt:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before or equal to end_date"
        )
    
    # Use database aggregation for counts, but we need individual records for currency conversion
    # Group by date and status for counts (efficient)
    from sqlalchemy import case
    
    daily_counts = db.query(
        func.date(TransactionCache.created_at).label('date'),
        TransactionCache.status,
        func.count(TransactionCache.id).label('count')
    ).filter(
        and_(
            TransactionCache.created_at >= start_dt,
            TransactionCache.created_at <= end_dt
        )
    ).group_by(
        func.date(TransactionCache.created_at),
        TransactionCache.status
    ).all()
    
    # For successful transactions, we need to fetch and convert to USD
    # Only fetch successful transactions to minimize data transfer
    success_transactions = db.query(
        func.date(TransactionCache.created_at).label('date'),
        TransactionCache.human_readable_amount,
        TransactionCache.human_readable_charge,
        TransactionCache.currency,
        TransactionCache.recipient
    ).filter(
        and_(
            TransactionCache.created_at >= start_dt,
            TransactionCache.created_at <= end_dt,
            TransactionCache.status == "success"
        )
    ).all()
    
    # Group results by date
    daily_data_dict = {}
    
    # First, populate counts from aggregated query
    for row in daily_counts:
        date_str = row.date.isoformat()
        
        if date_str not in daily_data_dict:
            daily_data_dict[date_str] = {
                "transaction_count": 0,
                "success_count": 0,
                "failed_count": 0,
                "pending_count": 0,
                "total_volume_usd": Decimal(0),
                "total_revenue_usd": Decimal(0)
            }
        
        # Aggregate counts by status
        daily_data_dict[date_str]["transaction_count"] += row.count
        
        if row.status == "success":
            daily_data_dict[date_str]["success_count"] += row.count
        elif row.status in ["failed", "declined", "reversed"]:
            daily_data_dict[date_str]["failed_count"] += row.count
        elif row.status == "pending":
            daily_data_dict[date_str]["pending_count"] += row.count
    
    # Now convert and sum amounts for successful transactions
    for row in success_transactions:
        date_str = row.date.isoformat()
        
        # Ensure date exists in dict (should already exist from counts)
        if date_str not in daily_data_dict:
            daily_data_dict[date_str] = {
                "transaction_count": 0,
                "success_count": 0,
                "failed_count": 0,
                "pending_count": 0,
                "total_volume_usd": Decimal(0),
                "total_revenue_usd": Decimal(0)
            }
        
        amount = row.human_readable_amount or Decimal(0)
        charge = row.human_readable_charge or Decimal(0)
        currency = row.currency or "USD"
        
        # Get rate from recipient JSON
        rate_from_json = None
        if row.recipient and isinstance(row.recipient, dict) and 'rate' in row.recipient:
            try:
                rate_from_json = Decimal(str(row.recipient['rate'])) if row.recipient['rate'] else None
            except:
                rate_from_json = None
        
        # Convert to USD
        amount_usd = convert_to_usd(amount, currency, rate_from_json)
        charge_usd = convert_to_usd(charge, currency, rate_from_json)
        
        daily_data_dict[date_str]["total_volume_usd"] += amount_usd
        daily_data_dict[date_str]["total_revenue_usd"] += charge_usd
    
    # Build daily data list
    daily_data = []
    total_transactions = 0
    total_success = 0
    total_volume_usd = Decimal(0)
    total_revenue_usd = Decimal(0)
    
    # Sort by date
    for date_str in sorted(daily_data_dict.keys()):
        data = daily_data_dict[date_str]
        
        # Calculate averages
        avg_transaction_size = (
            data["total_volume_usd"] / data["success_count"] 
            if data["success_count"] > 0 
            else Decimal(0)
        )
        
        # Calculate success rate
        success_rate = (
            data["success_count"] / data["transaction_count"] * 100 
            if data["transaction_count"] > 0 
            else 0.0
        )
        
        daily_data.append(DailyTrendData(
            date=date_str,
            transaction_count=data["transaction_count"],
            success_count=data["success_count"],
            failed_count=data["failed_count"],
            pending_count=data["pending_count"],
            total_volume_usd=format_currency(data["total_volume_usd"]),
            total_revenue_usd=format_currency(data["total_revenue_usd"]),
            avg_transaction_size_usd=format_currency(avg_transaction_size),
            success_rate=round(success_rate, 2)
        ))
        
        # Accumulate totals for summary
        total_transactions += data["transaction_count"]
        total_success += data["success_count"]
        total_volume_usd += data["total_volume_usd"]
        total_revenue_usd += data["total_revenue_usd"]
    
    # Calculate summary stats
    total_days = len(daily_data)
    overall_success_rate = (total_success / total_transactions * 100) if total_transactions > 0 else 0.0
    avg_daily_transactions = total_transactions / total_days if total_days > 0 else 0
    avg_daily_volume = total_volume_usd / total_days if total_days > 0 else Decimal(0)
    avg_transaction_size = total_volume_usd / total_success if total_success > 0 else Decimal(0)
    
    summary = {
        "total_transactions": total_transactions,
        "total_success": total_success,
        "overall_success_rate": round(overall_success_rate, 2),
        "total_volume_usd": format_currency(total_volume_usd),
        "total_revenue_usd": format_currency(total_revenue_usd),
        "avg_daily_transactions": round(avg_daily_transactions, 2),
        "avg_daily_volume_usd": format_currency(avg_daily_volume),
        "avg_transaction_size_usd": format_currency(avg_transaction_size)
    }
    
    return TransactionTrend(
        start_date=start_dt.date().isoformat(),
        end_date=end_dt.date().isoformat(),
        total_days=total_days,
        daily_data=daily_data,
        summary=summary
    )

@app.get("/api/reports/weekly-performance", response_model=WeeklyPerformanceReport)
def get_weekly_performance_report(
    week_start_date: str = Query(..., description="Week start date (YYYY-MM-DD, should be a Monday)"),
    db: Session = Depends(get_db)
):
    """
    Get weekly transaction performance report.
    
    Returns comprehensive metrics for the specified week including:
    - Transaction counts by status
    - Volume and revenue metrics
    - Currency breakdown (top 5)
    - Week-over-week comparison with previous week
    
    Args:
        week_start_date: Start date of the week (YYYY-MM-DD format, should be a Monday)
    
    Example:
        /api/reports/weekly-performance?week_start_date=2026-01-13
    
    Note: This endpoint is designed to be called by n8n for automated weekly email reports.
    """
    try:
        # Validate date format
        datetime.strptime(week_start_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD format (e.g., 2026-01-13)"
        )
    
    # Generate report
    report_data = generate_weekly_performance_report(db, week_start_date)
    
    return WeeklyPerformanceReport(**report_data)

@app.post("/api/reports/weekly-email")
def send_weekly_performance_email(
    request: SendWeeklyEmailRequest,
    db: Session = Depends(get_db)
):
    """
    Generate and send weekly performance email report.
    
    This endpoint:
    1. Generates the weekly performance report data
    2. Creates HTML and plain text email content
    3. Sends the email to specified recipients
    
    Request body:
    {
        "week_start_date": "2026-01-13",
        "recipients": ["finance@spennx.com", "management@spennx.com"]
    }
    
    Note: This endpoint is designed to be called by n8n automation.
    Email credentials should be configured in environment variables.
    
    Returns:
        Success message with report summary
    """
    try:
        # Validate date format
        datetime.strptime(request.week_start_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD format (e.g., 2026-01-13)"
        )
    
    # Generate report data
    report_data = generate_weekly_performance_report(db, request.week_start_date)
    
    # Format dates for subject
    start_date = datetime.strptime(report_data["period"]["start_date"], "%Y-%m-%d").strftime("%b %d")
    end_date = datetime.strptime(report_data["period"]["end_date"], "%Y-%m-%d").strftime("%b %d, %Y")
    
    # Create email subject
    subject = f"Weekly Transaction Performance Report - {start_date} to {end_date}"
    
    # Generate email content
    html_content = generate_html_email(report_data)
    plain_text_content = generate_plain_text_email(report_data)
    
    # Email sending using Gmail API
    from os import getenv
    sender_email = getenv("WEEKLY_REPORT_SENDER_EMAIL", None)
    
    # Send email using Gmail API (uses credentials.json and token.pickle)
    success = send_email(
        recipients=request.recipients,
        subject=subject,
        html_content=html_content,
        plain_text_content=plain_text_content,
        sender_email=sender_email
    )
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to send email. Check server logs for details. Ensure credentials.json is present and you've authenticated with Gmail API."
        )
    
    return {
        "success": True,
        "message": "Weekly performance email sent successfully via Gmail API",
        "subject": subject,
        "recipients": request.recipients,
        "report_summary": {
            "period": report_data["period"],
            "total_transactions": report_data["current_week"]["total_transactions"],
            "total_volume_usd": report_data["current_week"]["total_volume_usd"],
            "total_revenue_usd": report_data["current_week"]["total_revenue_usd"],
            "success_rate": report_data["current_week"]["success_rate"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
