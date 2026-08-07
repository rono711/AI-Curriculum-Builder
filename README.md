# AI Curriculum Builder Platform

Version: 1.0.0

Author: Mohammad Hassan

---

# Overview

The AI Curriculum Builder Platform is an automated curriculum production system that converts Australian Curriculum content into complete AI-generated lesson packages.

The platform uses:

- n8n for workflow orchestration
- Python for workbook generation
- Excel as the master data store
- Moodle for LMS publishing
- AI services (Gamma, OpenAI, Google AI, NotebookLM, etc.) for content generation

---

# Current Status

## Workflow 1

Lesson Database Builder

Status:

Completed

---

## Workflow 2

Workbook Builder

Status:

Completed

Functions:

- Reads Lesson_DB
- Creates WorkbookRequest
- Generates Curriculum Workbook
- Populates all worksheets
- Saves workbook automatically

---

# Folder Structure

```
AI-Curriculum-Builder/

│
├── data/
├── docs/
├── input/
├── logs/
├── output/
├── requests/
├── scripts/
│     └── workbook/
│
├── templates/
├── temp/
├── workflows/
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

# Workbook Structure

The workbook contains seven worksheets.

1. Curriculum_Master

Master curriculum database.

2. AI_Generation

Tracks AI generated resources.

3. Prompt_Library

Stores reusable prompts.

4. Moodle_Mapping

Tracks Moodle publishing.

5. Generation_Log

Generation history.

6. Dashboard

Reporting.

7. Instructions

Documentation.

---

# Technologies

- Python 3.8+
- openpyxl
- python-dateutil
- n8n
- Docker
- Synology NAS
- Git
- GitHub

---

# Installation

Clone repository

```
git clone <repository>
```

Create virtual environment

```
python3 -m venv venv
```

Activate

Linux

```
source venv/bin/activate
```

Windows

```
venv\Scripts\activate
```

Install packages

```
pip install -r requirements.txt
```

---

# Run Workbook Generator

```
cd scripts/workbook

python workbook_generator.py
```

---

# Workflow

```
Lesson_DB
      │
      ▼
Create Workbook Data
      │
      ▼
WorkbookRequest.json
      │
      ▼
Workbook Generator
      │
      ▼
Excel Workbook
```

---

# Version History

## Version 1.0.0

Initial working release.

Features

- Workbook generation
- Template preservation
- Worksheet population
- Logging
- JSON request processing

---

# Future Work

Workflow 3

Prompt Builder

Workflow 4

Gamma Presentation Generator

Workflow 5

Assessment Generator

Workflow 6

NotebookLM Package Builder

Workflow 7

Moodle Publisher

Workflow 8

Quality Assurance

Workflow 9

Deployment Dashboard

---
Starting the Engine

Development

API only

python -m scripts.engine.start_api

Complete Engine

python -m scripts.engine.start

# License

Private Repository

Copyright © Mohammad Hassan