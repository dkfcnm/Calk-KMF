#!/bin/bash
# Calk_KMF - Start Infrastructure (Git Bash version)

echo "=========================================="
echo "  Calk_KMF - Starting Infrastructure"
echo "=========================================="
echo ""

# 1. PostgreSQL
echo "[1/2] Starting PostgreSQL..."
if net start postgresql-x64-18 >/dev/null 2>&1; then
    echo "[OK] PostgreSQL started"
else
    echo "[!] PostgreSQL already running or start failed"
fi

# 2. Headroom Proxy
echo ""
echo "[2/2] Starting Headroom Proxy..."
echo "       URL: http://127.0.0.1:8788"
echo "       Memory: ENABLED"
echo "       Code-Aware: ENABLED"

if tasklist | grep -i "headroom" >/dev/null 2>&1; then
    echo "[!] Headroom proxy already running"
else
    cd "$(dirname "$0")/.."
    headroom proxy \
        --port 8788 \
        --memory \
        --memory-storage=project \
        --code-aware \
        --memory-db-path .headroom/memory.db \
        --log-file .headroom/logs/proxy.log \
        > .headroom/logs/proxy.stdout 2>&1 &
    sleep 3
    if tasklist | grep -i "headroom" >/dev/null 2>&1; then
        echo "[OK] Headroom proxy started"
    else
        echo "[!] Headroom proxy start failed"
    fi
fi

echo ""
echo "=========================================="
echo "  All services started"
echo "=========================================="
