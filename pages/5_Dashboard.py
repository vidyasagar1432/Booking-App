"""
Dashboard Page - Overview and Analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.excel_db import ExcelDatabase
from config import BOOKING_TYPES

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
db = ExcelDatabase()

st.title("📊 Booking Dashboard")

# Get statistics for all booking types
all_stats = {}
total_bookings = 0
total_revenue = 0

for booking_type in BOOKING_TYPES.keys():
    stats = db.get_statistics(booking_type)
    all_stats[booking_type] = stats
    total_bookings += stats.get("total_bookings", 0)
    total_revenue += stats.get("total_revenue", 0)

# Top metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📦 Total Bookings", total_bookings)

with col2:
    st.metric("💰 Total Revenue", f"${total_revenue:,.2f}")

with col3:
    confirmed = sum(stats.get("confirmed", 0) for stats in all_stats.values())
    st.metric("✅ Confirmed", confirmed)

with col4:
    pending = sum(stats.get("pending", 0) for stats in all_stats.values())
    st.metric("⏳ Pending", pending)

st.divider()

# Booking types breakdown
col1, col2 = st.columns(2)

with col1:
    st.subheader("Bookings by Type")

    booking_data = []
    for booking_type, stats in all_stats.items():
        booking_data.append(
            {"Type": booking_type.capitalize(), "Count": stats.get("total_bookings", 0)}
        )

    if booking_data and sum(item["Count"] for item in booking_data) > 0:
        df_bookings = pd.DataFrame(booking_data)
        fig = px.pie(
            df_bookings,
            values="Count",
            names="Type",
            title="Distribution of Bookings",
            hole=0.3,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No bookings yet")

with col2:
    st.subheader("Revenue by Type")

    revenue_data = []
    for booking_type in BOOKING_TYPES.keys():
        df = db.get_bookings(booking_type)
        if len(df) > 0 and "Total Cost" in df.columns:
            revenue = df["Total Cost"].sum()
        else:
            revenue = 0
        revenue_data.append({"Type": booking_type.capitalize(), "Revenue": revenue})

    if revenue_data and sum(item["Revenue"] for item in revenue_data) > 0:
        df_revenue = pd.DataFrame(revenue_data)
        fig = px.bar(
            df_revenue,
            x="Type",
            y="Revenue",
            title="Revenue by Booking Type",
            labels={"Revenue": "Total Revenue ($)"},
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No revenue data yet")

st.divider()

# Status breakdown
st.subheader("Booking Status Overview")

col1, col2, col3, col4 = st.columns(4)

status_totals = {"Confirmed": 0, "Pending": 0, "Cancelled": 0, "Completed": 0}

for booking_type in BOOKING_TYPES.keys():
    df = db.get_bookings(booking_type)
    if len(df) > 0 and "Status" in df.columns:
        for status in status_totals.keys():
            status_totals[status] += len(df[df["Status"] == status])

with col1:
    st.metric("Confirmed", status_totals["Confirmed"], delta=None)

with col2:
    st.metric("Pending", status_totals["Pending"], delta=None)

with col3:
    st.metric("Cancelled", status_totals["Cancelled"], delta=None)

with col4:
    st.metric("Completed", status_totals["Completed"], delta=None)

st.divider()

# Detailed breakdown by type
st.subheader("Detailed Statistics by Booking Type")

tabs = st.tabs(
    [
        f"{icon} {name}"
        for booking_type, (icon, name) in [
            (k, v.split())
            for k, v in {
                "flight": "✈️ Flight",
                "hotel": "🏨 Hotel",
                "train": "🚆 Train",
                "bus": "🚌 Bus",
            }.items()
        ]
    ]
)

for idx, booking_type in enumerate(BOOKING_TYPES.keys()):
    with tabs[idx]:
        stats = all_stats[booking_type]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                f"{booking_type.capitalize()} Total", stats.get("total_bookings", 0)
            )
        with col2:
            st.metric("Confirmed", stats.get("confirmed", 0))
        with col3:
            st.metric("Pending", stats.get("pending", 0))
        with col4:
            st.metric("Cancelled", stats.get("cancelled", 0))

        st.divider()

        # Show recent bookings
        df = db.get_bookings(booking_type)
        if len(df) > 0:
            st.write(f"**Recent {booking_type.capitalize()} Bookings**")

            # Show last 5 bookings
            display_df = df.tail(5).copy()

            # Format for display
            st.dataframe(display_df, use_container_width=True, height=250)
        else:
            st.info(f"No {booking_type} bookings yet")

st.divider()

# Export all data
st.subheader("Export Data")

col1, col2, col3, col4 = st.columns(4)

for idx, (booking_type, icon_name) in enumerate(BOOKING_TYPES.items()):
    with [col1, col2, col3, col4][idx]:
        df = db.get_bookings(booking_type)
        if len(df) > 0:
            csv = df.to_csv(index=False)
            st.download_button(
                label=f"📥 {icon_name}",
                data=csv,
                file_name=f"{booking_type}_bookings_export.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.write(f"No {booking_type} data")
