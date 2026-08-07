#!/bin/bash

echo "Stopping Rono's School services..."

pkill -f "uvicorn app:app"

echo "All services stopped."