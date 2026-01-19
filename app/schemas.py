from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

class TimeInterval(str, Enum):
    TODAY = "today"
    PREVIOUS_DAY = "previous_day"
    CURRENT_WEEK = "current_week"
    PREVIOUS_WEEK = "previous_week"
    CURRENT_MONTH = "current_month"
    PREVIOUS_MONTH = "previous_month"
    YEAR_TO_DATE = "year_to_date"

class RecipientData(BaseModel):
    id: Optional[int] = None
    transaction_id: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    amount: Optional[int] = None
    human_readable_recipient_amount: Optional[Decimal] = None
    currency_code: Optional[str] = None
    rate: Optional[Decimal] = None
    transfer_purpose: Optional[str] = None
    delivery_method: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    postal_code: Optional[str] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    routing_type: Optional[str] = None
    routing_code: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    amount: int
    currency: str
    human_readable_amount: str  # Changed to string for formatted output
    charge: int
    human_readable_charge: str  # Changed to string for formatted output
    status: str
    decline_reason: Optional[str]
    mode: str
    type: str
    description: Optional[str]
    external_id: Optional[str]
    from_wallet: Optional[str]
    to_wallet: Optional[str]
    debit_id: Optional[str]
    created_at: datetime
    recipient: Optional[RecipientData]
    
    class Config:
        from_attributes = True

class PeriodStats(BaseModel):
    period_name: str
    start_date: datetime
    end_date: datetime
    total_transactions: int
    total_volume: str  # Changed to string for formatted output
    total_revenue: str  # Changed to string for formatted output
    avg_transaction_amount: str  # Changed to string for formatted output
    avg_revenue_per_transaction: str  # Changed to string for formatted output
    error_rate: float

class TransactionsLiveView(BaseModel):
    today: PeriodStats
    previous_day: PeriodStats
    current_week: PeriodStats
    previous_week: PeriodStats
    current_month: PeriodStats
    previous_month: PeriodStats
    year_to_date: PeriodStats

class TransactionPulse(BaseModel):
    transactions_per_minute: float
    transactions_per_hour: float
    transactions_per_day: int
    transaction_volume_usd: str  # Changed to string for formatted output
    avg_transaction_size: str  # Changed to string for formatted output
    error_rate: float
    active_users_today: int
    active_users_week: int
    active_users_month: int
    new_users_today: int

class CountryCurrencyVolume(BaseModel):
    country: Optional[str]
    currency: Optional[str]
    volume: str  # Changed to string for formatted output
    transaction_count: int

class NetIncomeStats(BaseModel):
    income_per_minute: str  # Changed to string for formatted output
    income_per_hour: str  # Changed to string for formatted output
    income_per_day: str  # Changed to string for formatted output
    total_value_moved_usd: str  # Changed to string for formatted output
    avg_amount_sent: str  # Changed to string for formatted output
    error_rate: float
    top_countries: List[CountryCurrencyVolume]
    top_currencies: List[CountryCurrencyVolume]
    accumulated_revenue_ytd: str  # Changed to string for formatted output

class DashboardStats(BaseModel):
    total_transactions: int
    total_volume: str  # Changed to string for formatted output
    pending_count: int
    completed_count: int
    failed_count: int
    avg_transaction_amount: str  # Changed to string for formatted output

class TransactionStatusBreakdown(BaseModel):
    total_transactions: int
    statuses: Dict[str, Dict[str, float]]  # {"success": {"count": 100, "percentage": 50.0}}

class CurrencyVolumeBreakdown(BaseModel):
    currency: str
    transaction_count: int
    total_volume: str  # Changed to string for formatted output
    total_volume_usd: str  # Changed to string for formatted output
    avg_transaction_size: str  # Changed to string for formatted output
    percentage_of_total: float

class TransactionOverview(BaseModel):
    total_transactions: int
    success_count: int
    success_rate: float
    total_volume_usd: str  # Changed to string for formatted output
    total_revenue_usd: str  # Changed to string for formatted output
    avg_transaction_size: str  # Changed to string for formatted output
    status_breakdown: Dict[str, Dict[str, Any]]  # {"success": {"count": 100, "volume_usd": "1,000.00", "revenue_usd": "50.00", "percentage": 50.0}}

class DailyTrendData(BaseModel):
    date: str  # YYYY-MM-DD format
    transaction_count: int
    success_count: int
    failed_count: int
    pending_count: int
    total_volume_usd: str  # Formatted currency
    total_revenue_usd: str  # Formatted currency
    avg_transaction_size_usd: str  # Formatted currency
    success_rate: float

class TransactionTrend(BaseModel):
    start_date: str
    end_date: str
    total_days: int
    daily_data: List[DailyTrendData]
    summary: Dict[str, Any]  # Overall summary stats

class TodayTransactionItem(BaseModel):
    id: str
    time: str  # HH:MM:SS format
    created_at: datetime
    status: str
    amount: str  # Original amount formatted
    currency: str
    amount_usd: str  # Converted to USD
    charge: str  # Original charge formatted
    charge_usd: str  # Charge in USD
    type: str
    description: Optional[str]
    from_wallet: Optional[str]
    to_wallet: Optional[str]
    recipient_name: Optional[str]
    recipient_country: Optional[str]

class TodayTransactionsSummary(BaseModel):
    date: str
    total_count: int
    success_count: int
    pending_count: int
    failed_count: int
    total_volume_usd: str
    total_revenue_usd: str
    transactions: List[TodayTransactionItem]

class WeeklyReportPeriod(BaseModel):
    start_date: str
    end_date: str
    week_number: int

class WeeklyReportCurrencyBreakdown(BaseModel):
    currency: str
    transaction_count: int
    volume_usd: str
    percentage: float

class WeeklyReportWeekMetrics(BaseModel):
    total_transactions: int
    success_count: int
    failed_count: int
    pending_count: int
    declined_count: int
    reversed_count: int
    processing_swap_count: int
    other_count: int
    success_percentage: float
    failed_percentage: float
    pending_percentage: float
    declined_percentage: float
    success_rate: float
    total_volume_usd: str
    avg_transaction_size_usd: str
    total_revenue_usd: str
    avg_fee_per_transaction_usd: str
    fees_to_value_ratio: float
    currency_breakdown: List[WeeklyReportCurrencyBreakdown]

class WeeklyReportChanges(BaseModel):
    transaction_volume_change_pct: float
    transaction_volume_change_absolute: int
    success_rate_change_pct: float
    revenue_change_pct: float
    revenue_change_absolute_usd: str
    avg_transaction_size_change_pct: float

class WeeklyPerformanceReport(BaseModel):
    period: WeeklyReportPeriod
    current_week: WeeklyReportWeekMetrics
    previous_week: WeeklyReportWeekMetrics
    week_over_week_changes: WeeklyReportChanges

class SendWeeklyEmailRequest(BaseModel):
    week_start_date: str  # YYYY-MM-DD format (Monday)
    recipients: List[EmailStr]
