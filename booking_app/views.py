import io
from typing import Tuple, Union, cast

import datetime as dt
import pandas as pd
import plotly.express as px
import streamlit as st

from .storage import load_all_sheets_cached, load_sheet


def render_summary_metrics(df: pd.DataFrame):
    st.subheader("Summary")

    total_bookings = len(df)
    total_amount = pd.to_numeric(
        df.get("total_amount", pd.Series([])), errors="coerce"
    ).sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total bookings", int(total_bookings))
    col2.metric("Total amount", f"{total_amount:,.2f}")
    status_counts = df.get("status", pd.Series([])).value_counts()
    top_status = status_counts.index[0] if not status_counts.empty else "N/A"
    top_status_count = int(status_counts.iloc[0]) if not status_counts.empty else 0
    col3.metric(f"Top status", f"{top_status} ({top_status_count})")


def filtered_dataframe_ui(df: pd.DataFrame, booking_type: str) -> pd.DataFrame:
    if df.empty:
        st.info(f"No {booking_type} bookings found.")
        return df

    with st.expander("Filters", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            date_filter_field = st.selectbox(
                "Filter by date field",
                ["travel_start_date", "booking_date"],
            )

            date_series = pd.to_datetime(df[date_filter_field], errors="coerce")
            min_date = (
                date_series.min().date()
                if not date_series.dropna().empty
                else dt.date.today()
            )
            max_date = (
                date_series.max().date()
                if not date_series.dropna().empty
                else dt.date.today()
            )

            date_range = st.date_input("Date range", value=(min_date, max_date))
            date_range = cast(Union[Tuple[dt.date, dt.date], dt.date], date_range)
            start_date, end_date = (
                date_range
                if isinstance(date_range, tuple)
                else (date_range, date_range)
            )

        with col2:
            client_name_filter = st.text_input("Search by client name (contains)")
            status_options = ["All"] + sorted(
                [s for s in df["status"].dropna().unique().tolist()]
            )
            status_filter = st.selectbox("Filter by status", status_options)

            pnr_filter = ""
            if booking_type in ["Flight", "Train", "Bus"]:
                pnr_filter = st.text_input("Search by PNR (exact match)")

    filtered = df.copy()

    date_series = pd.to_datetime(filtered[date_filter_field], errors="coerce")
    mask = (date_series.dt.date >= start_date) & (date_series.dt.date <= end_date)
    filtered = filtered[mask]

    if client_name_filter:
        filtered = filtered[
            filtered["client_name"]
            .astype(str)
            .str.contains(client_name_filter, case=False, na=False)
        ]

    if status_filter != "All":
        filtered = filtered[filtered["status"] == status_filter]

    if pnr_filter and booking_type in ["Flight", "Train", "Bus"]:
        if "pnr" in filtered.columns:
            filtered = filtered[filtered["pnr"].astype(str) == pnr_filter]

    return filtered


def download_buttons(df: pd.DataFrame, label_prefix: str = "Download"):
    if df.empty:
        return

    col1, col2 = st.columns(2)

    with col1:
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"{label_prefix} as CSV",
            data=csv_data,
            file_name=f"{label_prefix.replace(' ', '_').lower()}.csv",
            mime="text/csv",
        )

    with col2:
        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Data")
        towrite.seek(0)
        st.download_button(
            label=f"{label_prefix} as Excel",
            data=towrite,
            file_name=f"{label_prefix.replace(' ', '_').lower()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def render_dashboard():
    st.subheader("Dashboard overview")

    sheets = load_all_sheets_cached()
    combined = (
        pd.concat(
            [
                df.assign(booking_type=name)
                for name, df in sheets.items()
                if not df.empty
            ],
            ignore_index=True,
        )
        if any([not df.empty for df in sheets.values()])
        else pd.DataFrame()
    )

    if combined.empty:
        st.info("No bookings found across all types yet.")
        return

    total_bookings = len(combined)
    total_amount = pd.to_numeric(
        combined.get("total_amount", pd.Series([])), errors="coerce"
    ).sum()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total bookings", int(total_bookings))
    col2.metric("Total amount", f"{total_amount:,.2f}")

    status_counts = combined.get("status", pd.Series([])).value_counts()
    top_status = status_counts.index[0] if not status_counts.empty else "N/A"
    top_status_count = int(status_counts.iloc[0]) if not status_counts.empty else 0
    col3.metric(f"Top status", f"{top_status} ({top_status_count})")

    st.markdown("### Bookings by type")
    type_counts = (
        combined["booking_type"]
        .value_counts()
        .rename_axis("type")
        .reset_index(name="count")
    )
    st.bar_chart(type_counts.set_index("type"))

    st.markdown("### Bookings by status")
    status_counts = (
        combined["status"]
        .fillna("Unknown")
        .value_counts()
        .rename_axis("status")
        .reset_index(name="count")
    )
    st.bar_chart(status_counts.set_index("status"))

    st.markdown("### Revenue by booking month")
    booking_dates = pd.to_datetime(combined["booking_date"], errors="coerce")
    revenue_df = combined.copy()
    revenue_df["booking_month"] = booking_dates.dt.to_period("M").dt.to_timestamp()
    revenue_df["total_amount_numeric"] = pd.to_numeric(
        revenue_df.get("total_amount", pd.Series([])), errors="coerce"
    )
    revenue_monthly = (
        revenue_df.groupby("booking_month")["total_amount_numeric"]
        .sum()
        .reset_index()
        .dropna()
    )
    if not revenue_monthly.empty:
        st.line_chart(revenue_monthly.set_index("booking_month"))
    else:
        st.info("No booking dates available to chart revenue.")

    st.markdown("### Recent bookings")
    recent = combined.copy()
    recent["booking_date_sort"] = pd.to_datetime(
        recent["booking_date"], errors="coerce"
    )
    recent = recent.sort_values(by="booking_date_sort", ascending=False)
    st.dataframe(
        recent.head(10).drop(columns=["booking_date_sort"], errors="ignore"),
        use_container_width=True,
    )

    st.markdown("---")
    st.subheader("Advanced Analytics")

    st.markdown("#### Distribution of bookings by type")
    booking_counts = {name: len(df) for name, df in sheets.items()}
    if sum(booking_counts.values()) > 0:
        fig = px.pie(
            values=list(booking_counts.values()),
            names=list(booking_counts.keys()),
            title="Distribution of Bookings by Type",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(
            "No bookings data available yet. Add data to your Excel sheets to see visualizations."
        )

    if (
        "total_amount" in combined.columns
        and not combined["total_amount"].dropna().empty
    ):
        st.markdown("#### Revenue by booking type")
        revenue_by_type = combined.groupby("booking_type")["total_amount"].sum()
        fig = px.bar(
            x=revenue_by_type.index,
            y=revenue_by_type.values,
            title="Revenue by Booking Type",
            labels={"x": "Booking Type", "y": "Revenue"},
            color=revenue_by_type.index,
        )
        st.plotly_chart(fig, use_container_width=True)

    if "client_name" in combined.columns:
        st.markdown("#### Top 10 Clients by booking count")
        top_clients = combined["client_name"].value_counts().head(10)
        fig = px.bar(
            top_clients.values,
            x=top_clients.values,
            y=top_clients.index,
            orientation="h",
            labels={"x": "Number of Bookings", "y": "Client Name"},
            title="Top 10 Clients",
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)


def search_bookings():
    st.subheader("Global Search")

    sheets = load_all_sheets_cached()
    combined = (
        pd.concat(
            [
                df.assign(booking_type=name)
                for name, df in sheets.items()
                if not df.empty
            ],
            ignore_index=True,
        )
        if any([not df.empty for df in sheets.values()])
        else pd.DataFrame()
    )

    if combined.empty:
        st.info("No bookings available to search.")
        return

    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Search (ID, client name, PNR, vendor, etc.)")
    with col2:
        field = st.selectbox(
            "Field", ["All", "id", "client_name", "pnr", "vendor", "booking_type"]
        )

    booking_types = ["All"] + list(sheets.keys())
    booking_filter = st.multiselect("Booking type", booking_types, default=["All"])

    status_opts = ["All"] + sorted(
        [s for s in combined.get("status", pd.Series([])).dropna().unique().tolist()]
    )
    status_filter = st.selectbox("Status", status_opts)

    date_field = st.selectbox(
        "Date field", ["booking_date", "travel_start_date", "travel_end_date"]
    )
    date_series = pd.to_datetime(
        combined.get(date_field, pd.Series([])), errors="coerce"
    )
    min_date = (
        date_series.min().date() if not date_series.dropna().empty else dt.date.today()
    )
    max_date = (
        date_series.max().date() if not date_series.dropna().empty else dt.date.today()
    )
    date_range = st.date_input("Date range", value=(min_date, max_date))
    date_range = cast(Union[Tuple[dt.date, dt.date], dt.date], date_range)
    start_date, end_date = (
        date_range if isinstance(date_range, tuple) else (date_range, date_range)
    )

    results = combined.copy()

    if booking_filter and "All" not in booking_filter:
        results = results[results["booking_type"].isin(booking_filter)]

    if status_filter != "All":
        results = results[results["status"] == status_filter]

    df_dates = pd.to_datetime(results.get(date_field, pd.Series([])), errors="coerce")
    results = results[(df_dates.dt.date >= start_date) & (df_dates.dt.date <= end_date)]

    if query:
        q = str(query).strip()
        if field == "All":
            mask = pd.Series(False, index=results.index)
            for col in ["id", "client_name", "pnr", "vendor", "booking_type"]:
                if col in results.columns:
                    if col == "id":
                        mask = mask | (results["id"].astype(str) == q)
                    else:
                        mask = mask | results[col].astype(str).str.contains(
                            q, case=False, na=False
                        )
            results = results[mask]
        else:
            if field in results.columns:
                if field == "id":
                    results = results[results["id"].astype(str) == q]
                else:
                    results = results[
                        results[field].astype(str).str.contains(q, case=False, na=False)
                    ]

    st.write(f"### Results ({len(results)})")
    st.dataframe(results.reset_index(drop=True), use_container_width=True)

    if not results.empty:
        download_buttons(results, label_prefix="search_results")


__all__ = [
    "render_summary_metrics",
    "filtered_dataframe_ui",
    "download_buttons",
    "render_dashboard",
    "search_bookings",
]
