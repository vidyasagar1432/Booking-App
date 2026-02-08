import os
from typing import Dict

import pandas as pd
import streamlit as st

from .constants import EXCEL_FILE, SHEETS_CONFIG


def initialize_excel_file():
    """Create the Excel file and required sheets if they don't exist."""
    if not os.path.exists(EXCEL_FILE):
        with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
            for sheet_name, cfg in SHEETS_CONFIG.items():
                df = pd.DataFrame(columns=cfg["columns"])
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        try:
            xl = pd.ExcelFile(EXCEL_FILE, engine="openpyxl")
            existing_sheets = xl.sheet_names
        except Exception:
            with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
                for sheet_name, cfg in SHEETS_CONFIG.items():
                    df = pd.DataFrame(columns=cfg["columns"])
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            return

        for sheet_name, cfg in SHEETS_CONFIG.items():
            required_cols = cfg["columns"]

            if sheet_name in existing_sheets:
                df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, engine="openpyxl")

                for col in required_cols:
                    if col not in df.columns:
                        df[col] = ""

                extra_cols = [c for c in df.columns if c not in required_cols]
                df = df[required_cols + extra_cols]

                with pd.ExcelWriter(
                    EXCEL_FILE,
                    engine="openpyxl",
                    mode="a",
                    if_sheet_exists="replace",
                ) as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                df = pd.DataFrame(columns=required_cols)
                with pd.ExcelWriter(
                    EXCEL_FILE,
                    engine="openpyxl",
                    mode="a",
                ) as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)


def load_sheet(sheet_name: str) -> pd.DataFrame:
    """Load a sheet into a DataFrame. Return empty DF with proper columns if missing."""
    initialize_excel_file()
    cfg = SHEETS_CONFIG.get(sheet_name)
    columns = cfg["columns"] if cfg else None

    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, engine="openpyxl")
    except ValueError:
        df = pd.DataFrame(columns=columns)
    except FileNotFoundError:
        initialize_excel_file()
        df = pd.DataFrame(columns=columns)

    if columns:
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        extra_cols = [c for c in df.columns if c not in columns]
        df = df[columns + extra_cols]

    return df


def save_sheet(sheet_name: str, df: pd.DataFrame):
    """Save a DataFrame back to the specific sheet in the Excel file."""
    initialize_excel_file()
    with pd.ExcelWriter(
        EXCEL_FILE,
        engine="openpyxl",
        mode="a",
        if_sheet_exists="replace",
    ) as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


def generate_new_id(df: pd.DataFrame) -> int:
    """Generate a new integer ID based on the current max ID in the sheet."""
    if df.empty or "id" not in df.columns:
        return 1

    try:
        numeric_ids = pd.to_numeric(df["id"], errors="coerce")
        max_id = numeric_ids.max()
        if pd.isna(max_id):
            return 1
        return int(max_id) + 1
    except Exception:
        return 1


def get_sheet_name_from_booking_type(booking_type: str) -> str:
    """Map booking type to sheet name (they are the same in this design)."""
    return booking_type


@st.cache_data
def load_all_sheets_cached() -> Dict[str, pd.DataFrame]:
    """Return a dictionary of sheet_name -> DataFrame (cached)."""
    result = {}
    for sheet in SHEETS_CONFIG.keys():
        result[sheet] = load_sheet(sheet)
    return result


__all__ = [
    "initialize_excel_file",
    "load_sheet",
    "save_sheet",
    "generate_new_id",
    "get_sheet_name_from_booking_type",
    "load_all_sheets_cached",
]
