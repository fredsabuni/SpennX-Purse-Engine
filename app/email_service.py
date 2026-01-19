"""
Email Service Module

Handles email template generation and sending for weekly performance reports.
Uses Gmail API for reliable email delivery.
"""

from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime
from app.gmail_service import send_gmail_message
from app.config import settings
import os
import base64


def format_number(value: str) -> str:
    """Format number with thousand separators"""
    try:
        num = Decimal(value)
        return f"{num:,.2f}"
    except:
        return value


def get_change_indicator(change_pct: float) -> tuple[str, str]:
    """
    Get indicator symbol and color based on change percentage.
    
    Returns:
        Tuple of (symbol, color)
    """
    if abs(change_pct) < 2:
        return "→", "#6B7280"  # Neutral gray
    elif change_pct > 0:
        return "↑", "#10B981"  # Green
    else:
        return "↓", "#EF4444"  # Red



def generate_html_email(report_data: Dict[str, Any]) -> str:
    """
    Generate HTML email from report data.
    
    Args:
        report_data: Complete report data structure
    
    Returns:
        HTML email content
    """
    period = report_data["period"]
    current = report_data["current_week"]
    changes = report_data["week_over_week_changes"]
    
    # Format dates
    start_date = datetime.strptime(period["start_date"], "%Y-%m-%d").strftime("%b %d")
    end_date = datetime.strptime(period["end_date"], "%Y-%m-%d").strftime("%b %d, %Y")
    date_range = f"{start_date} to {end_date}"
    
    # Get branding info
    company_name = settings.company_name
    
    # Get change indicators (Using text colors instead of arrows for cleaner look, or simple arrows)
    # We will stick to simple arrows but remove the emojis from the rest of the text
    
    # Build currency breakdown HTML
    currency_rows = ""
    for idx, currency_data in enumerate(current["currency_breakdown"], 1):
        bg_color = "#FAFBFC" if idx % 2 == 0 else "#FFFFFF"
        currency_rows += f"""
        <tr style="background-color: {bg_color};">
            <td style="padding: 12px 16px; text-align: left; color: #1F2937; font-size: 14px; font-weight: 500; border-bottom: 1px solid #F3F4F6;">{currency_data['currency']}</td>
            <td style="padding: 12px 16px; text-align: right; color: #4B5563; font-size: 14px; font-weight: 400; border-bottom: 1px solid #F3F4F6;">{currency_data['transaction_count']:,}</td>
            <td style="padding: 12px 16px; text-align: right; color: #1F2937; font-size: 14px; font-weight: 600; border-bottom: 1px solid #F3F4F6;">${format_number(currency_data['volume_usd'])}</td>
            <td style="padding: 12px 16px; text-align: right; color: #317CFF; font-size: 14px; font-weight: 600; border-bottom: 1px solid #F3F4F6;">{currency_data['percentage']:.1f}%</td>
        </tr>
        """
    
    # Generate insights based on data
    insights = generate_insights(current, changes)
    insights_html = "".join([f"<li style='margin-bottom: 12px; color: #4B5563;'>{insight}</li>" for insight in insights])
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Transaction Performance Report</title>
    <style>
        @media only screen and (max-width: 600px) {{
            .container {{
                width: 100% !important;
            }}
            .metric-card {{
                display: block !important;
                width: 100% !important;
                margin-bottom: 12px !important;
            }}
            .metric-table {{
                font-size: 13px !important;
            }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #F3F4F6;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #F3F4F6; padding: 40px 20px; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
        <tr>
            <td align="center">
                <table class="container" width="600" cellpadding="0" cellspacing="0" style="background-color: #FFFFFF; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                    


                    <!-- Header with Gradient -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #317CFF 0%, #1E5FD9 100%); padding: 32px 40px; text-align: center;">
                            <h1 style="margin: 0; color: #FFFFFF; font-size: 24px; font-weight: 600; letter-spacing: 0.5px;">
                                Weekly Performance Report
                            </h1>
                            <p style="margin: 8px 0 0 0; color: rgba(255,255,255,0.9); font-size: 15px; font-weight: 500;">
                                {date_range}
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Content Area -->
                    <tr>
                        <td style="padding: 40px;">
                            
                            <!-- Greeting & Summary -->
                            <p style="margin: 0 0 24px 0; color: #1F2937; font-size: 16px; line-height: 1.6;">
                                Dear Team,
                            </p>
                            <p style="margin: 0 0 32px 0; color: #4B5563; font-size: 16px; line-height: 1.6;">
                                Here is the transaction performance summary for <strong style="color: #1F2937;">{date_range}</strong>. 
                                We observed <strong style="color: {'#10B981' if changes['transaction_volume_change_pct'] > 5 else '#317CFF' if changes['transaction_volume_change_pct'] > -5 else '#EF4444'};">{'strong' if changes['transaction_volume_change_pct'] > 5 else 'stable' if changes['transaction_volume_change_pct'] > -5 else 'challenging'}</strong> 
                                performance across key metrics.
                            </p>
                            
                            <!-- Core Metrics Section -->
                            <h2 style="margin: 0 0 16px 0; color: #111827; font-size: 18px; font-weight: 700; border-bottom: 2px solid #E5E7EB; padding-bottom: 8px;">
                                Performance Snapshot
                            </h2>
                            
                            <!-- Transaction Volume -->
                            <div style="background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; padding: 20px; margin-bottom: 16px;">
                                <h3 style="margin: 0 0 16px 0; color: #374151; font-size: 15px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                    Transaction Volume
                                </h3>
                                <table width="100%" cellpadding="0" cellspacing="0" class="metric-table">
                                    <tr>
                                        <td style="padding: 4px 0; color: #6B7280; font-size: 14px;">Total Transactions</td>
                                        <td style="padding: 4px 0; color: #111827; font-size: 15px; font-weight: 600; text-align: right;">
                                            {current['total_transactions']:,}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 4px 0; color: #6B7280; font-size: 14px;">Successful</td>
                                        <td style="padding: 4px 0; color: #10B981; font-size: 15px; font-weight: 600; text-align: right;">
                                            {current['success_count']:,} <span style="color: #6B7280; font-weight: 400; font-size: 13px;">({current['success_percentage']:.1f}%)</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 4px 0; color: #6B7280; font-size: 14px;">Failed</td>
                                        <td style="padding: 4px 0; color: #EF4444; font-size: 15px; font-weight: 600; text-align: right;">
                                            {current['failed_count']:,} <span style="color: #6B7280; font-weight: 400; font-size: 13px;">({current['failed_percentage']:.1f}%)</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 4px 0; color: #6B7280; font-size: 14px;">Pending</td>
                                        <td style="padding: 4px 0; color: #F59E0B; font-size: 15px; font-weight: 600; text-align: right;">
                                            {current['pending_count']:,} <span style="color: #6B7280; font-weight: 400; font-size: 13px;">({current['pending_percentage']:.1f}%)</span>
                                        </td>
                                    </tr>
                                     <tr>
                                        <td style="padding: 4px 0; color: #6B7280; font-size: 14px;">Declined</td>
                                        <td style="padding: 4px 0; color: #6B7280; font-size: 15px; font-weight: 600; text-align: right;">
                                            {current['declined_count']:,} <span style="color: #9CA3AF; font-weight: 400; font-size: 13px;">({current['declined_percentage']:.1f}%)</span>
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            
                            <!-- Transaction Value -->
                            <div style="background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; padding: 20px; margin-bottom: 16px;">
                                <h3 style="margin: 0 0 16px 0; color: #374151; font-size: 15px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                    Transaction Value
                                </h3>
                                <table width="100%" cellpadding="0" cellspacing="0" class="metric-table">
                                    <tr>
                                        <td style="padding: 4px 0; color: #6B7280; font-size: 14px;">Total Volume</td>
                                        <td style="padding: 4px 0; color: #111827; font-size: 15px; font-weight: 600; text-align: right;">
                                            ${format_number(current['total_volume_usd'])} 
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 4px 0; color: #6B7280; font-size: 14px;">Average Transaction</td>
                                        <td style="padding: 4px 0; color: #111827; font-size: 15px; font-weight: 600; text-align: right;">
                                            ${format_number(current['avg_transaction_size_usd'])}
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            
                            <!-- Revenue Performance -->
                            <div style="background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; padding: 20px; margin-bottom: 32px;">
                                <h3 style="margin: 0 0 16px 0; color: #374151; font-size: 15px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">
                                    Revenue Performance
                                </h3>
                                <table width="100%" cellpadding="0" cellspacing="0" class="metric-table">
                                    <tr>
                                        <td style="padding: 4px 0; color: #6B7280; font-size: 14px;">Total Fees Collected</td>
                                        <td style="padding: 4px 0; color: #111827; font-size: 15px; font-weight: 600; text-align: right;">
                                            ${format_number(current['total_revenue_usd'])} 
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 4px 0; color: #6B7280; font-size: 14px;">Avg Fee per Txn</td>
                                        <td style="padding: 4px 0; color: #111827; font-size: 15px; font-weight: 600; text-align: right;">
                                            ${format_number(current['avg_fee_per_transaction_usd'])}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 4px 0; color: #6B7280; font-size: 14px;">Fees-to-Value Ratio</td>
                                        <td style="padding: 4px 0; color: #111827; font-size: 15px; font-weight: 600; text-align: right;">
                                            {current['fees_to_value_ratio']:.2f}%
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            
                            <!-- Currency Distribution -->
                            <h2 style="margin: 0 0 16px 0; color: #111827; font-size: 18px; font-weight: 700; border-bottom: 2px solid #E5E7EB; padding-bottom: 8px;">
                                Currency Distribution
                            </h2>
                            <table width="100%" cellpadding="0" cellspacing="0" style="border: 1px solid #E5E7EB; border-radius: 8px; overflow: hidden; margin-bottom: 32px;">
                                <thead>
                                    <tr style="background-color: #F9FAFB;">
                                        <th style="padding: 12px 16px; text-align: left; color: #4B5563; font-size: 12px; font-weight: 600; text-transform: uppercase;">Currency</th>
                                        <th style="padding: 12px 16px; text-align: right; color: #4B5563; font-size: 12px; font-weight: 600; text-transform: uppercase;">Txns</th>
                                        <th style="padding: 12px 16px; text-align: right; color: #4B5563; font-size: 12px; font-weight: 600; text-transform: uppercase;">Volume</th>
                                        <th style="padding: 12px 16px; text-align: right; color: #4B5563; font-size: 12px; font-weight: 600; text-transform: uppercase;">%</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {currency_rows}
                                </tbody>
                            </table>
                            
                            <!-- Week-over-Week Comparison -->
                            <h2 style="margin: 0 0 16px 0; color: #111827; font-size: 18px; font-weight: 700; border-bottom: 2px solid #E5E7EB; padding-bottom: 8px;">
                                Week-over-Week Comparison
                            </h2>
                            <div style="background-color: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 8px; padding: 20px; margin-bottom: 32px;">
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td style="padding: 8px 0; color: #6B7280; font-size: 14px; border-bottom: 1px solid #E5E7EB;">Transaction Volume</td>
                                        <td style="padding: 8px 0; color: #111827; font-size: 15px; font-weight: 600; text-align: right; border-bottom: 1px solid #E5E7EB;">
                                            {'+' if changes['transaction_volume_change_pct'] > 0 else ''}{changes['transaction_volume_change_pct']:.1f}% 
                                            <span style="color: #6B7280; font-size: 13px; font-weight: 400; margin-left: 4px;">({'+' if changes['transaction_volume_change_absolute'] > 0 else ''}{changes['transaction_volume_change_absolute']:,})</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px 0; color: #6B7280; font-size: 14px; border-bottom: 1px solid #E5E7EB;">Success Rate</td>
                                        <td style="padding: 8px 0; color: #111827; font-size: 15px; font-weight: 600; text-align: right; border-bottom: 1px solid #E5E7EB;">
                                            {'+' if changes['success_rate_change_pct'] > 0 else ''}{changes['success_rate_change_pct']:.1f} pts
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px 0; color: #6B7280; font-size: 14px; border-bottom: 1px solid #E5E7EB;">Revenue</td>
                                        <td style="padding: 8px 0; color: #111827; font-size: 15px; font-weight: 600; text-align: right; border-bottom: 1px solid #E5E7EB;">
                                            {'+' if changes['revenue_change_pct'] > 0 else ''}{changes['revenue_change_pct']:.1f}%
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px 0; color: #6B7280; font-size: 14px;">Avg Transaction Size</td>
                                        <td style="padding: 8px 0; color: #111827; font-size: 15px; font-weight: 600; text-align: right;">
                                            {'+' if changes['avg_transaction_size_change_pct'] > 0 else ''}{changes['avg_transaction_size_change_pct']:.1f}%
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            
                            <!-- Key Insights -->
                            <h2 style="margin: 0 0 16px 0; color: #111827; font-size: 18px; font-weight: 700; border-bottom: 2px solid #E5E7EB; padding-bottom: 8px;">
                                Key Insights
                            </h2>
                            <ul style="margin: 0; padding-left: 20px; color: #4B5563; font-size: 15px; line-height: 1.6;">
                                {insights_html}
                            </ul>

                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #F9FAFB; padding: 24px 30px; text-align: center; border-top: 1px solid #E5E7EB;">
                            <p style="margin: 0; color: #6B7280; font-size: 12px; line-height: 1.6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;">
                                <strong style="color: #1F2937; font-weight: 600;">SpennX Transaction Performance Report</strong><br>
                                Generated on {datetime.now().strftime("%B %d, %Y at %H:%M UTC")}
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """
    
    return html


def generate_insights(current: Dict[str, Any], changes: Dict[str, Any]) -> List[str]:
    """
    Generate dynamic insights based on the data.
    
    Args:
        current: Current week metrics
        changes: Week-over-week changes
    
    Returns:
        List of insight strings
    """
    insights = []
    
    # Success rate insight
    if changes["success_rate_change_pct"] > 2:
        insights.append(
            f"Success rate improved to {current['success_percentage']:.1f}%, "
            f"up {changes['success_rate_change_pct']:.1f} percentage points from last week, "
            f"reflecting enhanced payment gateway stability"
        )
    elif changes["success_rate_change_pct"] < -2:
        insights.append(
            f"Success rate decreased to {current['success_percentage']:.1f}%, "
            f"down {abs(changes['success_rate_change_pct']):.1f} percentage points from last week, "
            f"requiring attention to payment processing"
        )
    else:
        insights.append(
            f"Success rate remained stable at {current['success_percentage']:.1f}%, "
            f"demonstrating consistent platform reliability"
        )
    
    # Volume insight
    if changes["transaction_volume_change_pct"] > 10:
        insights.append(
            f"Transaction volume surged by {changes['transaction_volume_change_pct']:.1f}%, "
            f"indicating strong user engagement and platform growth"
        )
    elif changes["transaction_volume_change_pct"] < -10:
        insights.append(
            f"Transaction volume declined by {abs(changes['transaction_volume_change_pct']):.1f}%, "
            f"suggesting need for user engagement initiatives"
        )
    
    # Revenue insight
    if changes["revenue_change_pct"] > 5:
        insights.append(
            f"Revenue increased by {changes['revenue_change_pct']:.1f}%, "
            f"demonstrating strong monetization performance"
        )
    
    # Currency insight
    if current["currency_breakdown"]:
        top_currency = current["currency_breakdown"][0]
        insights.append(
            f"{top_currency['currency']} transactions continue to dominate, "
            f"representing {top_currency['percentage']:.1f}% of total volume"
        )
    
    # Failed transactions insight
    if current["failed_percentage"] > 5:
        insights.append(
            f"Failed transaction rate at {current['failed_percentage']:.1f}% requires attention "
            f"to improve overall platform performance"
        )
    
    return insights[:4]  # Return max 4 insights


def generate_plain_text_email(report_data: Dict[str, Any]) -> str:
    """
    Generate plain text email fallback.
    
    Args:
        report_data: Complete report data structure
    
    Returns:
        Plain text email content
    """
    period = report_data["period"]
    current = report_data["current_week"]
    changes = report_data["week_over_week_changes"]
    
    # Format dates
    start_date = datetime.strptime(period["start_date"], "%Y-%m-%d").strftime("%b %d")
    end_date = datetime.strptime(period["end_date"], "%Y-%m-%d").strftime("%b %d, %Y")
    date_range = f"{start_date} to {end_date}"
    
    text = f"""
Weekly Transaction Performance Report - {date_range}

Dear Team,

I am pleased to share our transaction performance for the week of {date_range}.

WEEKLY PERFORMANCE SNAPSHOT

Transaction Volume:
- Total Transactions: {current['total_transactions']:,}
- Successful: {current['success_count']:,} ({current['success_percentage']:.1f}%)
- Failed: {current['failed_count']:,} ({current['failed_percentage']:.1f}%)
- Pending: {current['pending_count']:,} ({current['pending_percentage']:.1f}%)
- Declined: {current['declined_count']:,} ({current['declined_percentage']:.1f}%)

Transaction Value:
- Total Volume: ${format_number(current['total_volume_usd'])}
- Average Transaction: ${format_number(current['avg_transaction_size_usd'])}

Revenue Performance:
- Total Fees Collected: ${format_number(current['total_revenue_usd'])}
- Average Fee per Transaction: ${format_number(current['avg_fee_per_transaction_usd'])}
- Fees-to-Value Ratio: {current['fees_to_value_ratio']:.2f}%

CURRENCY DISTRIBUTION

"""
    
    for idx, currency_data in enumerate(current["currency_breakdown"], 1):
        text += f"{idx}. {currency_data['currency']} - {currency_data['transaction_count']:,} transactions, ${format_number(currency_data['volume_usd'])} ({currency_data['percentage']:.1f}%)\n"
    
    text += f"""
WEEK-OVER-WEEK COMPARISON

- Transaction Volume: {'+' if changes['transaction_volume_change_pct'] > 0 else ''}{changes['transaction_volume_change_pct']:.1f}% ({'+' if changes['transaction_volume_change_absolute'] > 0 else ''}{changes['transaction_volume_change_absolute']:,} transactions)
- Success Rate: {'+' if changes['success_rate_change_pct'] > 0 else ''}{changes['success_rate_change_pct']:.1f} percentage points
- Revenue: {'+' if changes['revenue_change_pct'] > 0 else ''}{changes['revenue_change_pct']:.1f}% (${format_number(changes['revenue_change_absolute_usd'])})
- Average Transaction Size: {'+' if changes['avg_transaction_size_change_pct'] > 0 else ''}{changes['avg_transaction_size_change_pct']:.1f}%

Thank you for your continued dedication to maintaining our platform's reliability and performance.

Best regards,
Finance Team

---
SpennX Transaction Performance Report
Generated on {datetime.now().strftime("%B %d, %Y at %H:%M UTC")}
"""
    
    return text


def send_email(
    recipients: List[str],
    subject: str,
    html_content: str,
    plain_text_content: str,
    sender_email: str = None,
    **kwargs  # Accept but ignore SMTP-related kwargs for backward compatibility
) -> bool:
    """
    Send email using Gmail API.
    
    Args:
        recipients: List of recipient email addresses
        subject: Email subject
        html_content: HTML email content
        plain_text_content: Plain text fallback content
        sender_email: Sender email address (optional, uses authenticated user if not provided)
        **kwargs: Additional arguments (ignored, for backward compatibility)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        return send_gmail_message(
            recipients=recipients,
            subject=subject,
            html_content=html_content,
            plain_text_content=plain_text_content,
            sender_email=sender_email
        )
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
