
import os
import sys
from datetime import datetime
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock google module and app.gmail_service
sys.modules["google"] = MagicMock()
sys.modules["google.auth"] = MagicMock()
sys.modules["google.auth.transport"] = MagicMock()
sys.modules["google.auth.transport.requests"] = MagicMock()
sys.modules["app.gmail_service"] = MagicMock()

from app.email_service import generate_html_email

def test_generate_email():
    # Mock data
    report_data = {
        "period": {
            "start_date": "2023-10-23",
            "end_date": "2023-10-29"
        },
        "current_week": {
            "total_transactions": 15420,
            "success_count": 14200,
            "success_percentage": 92.1,
            "failed_count": 800,
            "failed_percentage": 5.2,
            "pending_count": 300,
            "pending_percentage": 1.9,
            "declined_count": 120,
            "declined_percentage": 0.8,
            "total_volume_usd": 1250000.50,
            "avg_transaction_size_usd": 81.06,
            "total_revenue_usd": 12500.00,
            "avg_fee_per_transaction_usd": 0.81,
            "fees_to_value_ratio": 1.0,
            "currency_breakdown": [
                {"currency": "USD", "transaction_count": 10000, "volume_usd": 800000, "percentage": 64.0},
                {"currency": "EUR", "transaction_count": 5420, "volume_usd": 450000.50, "percentage": 36.0}
            ]
        },
        "week_over_week_changes": {
            "transaction_volume_change_pct": 12.5,
            "transaction_volume_change_absolute": 1500,
            "success_rate_change_pct": 1.2,
            "revenue_change_pct": 10.0,
            "revenue_change_absolute_usd": 1100.00,
            "avg_transaction_size_change_pct": -2.1
        }
    }

    # Generate HTML
    html_content = generate_html_email(report_data)
    
    # Save to file
    output_path = "test_email_output.html"
    with open(output_path, "w") as f:
        f.write(html_content)
    
    print(f"Generated email saved to {output_path}")
    
    # Basic assertions
    if "data:image/png;base64," in html_content:
        print("PASS: Base64 logo found.")
    else:
        print("FAIL: Base64 logo not found.")
        
    if "🚀" in html_content or "💰" in html_content or "📈" in html_content:
        print("FAIL: Emojis found.")
    else:
        print("PASS: No common emojis found.")

if __name__ == "__main__":
    test_generate_email()
