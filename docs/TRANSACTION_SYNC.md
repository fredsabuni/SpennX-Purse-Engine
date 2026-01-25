# Transaction Cache Sync Module

## Overview

The Transaction Sync module provides automated and manual synchronization of transaction data from the external SpennX API (`https://app.spennx.com/api/v1/globaltransactions`) to a local cache database.

## Features

- **Full Sync**: Fetch all transactions from all pages and cache them locally
- **Daily Sync**: Fetch transactions for a specific day (defaults to today)
- **Automatic Scheduling**: Background scheduler runs daily sync every 30 minutes
- **Upsert Logic**: Inserts new transactions and updates existing ones based on `id` (unique identifier)
- **Pagination Handling**: Automatically fetches all pages of data
- **Bearer Token Authentication**: Uses `GLOBAL_TRANSACTION_API_KEY` from environment

## Database Table

The module syncs data to the `transaction_cache` table:

```sql
CREATE TABLE transaction_cache (
    id CHAR(40) NOT NULL PRIMARY KEY,
    amount INT NOT NULL,
    human_readable_amount DECIMAL(10,2),
    charge INT,
    human_readable_charge DECIMAL(10,2),
    status VARCHAR(20),
    decline_reason VARCHAR(255),
    mode VARCHAR(20),
    type VARCHAR(20),
    description VARCHAR(255),
    external_id VARCHAR(100),
    currency CHAR(3),
    created_at DATETIME,
    recipient JSON NULL,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

## API Endpoints

### 1. Full Sync (Manual)

**POST** `/api/sync/full`

Triggers a complete sync of all transactions from the external API.

```bash
curl -X POST http://localhost:8000/api/sync/full
```

**Response:**
```json
{
  "success": true,
  "message": "Full sync completed successfully",
  "sync_type": "full",
  "started_at": "2026-01-25T10:00:00",
  "completed_at": "2026-01-25T10:02:15",
  "elapsed_seconds": 135.5,
  "inserted": 150,
  "updated": 23,
  "total": 173
}
```

### 2. Daily Sync (Manual)

**POST** `/api/sync/daily?target_date=YYYY-MM-DD`

Triggers a sync for a specific date (defaults to today).

```bash
# Sync today's transactions
curl -X POST http://localhost:8000/api/sync/daily

# Sync specific date
curl -X POST http://localhost:8000/api/sync/daily?target_date=2026-01-24
```

**Response:**
```json
{
  "success": true,
  "message": "Daily sync completed successfully for 2026-01-25",
  "sync_type": "daily",
  "date": "2026-01-25",
  "started_at": "2026-01-25T10:00:00",
  "completed_at": "2026-01-25T10:00:45",
  "elapsed_seconds": 45.2,
  "inserted": 15,
  "updated": 5,
  "total": 20
}
```

### 3. Scheduler Status

**GET** `/api/sync/scheduler/status`

Check the status of the background scheduler.

```bash
curl http://localhost:8000/api/sync/scheduler/status
```

**Response:**
```json
{
  "is_running": true,
  "jobs": [
    {
      "id": "daily_transaction_sync",
      "name": "Daily Transaction Sync (Every 30 minutes)",
      "next_run_time": "2026-01-25T10:30:00",
      "trigger": "interval[0:30:00]"
    }
  ]
}
```

### 4. Start Scheduler

**POST** `/api/sync/scheduler/start`

Manually start the background scheduler (auto-starts on application startup).

```bash
curl -X POST http://localhost:8000/api/sync/scheduler/start
```

### 5. Stop Scheduler

**POST** `/api/sync/scheduler/stop`

Stop the background scheduler.

```bash
curl -X POST http://localhost:8000/api/sync/scheduler/stop
```

## How It Works

### Authentication

The module uses Bearer token authentication:

```python
headers = {
    "Authorization": f"Bearer {GLOBAL_TRANSACTION_API_KEY}",
    "Accept": "application/json"
}
```

### Pagination

The external API returns paginated results. The module automatically:
1. Fetches the first page
2. Checks `meta.last_page` to determine total pages
3. Iterates through all pages until complete

### Upsert Logic

For each transaction:
- **If `id` exists**: Updates all fields (status, amount, recipient, etc.)
- **If `id` is new**: Inserts a new record
- Uses MySQL's `INSERT ... ON DUPLICATE KEY UPDATE` for efficiency

### Automatic Scheduling

On application startup:
- The scheduler automatically starts
- A background job runs every 30 minutes
- Each run syncs today's transactions using: `https://app.spennx.com/api/v1/globaltransactions?day=2026-01-25`

## Module Files

- **`app/transaction_sync.py`**: Core sync service with API client and database logic
- **`app/sync_routes.py`**: FastAPI routes for manual sync triggers
- **`app/scheduler.py`**: Background scheduler using APScheduler
- **`app/models.py`**: SQLAlchemy model for `transaction_cache` table

## Configuration

Required environment variables in `.env`:

```env
GLOBAL_TRANSACTION_API_KEY=your-api-key-here
DATABASE_URL=mysql+pymysql://user:password@host:port/database
```

## Installation

1. Install new dependencies:
```bash
pip install -r requirements.txt
```

2. The `transaction_cache` table should already exist in your database. If not, create it using the SQL above.

3. Ensure `GLOBAL_TRANSACTION_API_KEY` is set in your `.env` file.

4. Start the application:
```bash
python -m uvicorn app.main:app --reload
```

## Usage Scenarios

### Initial Setup

When first deploying, run a full sync to populate the cache:

```bash
curl -X POST http://localhost:8000/api/sync/full
```

### Daily Operations

The scheduler automatically handles daily syncs every 30 minutes. No manual intervention needed.

### Manual Refresh

If you need to refresh a specific day's data:

```bash
curl -X POST "http://localhost:8000/api/sync/daily?target_date=2026-01-24"
```

### Monitoring

Check scheduler status regularly:

```bash
curl http://localhost:8000/api/sync/scheduler/status
```

## Logging

The module logs all operations:

```
INFO - Starting full transaction sync...
INFO - Fetching page 1 for day=all
INFO - Fetched 20 transactions from page 1/5
INFO - Total transactions fetched: 100
INFO - Sync complete: 85 inserted, 15 updated
INFO - Full sync completed in 45.32s
```

## Error Handling

- **API failures**: Logged with error details, sync aborted
- **Database errors**: Individual transaction errors logged, sync continues
- **Invalid dates**: Returns 400 Bad Request with clear error message
- **Scheduler conflicts**: Only one sync job runs at a time (max_instances=1)

## Performance Considerations

- **Pagination**: Fetches data in chunks (20 per page by default)
- **Batch processing**: Database commits are batched per page
- **Timeout**: API requests timeout after 30 seconds
- **Scheduler grace period**: 5-minute grace period for delayed job starts

## Security

- API key stored in environment variable (never hardcoded)
- Bearer token authentication for all API requests
- Database credentials managed via DATABASE_URL

## Troubleshooting

### Scheduler not running

Check status:
```bash
curl http://localhost:8000/api/sync/scheduler/status
```

If stopped, start it:
```bash
curl -X POST http://localhost:8000/api/sync/scheduler/start
```

### Missing API key

Ensure `.env` contains:
```
GLOBAL_TRANSACTION_API_KEY=your-key-here
```

### Database connection issues

Verify `DATABASE_URL` in `.env` points to the new database location.

### Duplicate key errors

Should not occur - the upsert logic handles duplicates automatically. If you see errors, check that the `id` column is set as PRIMARY KEY.
