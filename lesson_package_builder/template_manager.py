from pathlib import Path
from shutil import copy2

from openpyxl import load_workbook

from config import WORKBOOK_TEMPLATE


# ==========================================================
# Copy Workbook Template
# ==========================================================

def create_workbook(destination):
    destination = Path(destination)

    destination.parent.mkdir(

        parents=True,

        exist_ok=True

    )

    copy2(

        WORKBOOK_TEMPLATE,

        destination

    )

    return destination


# ==========================================================
# Open Workbook
# ==========================================================

def open_workbook(workbook_path):
    workbook = load_workbook(

        workbook_path

    )

    return workbook


# ==========================================================
# Save Workbook
# ==========================================================

def save_workbook(

        workbook,

        workbook_path

):
    workbook.save(

        workbook_path

    )


# ==========================================================
# Close Workbook
# ==========================================================

def close_workbook(

        workbook

):
    workbook.close()


# ==========================================================
# Create + Open
# ==========================================================

def new_workbook(destination):
    create_workbook(destination)

    return open_workbook(destination)
