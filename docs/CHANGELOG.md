# Changelog

All notable changes to the SpennX Dashboard API will be documented in this file.

## [2.1.0] - 2026-01-18

### Added - Weekly Email Report Feature

#### New Modules
- **`app/reports.py`**: Complete report generation module
  - Week boundary calculations
  - Transaction metrics aggregation
  - Currency conversion and breakdown
  - Week-over-week comparison analytics
  
- **`app/email_service.py`**: Email template and delivery module
  - Professional HTML email template with responsive design
  - Plain text email fallback
  - Dynamic insights generation
  - SMTP email sending (Gmail support)
  - Color-coded metrics and indicators

#### New API Endpoints
- **`GET /api/reports/weekly-performance`**: Get weekly performance report data as JSON
  - Returns current week metrics
  - Returns previous week metrics
  - Returns week-over-week changes
  - Returns top 5 currencies breakdown
  
- **`POST /api/reports/weekly-email`**: Generate and send weekly email report
  - Accepts week start date and recipient list
  - Generates HTML and plain text email
  - Sends via SMTP (configurable)
  - Returns report summary

#### New Schemas
- `WeeklyReportPeriod`: Period information (start, end, week number)
- `WeeklyReportCurrencyBreakdown`: Currency breakdown data
- `WeeklyReportWeekMetrics`: Complete week metrics
- `WeeklyReportChanges`: Week-over-week changes
- `WeeklyPerformanceReport`: Complete report structure
- `SendWeeklyEmailRequest`: Email request body

#### Documentation
- `WEEKLY_EMAIL_IMPLEMENTATION.md`: Complete technical documentation
- `WEEKLY_EMAIL_QUICK_START.md`: Quick start guide
- `WEEKLY_EMAIL_SUMMARY.md`: Implementation summary
- `WEEKLY_EMAIL_ARCHITECTURE.md`: System architecture diagrams
- `weekly-email-specification.md`: Original requirements (existing)

#### Testing & Tools
- `test_weekly_report.py`: Automated test script for new endpoints
- `Weekly_Email_Report.postman_collection.json`: Postman collection for API testing

#### Configuration
- Added email configuration variables to `.env.example`:
  - `WEEKLY_REPORT_SENDER_EMAIL`
  - `WEEKLY_REPORT_SENDER_PASSWORD`
  - `WEEKLY_REPORT_SMTP_SERVER`
  - `WEEKLY_REPORT_SMTP_PORT`

#### Features
- ✅ Automated weekly transaction performance reports
- ✅ Multi-currency support with USD conversion
- ✅ Week-over-week comparison analytics
- ✅ Top 5 currencies breakdown
- ✅ Dynamic insights generation based on data patterns
- ✅ Professional HTML email template
- ✅ Mobile-responsive email design
- ✅ Plain text email fallback
- ✅ Color-coded metrics (green/red/gray indicators)
- ✅ SMTP email sending (Gmail configured)
- ✅ n8n automation ready
- ✅ Comprehensive error handling
- ✅ Input validation

### Changed
- Updated `README.md` with weekly email feature information
- Updated `app/schemas.py` with new report schemas
- Updated `app/main.py` with new endpoints and imports

### Technical Details

**Metrics Included**:
- Transaction counts by status (success, failed, pending, declined, etc.)
- Total volume and average transaction size (USD)
- Total revenue and average fee per transaction (USD)
- Fees-to-value ratio
- Success rate and error rate
- Currency distribution (top 5)
- Week-over-week changes (percentage and absolute)

**Email Template Features**:
- Professional header with branding
- Card-based metric display
- Clean table for currency breakdown
- Color-coded week-over-week comparison
- Dynamic insights section (2-4 insights)
- Professional footer with timestamp
- Inline CSS for email client compatibility
- Mobile-responsive design

**Integration**:
- RESTful API design
- JSON request/response format
- Designed for n8n automation
- SMTP email delivery
- Environment-based configuration

### Security
- Email credentials stored in environment variables
- Input validation on all parameters
- SQL injection prevention via SQLAlchemy ORM
- Error messages don't expose sensitive data
- HTTPS recommended for production

### Performance
- Efficient database queries with aggregation
- Minimal data transfer
- Batch processing for currency conversion
- Optimized for weekly data volumes

---

## [2.0.0] - Previous Release

### Added
- Live transaction monitoring endpoints
- Transaction pulse metrics
- Net income statistics
- Custom date range analytics
- Status breakdown analytics
- Currency breakdown analytics
- Transaction overview
- Daily trend analytics
- Today's transactions endpoint

### Features
- Multi-currency support with USD conversion
- Real-time transaction monitoring
- Advanced filtering and date range queries
- Comprehensive analytics endpoints
- Interactive API documentation (Swagger/ReDoc)

---

## [1.0.0] - Initial Release

### Added
- Basic transaction API
- Dashboard statistics
- Transaction listing with pagination
- Transaction filtering by status
- Database integration (MySQL)
- Docker support
- Environment-based configuration

---

## Notes

### Version Numbering
- **Major version** (X.0.0): Breaking changes or major new features
- **Minor version** (0.X.0): New features, backward compatible
- **Patch version** (0.0.X): Bug fixes, backward compatible

### Upgrade Instructions

#### From 2.0.0 to 2.1.0

1. **Update code**:
   ```bash
   git pull origin main
   ```

2. **Update environment variables**:
   ```bash
   # Add to .env file
   WEEKLY_REPORT_SENDER_EMAIL=finance@spennx.com
   WEEKLY_REPORT_SENDER_PASSWORD=your_app_password
   WEEKLY_REPORT_SMTP_SERVER=smtp.gmail.com
   WEEKLY_REPORT_SMTP_PORT=587
   ```

3. **Restart application**:
   ```bash
   # Docker
   docker-compose restart
   
   # Or direct
   python -m uvicorn app.main:app --reload
   ```

4. **Test new endpoints**:
   ```bash
   python test_weekly_report.py
   ```

5. **Enable email sending** (optional):
   - Uncomment email sending code in `app/main.py`
   - Configure Gmail App Password
   - Restart server

6. **Set up automation** (optional):
   - Create n8n workflow
   - Schedule for Sunday 9:00 AM
   - Configure recipient list

### Breaking Changes
- None in this release (backward compatible)

### Deprecations
- None in this release

### Known Issues
- Email sending is disabled by default (requires manual configuration)
- Gmail has daily sending limit of 500 emails
- Large date ranges may cause slow response times

### Future Roadmap
- Built-in scheduler (remove n8n dependency)
- Multiple email templates
- PDF report generation
- Email engagement tracking
- Multi-language support
- Embedded chart images
- Web UI for report preview
- Slack/Teams integration
