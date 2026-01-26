# SpennX Live Pulse Dashboard API

FastAPI backend for the SpennX Live Pulse Dashboard with comprehensive transaction analytics and automated reporting.

## Features

- 📊 Real-time transaction monitoring and analytics
- 💰 Multi-currency support with USD conversion
- 📈 Transaction trends and performance metrics
- 📧 Automated weekly performance email reports with professional design
- 🎨 Beautiful HTML email templates with system fonts and gradients
- 🔍 Advanced filtering and date range queries
- 📱 Mobile-responsive email templates

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Run the Application

```bash
python -m uvicorn app.main:app --reload
```

Or with Docker:
```bash
docker compose up -d --build
docker compose logs -f
docker compose down
```

## API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/transactions` - List transactions (paginated)
- `GET /api/transactions/{transaction_id}` - Get specific transaction
- `GET /api/transactions/status/{status}` - Filter by status

### Analytics Endpoints
- `GET /api/live-view` - Transactions live view by time intervals
- `GET /api/transaction-pulse` - Real-time transaction pulse metrics
- `GET /api/net-income` - Net income statistics
- `GET /api/analytics/custom-range` - Custom date range analytics
- `GET /api/analytics/status-breakdown` - Transaction status breakdown
- `GET /api/analytics/currency-breakdown` - Currency volume breakdown
- `GET /api/analytics/transaction-overview` - Comprehensive transaction overview
- `GET /api/analytics/daily-trend` - Daily transaction trends
- `GET /api/transactions/today` - Today's transactions with USD conversion

### Weekly Report Endpoints
- `GET /api/reports/weekly-performance` - Get weekly performance report data
- `POST /api/reports/weekly-email` - Generate and send weekly email report

## Weekly Email Reports

Automated weekly transaction performance reports with:
- Transaction volume and success rate metrics
- Revenue and fee analysis
- Currency distribution (top 5)
- Week-over-week comparison
- Dynamic insights generation
- Professional HTML email template
- **Gmail API integration** (OAuth2, no passwords!)

### Quick Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Authenticate with Gmail API
python setup_gmail_api.py

# 3. Test email sending
python test_weekly_report.py
```

See **[docs/GMAIL_API_SETUP.md](docs/GMAIL_API_SETUP.md)** for detailed setup instructions.

## Documentation

### 📚 Complete Documentation

All documentation is organized in the **[docs/](docs/)** folder:

- **[docs/README.md](docs/README.md)** - Documentation index
- **[docs/GMAIL_API_SETUP.md](docs/GMAIL_API_SETUP.md)** - Gmail API setup guide
- **[docs/WEEKLY_EMAIL_QUICK_START.md](docs/WEEKLY_EMAIL_QUICK_START.md)** - Quick start guide
- **[docs/WEEKLY_EMAIL_IMPLEMENTATION.md](docs/WEEKLY_EMAIL_IMPLEMENTATION.md)** - Technical documentation
- **[docs/API_TESTING.md](docs/API_TESTING.md)** - API testing guide
- **[docs/CHANGELOG.md](docs/CHANGELOG.md)** - Version history

### 🚀 Quick Links

- **Getting Started**: [docs/WEEKLY_EMAIL_QUICK_START.md](docs/WEEKLY_EMAIL_QUICK_START.md)
- **Gmail Setup**: [docs/GMAIL_API_SETUP.md](docs/GMAIL_API_SETUP.md)
- **API Reference**: [docs/NEW_ENDPOINTS_SUMMARY.md](docs/NEW_ENDPOINTS_SUMMARY.md)
- **Architecture**: [docs/WEEKLY_EMAIL_ARCHITECTURE.md](docs/WEEKLY_EMAIL_ARCHITECTURE.md)

### 🔧 Interactive API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

### Automated Tests

```bash
# Test weekly report endpoints
python test_weekly_report.py

# Test Gmail API connection
python setup_gmail_api.py
```

### Manual Testing

```bash
# Get weekly report data
curl "http://localhost:8000/api/reports/weekly-performance?week_start_date=2026-01-13"

# Send test email
curl -X POST "http://localhost:8000/api/reports/weekly-email" \
  -H "Content-Type: application/json" \
  -d '{
    "week_start_date": "2026-01-13",
    "recipients": ["your-email@gmail.com"]
  }'
```

## Project Structure

```
SpennX-Dashboard-API/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── reports.py           # Report generation
│   ├── email_service.py     # Email templates
│   ├── gmail_service.py     # Gmail API integration
│   └── ...
├── docs/                    # 📚 All documentation
│   ├── README.md            # Documentation index
│   ├── GMAIL_API_SETUP.md   # Gmail setup guide
│   └── ...
├── credentials.json         # Gmail API credentials
├── setup_gmail_api.py       # Gmail setup script
├── test_weekly_report.py    # Test script
├── requirements.txt         # Python dependencies
├── .env                     # Configuration
└── README.md               # This file
```

## Configuration

### Environment Variables

```env
# Database
DATABASE_URL=mysql+pymysql://user:pass@host:3306/db

# API
API_HOST=0.0.0.0
API_PORT=8000

# Weekly Email (Gmail API)
WEEKLY_REPORT_SENDER_EMAIL=finance@spennx.com
```

### Gmail API Setup

1. Ensure `credentials.json` is in project root
2. Run `python setup_gmail_api.py` to authenticate
3. Token will be saved to `token.pickle`

See **[docs/GMAIL_API_SETUP.md](docs/GMAIL_API_SETUP.md)** for detailed instructions.

## Technology Stack

- **Framework**: FastAPI 0.115.0
- **Database**: MySQL (via SQLAlchemy)
- **Email**: Gmail API (OAuth2)
- **Authentication**: Google OAuth2
- **Validation**: Pydantic
- **Server**: Uvicorn

## Version

**Current Version**: 2.1.1

See **[docs/CHANGELOG.md](docs/CHANGELOG.md)** for version history.

## Features Highlights

### Real-time Analytics
- Live transaction monitoring
- Transaction pulse metrics
- Net income statistics
- Multi-currency support

### Weekly Reports
- Automated email reports
- Professional HTML templates
- Dynamic insights generation
- Week-over-week comparison

### Gmail API Integration
- OAuth2 authentication
- No passwords needed
- Automatic token refresh
- Production-ready

## Support

### Documentation
- **All Docs**: [docs/](docs/)
- **Quick Start**: [docs/WEEKLY_EMAIL_QUICK_START.md](docs/WEEKLY_EMAIL_QUICK_START.md)
- **Gmail Setup**: [docs/GMAIL_API_SETUP.md](docs/GMAIL_API_SETUP.md)

### Testing
```bash
python test_weekly_report.py
python setup_gmail_api.py
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

Copyright © 2026 SpennX

---

**Ready to get started?** See [docs/WEEKLY_EMAIL_QUICK_START.md](docs/WEEKLY_EMAIL_QUICK_START.md)
