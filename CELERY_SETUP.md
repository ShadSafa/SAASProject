# Celery Analysis Workflow Setup & Troubleshooting

This guide helps you get the analysis workflow fully operational. The workflow is:
1. User creates a scan
2. Scan generates viral posts
3. Analysis task dispatched to Celery queue
4. Celery worker processes tasks in background
5. Analysis records created in database
6. API returns analysis data to frontend

## Prerequisites

You need these services running:
1. **PostgreSQL** - database for posts and analysis
2. **Redis** - message broker for Celery + result backend
3. **Celery Worker** - processes analysis tasks in background
4. **Backend API** - FastAPI server (uvicorn)

## Quick Start (Windows)

### 1. Start PostgreSQL
PostgreSQL should already be running if your app was working.
```
# Check if running: Try connecting in pgAdmin or:
psql -U postgres -d instagram_analyzer
```

### 2. Start Redis (NEW - Required for Celery)

**Option A: Using Windows Subsystem for Linux (WSL) - EASIEST**
```bash
# In any terminal:
redis-server
```

**Option B: Using Docker**
```bash
docker run -d -p 6379:6379 redis:7
```

**Option C: Download standalone**
- Download from: https://github.com/microsoftarchive/redis/releases
- Extract and run `redis-server.exe`

**Verify Redis is running:**
```
redis-cli ping
# Should output: PONG
```

### 3. Start Celery Worker (Terminal 1)

```bash
cd backend
python -m celery -A app.celery_app worker --loglevel=debug
```

**Expected output:**
```
 -------------- celery@YOURCOMPUTER v5.x.x (mango)
--- ***** -----
-- ******* ----
- *** --- * ---
- ** ---------- [config]
- ** ---------- .broker: redis://localhost:6379/0
- ** ---------- .app: app.celery_app:0x...
- ** ---------- .concurrency: 4 (prefork)
- ** ---------- .events: OFF (enable -E to monitor)
- ** ---------- .max_retries: 100
- *** --- * --- [queues]
--- ******* ---- . celery
- ** ----------
[tasks]
  . app.tasks.analysis_jobs.analyze_posts_batch
  . app.tasks.scan_jobs.run_scan

[2026-02-21 XX:XX:XX,XXX: INFO/MainProcess] Ready to accept tasks
```

**If you see "Ready to accept tasks" - the worker is running correctly!**

### 4. Start Backend API (Terminal 2)

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### 5. Run Diagnostic Test (Terminal 3)

```bash
python celery_diagnostic.py
```

This tests:
- Can connect to Redis broker
- Can dispatch task to Celery
- Does worker process the task

**Expected output:**
```
[1/3] Testing Celery broker connection...
[OK] Connected to Celery broker
    Active workers: ['celery@YOURCOMPUTER']

[2/3] Testing task dispatch to Celery...
[OK] Task queued successfully
    Task ID: abc-123-def...
    Task state: PENDING

[3/3] Waiting for Celery worker to process task (30s timeout)...
  [1s] Task state: STARTED... (waiting)
  [2s] Task state: SUCCESS... (waiting)
[OK] Task completed!
    Final state: SUCCESS
```

### 6. Run Full End-to-End Test (Terminal 3 - After diagnostic passes)

```bash
python end_to_end_test.py
```

This tests the complete workflow:
1. Creates a test user
2. Creates a scan
3. Generates viral posts
4. Dispatches analysis to Celery
5. Waits for Celery worker to create analysis records
6. Verifies all analysis data
7. Tests API response format

**Expected output:**
```
======================================================================
END-TO-END ANALYSIS WORKFLOW TEST
======================================================================

[1/5] Creating test user...
[OK] User ID: 1

[2/5] Creating scan...
[OK] Scan ID: 1

[3/5] Running scan and dispatching analysis...
[SCAN] Running scan 1...
[OK] Scan complete: 5 posts created
[CELERY] Dispatching analysis task to Celery...
[OK] Task queued for 5 posts

[4/5] Waiting for Celery worker to process analysis...
[WAIT] Waiting for Celery to process analysis (max 60s)...
  [2s] Checking... (0 records found)
  [4s] Checking... (0 records found)
  [6s] Checking... (5 records found)
[OK] Analysis complete: 5 records created

[5/5] Verifying analysis data and testing API endpoint...
[VERIFY] Checking analysis data...
[OK] Found 5 analysis records:
  Post 1:
    Summary: This post exploded with high engagement velocity (82/100)...
    Hook Strength: 75
    Emotional Trigger: awe
    Engagement Velocity: 82
[OK] All 5 records have required data

[API] Testing API endpoint simulation...
[OK] API would return for viral_post 1:
     {
       "id": 1,
       "why_viral_summary": "...",
       "hook_strength_score": 75,
       ...
     }

======================================================================
SUCCESS: Analysis workflow is fully functional!
======================================================================
```

## Troubleshooting

### Problem: "Cannot connect to Celery broker"

**Cause**: Redis is not running

**Solution**:
1. Make sure Redis is running (see Step 2 above)
2. Verify Redis is on localhost:6379: `redis-cli ping`
3. Check .env file has:
   ```
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/1
   ```

### Problem: Celery worker not showing "Ready to accept tasks"

**Cause**: Worker failed to start due to import or config error

**Solution**:
1. Look for error messages in the worker terminal
2. Check these exist in backend/:
   - `app/celery_app.py` (should have task imports)
   - `app/tasks/analysis_jobs.py`
   - `app/tasks/scan_jobs.py`
3. Restart worker: `python -m celery -A app.celery_app worker --loglevel=debug`

### Problem: "Task state: PENDING" after 30 seconds (doesn't process)

**Cause**: Worker is not picking up tasks

**Solution**:
1. Verify worker shows "Ready to accept tasks" in its terminal
2. Look for messages like "app.tasks.analysis_jobs.analyze_posts_batch" in worker output
3. If no task messages appear when you run the test:
   - Tasks aren't being dispatched correctly
   - Or worker isn't watching the queue
4. Try restarting everything:
   ```bash
   # Kill all Python processes
   # Restart Redis
   redis-server
   # Restart Celery worker
   cd backend && python -m celery -A app.celery_app worker --loglevel=debug
   # Restart backend
   cd backend && python -m uvicorn app.main:app --reload
   # Run diagnostic
   python celery_diagnostic.py
   ```

### Problem: Timeout waiting for analysis records in end-to-end test

**Cause**: Celery worker processed task but analysis records weren't created

**Solution**:
1. Check Celery worker terminal for error messages
2. Verify database has tables:
   ```sql
   \dt
   # Should show: scans, viral_posts, analyses, users
   ```
3. Run diagnostic test to see if worker can execute tasks at all
4. Check if there are errors in app/tasks/analysis_jobs.py

### Problem: "Another operation is in progress" error in Celery worker

**Cause**: asyncpg concurrent operation conflict (Windows/Celery specific)

**Solution**: This should be fixed by db.flush() after each record in analysis_jobs.py
- If you see this error, verify line 90 and 120 in analysis_jobs.py have `await db.flush()`

## Verification Checklist

- [ ] Redis is running and responds to `redis-cli ping`
- [ ] Celery worker started and shows "Ready to accept tasks"
- [ ] Backend API running on http://localhost:8000
- [ ] `celery_diagnostic.py` shows "Task completed" with SUCCESS state
- [ ] `end_to_end_test.py` shows "Analysis complete: N records created"
- [ ] Analysis API endpoint returns data with proper fields

## Manual Testing in UI

Once diagnostic and end-to-end tests pass:

1. Open http://localhost:5173 (frontend)
2. Create a scan (Trending, 24h)
3. Wait 2-3 seconds for scan to complete
4. Click on a viral post
5. You should see:
   - "Hook Strength: XX"
   - "Emotional Trigger: [emotion]"
   - "Why it went viral: ..." summary
   - Other analysis factors

## Architecture Overview

```
┌─────────────────────┐
│   Frontend (React)  │
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐      ┌──────────────┐
│  Backend API        │─────▶│  PostgreSQL  │
│  (FastAPI/Uvicorn)  │      │  (Database)  │
└──────────┬──────────┘      └──────────────┘
           │
           │ .delay()
           ▼
      ┌────────────┐       ┌──────────────┐
      │   Redis    │◀──────│  Celery      │
      │  (Broker)  │       │  Worker      │
      └────────────┘       │  (Process)   │
                           └──────────────┘
                                  │
                                  │ Save results
                                  ▼
                           ┌──────────────┐
                           │  PostgreSQL  │
                           │  (Analysis)  │
                           └──────────────┘
```

## Files Modified

- `backend/.env` - Added Redis config
- `backend/app/celery_app.py` - Task imports
- `backend/app/config.py` - Fixed .env loading
- `backend/app/tasks/analysis_jobs.py` - Fixed async/db operations
- `backend/app/models/analysis.py` - Fixed column types
- `celery_diagnostic.py` - NEW: Tests Celery connectivity
- `end_to_end_test.py` - NEW: Tests complete workflow

## Next Steps

1. **Setup Redis** (if not already running)
2. **Run `celery_diagnostic.py`** to verify infrastructure
3. **Run `end_to_end_test.py`** to verify complete workflow
4. **Test in UI** by creating a scan and viewing analysis
