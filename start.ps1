# Start Redis
Write-Host "Starting Redis..." -ForegroundColor Green
docker start redis

# Wait for Redis
Start-Sleep -Seconds 2

# Start Celery in a new window
Write-Host "Starting Celery Worker..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PWD\backend'; .\.venv\Scripts\Activate.ps1; python -m celery -A app.celery_app worker --pool=solo -n analysis_worker@%h --loglevel=info`""

# Wait for Celery to start
Start-Sleep -Seconds 2

# Start Backend in a new window
Write-Host "Starting Backend..." -ForegroundColor DarkGray
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PWD\backend'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000`""

# Wait for Backend to start
Start-Sleep -Seconds 2

# Start Frontend in a new window
Write-Host "Starting Frontend..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PWD\frontend'; npm run dev`""

# Wait for Frontend to start
Start-Sleep -Seconds 2

# Start Kanban board server on port 8080
Write-Host "Starting Kanban board server..." -ForegroundColor Magenta
$projectRoot = Get-Location
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$projectRoot'; python -m http.server 8080 --directory '$projectRoot'`""

Write-Host "`n✓ All services started!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Kanban Board: http://localhost:8080/kanban.html" -ForegroundColor Magenta