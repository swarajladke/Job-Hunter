"""Excel Exporter producing the exact 15-column schema with professional styling."""
from pathlib import Path
from typing import List
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from .config import EXCEL_COLUMNS
from .models import EvaluatedJob


class ExcelExporter:
    """Exports evaluated job postings into formatted Excel sheets."""

    @staticmethod
    def export(jobs: List[EvaluatedJob], output_path: Path) -> Path:
        """Create formatted .xlsx workbook with exact 15-column schema."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Applications"

        # Define Styles
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid") # Navy blue
        header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

        data_font = Font(name="Calibri", size=10, color="000000")
        link_font = Font(name="Calibri", size=10, color="0563C1", underline="single")
        regular_align = Alignment(vertical="top", wrap_text=True)
        center_align = Alignment(horizontal="center", vertical="top")

        thin_border = Border(
            left=Side(style="thin", color="D9D9D9"),
            right=Side(style="thin", color="D9D9D9"),
            top=Side(style="thin", color="D9D9D9"),
            bottom=Side(style="thin", color="D9D9D9")
        )

        # Write Headers
        ws.row_dimensions[1].height = 28
        for col_idx, col_name in enumerate(EXCEL_COLUMNS, start=1):
            cell = ws.cell(row=1, column=col_idx, value=col_name)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_align
            cell.border = thin_border

        # Write Rows
        for row_idx, job in enumerate(jobs, start=2):
            ws.row_dimensions[row_idx].height = 42
            row_data = job.to_row()
            
            for col_idx, val in enumerate(row_data, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                cell.font = data_font
                cell.alignment = regular_align
                cell.border = thin_border

                # Hyperlink for Job Posting Link
                if col_idx == 3 and val and str(val).startswith("http"):
                    cell.hyperlink = str(val)
                    cell.font = link_font

                # Center align status & applied date
                if col_idx in (5, 9):
                    cell.alignment = center_align

        # Auto-adjust column widths with bounds
        col_widths = {
            1: 18,  # Company
            2: 32,  # Role
            3: 38,  # Job Posting Link
            4: 38,  # POC
            5: 16,  # Status
            6: 28,  # Location
            7: 26,  # Salary
            8: 34,  # H1B Status
            9: 14,  # Applied Date
            10: 36, # Notes
            11: 30, # Role focus
            12: 34, # Salary review
            13: 36, # Qualification review
            14: 42, # Resume fit / why included
            15: 36  # Gaps and restrictions
        }

        for col_idx, width in col_widths.items():
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = width

        # Freeze top row
        ws.freeze_panes = "A2"

        wb.save(output_path)
        return output_path

