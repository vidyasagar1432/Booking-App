from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.app_utils import build_unified_bookings, format_currency, get_db, to_display_frame

SEARCH_CANDIDATE_COLUMNS = [
    "Booking ID",
    "Traveler",
    "Company Name",
    "From Airport",
    "To Airport",
    "From City",
    "To City",
    "From Station",
    "To Station",
    "Airline",
    "Vendor",
    "Hotel Name",
    "Bus Company",
    "Train Name",
    "Status",
]


def _apply_search_filter(frame: pd.DataFrame, query: str) -> pd.DataFrame:
    if not query.strip():
        return frame

    available = [column for column in SEARCH_CANDIDATE_COLUMNS if column in frame.columns]
    if not available:
        return frame

    blob = frame[available].fillna("").astype(str).agg(" ".join, axis=1)
    matches = blob.str.contains(query, case=False, na=False)
    return frame[matches]


def render() -> None:
    st.title("Bookings Explorer")
    st.caption("Filter and export booking records across all channels")

    db = get_db()
    bookings = build_unified_bookings(db)

    if bookings.empty:
        st.info("No booking records available yet.")
        return

    mode_options = db.booking_sheets()
    status_options = sorted(
        status for status in bookings["Status"].dropna().astype(str).unique().tolist() if status
    )

    f1, f2, f3 = st.columns([1, 1, 2])
    with f1:
        selected_modes = st.multiselect("Mode", mode_options, default=mode_options)
    with f2:
        selected_status = st.multiselect("Status", status_options, default=status_options)
    with f3:
        search_text = st.text_input("Search", placeholder="Booking ID, traveler, route, vendor...")

    filtered = bookings.copy()
    if selected_modes:
        filtered = filtered[filtered["Mode"].isin(selected_modes)]
    if selected_status:
        filtered = filtered[filtered["Status"].isin(selected_status)]
    filtered = _apply_search_filter(filtered, search_text)

    dated = filtered.dropna(subset=["Trip Date"])
    if not dated.empty:
        min_date = dated["Trip Date"].min().date()
        max_date = dated["Trip Date"].max().date()
        date_value = st.date_input(
            "Trip date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

        if isinstance(date_value, (tuple, list)):
            if len(date_value) >= 2:
                start_date, end_date = date_value[0], date_value[1]
            elif len(date_value) == 1:
                start_date = end_date = date_value[0]
            else:
                start_date, end_date = min_date, max_date
        else:
            start_date = end_date = date_value or min_date

        filtered = filtered[
            filtered["Trip Date"].between(
                pd.Timestamp(start_date), pd.Timestamp(end_date)
            )
            | filtered["Trip Date"].isna()
        ]

    metric1, metric2 = st.columns(2)
    metric1.metric("Filtered Bookings", f"{len(filtered):,}")
    metric2.metric("Filtered Spend", format_currency(float(filtered["Total Cost"].sum())))

    display_columns = [
        "Mode",
        "Booking ID",
        "Traveler",
        "Status",
        "Trip Date",
        "Total Cost",
        "Company Name",
        "Vendor",
        "Airline",
        "Hotel Name",
        "Bus Company",
        "Train Name",
    ]
    safe_columns = [column for column in display_columns if column in filtered.columns]

    view = filtered[safe_columns].copy()
    if "Trip Date" in view.columns:
        view["Trip Date"] = view["Trip Date"].dt.strftime("%Y-%m-%d")
    st.dataframe(to_display_frame(view), width="stretch", hide_index=True)

    csv_bytes = to_display_frame(filtered).to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Filtered CSV",
        data=csv_bytes,
        file_name="filtered_bookings.csv",
        mime="text/csv",
    )
