from __future__ import annotations

import threading
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd

UPDATE_SHEET_NAME = "update time"
DEFAULT_BOOKING_SHEETS = ("Flight", "Hotel", "Train", "Bus")


class ExcelDB:
    """Thin Excel-backed storage layer for booking operations."""

    def __init__(self, file_path: Path | str) -> None:
        self.file_path = Path(file_path)
        self._lock = threading.Lock()
        if not self.file_path.exists():
            raise FileNotFoundError(f"Workbook not found: {self.file_path}")

    def _read_workbook(self) -> dict[str, pd.DataFrame]:
        return pd.read_excel(self.file_path, sheet_name=None, engine="openpyxl")

    def _write_workbook(self, sheets: dict[str, pd.DataFrame]) -> None:
        with pd.ExcelWriter(self.file_path, engine="openpyxl", mode="w") as writer:
            for sheet_name, frame in sheets.items():
                frame.to_excel(writer, sheet_name=sheet_name, index=False)

    def _normalize_dataframe(
        self, frame: pd.DataFrame, reference_columns: list[str]
    ) -> pd.DataFrame:
        normalized = frame.copy()
        for column in reference_columns:
            if column not in normalized.columns:
                normalized[column] = ""
        normalized = normalized[reference_columns]
        return normalized.where(pd.notna(normalized), "")

    def booking_sheets(self) -> list[str]:
        workbook = self._read_workbook()
        available = [sheet for sheet in DEFAULT_BOOKING_SHEETS if sheet in workbook]
        if available:
            return available
        return [sheet for sheet in workbook if sheet.lower() != UPDATE_SHEET_NAME.lower()]

    def get_sheet(self, sheet_name: str) -> pd.DataFrame:
        workbook = self._read_workbook()
        if sheet_name not in workbook:
            raise ValueError(f"Sheet not found: {sheet_name}")
        return workbook[sheet_name].copy()

    def get_all_booking_data(self) -> dict[str, pd.DataFrame]:
        workbook = self._read_workbook()
        return {sheet: workbook[sheet].copy() for sheet in self.booking_sheets()}

    def _build_update_sheet(self) -> pd.DataFrame:
        now = datetime.now()
        return pd.DataFrame(
            [{"Updated on": now.date().isoformat(), "TIme": now.strftime("%H:%M:%S")}]
        )

    def save_sheet(self, sheet_name: str, frame: pd.DataFrame) -> None:
        with self._lock:
            workbook = self._read_workbook()
            if sheet_name not in workbook:
                raise ValueError(f"Sheet not found: {sheet_name}")

            reference_columns = list(workbook[sheet_name].columns)
            workbook[sheet_name] = self._normalize_dataframe(frame, reference_columns)
            workbook[UPDATE_SHEET_NAME] = self._build_update_sheet()
            self._write_workbook(workbook)

    def append_record(self, sheet_name: str, record: dict[str, Any]) -> str:
        current = self.get_sheet(sheet_name)
        record_row: dict[str, Any] = {}
        for column in current.columns:
            record_row[column] = record.get(column, "")

        if "Booking ID" in current.columns and not str(
            record_row.get("Booking ID", "")
        ).strip():
            record_row["Booking ID"] = self.generate_booking_id(sheet_name)

        updated = pd.concat([current, pd.DataFrame([record_row])], ignore_index=True)
        self.save_sheet(sheet_name, updated)
        return str(record_row.get("Booking ID", ""))

    def generate_booking_id(self, sheet_name: str) -> str:
        prefix_map = {"Flight": "FL", "Hotel": "HT", "Train": "TR", "Bus": "BS"}
        prefix = prefix_map.get(sheet_name, (sheet_name[:2] or "BK").upper())
        timestamp = datetime.now().strftime("%y%m%d%H%M%S")
        suffix = uuid4().hex[:4].upper()
        return f"{prefix}{timestamp}{suffix}"

    def update_record(
        self, sheet_name: str, booking_id: str, updates: dict[str, Any]
    ) -> bool:
        current = self.get_sheet(sheet_name)
        if "Booking ID" not in current.columns:
            return False

        booking_id_value = str(booking_id).strip()
        matches = current["Booking ID"].astype(str).str.strip() == booking_id_value
        if not matches.any():
            return False

        row_index = current[matches].index[0]
        for column, value in updates.items():
            if column in current.columns:
                current.at[row_index, column] = value

        self.save_sheet(sheet_name, current)
        return True

    def delete_record(self, sheet_name: str, booking_id: str) -> bool:
        current = self.get_sheet(sheet_name)
        if "Booking ID" not in current.columns:
            return False

        booking_id_value = str(booking_id).strip()
        matches = current["Booking ID"].astype(str).str.strip() == booking_id_value
        if not matches.any():
            return False

        updated = current.loc[~matches].reset_index(drop=True)
        self.save_sheet(sheet_name, updated)
        return True

    def get_last_updated(self) -> str:
        workbook = self._read_workbook()
        update_sheet = workbook.get(UPDATE_SHEET_NAME)
        if update_sheet is None or update_sheet.empty:
            return "Unknown"

        row = update_sheet.iloc[0]
        updated_on = row.get("Updated on", "")
        updated_time = row.get("TIme", "")

        if pd.notna(updated_on) and hasattr(updated_on, "strftime"):
            updated_on_str = updated_on.strftime("%Y-%m-%d")
        else:
            updated_on_str = str(updated_on).strip()

        updated_time_str = str(updated_time).strip()
        timestamp = " ".join(part for part in [updated_on_str, updated_time_str] if part)
        return timestamp or "Unknown"
