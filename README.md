# SpennX Live Pulse Dashboard API

FastAPI backend for the SpennX Live Pulse Dashboard.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Run the application:
```bash
python -m app.main
```

Or with uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Health check
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/transactions` - List transactions (paginated)
- `GET /api/transactions/{transaction_id}` - Get specific transaction
- `GET /api/transactions/status/{status}` - Filter by status

## Documentation

Interactive API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
