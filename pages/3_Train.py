"""
Train Booking Management Page
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.excel_db import ExcelDatabase
from utils.validators import Validators
from config import TRAIN_FIELDS, CLASS_OPTIONS, STATUS_OPTIONS
import json


st.set_page_config(
    page_title="Train Bookings",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
db = ExcelDatabase()

st.title("🚆 Train Bookings")

# Tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["📋 View", "➕ Add", "✏️ Edit", "🗑️ Delete"])

with tab1:
    st.subheader("Train Bookings List")

    # Get all bookings
    df = db.get_bookings("train")

    if len(df) == 0:
        st.info("No train bookings found. Add one to get started!")
    else:
        # Statistics
        col1, col2, col3, col4, col5 = st.columns(5)
        stats = db.get_statistics("train")

        with col1:
            st.metric("Total Bookings", stats.get("total_bookings", 0))
        with col2:
            st.metric("Confirmed", stats.get("confirmed", 0))
        with col3:
            st.metric("Pending", stats.get("pending", 0))
        with col4:
            st.metric("Cancelled", stats.get("cancelled", 0))
        with col5:
            try:
                rev = float(stats.get("total_revenue", 0))
            except (ValueError, TypeError):
                rev = 0.0
            st.metric("Total Revenue", f"${rev:,.2f}")

        st.divider()

        # Search and filter
        col1, col2, col3 = st.columns(3)

        with col1:
            search_field = st.selectbox(
                "Search by", df.columns, key="train_search_field"
            )

        with col2:
            search_value = st.text_input("Search value", key="train_search_value")

        if search_value:
            df_filtered = db.search_bookings("train", search_field, search_value)
        else:
            df_filtered = df

        with col3:
            filter_status = st.multiselect(
                "Filter by Status",
                STATUS_OPTIONS,
                default=STATUS_OPTIONS,
                key="train_status_filter",
            )
            if filter_status:
                df_filtered = df_filtered[df_filtered["Status"].isin(filter_status)]

        st.divider()

        # Display table
        st.dataframe(
            df_filtered,
            use_container_width=True,
            height=400,
        )

        # Export button
        if len(df_filtered) > 0:
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"train_bookings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

with tab2:
    st.subheader("Add New Train Booking")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Passenger Info**")
        passenger_name = st.text_input("Passenger Name *", key="train_pname")
        email = st.text_input("Email", key="train_email")
        phone = st.text_input("Phone Number *", key="train_phone")
        company_name = st.text_input("Company Name", key="train_company")

    with col2:
        st.write("**Journey Details**")
        from_station = st.text_input("From Station *", key="train_from")
        to_station = st.text_input("To Station *", key="train_to")
        departure_date = st.date_input("Departure Date *", key="train_dep_date")
        departure_time = st.time_input("Departure Time", key="train_dep_time")
        arrival_date = st.date_input("Arrival Date", key="train_arr_date")
        arrival_time = st.time_input("Arrival Time", key="train_arr_time")

    with col3:
        st.write("**Booking Details**")
        train_name = st.text_input("Train Name *", key="train_name")
        train_number = st.text_input("Train Number", key="train_number")
        coach = st.text_input("Coach", key="train_coach", placeholder="e.g., A1")
        seat_number = st.text_input(
            "Seat Number", key="train_seat", placeholder="e.g., 45A"
        )
        train_class = st.selectbox("Class", CLASS_OPTIONS, key="train_class")
        total_cost = st.number_input(
            "Total Cost ($)", min_value=0.0, step=0.01, key="train_cost"
        )
        status = st.selectbox("Status", STATUS_OPTIONS, index=0, key="train_status")

    col1, col2 = st.columns(2)

    with col1:
        notes = st.text_area("Notes", height=100, key="train_notes")
    with col2:
        passengers_text = st.text_area(
            "Passengers (one per line: Name|Seat|Email|Phone)",
            height=100,
            key="train_passengers_text",
        )

    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("➕ Add Train Booking", use_container_width=True):
            # Validate data
            data = {
                "Passenger Name": passenger_name,
                "Email": email,
                "Phone": phone,
                "Train Name": train_name,
                "Company Name": company_name,
                "Departure Date": str(departure_date),
                "From Station": from_station,
                "To Station": to_station,
            }

            is_valid, error_msg = Validators.validate_train_data(data)

            if not is_valid:
                st.error(f"❌ {error_msg}")
            else:
                # Generate booking ID
                booking_id = db.generate_booking_id("train")

                # Prepare complete data
                passengers_list = [
                    l.strip() for l in passengers_text.splitlines() if l.strip()
                ]

                complete_data = {
                    "Booking ID": booking_id,
                    "Passenger Name": passenger_name,
                    "Email": email,
                    "Phone": phone,
                    "Train Name": train_name,
                    "Company Name": company_name,
                    "Train Number": train_number,
                    "Departure Date": str(departure_date),
                    "Departure Time": str(departure_time),
                    "Arrival Date": str(arrival_date),
                    "Arrival Time": str(arrival_time),
                    "From Station": from_station,
                    "To Station": to_station,
                    "Coach": coach,
                    "Seat Number": seat_number,
                    "Class": train_class,
                    "Total Cost": total_cost,
                    "Passengers": json.dumps(passengers_list),
                    "Passenger Count": len(passengers_list),
                    "Booking Date": datetime.now().strftime("%Y-%m-%d"),
                    "Status": status,
                    "Notes": notes,
                }

                success, message = db.add_booking("train", complete_data)
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)

with tab3:
    st.subheader("Edit Train Booking")

    df = db.get_bookings("train")

    if len(df) == 0:
        st.info("No train bookings to edit.")
    else:
        # Select booking to edit
        booking_id = st.selectbox(
            "Select Booking ID to Edit", df["Booking ID"].unique(), key="train_edit_id"
        )

        # Get booking data
        booking = df[df["Booking ID"] == booking_id].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            passenger_name = st.text_input(
                "Passenger Name",
                value=booking.get("Passenger Name", ""),
                key="train_edit_pname",
            )
            email = st.text_input(
                "Email", value=booking.get("Email", ""), key="train_edit_email"
            )
            phone = st.text_input(
                "Phone Number", value=booking.get("Phone", ""), key="train_edit_phone"
            )
            train_name = st.text_input(
                "Train Name", value=booking.get("Train Name", ""), key="train_edit_name"
            )
            company_name = st.text_input(
                "Company Name",
                value=booking.get("Company Name", ""),
                key="train_edit_company",
            )
            train_number = st.text_input(
                "Train Number",
                value=booking.get("Train Number", ""),
                key="train_edit_number",
            )
            from_station = st.text_input(
                "From Station",
                value=booking.get("From Station", ""),
                key="train_edit_from",
            )
            to_station = st.text_input(
                "To Station", value=booking.get("To Station", ""), key="train_edit_to"
            )

        with col2:
            departure_date = st.date_input(
                "Departure Date",
                value=pd.to_datetime(
                    booking.get("Departure Date", datetime.now())
                ).date(),
                key="train_edit_dep_date",
            )
            departure_time = st.text_input(
                "Departure Time",
                value=booking.get("Departure Time", ""),
                key="train_edit_dep_time",
                placeholder="HH:MM",
            )
            arrival_date = st.date_input(
                "Arrival Date",
                value=pd.to_datetime(
                    booking.get("Arrival Date", datetime.now())
                ).date(),
                key="train_edit_arr_date",
            )
            arrival_time = st.text_input(
                "Arrival Time",
                value=booking.get("Arrival Time", ""),
                key="train_edit_arr_time",
                placeholder="HH:MM",
            )
            coach = st.text_input(
                "Coach", value=booking.get("Coach", ""), key="train_edit_coach"
            )
            seat_number = st.text_input(
                "Seat Number",
                value=booking.get("Seat Number", ""),
                key="train_edit_seat",
            )
            train_class = st.selectbox(
                "Class",
                CLASS_OPTIONS,
                index=(
                    CLASS_OPTIONS.index(booking.get("Class", "Economy"))
                    if booking.get("Class") in CLASS_OPTIONS
                    else 0
                ),
                key="train_edit_class",
            )
            try:
                total_cost_val = float(booking.get("Total Cost", 0))
            except (ValueError, TypeError):
                total_cost_val = 0.0

            total_cost = st.number_input(
                "Total Cost",
                value=total_cost_val,
                min_value=0.0,
                step=0.01,
                key="train_edit_cost",
            )

        status = st.selectbox(
            "Status",
            STATUS_OPTIONS,
            index=(
                STATUS_OPTIONS.index(booking.get("Status", "Confirmed"))
                if booking.get("Status") in STATUS_OPTIONS
                else 0
            ),
            key="train_edit_status",
        )
        notes = st.text_area(
            "Notes", value=booking.get("Notes", ""), height=100, key="train_edit_notes"
        )
        # Prefill passengers text area from stored JSON (if available)
        existing_passengers = booking.get("Passengers", "")
        try:
            if existing_passengers:
                if isinstance(existing_passengers, str):
                    parsed = json.loads(existing_passengers)
                else:
                    parsed = list(existing_passengers)
                passengers_edit_text = "\n".join(parsed)
            else:
                passengers_edit_text = ""
        except Exception:
            passengers_edit_text = str(existing_passengers)

        passengers_edit_text = st.text_area(
            "Passengers (one per line: Name|Company|Phone|Email)",
            value=passengers_edit_text,
            height=120,
            key="train_passengers_edit_text",
        )

        if st.button("✏️ Update Booking", use_container_width=True):
            data = {
                "Passenger Name": passenger_name,
                "Email": email,
                "Phone": phone,
                "Train Name": train_name,
                "Company Name": company_name,
                "Train Number": train_number,
                "Departure Date": str(departure_date),
                "Departure Time": departure_time,
                "Arrival Date": str(arrival_date),
                "Arrival Time": arrival_time,
                "From Station": from_station,
                "To Station": to_station,
                "Coach": coach,
                "Seat Number": seat_number,
                "Class": train_class,
                "Total Cost": total_cost,
                "Status": status,
                "Notes": notes,
            }
            passengers_edit_list = [
                l.strip() for l in passengers_edit_text.splitlines() if l.strip()
            ]
            data["Passengers"] = json.dumps(passengers_edit_list)
            data["Passenger Count"] = len(passengers_edit_list)

            success, message = db.update_booking("train", booking_id, data)
            if success:
                st.success(message)
            else:
                st.error(message)

with tab4:
    st.subheader("Delete Train Booking")

    df = db.get_bookings("train")

    if len(df) == 0:
        st.info("No train bookings to delete.")
    else:
        booking_id = st.selectbox(
            "Select Booking ID to Delete",
            df["Booking ID"].unique(),
            key="train_delete_id",
        )

        booking = df[df["Booking ID"] == booking_id].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Passenger Name:** {booking.get('Passenger Name', 'N/A')}")
            st.write(f"**Train Name:** {booking.get('Train Name', 'N/A')}")
            st.write(f"**Train Number:** {booking.get('Train Number', 'N/A')}")

        with col2:
            st.write(
                f"**Route:** {booking.get('From Station', 'N/A')} → {booking.get('To Station', 'N/A')}"
            )
            st.write(f"**Departure Date:** {booking.get('Departure Date', 'N/A')}")
            st.write(f"**Status:** {booking.get('Status', 'N/A')}")
            try:
                total_cost_val = float(booking.get("Total Cost", 0))
            except (ValueError, TypeError):
                total_cost_val = 0.0
            st.write(f"**Total Cost:** ${total_cost_val:,.2f}")

        st.warning("⚠️ This action cannot be undone!")

        if st.button("🗑️ Delete Booking", use_container_width=True, type="secondary"):
            success, message = db.delete_booking("train", booking_id)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
