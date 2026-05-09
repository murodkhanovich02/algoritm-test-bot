import json
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.utils.time_format import format_time_limit


REPORTS_DIR = "reports"


def safe_filename(value: str) -> str:
    value = value.replace("#", "")
    value = value.replace("/", "_")
    value = value.replace("\\", "_")
    value = value.replace(" ", "_")
    return value


def get_question_statuses(answers_detail: str) -> list[str]:
    details = json.loads(answers_detail)

    statuses = []

    for item in details:
        if item.get("is_correct"):
            statuses.append("OK")
        else:
            statuses.append("X")

    return statuses


def generate_results_pdf(test, results: list) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)

    file_name = (
        f"results_{safe_filename(test.test_code)}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )
    file_path = os.path.join(REPORTS_DIR, file_name)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=landscape(A4),
        rightMargin=15,
        leftMargin=15,
        topMargin=20,
        bottomMargin=20,
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph(
            f"<b>Test natijalari</b> - {test.test_code}",
            styles["Title"],
        )
    )

    elements.append(
        Paragraph(
            f"Savollar soni: {test.question_count} | "
            f"Vaqt: {format_time_limit(test.time_limit_seconds)} | "
            f"O'quvchilar soni: {len(results)}",
            styles["Normal"],
        )
    )

    elements.append(Spacer(1, 14))

    header = ["Student name"]

    for i in range(1, test.question_count + 1):
        header.append(str(i))

    header.extend(["Correct", "Wrong", "Percent"])

    data = [header]

    for result in results:
        statuses = get_question_statuses(result.answers_detail)

        row = [result.full_name]
        row.extend(statuses)
        row.extend(
            [
                str(result.correct_count),
                str(result.wrong_count),
                f"{result.percentage}%",
            ]
        )

        data.append(row)

    question_col_width = 28

    col_widths = [160]
    col_widths.extend([question_col_width] * test.question_count)
    col_widths.extend([55, 55, 65])

    table = Table(
        data,
        repeatRows=1,
        colWidths=col_widths,
    )

    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
        ]
    )

    for row_index in range(1, len(data)):
        for col_index in range(1, 1 + test.question_count):
            value = data[row_index][col_index]

            if value == "OK":
                style.add("TEXTCOLOR", (col_index, row_index), (col_index, row_index), colors.green)
            elif value == "X":
                style.add("TEXTCOLOR", (col_index, row_index), (col_index, row_index), colors.red)

    table.setStyle(style)

    elements.append(table)
    doc.build(elements)

    return file_path