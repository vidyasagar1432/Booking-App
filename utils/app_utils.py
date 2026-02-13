from __future__ import annotations

import os
from datetime import date, datetime, time
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from utils.excel_db import ExcelDB

DATE_COLUMNS_BY_PRIORITY = [
    "Departure Date",
    "Check-in Date",
    "Booking Date",
]
NAME_COLUMNS_BY_PRIORITY = ["Passenger Name", "Guest Name"]


def get_db_path() -> Path:
    try:
        secret_path = st.secrets.get("BOOKINGS_FILE", "")
    except Exception:
        secret_path = ""
    env_path = os.getenv("BOOKINGS_FILE", "")
    configured = str(secret_path or env_path or "bookings.xlsx")
    return Path(configured)


def get_db() -> ExcelDB:
    path = get_db_path()
    path_key = str(path.resolve()) if path.exists() else str(path)

    if st.session_state.get("_db_path_key") != path_key:
        st.session_state["_excel_db"] = ExcelDB(path)
        st.session_state["_db_path_key"] = path_key

    return st.session_state["_excel_db"]


def normalize_display_value(value: Any) -> Any:
    if pd.isna(value):
        return ""
    if isinstance(value, pd.Timestamp):
        if value.hour == 0 and value.minute == 0 and value.second == 0:
            return value.strftime("%Y-%m-%d")
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, time):
        return value.strftime("%H:%M:%S")
    return value


def to_display_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    if hasattr(frame, "map"):
        display = frame.map(normalize_display_value)
    else:
        display = frame.applymap(normalize_display_value)

    # Streamlit's Arrow serializer can fail on mixed object columns (e.g. str + int).
    # Coerce object columns to consistent strings for stable rendering.
    object_columns = display.select_dtypes(include=["object"]).columns
    for column in object_columns:
        display[column] = display[column].astype(str)

    return display


def sanitize_editor_frame(frame: pd.DataFrame, reference_columns: list[str]) -> pd.DataFrame:
    clean = frame.copy()
    for column in reference_columns:
        if column not in clean.columns:
            clean[column] = ""
    clean = clean[reference_columns]
    clean = clean.where(pd.notna(clean), "")
    return clean


def infer_name_column(frame: pd.DataFrame) -> str | None:
    for candidate in NAME_COLUMNS_BY_PRIORITY:
        if candidate in frame.columns:
            return candidate
    return None


def infer_trip_date_column(frame: pd.DataFrame) -> str | None:
    for candidate in DATE_COLUMNS_BY_PRIORITY:
        if candidate in frame.columns:
            return candidate
    return None


def build_unified_bookings(db: ExcelDB) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for mode, frame in db.get_all_booking_data().items():
        if frame.empty:
            continue

        prepared = frame.copy()
        prepared["Mode"] = mode

        name_col = infer_name_column(prepared)
        prepared["Traveler"] = (
            prepared[name_col].astype(str).str.strip() if name_col else ""
        )

        if "Status" not in prepared.columns:
            prepared["Status"] = ""
        prepared["Status"] = prepared["Status"].astype(str).str.strip()

        if "Total Cost" in prepared.columns:
            prepared["Total Cost"] = (
                pd.to_numeric(prepared["Total Cost"], errors="coerce").fillna(0)
            )
        else:
            prepared["Total Cost"] = 0

        trip_date_col = infer_trip_date_column(prepared)
        if trip_date_col:
            prepared["Trip Date"] = pd.to_datetime(
                prepared[trip_date_col], errors="coerce"
            )
        else:
            prepared["Trip Date"] = pd.NaT

        if "Booking Date" in prepared.columns:
            prepared["Booking Date Parsed"] = pd.to_datetime(
                prepared["Booking Date"], errors="coerce"
            )
        else:
            prepared["Booking Date Parsed"] = pd.NaT

        rows.append(prepared)

    if not rows:
        return pd.DataFrame(
            columns=[
                "Booking ID",
                "Mode",
                "Traveler",
                "Trip Date",
                "Booking Date Parsed",
                "Total Cost",
                "Status",
            ]
        )
    return pd.concat(rows, ignore_index=True)


def format_currency(value: float) -> str:
    return f"INR {value:,.0f}"


def parse_user_input(column_name: str, value: Any) -> Any:
    if value is None:
        return ""

    text_value = str(value).strip()
    if not text_value:
        return ""

    if "Date" in column_name:
        parsed = pd.to_datetime(text_value, errors="coerce")
        if pd.notna(parsed):
            return parsed.date()
        return text_value

    if "Time" in column_name:
        parsed = pd.to_datetime(text_value, errors="coerce")
        if pd.notna(parsed):
            return parsed.strftime("%H:%M:%S")
        return text_value

    numeric_keywords = ("Cost", "Count", "Nights", "Number of Rooms")
    if any(keyword in column_name for keyword in numeric_keywords):
        numeric = pd.to_numeric(text_value, errors="coerce")
        if pd.notna(numeric):
            if float(numeric).is_integer():
                return int(numeric)
            return float(numeric)
        return text_value

    return text_value
