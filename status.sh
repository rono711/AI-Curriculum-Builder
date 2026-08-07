#!/bin/bash

echo "=============================================="
echo " Rono's School AI Curriculum Builder"
echo " Service Status"
echo "=============================================="
echo ""

check_service () {

    NAME=$1
    URL=$2

    if curl -s --connect-timeout 2 "$URL" > /dev/null
    then
        printf "%-30s %s\n" "$NAME" "✅ RUNNING"
    else
        printf "%-30s %s\n" "$NAME" "❌ STOPPED"
    fi

}

check_service "Build App" \
"http://127.0.0.1:8001/health"

check_service "Curriculum Service" \
"http://127.0.0.1:8003/health"

check_service "Lesson Package Builder" \
"http://127.0.0.1:8004/health"

check_service "Prompt Engine" \
"http://127.0.0.1:8005/health"

check_service "AI Engine" \
"http://127.0.0.1:8007/health"

check_service "Workbook Service" \
"http://127.0.0.1:8009/health"

check_service "Gamma engine" \
"http://127.0.0.1:8006/health"

echo ""
echo "=============================================="
echo "Ports"
echo "=============================================="

ss -tln | grep -E '8001|8003|8004|8005|8006|8007|8009'

echo ""
echo "=============================================="
echo "Running Uvicorn Processes"
echo "=============================================="

ps -ef | grep uvicorn | grep -v grep

echo ""
echo "=============================================="

