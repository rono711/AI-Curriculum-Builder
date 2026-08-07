from datetime import datetime

from config import SHEET_BUILD_LOG


def write_build_log(

        workbook,

        request

):
    sheet = workbook[SHEET_BUILD_LOG]

    sheet.append([

        datetime.now().strftime(

            "%Y-%m-%d %H:%M:%S"

        ),

        "Lesson Package Builder",

        "Workbook Created",

        "SUCCESS",

        request["build_filename"]

    ])
