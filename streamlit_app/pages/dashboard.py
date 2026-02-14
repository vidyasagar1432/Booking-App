from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.app_utils import build_unified_bookings, format_currency, get_db


def render() -> None:
    st.title("Dashboard")
    st.caption("Cross-channel booking summary from the Excel workbook")

    db = get_db()
    bookings = build_unified_bookings(db)

    if bookings.empty:
        st.info("No booking records available yet.")
        return

    total_bookings = len(bookings)
    total_spend = float(bookings["Total Cost"].sum())
    upcoming_count = int(bookings["Is Upcoming"].fillna(False).sum())
    completed_count = int(
        bookings["Status"].str.lower().str.strip().eq("travelled").sum()
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Bookings", f"{total_bookings:,}")
    m2.metric("Total Spend", format_currency(total_spend))
    m3.metric("Upcoming Trips", f"{upcoming_count:,}")
    m4.metric("Completed Trips", f"{completed_count:,}")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Bookings by Mode")
        by_mode = (
            bookings.groupby("Mode")
            .agg(Bookings=("Mode", "count"), Spend=("Total Cost", "sum"))
            .sort_values("Bookings", ascending=False)
        )
        st.bar_chart(by_mode["Bookings"], width="stretch")
        st.dataframe(by_mode, width="stretch")

    with c2:
        st.subheader("Status Distribution")
        by_status = (
            bookings.assign(Status=bookings["Status"].replace({"": "Unknown"}))
            .groupby("Status")
            .size()
            .sort_values(ascending=False)
        )
        st.bar_chart(by_status, width="stretch")

    trend_source = bookings.dropna(subset=["Trip Date"]).copy()
    if not trend_source.empty:
        st.subheader("Monthly Spend Trend")
        trend_source["Month"] = trend_source["Trip Date"].dt.to_period("M").dt.to_timestamp()
        monthly_spend = trend_source.groupby("Month")["Total Cost"].sum().sort_index()
        st.line_chart(monthly_spend, width="stretch")

    upcoming = bookings.loc[bookings["Is Upcoming"].fillna(False)].copy()
    upcoming = upcoming.sort_values(["Trip Start", "Trip End"], na_position="last").head(20)
    if not upcoming.empty:
        st.subheader("Upcoming Bookings")
        display_columns = [
            "Mode",
            "Booking ID",
            "Traveler",
            "Trip Start",
            "Trip End",
            "Status",
            "Total Cost",
        ]
        safe_columns = [column for column in display_columns if column in upcoming.columns]
        if "Trip Start" in upcoming.columns:
            upcoming["Trip Start"] = upcoming["Trip Start"].dt.strftime("%Y-%m-%d")
        if "Trip End" in upcoming.columns:
            upcoming["Trip End"] = upcoming["Trip End"].dt.strftime("%Y-%m-%d")
        st.dataframe(upcoming[safe_columns], width="stretch", hide_index=True)
