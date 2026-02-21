# Complete Startup Guide for Analysis Workflow

Follow these steps **in order** to get the analysis workflow fully functional. This guide handles all the most common issues.

## What You Need

1. **PostgreSQL** (database) - should already be running
2. **Redis** (message broker) - needed for Celery
3. **Celery Worker** (background task processor) - processes analysis jobs
4. **Backend API** (FastAPI) - handles requests
5. **Frontend** (React) - optional for testing, use API directly

## Step-by-Step Startup

### Step 1: Verify Configuration (5 minutes)

Run this diagnostic to check your setup:

```bash
python quick_fix.py
```

This will check:
- ✓ PostgreSQL is accessible
- ✓ Redis is accessible (if running)
- ✓ Celery can connect to broker
- ✓ Analysis schema exists
- ✓ Celery tasks are registered

**If quick_fix.py reports errors, fix them first before proceeding.**

### Step 2: Start Redis (5 minutes)

Redis is the message broker that Celery uses. You **must** have it running.

**Option A: Using Windows Subsystem for Linux (RECOMMENDED)**
```bash
# In PowerShell or Command Prompt:
wsl
# Then in WSL shell:
redis-server
```
You should see: `Ready to accept connections`

**Option B: Using Docker**
```bash
docker run -d -p 6379:6379 redis:7
```

**Option C: Download Redis Windows Binary**
1. Download from: https://github.com/microsoftarchive/redis/releases
2. Extract the zip file
3. Run `redis-server.exe`

**Verify Redis is running:**
```bash
redis-cli ping
# Should output: PONG
```

### Step 3: Start Celery Worker (Terminal 1)

Open a **new terminal window** (keep Redis running in its terminal):

```bash
cd backend
python -m celery -A app.celery_app worker --loglevel=debug
```

**Wait for this message:**
```
[XXX] celery@YOURCOMPUTER ready to accept tasks
```

Or look for:
```
Ready to accept tasks
```

**If you see this, Celery is ready!** Keep this terminal open.

If you see errors:
- "Connection refused" → Redis isn't running (go back to Step 2)
- "ModuleNotFoundError" → Missing Python package, run: `pip install -r requirements.txt`
- "Port already in use" → Another process is using this port

### Step 4: Start Backend API (Terminal 2)

Open **another new terminal** and run:

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Keep this terminal open.

### Step 5: Run Tests (Terminal 3)

Open **another new terminal** and test:

```bash
# First, verify Celery is working:
python celery_diagnostic.py
```

This should show:
```
[1/3] Testing Celery broker connection...
[OK] Connected to Celery broker
    Active workers: ['celery@YOURCOMPUTER']

[2/3] Testing task dispatch to Celery...
[OK] Task queued successfully

[3/3] Waiting for Celery worker to process task...
[OK] Task completed!
    Final state: SUCCESS
```

**If celery_diagnostic.py passes, run the full end-to-end test:**

```bash
python end_to_end_test.py
```

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
[OK] Scan complete: 5 posts created
[CELERY] Dispatching analysis task to Celery...
[OK] Task queued for 5 posts

[4/5] Waiting for Celery worker to process analysis (max 60s)...
  [2s] Checking... (0 records found)
  [4s] Checking... (5 records found)
[OK] Analysis complete: 5 records created

[5/5] Verifying analysis data and testing API endpoint...
[OK] Found 5 analysis records
[OK] API would return for viral_post 1:
     {...analysis data...}

======================================================================
SUCCESS: Analysis workflow is fully functional!
======================================================================
```

## Troubleshooting

### "Timeout: No analysis records created after 60s"

This means the Celery worker started the task but didn't complete it.

**Check Celery worker terminal for errors:**
- Look for any red error messages
- If there are errors, copy them and we can debug

**Common causes:**
1. **Database error**: Worker can't connect to PostgreSQL
   - Check database is running: `psql -U postgres -d instagram_analyzer`
   - Check .env DATABASE_URL is correct

2. **Import error**: One of the app modules failed to import
   - Check for "ModuleNotFoundError" in worker output
   - Run: `cd backend && python -c "from app.tasks import analysis_jobs"`

3. **Async error**: Event loop or database session issue
   - Look for "another operation is in progress" error
   - This should be fixed by db.flush() calls

### "Cannot connect to Celery broker"

This means Redis isn't running.

**Fix:**
1. Make sure Redis is running (from Step 2)
2. Verify: `redis-cli ping` should output `PONG`
3. Restart Celery worker once Redis is running

### API endpoint returns empty analysis

This means analysis records weren't created. See "Timeout: No analysis records" above.

### "Port already in use" errors

Use a different port:
```bash
# Backend on different port:
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# But also update in frontend .env if needed
```

## Quick Terminal Reference

**Terminal 1: Redis**
```bash
# WSL:
wsl redis-server

# Or Docker:
docker run -d -p 6379:6379 redis:7

# Verify:
redis-cli ping
```

**Terminal 2: Celery Worker**
```bash
cd backend
python -m celery -A app.celery_app worker --loglevel=debug
# Watch for: "Ready to accept tasks"
```

**Terminal 3: Backend API**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Watch for: "Uvicorn running on http://0.0.0.0:8000"
```

**Terminal 4: Tests**
```bash
# Verify Celery works:
python celery_diagnostic.py

# Full workflow test:
python end_to_end_test.py
```

## Expected Timeline

- Step 2 (Redis): 2-3 minutes
- Step 3 (Celery): 1 minute (once Redis is up)
- Step 4 (API): 30 seconds
- Step 5 (Tests): 2-3 minutes
- **Total: ~10 minutes** (first time only)

## After Successful Test

Once `end_to_end_test.py` shows SUCCESS:

1. **Test in UI:**
   - Open frontend (http://localhost:5173)
   - Create a scan
   - Click on a viral post
   - You should see analysis data

2. **Run Full Stack:**
   - Keep Terminals 2 & 3 running
   - Use the API/UI normally
   - Analysis happens in background via Celery

3. **Next Development:**
   - Add more analysis features to Phase 4
   - Modify analysis logic in `backend/app/services/openai_service.py`
   - Celery will automatically pick up changes (watch for re-registration in worker terminal)

## Files You'll Need to Know About

- `backend/.env` - Configuration (database, Redis, API keys)
- `backend/app/celery_app.py` - Celery configuration and task imports
- `backend/app/tasks/analysis_jobs.py` - Actual analysis task code
- `backend/app/services/openai_service.py` - AI analysis logic (currently in dev mode)
- `quick_fix.py` - Diagnostic script to verify setup
- `celery_diagnostic.py` - Test Celery task execution
- `end_to_end_test.py` - Complete workflow verification

## Getting Help

If something doesn't work:

1. **Run**: `python quick_fix.py` (shows what's broken)
2. **Check Terminals**: Look for error messages in Celery or API terminals
3. **Common issues**:
   - Redis not running → see Step 2
   - Celery not ready → wait 30 seconds and check worker terminal
   - Import errors → run `cd backend && python -c "from app.tasks import analysis_jobs"`
   - Database errors → check PostgreSQL is running

**After fixes, always re-run**: `python end_to_end_test.py`
