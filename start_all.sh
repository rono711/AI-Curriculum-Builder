#!/bin/bash

echo "========================================="
echo " Rono's School AI Curriculum Builder"
echo "========================================="

###################################################
# Project Root
###################################################

export PYTHONPATH=/volume1/docker/curriculum-builder

###################################################
# Curriculum Normalizer
###################################################

echo ""
echo "Starting Curriculum Normalizer..."

cd /volume1/docker/curriculum-builder/curriculum_normalizer || exit

nohup .venv/bin/python -m uvicorn app:app \
    --host 0.0.0.0 \
    --port 8003 \
    > curriculum_normalizer.log 2>&1 &

###################################################
# Build App
###################################################

echo ""
echo "Starting Build App..."

cd /volume1/docker/curriculum-builder/build-app || exit

nohup .venv/bin/python -m uvicorn app:app \
    --host 0.0.0.0 \
    --port 8001 \
    > build_app.log 2>&1 &

###################################################
# Lesson Package Builder
###################################################

echo ""
echo "Starting Lesson Package Builder..."

cd /volume1/docker/curriculum-builder/lesson_package_builder || exit

nohup .venv/bin/python -m uvicorn app:app \
    --host 0.0.0.0 \
    --port 8004 \
    > lesson_package_builder.log 2>&1 &

###################################################
# Prompt Engine
###################################################

echo ""
echo "Starting Prompt Engine..."

cd /volume1/docker/curriculum-builder/prompts || exit

nohup .venv/bin/python -m uvicorn app:app \
    --host 0.0.0.0 \
    --port 8005 \
    > prompt_engine.log 2>&1 &

###################################################
# CONTENT Engine
###################################################

echo ""
echo "Starting CONTENT Engine..."

cd /volume1/docker/curriculum-builder/content_engine || exit

nohup .venv/bin/python -m uvicorn app:app \
    --host 0.0.0.0 \
    --port 8007 \
    > ai_engine.log 2>&1 &

###################################################
# Workbook Service
###################################################

echo ""
echo "Starting Workbook Service..."

cd /volume1/docker/curriculum-builder/workbook_service || exit

nohup .venv/bin/python -m uvicorn app:app \
    --host 0.0.0.0 \
    --port 8009 \
    > workbook_service.log 2>&1 &


##########################################################
# Gamma Engine
##########################################################

echo
echo "Starting Gamma Engine..."

cd /volume1/docker/curriculum-builder/gamma_engine

source .venv/bin/activate

nohup .venv/bin/python -m uvicorn app:app \
    --host 0.0.0.0 \
    --port 8006 \
    > workbook_service.log 2>&1 &


##########################################################
# Quiz Engine
##########################################################

echo
echo "Starting Quiz Engine..."

cd /volume1/docker/curriculum-builder/quiz_engine

source .venv/bin/activate

nohup .venv/bin/python -m uvicorn app:app \
    --host 0.0.0.0 \
    --port 8002 \
    > workbook_service.log 2>&1 &

##########################################################
# Activities Engine
##########################################################

echo
echo "Starting Activities Engine..."

cd /volume1/docker/curriculum-builder/activities_engine || exit

nohup .venv/bin/python -m uvicorn app:app \
    --host 0.0.0.0 \
    --port 8010 \
    > activities_engine.log 2>&1 &

##########################################################
# Recap Engine
##########################################################

echo
echo "Starting Recap Engine..."

cd /volume1/docker/curriculum-builder/recap_engine || exit

nohup .venv/bin/python -m uvicorn app:app \
    --host 0.0.0.0 \
    --port 8011 \
    > recap_engine.log 2>&1 &

##########################################################
# Publisher Engine
##########################################################

echo
echo "Starting Publisher Engine..."

cd /volume1/docker/curriculum-builder/publisher_engine || exit

nohup .venv/bin/python -m uvicorn app:app \
--host 0.0.0.0 \
--port 8012 \
> publisher_engine.log 2>&1 &

###################################################
# Finished
###################################################

echo ""
echo "========================================="
echo "All services started successfully."
echo "========================================="
echo ""
echo "Service URLs:"
echo "-----------------------------------------"
echo "Build App              : http://192.168.1.108:8001"
echo "Curriculum Service     : http://192.168.1.108:8003/docs"
echo "Lesson Package Builder : http://192.168.1.108:8004/docs"
echo "Prompt Engine          : http://192.168.1.108:8005/docs"
echo "AI Engine              : http://192.168.1.108:8007/docs"
echo "Workbook Service       : http://192.168.1.108:8009/docs"
echo "Gamma Engine           : http://192.168.1.108:8006/docs"
echo "Quiz Engine            : http://192.168.1.108:8002/docs"
echo "Activities Engine      : http://192.168.1.108:8010/docs"
echo "Recap Engine           : http://192.168.1.108:8011/docs"
echo "Publisher Engine       : http://192.168.1.108:8012/docs"

echo "-----------------------------------------"
