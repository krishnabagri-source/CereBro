# CereBro / AdaptIQ - Startup Script
# Run this from the CereBro root directory to start both backend and frontend

$PYTHON = "C:\Users\DELL\AppData\Local\Programs\Python\Python313\python.exe"
$ROOT = $PSScriptRoot

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "   CereBro / AdaptIQ Adaptive Tutor" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
if (-not (Test-Path $PYTHON)) {
    Write-Host "ERROR: Python not found at $PYTHON" -ForegroundColor Red
    Write-Host "Please install Python 3.13 or update the PYTHON path in start.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    Set-Location '$ROOT\backend'
    Write-Host 'Backend starting...' -ForegroundColor Green
    & '$PYTHON' -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
" -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host "Starting Vite frontend on http://localhost:5173 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    Set-Location '$ROOT\frontend'
    Write-Host 'Frontend starting...' -ForegroundColor Blue
    npm run dev
" -WindowStyle Normal

Write-Host ""
Write-Host "Both servers are launching in separate windows." -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:8000  (API + Swagger docs at /docs)" -ForegroundColor White
Write-Host "  Frontend: http://localhost:5173  (React App)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop them." -ForegroundColor Yellow
