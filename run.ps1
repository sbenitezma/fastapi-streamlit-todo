<#
==============================================================================
  TASK MANAGER  -  startup script (everything runs in Docker)
==============================================================================

  Usage:   .\run.ps1 <command>

  Commands:
    start      Build (if needed) and start API + dashboard in the background
    stop       Stop and remove the containers (data is kept)
    restart    stop + start
    rebuild    Rebuild the image from scratch and start again
    logs       Follow the live logs (Ctrl+C to exit)
    status     Container status
    test       Run the test suite (pytest) inside a container
    shell      Open a shell inside the API container
    clean      Stop everything and ALSO delete the data volume (drops the tasks)
    help       Show this help

  No command is the same as "start".

  Only requirement: Docker Desktop installed and running.
  Download: https://www.docker.com/products/docker-desktop/

  URLs once started:
    Dashboard (Streamlit) ->  http://localhost:8501
    API       (FastAPI)   ->  http://localhost:8000
    API docs              ->  http://localhost:8000/docs
==============================================================================
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet('start', 'stop', 'restart', 'rebuild', 'logs', 'status', 'test', 'shell', 'clean', 'help')]
    [string]$Command = 'start'
)

$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

function Assert-Docker {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: 'docker' not found." -ForegroundColor Red
        Write-Host "Install Docker Desktop and try again:" -ForegroundColor Yellow
        Write-Host "  https://www.docker.com/products/docker-desktop/"
        exit 1
    }
    try {
        docker info *> $null
    }
    catch {
        Write-Host "ERROR: Docker is installed but the engine is not responding." -ForegroundColor Red
        Write-Host "Open Docker Desktop and wait until it shows 'Engine running'." -ForegroundColor Yellow
        exit 1
    }
}

function Show-Urls {
    Write-Host ""
    Write-Host "  Ready. Open in your browser:" -ForegroundColor Green
    Write-Host "    Dashboard ->  http://localhost:8501"
    Write-Host "    API       ->  http://localhost:8000"
    Write-Host "    API docs  ->  http://localhost:8000/docs"
    Write-Host ""
    Write-Host "  Logs:  .\run.ps1 logs      Stop:  .\run.ps1 stop" -ForegroundColor DarkGray
}

switch ($Command) {
    'help' {
        Get-Help $PSCommandPath -Detailed | Out-String | Write-Host
        break
    }
    'start' {
        Assert-Docker
        Write-Host "Starting containers..." -ForegroundColor Cyan
        docker compose up -d --build
        docker compose ps
        Show-Urls
        break
    }
    'stop' {
        Assert-Docker
        docker compose down
        Write-Host "Containers stopped. Data is still saved." -ForegroundColor Green
        break
    }
    'restart' {
        Assert-Docker
        docker compose down
        docker compose up -d --build
        docker compose ps
        Show-Urls
        break
    }
    'rebuild' {
        Assert-Docker
        docker compose down
        docker compose build --no-cache
        docker compose up -d
        docker compose ps
        Show-Urls
        break
    }
    'logs' {
        Assert-Docker
        docker compose logs -f
        break
    }
    'status' {
        Assert-Docker
        docker compose ps
        break
    }
    'test' {
        Assert-Docker
        Write-Host "Running pytest inside a container..." -ForegroundColor Cyan
        docker compose run --rm --no-deps api python -m pytest -v
        break
    }
    'shell' {
        Assert-Docker
        docker compose exec api /bin/bash
        break
    }
    'clean' {
        Assert-Docker
        Write-Host "This ALSO deletes the data volume (tasks will be lost)." -ForegroundColor Yellow
        $r = Read-Host "Type 'yes' to continue"
        if ($r -eq 'yes') {
            docker compose down -v --rmi local
            Write-Host "Environment removed completely." -ForegroundColor Green
        }
        else {
            Write-Host "Cancelled." -ForegroundColor DarkGray
        }
        break
    }
}
