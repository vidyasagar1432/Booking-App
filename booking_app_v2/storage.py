from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable

import pandas as pd

from booking_app_v2.constants import ALL_COLUMNS, DATA_FILE


def initialize_storage() -> Path:
    path = Path(DATA_FILE)
    if not path.exists():
        empty_frame = pd.DataFrame(columns=ALL_COLUMNS)
        empty_frame.to_csv(path, index=False)
    return path


def load_bookings() -> pd.DataFrame:
    initialize_storage()
    return pd.read_csv(DATA_FILE)


def save_bookings(data: pd.DataFrame) -> None:
    data.to_csv(DATA_FILE, index=False)


def next_booking_id(data: pd.DataFrame) -> int:
    if data.empty:
        return 1001
    return int(data["booking_id"].max()) + 1


def normalize_record(record: Dict[str, str], columns: Iterable[str]) -> Dict[str, str]:
    return {column: record.get(column, "") for column in columns}
