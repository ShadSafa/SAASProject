# How to Run the Analysis Workflow

The analysis workflow is now **fully functional**. Follow these steps to get it running.

## Summary

The analysis workflow enables AI-powered analysis of viral posts:
```
Scan Created → Viral Posts Generated → Analysis Task Queued → Celery Worker Processes → Analysis Records Created → API Returns Results
```

## Prerequisites

These need to be running:
1. **PostgreSQL** - Database (should already be running)
2. **Redis** - Message broker (via Docker)
3. **Celery Worker** - Background task processor (single process mode for Windows)
4. **Backend API** - FastAPI server

## Quick Start

### 1. Start Redis via Docker

```bash
docker start redis
```

If the container doesn't exist:
```bash
docker run -d -p 6379:6379 --name redis redis:7
```

Verify it's working:
```bash
docker exec redis redis-cli ping
# Should output: PONG
```

### 2. Start Celery Worker (Use `--pool=solo` on Windows!)

```bash
cd backend
python -m celery -A app.celery_app worker --pool=solo --loglevel=info
```

**Important**: The `--pool=solo` flag is required on Windows. The default multiprocessing pool causes permission errors on Windows.

You should see:
```
celery@YOURCOMPUTER ready.
```

### 3. Start Backend API

In a new terminal:

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Verify Everything Works

In a new terminal:

```bash
python end_to_end_test.py
```

Expected output:
```
SUCCESS: Analysis workflow is fully functional!
======================================================================

What this means:
  1. Scans create viral posts [OK]
  2. Analysis tasks are dispatched to Celery [OK]
  3. Celery worker processes the tasks [OK]
  4. Analysis records are created in database [OK]
  5. API endpoint can retrieve the data [OK]
```

## How It Works

1. **User creates scan** (API: POST /scans/trigger)
   - Backend creates Scan and ViralPost records
   - Dispatch `analyze_posts_batch` task to Celery

2. **Task queued to Redis** (Message Broker)
   - Task sits in queue waiting for worker

3. **Celery Worker picks up task**
   - Processes each viral post
   - Calls analyze_viral_post() for AI analysis
   - Stores Analysis records in database

4. **API returns results**
   - GET /analyses/{post_id} returns analysis data
   - Frontend displays: Hook Strength, Emotional Trigger, Why It Went Viral, etc.

## Configuration

Key files:
- **backend/.env** - Redis URLs configured
- **backend/app/celery_app.py** - Celery configuration and task imports
- **backend/app/tasks/analysis_jobs.py** - Analysis task implementation
- **backend/app/services/openai_service.py** - AI analysis logic (currently in dev mode using mock data)

## Troubleshooting

### "Connection refused" error from Celery

**Problem**: Redis is not running or not accessible

**Solution**:
```bash
docker start redis
docker exec redis redis-cli ping
# Should output: PONG
```

### Celery worker process crashes

**Problem**: Default multiprocessing pool on Windows causes errors

**Solution**: Always use `--pool=solo` flag:
```bash
python -m celery -A app.celery_app worker --pool=solo --loglevel=info
```

### Tasks not being processed by worker

**Problem**: Multiple Celery workers running or worker not ready

**Solution**:
1. Make sure only one worker is running
2. Wait for "celery@YOURCOMPUTER ready." message
3. Check that Redis is running: `docker exec redis redis-cli ping`

### Analysis records not created

**Problem**: Task failed during processing (error in analysis logic)

**Solution**:
1. Check Celery worker terminal for error messages
2. Check PostgreSQL is running and accessible
3. Check database has tables: `select * from analyses;` in psql

## Running in Production

The same workflow works in production. Key differences:

1. **Celery Configuration**:
   - Use `--pool=prefork` on Linux/Mac (multiprocessing works)
   - Increase concurrency: `--concurrency=4` or more
   - Use `--pool=solo` only for Windows development

2. **Redis**:
   - Use managed Redis service (AWS ElastiCache, Redis Cloud, etc.)
   - Update DATABASE_URL and CELERY_BROKER_URL in .env

3. **AI Analysis**:
   - Switch from dev mode to real OpenRouter API calls
   - Update OPENAI_API_KEY with valid key
   - Remove `print()` statements (already using logger)

## Next Steps

Once the workflow is verified:

1. **Test in UI** (if frontend is running on port 5173):
   - Create a scan
   - Click on a viral post
   - Verify analysis data is displayed

2. **Monitor Tasks**:
   - Celery worker terminal shows all processing logs
   - Analysis records visible in database

3. **Customize Analysis**:
   - Modify `backend/app/services/openai_service.py`
   - Change analysis algorithm factors
   - Celery worker auto-reloads on changes (with --reload)

## Files

- **end_to_end_test.py** - Comprehensive workflow test
- **celery_diagnostic.py** - Verify Celery connectivity
- **quick_fix.py** - System diagnostics
- **RUN_ANALYSIS_WORKFLOW.md** - This file

## Architecture

```
┌──────────────┐
│  Frontend    │
│  (React)     │
└──────┬───────┘
       │ HTTP POST /scans/trigger
       ▼
┌──────────────────────┐
│  Backend API         │
│  (FastAPI/Uvicorn)   │
└──────┬───────────────┘
       │ Create Scan + ViralPosts
       │ Dispatch task via .delay()
       ▼
┌──────────────────────┐        ┌──────────────┐
│  Redis Queue         │◀──────▶│  Celery      │
│  (Task Broker)       │        │  Worker      │
└──────────────────────┘        │  (solo mode) │
       ▲                         └──────┬───────┘
       │ Store results                  │
       │ (cached analysis)              │ Process tasks
       └──────────────────────────────┬─┘
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │  PostgreSQL          │
                          │  (Analysis Records)  │
                          └──────────────────────┘
```

## Notes

- All timestamps in UTC
- Analysis uses pre-calculated algorithm factors in dev mode
- 7-day Redis cache TTL for analysis results
- Async/await pattern throughout for scalability
- Proper error handling: single post failure doesn't fail entire batch
