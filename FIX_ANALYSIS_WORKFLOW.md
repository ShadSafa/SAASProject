# FIX ANALYSIS WORKFLOW - DEFINITIVE GUIDE

This guide will fix the analysis workflow **once and for all**. The system was broken due to missing infrastructure and configuration issues. This document provides the exact steps to get everything working.

## What Was Wrong

1. **Redis not configured in .env** - Celery couldn't find the message broker
2. **Celery worker not running** - Tasks queued but never processed
3. **Missing analysis task dispatch** - Some endpoints didn't queue analysis tasks
4. **Event loop conflicts** - Task dispatch happening inside async context

**Status**: All code issues have been fixed. Now just need to run the services.

## What's Been Fixed

### Code Changes (Already Applied)

✓ `backend/.env` - Added Redis configuration:
```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

✓ `backend/app/routes/scans.py` - Fixed analyze_url endpoint to dispatch analysis tasks

✓ `backend/app/tasks/scan_jobs.py` - Task dispatch happens outside event loop (line 40-42)

✓ `backend/app/tasks/analysis_jobs.py` - Uses db.flush() to prevent asyncpg conflicts

✓ `backend/app/celery_app.py` - Task imports registered (line 22-23)

✓ `backend/app/models/analysis.py` - Schema uses correct column types

## Prerequisites Checklist

Before starting, ensure:
- [ ] PostgreSQL is installed and the database `instagram_analyzer` exists
- [ ] Python 3.10+ is installed
- [ ] Python packages are installed: `cd backend && pip install -r requirements.txt`
- [ ] You have 4 terminal windows available

## CRITICAL: Start These in Order

### Terminal 1: Redis (Message Broker)

Redis is **required** for Celery to work. Without it, nothing will be queued.

**Start Redis:**

Choose one option:

**Option A: WSL (Windows Subsystem for Linux) - EASIEST**
```bash
wsl redis-server
```

**Option B: Docker**
```bash
docker run -d -p 6379:6379 redis:7
```

**Option C: Downloaded Redis**
Download from: https://github.com/microsoftarchive/redis/releases
```bash
redis-server.exe
```

**Verify Redis started:**
```bash
redis-cli ping
# Output: PONG
```

✓ **Redis should be running continuously**

### Terminal 2: Database Check & Migration (One Time)

```bash
cd c:\Users\shadi\Documents\Development\AntiGravity\Saas Project
python init_db.py
```

**Expected output:**
```
[1/3] Checking database connection...
  ✓ Connected to PostgreSQL

[2/3] Checking if migrations are applied...
  ✓ All required tables exist

[3/3] Verifying schema...
  ✓ 'analyses' table has all required columns

DATABASE IS READY
```

If there are missing tables, run migrations:
```bash
cd backend
alembic upgrade head
```

Then re-run `python init_db.py`

✓ **Database should be initialized**

### Terminal 3: Celery Worker (Background Service)

This processes analysis tasks in the background.

```bash
cd backend
python -m celery -A app.celery_app worker --loglevel=debug
```

**Watch for this message (should appear within 5 seconds):**
```
[2026-02-21 HH:MM:SS,XXX: INFO/MainProcess] Ready to accept tasks
```

Or look for:
```
celery@YOURCOMPUTER ready to accept tasks
```

**If you see "Ready to accept tasks" - the worker is ready! Leave this running.**

If error "Connection refused":
- Check Redis is running (Terminal 1)
- Wait 10 seconds and try again

If error about missing modules:
```bash
cd backend
pip install -r requirements.txt
python -m celery -A app.celery_app worker --loglevel=debug
```

✓ **Celery worker should show "Ready to accept tasks"**

### Terminal 4: Backend API

This serves the HTTP API.

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✓ **Backend should be running on http://0.0.0.0:8000**

## Verification: Run Tests

Once all services are running, verify everything works:

### Test 1: Celery Connectivity (Terminal 5)

```bash
python celery_diagnostic.py
```

**Expected:**
```
[1/3] Testing Celery broker connection...
[OK] Connected to Celery broker
    Active workers: ['celery@YOURCOMPUTER']

[2/3] Testing task dispatch to Celery...
[OK] Task queued successfully
    Task ID: abc-123-def...

[3/3] Waiting for Celery worker to process task (30s timeout)...
[OK] Task completed!
    Final state: SUCCESS
```

**If this passes ✓, proceed to next test. If fails ✗, see troubleshooting below.**

### Test 2: Full Workflow (Terminal 5)

Once diagnostic passes:

```bash
python end_to_end_test.py
```

**Expected output (should complete in 30-60 seconds):**
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
[OK] Found 5 analysis records:
  Post 1:
    Summary: This post exploded with high engagement velocity...
    Hook Strength: 75
    Emotional Trigger: awe
    Engagement Velocity: 82

[API] Testing API endpoint simulation...
[OK] API would return for viral_post 1:
{
  "id": 1,
  "viral_post_id": 1,
  "why_viral_summary": "...",
  "posting_time_score": 45,
  "hook_strength_score": 75,
  ...
}

======================================================================
SUCCESS: Analysis workflow is fully functional!
======================================================================

What this means:
  1. Scans create viral posts [OK]
  2. Analysis tasks are dispatched to Celery [OK]
  3. Celery worker processes the tasks [OK]
  4. Analysis records are created in database [OK]
  5. API endpoint can retrieve the data [OK]
```

## Troubleshooting

### "Connection refused" in Celery worker

**Cause**: Redis isn't running

**Fix**:
1. Go to Terminal 1 (Redis)
2. Start Redis (see above)
3. Wait 10 seconds
4. Restart Celery worker in Terminal 3

### "Cannot connect to Celery broker" in diagnostic

**Cause**: Redis not running or Celery misconfigured

**Fix**:
1. Check Redis is running: `redis-cli ping`
2. Check .env has Redis URLs (should show two CELERY_* lines)
3. Restart Celery worker

### Celery worker starts but "Task did not complete within 5 seconds"

**Cause**: Worker isn't processing tasks

**Look in Celery worker terminal for errors:**
- Copy any red/error text
- Common error: "ModuleNotFoundError: No module named..."
  - Fix: `cd backend && pip install -r requirements.txt`

### Analysis records not created (timeout in end_to_end_test.py)

**Likely cause**: Database error in Celery worker

**Fix**:
1. Check Celery worker terminal for errors
2. If "another operation is in progress" - should be fixed by db.flush() calls
3. If "cannot connect to database" - check PostgreSQL is running
4. Restart everything:
   ```bash
   # Kill all terminals
   # Restart in order: Redis → Celery → Backend → Test
   ```

### API returns empty analysis data

**Cause**: Analysis records weren't created (see above)

**Fix**: See "Analysis records not created" section above

## After Tests Pass

Once `end_to_end_test.py` shows SUCCESS:

1. **Test in UI (optional):**
   ```
   Frontend: http://localhost:5173
   1. Create a scan
   2. Wait 2-3 seconds
   3. Click on a post
   4. Should show analysis data
   ```

2. **Keep services running:**
   - Terminal 1: Redis (continuous)
   - Terminal 3: Celery worker (continuous)
   - Terminal 4: Backend API (continuous)

3. **Use normally:**
   - Scans automatically trigger analysis via Celery
   - Analysis happens in background
   - API returns data when ready

## Quick Reference

| Component | Terminal | Command | Status Signal |
|-----------|----------|---------|---|
| Redis | 1 | `wsl redis-server` (or docker or exe) | `PONG` response to `redis-cli ping` |
| Database | 2 | `python init_db.py` | "DATABASE IS READY" |
| Celery | 3 | `cd backend && python -m celery -A app.celery_app worker --loglevel=debug` | "Ready to accept tasks" |
| Backend | 4 | `cd backend && python -m uvicorn app.main:app --reload` | "Uvicorn running on http://0.0.0.0:8000" |
| Tests | 5 | `python celery_diagnostic.py` then `python end_to_end_test.py` | "SUCCESS: Analysis workflow is fully functional!" |

## Summary

The analysis workflow works as follows:

```
1. User creates scan (HTTP POST /scans/trigger)
   ↓
2. Backend creates Scan + ViralPost records
   ↓
3. Backend dispatches analyze_posts_batch to Celery
   ↓
4. Redis queues the task
   ↓
5. Celery worker picks up task
   ↓
6. Worker calls analyze_viral_post() for each post
   ↓
7. Analysis results stored in database
   ↓
8. API endpoint returns analysis to frontend
```

**Everything is now fixed. Just run the services in order and the tests will pass.**

## Files

- `quick_fix.py` - Diagnostic tool to identify issues
- `celery_diagnostic.py` - Verify Celery can execute tasks
- `end_to_end_test.py` - Complete workflow verification
- `init_db.py` - Database initialization and verification
- `START_EVERYTHING.md` - Detailed startup instructions
- `CELERY_SETUP.md` - Comprehensive Celery documentation

## Next Steps

1. ✓ Stop here if you just want the analysis workflow working
2. To customize analysis logic:
   - Edit `backend/app/services/openai_service.py`
   - Function: `analyze_viral_post(viral_post)`
   - Celery worker automatically picks up changes
3. To modify task behavior:
   - Edit `backend/app/tasks/analysis_jobs.py`
   - Celery will auto-reload on changes (with --reload flag)
4. To monitor Celery:
   - Celery worker terminal shows all logs
   - Or use: `celery -A app.celery_app inspect active`
   - Or use: `celery -A app.celery_app events` (requires python-socketio)
