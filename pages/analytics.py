from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.app_utils import build_unified_bookings, format_currency, get_db, to_display_frame

ROUTE_COLUMN_PAIRS = [
    ("From Airport", "To Airport"),
    ("From City", "To City"),
    ("From Station", "To Station"),
]
LEAD_TIME_BINS = [-9999, 0, 3, 7, 14, 30, 60, 9999]
LEAD_TIME_LABELS = [
    "Same day / Past",
    "1-3 days",
    "4-7 days",
    "8-14 days",
    "15-30 days",
    "31-60 days",
    "61+ days",
]


def _resolve_date_range_input(
    selected_value, fallback_start: pd.Timestamp, fallback_end: pd.Timestamp
) -> tuple[pd.Timestamp, pd.Timestamp]:
    start = fallback_start
    end = fallback_end

    if isinstance(selected_value, (tuple, list)):
        if len(selected_value) >= 2:
            start = pd.Timestamp(selected_value[0])
            end = pd.Timestamp(selected_value[1])
        elif len(selected_value) == 1:
            start = pd.Timestamp(selected_value[0])
            end = pd.Timestamp(selected_value[0])
    elif selected_value is not None:
        start = pd.Timestamp(selected_value)
        end = pd.Timestamp(selected_value)

    if end < start:
        start, end = end, start

    return start.normalize(), end.normalize()


def _build_route_series(frame: pd.DataFrame) -> pd.Series:
    route = pd.Series("", index=frame.index, dtype="object")
    for from_col, to_col in ROUTE_COLUMN_PAIRS:
        if from_col not in frame.columns or to_col not in frame.columns:
            continue
        from_value = frame[from_col].fillna("").astype(str).str.strip()
        to_value = frame[to_col].fillna("").astype(str).str.strip()
        candidate = from_value + " -> " + to_value
        valid = from_value.ne("") & to_value.ne("")
        route = route.mask(route.eq("") & valid, candidate)
    return route.replace("", pd.NA)


def render() -> None:
    st.title("Analytics Dashboard")
    st.caption("Trends, performance, and booking intelligence across all channels")

    db = get_db()
    bookings = build_unified_bookings(db)

    if bookings.empty:
        st.info("No booking records available yet.")
        return

    mode_options = sorted(bookings["Mode"].dropna().astype(str).unique().tolist())
    status_options = sorted(
        status for status in bookings["Status"].dropna().astype(str).unique().tolist() if status
    )

    filters_row = st.columns([1, 1, 1])
    with filters_row[0]:
        selected_modes = st.multiselect("Modes", mode_options, default=mode_options)
    with filters_row[1]:
        selected_status = st.multiselect("Status", status_options, default=status_options)
    with filters_row[2]:
        date_basis = st.radio(
            "Date basis",
            options=["Trip Start", "Booking Date"],
            horizontal=True,
        )

    filtered = bookings.copy()
    if selected_modes:
        filtered = filtered[filtered["Mode"].isin(selected_modes)]
    if selected_status:
        filtered = filtered[filtered["Status"].isin(selected_status)]

    date_column = "Trip Start" if date_basis == "Trip Start" else "Booking Date Parsed"
    date_source = pd.to_datetime(filtered[date_column], errors="coerce")
    dated = filtered[date_source.notna()].copy()
    if not dated.empty:
        min_date = pd.to_datetime(dated[date_column], errors="coerce").min().normalize()
        max_date = pd.to_datetime(dated[date_column], errors="coerce").max().normalize()
        date_input_value = st.date_input(
            f"{date_basis} range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
        )
        start_date, end_date = _resolve_date_range_input(date_input_value, min_date, max_date)
        filter_dates = pd.to_datetime(filtered[date_column], errors="coerce")
        filtered = filtered[
            filter_dates.between(start_date, end_date + pd.Timedelta(days=1), inclusive="left")
            | filter_dates.isna()
        ]

    total_bookings = len(filtered)
    total_spend = float(filtered["Total Cost"].sum())
    average_cost = float(filtered["Total Cost"].mean()) if total_bookings else 0.0
    upcoming_count = int(filtered["Is Upcoming"].fillna(False).sum())
    cancelled_count = int(filtered["Status"].astype(str).str.strip().str.lower().eq("cancelled").sum())
    cancellation_rate = (cancelled_count / total_bookings * 100.0) if total_bookings else 0.0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Bookings", f"{total_bookings:,}")
    k2.metric("Spend", format_currency(total_spend))
    k3.metric("Avg Cost", format_currency(average_cost))
    k4.metric("Upcoming", f"{upcoming_count:,}")
    k5.metric("Cancellation %", f"{cancellation_rate:.1f}%")

    trend_date = pd.to_datetime(filtered[date_column], errors="coerce")
    trend_source = filtered[trend_date.notna()].copy()
    if not trend_source.empty:
        st.subheader("Monthly Trend")
        trend_source["Month"] = pd.to_datetime(
            trend_source[date_column], errors="coerce"
        ).dt.to_period("M").dt.to_timestamp()
        monthly = (
            trend_source.groupby("Month")
            .agg(Bookings=("Mode", "count"), Spend=("Total Cost", "sum"))
            .sort_index()
        )
        t1, t2 = st.columns(2)
        with t1:
            st.caption("Bookings")
            st.line_chart(monthly["Bookings"], width="stretch")
        with t2:
            st.caption("Spend")
            st.line_chart(monthly["Spend"], width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Mode Performance")
        by_mode = (
            filtered.groupby("Mode")
            .agg(
                Bookings=("Mode", "count"),
                Spend=("Total Cost", "sum"),
                Avg_Cost=("Total Cost", "mean"),
                Upcoming=("Is Upcoming", "sum"),
            )
            .sort_values("Spend", ascending=False)
        )
        st.bar_chart(by_mode["Spend"], width="stretch")
        st.dataframe(to_display_frame(by_mode.reset_index()), width="stretch", hide_index=True)

    with c2:
        st.subheader("Status by Mode")
        status_view = filtered.copy()
        status_view["Status"] = status_view["Status"].replace({"": "Unknown"})
        pivot = (
            status_view.pivot_table(
                index="Mode",
                columns="Status",
                values="Booking ID",
                aggfunc="count",
                fill_value=0,
            )
            .sort_index()
        )
        if not pivot.empty:
            st.bar_chart(pivot, width="stretch")
            st.dataframe(to_display_frame(pivot.reset_index()), width="stretch", hide_index=True)
        else:
            st.info("No status data available.")

    d1, d2 = st.columns(2)
    with d1:
        st.subheader("Top Travelers")
        travelers = filtered[filtered["Traveler"].astype(str).str.strip().ne("")]
        if travelers.empty:
            st.info("Traveler names are not available.")
        else:
            top_travelers = (
                travelers.groupby("Traveler")
                .agg(Bookings=("Traveler", "count"), Spend=("Total Cost", "sum"))
                .sort_values(["Spend", "Bookings"], ascending=False)
                .head(10)
            )
            st.dataframe(to_display_frame(top_travelers.reset_index()), width="stretch", hide_index=True)

    with d2:
        st.subheader("Top Routes")
        routes = filtered.copy()
        routes["Route"] = _build_route_series(routes)
        routes = routes[routes["Route"].notna()]
        if routes.empty:
            st.info("Route columns are not available for current filters.")
        else:
            top_routes = (
                routes.groupby("Route")
                .agg(Bookings=("Route", "count"), Spend=("Total Cost", "sum"))
                .sort_values(["Bookings", "Spend"], ascending=False)
                .head(10)
            )
            st.dataframe(to_display_frame(top_routes.reset_index()), width="stretch", hide_index=True)

    st.subheader("Lead Time Analysis")
    lead_source = filtered.dropna(subset=["Trip Start", "Booking Date Parsed"]).copy()
    if lead_source.empty:
        st.info("Lead-time analysis needs both booking date and trip start date.")
    else:
        lead_days = (
            pd.to_datetime(lead_source["Trip Start"], errors="coerce")
            - pd.to_datetime(lead_source["Booking Date Parsed"], errors="coerce")
        ).dt.days.dropna()
        if lead_days.empty:
            st.info("Lead-time analysis needs valid dates.")
        else:
            l1, l2 = st.columns(2)
            l1.metric("Median Lead Time", f"{int(lead_days.median()):,} days")
            l2.metric("Average Lead Time", f"{lead_days.mean():.1f} days")

            buckets = pd.cut(lead_days, bins=LEAD_TIME_BINS, labels=LEAD_TIME_LABELS)
            lead_distribution = buckets.value_counts().reindex(LEAD_TIME_LABELS, fill_value=0)
            st.bar_chart(lead_distribution, width="stretch")

    csv_bytes = to_display_frame(filtered).to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Analytics Dataset",
        data=csv_bytes,
        file_name="analytics_dataset.csv",
        mime="text/csv",
    )

