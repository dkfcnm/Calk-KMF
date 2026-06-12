#!/bin/bash
# Calk_KMF - Stop Infrastructure (Git Bash version)

echo "=========================================="
echo "  Calk_KMF - Stopping Infrastructure"
echo "=========================================="
echo ""

# 1. Headroom Proxy
echo "[1/2] Stopping Headroom Proxy..."
if tasklist | grep -i "headroom" >/dev/null 2>&1; then
    taskkill //F //IM headroom.exe >/dev/null 2>&1
    echo "[OK] Headroom proxy stopped"
else
    echo "[!] Headroom proxy not running"
fi

# 2. PostgreSQL
echo ""
echo "[2/2] Stopping PostgreSQL..."
if net stop postgresql-x64-18 >/dev/null 2>&1; then
    echo "[OK] PostgreSQL stopped"
else
    echo "[!] PostgreSQL already stopped or stop failed"
fi

echo ""
echo "=========================================="
echo "  All services stopped"
echo "=========================================="
