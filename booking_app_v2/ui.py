from __future__ import annotations

from datetime import date
from typing import Dict

import pandas as pd
import streamlit as st

from booking_app_v2.constants import (
    BOOKING_FIELDS,
    COMMON_FIELDS,
    CURRENCY_OPTIONS,
    STATUS_OPTIONS,
)


def render_common_fields(existing: Dict[str, str] | None = None) -> Dict[str, str]:
    values: Dict[str, str] = {}
    existing = existing or {}
    left, right = st.columns(2)

    with left:
        values["client_name"] = st.text_input(
            "Client Name", value=existing.get("client_name", "")
        )
        values["client_contact"] = st.text_input(
            "Client Contact", value=existing.get("client_contact", "")
        )
        values["number_of_passengers"] = st.number_input(
            "Number of Passengers", min_value=1, value=_to_int(existing, "number_of_passengers", 1)
        )
        values["booking_date"] = st.date_input(
            "Booking Date", value=_to_date(existing, "booking_date")
        ).isoformat()
        values["travel_start_date"] = st.date_input(
            "Travel Start Date", value=_to_date(existing, "travel_start_date")
        ).isoformat()

    with right:
        values["travel_end_date"] = st.date_input(
            "Travel End Date", value=_to_date(existing, "travel_end_date")
        ).isoformat()
        values["total_amount"] = st.text_input(
            "Total Amount", value=existing.get("total_amount", "")
        )
        values["currency"] = st.selectbox(
            "Currency",
            options=CURRENCY_OPTIONS,
            index=_option_index(CURRENCY_OPTIONS, existing.get("currency")),
        )
        values["vendor"] = st.text_input("Vendor", value=existing.get("vendor", ""))
        values["status"] = st.selectbox(
            "Status",
            options=STATUS_OPTIONS,
            index=_option_index(STATUS_OPTIONS, existing.get("status")),
        )

    values["remarks"] = st.text_area("Remarks", value=existing.get("remarks", ""))
    return values


def render_booking_fields(booking_type: str, existing: Dict[str, str] | None = None) -> Dict[str, str]:
    fields = BOOKING_FIELDS.get(booking_type, [])
    values: Dict[str, str] = {}
    existing = existing or {}

    for label, key in fields:
        if "date" in key and "time" not in key:
            values[key] = st.date_input(label, value=_to_date(existing, key)).isoformat()
        else:
            values[key] = st.text_input(label, value=existing.get(key, ""))
    return values


def render_metrics(data: pd.DataFrame) -> None:
    st.subheader("Snapshot")
    total_bookings = len(data)
    total_revenue = data["total_amount"].replace("", 0).astype(float).sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Bookings", total_bookings)
    col2.metric("Total Revenue", f"{total_revenue:,.2f}")
    col3.metric("Active Clients", data["client_name"].nunique())


def _to_date(existing: Dict[str, str], key: str) -> date:
    raw_value = existing.get(key)
    if not raw_value:
        return date.today()
    try:
        return date.fromisoformat(str(raw_value))
    except ValueError:
        return date.today()


def _to_int(existing: Dict[str, str], key: str, default: int) -> int:
    value = existing.get(key)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _option_index(options: list[str], value: str | None) -> int:
    if value in options:
        return options.index(value)
    return 0
