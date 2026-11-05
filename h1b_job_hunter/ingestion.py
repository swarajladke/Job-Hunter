"""Ingestion module to parse historical Excel tracking sheets and populate persistent SQLite state."""
from pathlib import Path
from typing import List, Dict, Any, Optional
import openpyxl

from .config import DEFAULT_TRACKERS
from .database import DatabaseManager, normalize_company_name


class TrackerIngestion:
    """Ingests historical application tracker Excel files into SQLite database."""

    def __init__(self, db: DatabaseManager):
        self.db = db

    def ingest_trackers(self, tracker_paths: Optional[List[Path]] = None) -> Dict[str, Any]:
        """Ingest all configured or provided tracker files."""
        paths = tracker_paths or DEFAULT_TRACKERS
        total_companies_added = 0
        total_links_added = 0
        details = []

        for p in paths:
            path = Path(p)
            if not path.exists():
                details.append({"path": str(path), "status": "FILE_NOT_FOUND"})
                continue

            comps, links = self._ingest_single_tracker(path)
            total_companies_added += comps
            total_links_added += links
            details.append({
                "path": str(path),
                "companies_ingested": comps,
                "links_ingested": links,
                "status": "SUCCESS"
            })

        return {
            "total_files": len(paths),
            "total_companies_ingested": total_companies_added,
            "total_links_ingested": total_links_added,
            "files": details,
            "db_stats": self.db.get_stats()
        }

    def _ingest_single_tracker(self, file_path: Path) -> tuple[int, int]:
        """Read applications sheet and store records in database."""
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet_name = "Applications" if "Applications" in wb.sheetnames else wb.sheetnames[0]
        ws = wb[sheet_name]

        # Identify column indices from header row
        header_map = {}
        for col_idx in range(1, ws.max_column + 1):
            val = ws.cell(1, col_idx).value
            if val:
                header_map[str(val).strip().lower()] = col_idx

        comp_col = header_map.get("company", 1)
        role_col = header_map.get("role", 2)
        link_col = header_map.get("job posting link", 3)

        companies_list = []
        links_list = []
        filename = file_path.name

        for row_idx in range(2, ws.max_row + 1):
            comp_val = ws.cell(row_idx, comp_col).value
            role_val = ws.cell(row_idx, role_col).value
            link_val = ws.cell(row_idx, link_col).value

            if comp_val:
                companies_list.append((str(comp_val), filename))

            if link_val:
                links_list.append((
                    str(link_val).strip(),
                    str(comp_val or "").strip(),
                    str(role_val or "").strip(),
                    filename
                ))

        self.db.add_applied_batch(companies_list, links_list)
        return len(companies_list), len(links_list)
