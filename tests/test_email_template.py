"""
Test script to verify email template generation
"""

from decimal import Decimal
from datetime import datetime

# Mock report data for testing
mock_report_data = {
    "period": {
        "start_date": "2026-01-13",
        "end_date": "2026-01-19",
        "week_number": 3
    },
    "current_week": {
        "total_transactions": 1234,
        "success_count": 1145,
        "failed_count": 45,
        "pending_count": 34,
        "declined_count": 10,
        "reversed_count": 0,
        "processing_swap_count": 0,
        "other_count": 0,
        "success_percentage": 92.8,
        "failed_percentage": 3.6,
        "pending_percentage": 2.8,
        "declined_percentage": 0.8,
        "success_rate": 92.8,
        "total_volume_usd": "567890.50",
        "avg_transaction_size_usd": "460.15",
        "total_revenue_usd": "1234.56",
        "avg_fee_per_transaction_usd": "1.00",
        "fees_to_value_ratio": 0.22,
        "currency_breakdown": [
            {
                "currency": "USD",
                "transaction_count": 456,
                "volume_usd": "234567.00",
                "percentage": 41.3
            },
            {
                "currency": "NGN",
                "transaction_count": 345,
                "volume_usd": "123456.00",
                "percentage": 21.7
            },
            {
                "currency": "EUR",
                "transaction_count": 234,
                "volume_usd": "98765.00",
                "percentage": 17.4
            },
            {
                "currency": "KES",
                "transaction_count": 123,
                "volume_usd": "67890.00",
                "percentage": 12.0
            },
            {
                "currency": "GBP",
                "transaction_count": 76,
                "volume_usd": "43212.50",
                "percentage": 7.6
            }
        ]
    },
    "previous_week": {
        "total_transactions": 1173,
        "success_count": 1080,
        "failed_count": 50,
        "pending_count": 33,
        "declined_count": 10,
        "success_rate": 92.0,
        "total_volume_usd": "539500.00",
        "avg_transaction_size_usd": "450.50",
        "total_revenue_usd": "1140.00",
        "avg_fee_per_transaction_usd": "0.97",
        "fees_to_value_ratio": 0.21
    },
    "week_over_week_changes": {
        "transaction_volume_change_pct": 5.2,
        "transaction_volume_change_absolute": 61,
        "success_rate_change_pct": 0.8,
        "revenue_change_pct": 8.3,
        "revenue_change_absolute_usd": "94.56",
        "avg_transaction_size_change_pct": 2.1
    }
}

if __name__ == "__main__":
    from app.email_service import generate_html_email, generate_plain_text_email
    
    print("Generating HTML email template...")
    html_content = generate_html_email(mock_report_data)
    
    print("Generating plain text email template...")
    text_content = generate_plain_text_email(mock_report_data)
    
    # Save to files for inspection
    with open("test_email_output.html", "w") as f:
        f.write(html_content)
    
    with open("test_email_output.txt", "w") as f:
        f.write(text_content)
    
    print("\n✅ Email templates generated successfully!")
    print("📄 HTML output saved to: test_email_output.html")
    print("📄 Text output saved to: test_email_output.txt")
    print("\nYou can open test_email_output.html in a browser to preview the email.")
