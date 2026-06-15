from io import BytesIO

from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROLE_LABELS = {
    "R": "Responsible",
    "A": "Accountable",
    "C": "Consulted",
    "I": "Informed",
    "V": "Verificator",
    "S": "Signator",
}


def _add_field(doc: Document, label: str, value: str) -> None:
    p = doc.add_paragraph()
    run_label = p.add_run(f"{label}: ")
    run_label.bold = True
    p.add_run(value or "—")


def _set_table_header_style(row) -> None:
    for cell in row.cells:
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
        cell._tc.get_or_add_tcPr()


def generate_function_description(fn) -> BytesIO:
    doc = Document()

    doc.add_heading(fn.name, level=1)
    doc.add_heading("Function Details", level=2)

    parts = []
    current = fn
    while current:
        parts.append(current.name)
        current = current.parent
    hierarchy = " > ".join(reversed(parts))

    _add_field(doc, "Hierarchy", hierarchy)
    _add_field(doc, "Description", fn.description)
    _add_field(doc, "Aim", fn.aim)
    _add_field(
        doc,
        "Emergency Representative",
        fn.emergency_rep.name if fn.emergency_rep else "—",
    )

    doc.add_heading("Tasks & Roles", level=2)

    if fn.task_roles:
        table = doc.add_table(rows=1, cols=3)
        table.style = "Table Grid"
        hdr = table.rows[0].cells
        hdr[0].text = "Task"
        hdr[1].text = "Role"
        hdr[2].text = "Task Description"
        _set_table_header_style(table.rows[0])

        for tr in fn.task_roles:
            row = table.add_row().cells
            row[0].text = tr.task.title
            row[1].text = f"{tr.role} — {ROLE_LABELS.get(tr.role, tr.role)}"
            row[2].text = tr.task.description
    else:
        doc.add_paragraph("No tasks assigned to this function.")

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


def generate_task_description(task) -> BytesIO:
    doc = Document()

    doc.add_heading(task.title, level=1)
    doc.add_heading("Task Details", level=2)
    _add_field(doc, "Description", task.description)

    doc.add_heading("Involved Functions", level=2)

    if task.function_roles:
        table = doc.add_table(rows=1, cols=3)
        table.style = "Table Grid"
        hdr = table.rows[0].cells
        hdr[0].text = "Function"
        hdr[1].text = "Role"
        hdr[2].text = "Hierarchy"
        _set_table_header_style(table.rows[0])

        for fr in task.function_roles:
            parts = []
            current = fr.function
            while current:
                parts.append(current.name)
                current = current.parent
            hierarchy = " > ".join(reversed(parts))

            row = table.add_row().cells
            row[0].text = fr.function.name
            row[1].text = f"{fr.role} — {ROLE_LABELS.get(fr.role, fr.role)}"
            row[2].text = hierarchy
    else:
        doc.add_paragraph("No functions assigned to this task.")

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


def generate_interface_description(fn1, fn2, shared_tasks: list[dict]) -> BytesIO:
    doc = Document()

    doc.add_heading(f"Interface: {fn1.name} ↔ {fn2.name}", level=1)

    p = doc.add_paragraph()
    p.add_run("This document describes the shared tasks between ")
    p.add_run(fn1.name).bold = True
    p.add_run(" and ")
    p.add_run(fn2.name).bold = True
    p.add_run(" and their respective roles.")

    doc.add_heading("Shared Tasks", level=2)

    if shared_tasks:
        table = doc.add_table(rows=1, cols=4)
        table.style = "Table Grid"
        hdr = table.rows[0].cells
        hdr[0].text = "Task"
        hdr[1].text = f"Role of {fn1.name}"
        hdr[2].text = f"Role of {fn2.name}"
        hdr[3].text = "Task Description"
        _set_table_header_style(table.rows[0])

        for item in shared_tasks:
            row = table.add_row().cells
            row[0].text = item["task_title"]
            role1 = item["role_f1"]
            role2 = item["role_f2"]
            row[1].text = f"{role1} — {ROLE_LABELS.get(role1, role1)}"
            row[2].text = f"{role2} — {ROLE_LABELS.get(role2, role2)}"
            row[3].text = item["task_description"]
    else:
        doc.add_paragraph(f"{fn1.name} and {fn2.name} share no tasks.")

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf
