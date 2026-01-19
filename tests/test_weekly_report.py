#!/usr/bin/env python3
"""
Test script for weekly report endpoints.

Usage:
    python test_weekly_report.py
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "http://localhost:8000"

def get_last_monday():
    """Get the date of last Monday in YYYY-MM-DD format."""
    today = datetime.now()
    days_since_monday = (today.weekday() - 0) % 7  # 0 = Monday
    last_monday = today - timedelta(days=days_since_monday + 7)
    return last_monday.strftime("%Y-%m-%d")

def test_weekly_performance_endpoint():
    """Test the GET /api/reports/weekly-performance endpoint."""
    print("\n" + "="*60)
    print("Testing GET /api/reports/weekly-performance")
    print("="*60)
    
    week_start_date = get_last_monday()
    print(f"\nWeek start date: {week_start_date}")
    
    url = f"{API_BASE_URL}/api/reports/weekly-performance"
    params = {"week_start_date": week_start_date}
    
    try:
        print(f"\nSending request to: {url}")
        response = requests.get(url, params=params)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS! Report generated successfully.")
            print("\nReport Summary:")
            print(f"  Period: {data['period']['start_date']} to {data['period']['end_date']}")
            print(f"  Week Number: {data['period']['week_number']}")
            print(f"\nCurrent Week Metrics:")
            print(f"  Total Transactions: {data['current_week']['total_transactions']:,}")
            print(f"  Success Count: {data['current_week']['success_count']:,} ({data['current_week']['success_rate']:.1f}%)")
            print(f"  Total Volume (USD): ${data['current_week']['total_volume_usd']}")
            print(f"  Total Revenue (USD): ${data['current_week']['total_revenue_usd']}")
            print(f"\nWeek-over-Week Changes:")
            print(f"  Transaction Volume: {data['week_over_week_changes']['transaction_volume_change_pct']:+.1f}%")
            print(f"  Success Rate: {data['week_over_week_changes']['success_rate_change_pct']:+.1f} pp")
            print(f"  Revenue: {data['week_over_week_changes']['revenue_change_pct']:+.1f}%")
            
            if data['current_week']['currency_breakdown']:
                print(f"\nTop Currencies:")
                for i, currency in enumerate(data['current_week']['currency_breakdown'][:3], 1):
                    print(f"  {i}. {currency['currency']}: {currency['transaction_count']:,} txns, ${currency['volume_usd']} ({currency['percentage']:.1f}%)")
            
            return True
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server.")
        print(f"   Make sure the server is running at {API_BASE_URL}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def test_weekly_email_endpoint():
    """Test the POST /api/reports/weekly-email endpoint."""
    print("\n" + "="*60)
    print("Testing POST /api/reports/weekly-email")
    print("="*60)
    
    week_start_date = get_last_monday()
    print(f"\nWeek start date: {week_start_date}")
    
    url = f"{API_BASE_URL}/api/reports/weekly-email"
    payload = {
        "week_start_date": week_start_date,
        "recipients": ["test@example.com"]
    }
    
    try:
        print(f"\nSending request to: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS! Email generated successfully.")
            print(f"\nSubject: {data['subject']}")
            print(f"Recipients: {', '.join(data['recipients'])}")
            print(f"\nReport Summary:")
            print(f"  Period: {data['report_summary']['period']['start_date']} to {data['report_summary']['period']['end_date']}")
            print(f"  Total Transactions: {data['report_summary']['total_transactions']:,}")
            print(f"  Total Volume (USD): ${data['report_summary']['total_volume_usd']}")
            print(f"  Total Revenue (USD): ${data['report_summary']['total_revenue_usd']}")
            print(f"  Success Rate: {data['report_summary']['success_rate']:.1f}%")
            
            if 'note' in data:
                print(f"\n⚠️  Note: {data['note']}")
            
            return True
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server.")
        print(f"   Make sure the server is running at {API_BASE_URL}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Weekly Report Endpoints Test Suite")
    print("="*60)
    print(f"\nAPI Base URL: {API_BASE_URL}")
    print(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test both endpoints
    test1_passed = test_weekly_performance_endpoint()
    test2_passed = test_weekly_email_endpoint()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"GET /api/reports/weekly-performance: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"POST /api/reports/weekly-email: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed!")
        print("\nNext steps:")
        print("1. Configure email credentials in .env file")
        print("2. Uncomment email sending code in app/main.py")
        print("3. Restart the server")
        print("4. Test email sending with real recipients")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
