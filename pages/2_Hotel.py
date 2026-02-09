"""
Hotel Booking Management Page
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from utils.excel_db import ExcelDatabase
from utils.validators import Validators
from config import HOTEL_FIELDS, ROOM_TYPES, STATUS_OPTIONS
import json


st.set_page_config(
    page_title="Hotel Bookings",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
db = ExcelDatabase()

st.title("🏨 Hotel Bookings")

# Tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["📋 View", "➕ Add", "✏️ Edit", "🗑️ Delete"])

with tab1:
    st.subheader("Hotel Bookings List")

    # Get all bookings
    df = db.get_bookings("hotel")

    if len(df) == 0:
        st.info("No hotel bookings found. Add one to get started!")
    else:
        # Statistics
        col1, col2, col3, col4, col5 = st.columns(5)
        stats = db.get_statistics("hotel")

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
                "Search by", df.columns, key="hotel_search_field"
            )

        with col2:
            search_value = st.text_input("Search value", key="hotel_search_value")

        if search_value:
            df_filtered = db.search_bookings("hotel", search_field, search_value)
        else:
            df_filtered = df

        with col3:
            filter_status = st.multiselect(
                "Filter by Status",
                STATUS_OPTIONS,
                default=STATUS_OPTIONS,
                key="hotel_status_filter",
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
                file_name=f"hotel_bookings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

with tab2:
    st.subheader("Add New Hotel Booking")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Guest Info**")
        guest_name = st.text_input("Guest Name *", key="hotel_gname")
        email = st.text_input("Email", key="hotel_email")
        phone = st.text_input("Phone Number *", key="hotel_phone")
        company_name = st.text_input("Company Name", key="hotel_company")

    with col2:
        st.write("**Stay Details**")
        hotel_name = st.text_input("Hotel Name *", key="hotel_name")
        city = st.text_input("City *", key="hotel_city")
        check_in_date = st.date_input("Check-in Date *", key="hotel_check_in")
        check_out_date = st.date_input(
            "Check-out Date *",
            value=check_in_date + timedelta(days=1),
            key="hotel_check_out",
        )
        nights = (check_out_date - check_in_date).days
        st.metric("Number of Nights", nights)

    with col3:
        st.write("**Booking Details**")
        booking_id_input = st.text_input("Booking ID *", key="hotel_booking_id")
        room_type = st.selectbox("Room Type", ROOM_TYPES, key="hotel_room_type")
        number_of_rooms = st.number_input(
            "Number of Rooms", min_value=1, value=1, step=1, key="hotel_rooms"
        )
        total_guests = st.number_input(
            "Total Guests", min_value=1, value=1, step=1, key="hotel_guests"
        )
        confirmation_number = st.text_input(
            "Confirmation Number", key="hotel_conf_number"
        )
        booking_date = st.date_input("Booking Date *", key="hotel_booking_date")
        total_cost = st.number_input(
            "Total Cost ($)", min_value=0.0, step=0.01, key="hotel_cost"
        )
        status = st.selectbox("Status", STATUS_OPTIONS, index=0, key="hotel_status")

    col1, col2 = st.columns(2)

    with col1:
        notes = st.text_area("Notes", height=100, key="hotel_notes")
    with col2:
        passengers_text = st.text_area(
            "Passengers (one per line: Name|Company|Phone|Email)",
            height=100,
            key="hotel_passengers_text",
        )

    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("➕ Add Hotel Booking", use_container_width=True):
            # Validate data
            data = {
                "Guest Name": guest_name,
                "Email": email,
                "Phone": phone,
                "Hotel Name": hotel_name,
                "Company Name": company_name,
                "City": city,
                "Check-in Date": str(check_in_date),
                "Check-out Date": str(check_out_date),
            }

            is_valid, error_msg = Validators.validate_hotel_data(data)

            if not is_valid:
                st.error(f"❌ {error_msg}")
            elif check_out_date <= check_in_date:
                st.error("❌ Check-out date must be after check-in date")
            else:
                # Handle booking ID
                if booking_id_input.strip():
                    df_existing = db.get_bookings("hotel")
                    if booking_id_input in df_existing["Booking ID"].values:
                        st.error(
                            f"❌ Booking ID '{booking_id_input}' already exists. Please choose a different one."
                        )
                        st.stop()
                    else:
                        booking_id = booking_id_input.strip()
                else:
                    st.error("❌ Booking ID is required.")
                    st.stop()

                # Prepare passengers list and complete data
                passengers_list = [
                    l.strip() for l in passengers_text.splitlines() if l.strip()
                ]

                # Prepare complete data
                complete_data = {
                    "Booking ID": booking_id,
                    "Guest Name": guest_name,
                    "Email": email,
                    "Phone": phone,
                    "Hotel Name": hotel_name,
                    "Company Name": company_name,
                    "City": city,
                    "Check-in Date": str(check_in_date),
                    "Check-out Date": str(check_out_date),
                    "Number of Nights": nights,
                    "Room Type": room_type,
                    "Number of Rooms": number_of_rooms,
                    "Total Guests": total_guests,
                    "Passengers": json.dumps(passengers_list),
                    "Passenger Count": len(passengers_list),
                    "Total Cost": total_cost,
                    "Booking Date": datetime.now().strftime("%Y-%m-%d"),
                    "Status": status,
                    "Confirmation Number": confirmation_number,
                    "Notes": notes,
                }

                success, message = db.add_booking("hotel", complete_data)
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)

with tab3:
    st.subheader("Edit Hotel Booking")

    df = db.get_bookings("hotel")

    if len(df) == 0:
        st.info("No hotel bookings to edit.")
    else:
        # Select booking to edit
        booking_id = st.selectbox(
            "Select Booking ID to Edit", df["Booking ID"].unique(), key="hotel_edit_id"
        )

        # Get booking data
        booking = df[df["Booking ID"] == booking_id].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            guest_name = st.text_input(
                "Guest Name",
                value=booking.get("Guest Name", ""),
                key="hotel_edit_gname",
            )
            email = st.text_input(
                "Email", value=booking.get("Email", ""), key="hotel_edit_email"
            )
            phone = st.text_input(
                "Phone Number", value=booking.get("Phone", ""), key="hotel_edit_phone"
            )
            hotel_name = st.text_input(
                "Hotel Name", value=booking.get("Hotel Name", ""), key="hotel_edit_name"
            )
            company_name = st.text_input(
                "Company Name",
                value=booking.get("Company Name", ""),
                key="hotel_edit_company",
            )
            city = st.text_input(
                "City", value=booking.get("City", ""), key="hotel_edit_city"
            )
            room_type = st.selectbox(
                "Room Type",
                ROOM_TYPES,
                index=(
                    ROOM_TYPES.index(booking.get("Room Type", "Single"))
                    if booking.get("Room Type") in ROOM_TYPES
                    else 0
                ),
                key="hotel_edit_room_type",
            )
            try:
                num_rooms_val = int(booking.get("Number of Rooms", 1))
            except (ValueError, TypeError):
                num_rooms_val = 1

            number_of_rooms = st.number_input(
                "Number of Rooms",
                value=num_rooms_val,
                min_value=1,
                step=1,
                key="hotel_edit_rooms",
            )

        with col2:
            check_in_date = st.date_input(
                "Check-in Date",
                value=pd.to_datetime(
                    booking.get("Check-in Date", datetime.now())
                ).date(),
                key="hotel_edit_check_in",
            )
            check_out_date = st.date_input(
                "Check-out Date",
                value=pd.to_datetime(
                    booking.get("Check-out Date", datetime.now())
                ).date(),
                key="hotel_edit_check_out",
            )
            try:
                total_guests_val = int(booking.get("Total Guests", 1))
            except (ValueError, TypeError):
                total_guests_val = 1

            total_guests = st.number_input(
                "Total Guests",
                value=total_guests_val,
                min_value=1,
                step=1,
                key="hotel_edit_guests",
            )
            confirmation_number = st.text_input(
                "Confirmation Number",
                value=booking.get("Confirmation Number", ""),
                key="hotel_edit_conf_number",
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
                key="hotel_edit_cost",
            )
            booking_date = st.date_input(
                "Booking Date",
                value=pd.to_datetime(
                    booking.get("Booking Date", datetime.now())
                ).date(),
                key="hotel_edit_booking_date",
            )

        status = st.selectbox(
            "Status",
            STATUS_OPTIONS,
            index=(
                STATUS_OPTIONS.index(booking.get("Status", "Confirmed"))
                if booking.get("Status") in STATUS_OPTIONS
                else 0
            ),
            key="hotel_edit_status",
        )
        notes = st.text_area(
            "Notes", value=booking.get("Notes", ""), height=100, key="hotel_edit_notes"
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
            key="hotel_passengers_edit_text",
        )

        if st.button("✏️ Update Booking", use_container_width=True):
            nights = (check_out_date - check_in_date).days
            passengers_edit_list = [
                l.strip() for l in passengers_edit_text.splitlines() if l.strip()
            ]

            data = {
                "Guest Name": guest_name,
                "Email": email,
                "Phone": phone,
                "Hotel Name": hotel_name,
                "Company Name": company_name,
                "City": city,
                "Check-in Date": str(check_in_date),
                "Check-out Date": str(check_out_date),
                "Number of Nights": nights,
                "Room Type": room_type,
                "Number of Rooms": number_of_rooms,
                "Total Guests": total_guests,
                "Passengers": json.dumps(passengers_edit_list),
                "Passenger Count": len(passengers_edit_list),
                "Total Cost": total_cost,
                "Status": status,
                "Confirmation Number": confirmation_number,
                "Notes": notes,
            }

            success, message = db.update_booking("hotel", booking_id, data)
            if success:
                st.success(message)
            else:
                st.error(message)

with tab4:
    st.subheader("Delete Hotel Booking")

    df = db.get_bookings("hotel")

    if len(df) == 0:
        st.info("No hotel bookings to delete.")
    else:
        booking_id = st.selectbox(
            "Select Booking ID to Delete",
            df["Booking ID"].unique(),
            key="hotel_delete_id",
        )

        booking = df[df["Booking ID"] == booking_id].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Guest Name:** {booking.get('Guest Name', 'N/A')}")
            st.write(f"**Hotel Name:** {booking.get('Hotel Name', 'N/A')}")
            st.write(f"**City:** {booking.get('City', 'N/A')}")

        with col2:
            st.write(f"**Check-in:** {booking.get('Check-in Date', 'N/A')}")
            st.write(f"**Check-out:** {booking.get('Check-out Date', 'N/A')}")
            st.write(f"**Status:** {booking.get('Status', 'N/A')}")
            try:
                total_cost_val = float(booking.get("Total Cost", 0))
            except (ValueError, TypeError):
                total_cost_val = 0.0
            st.write(f"**Total Cost:** ${total_cost_val:,.2f}")

        st.warning("⚠️ This action cannot be undone!")

        if st.button("🗑️ Delete Booking", use_container_width=True, type="secondary"):
            success, message = db.delete_booking("hotel", booking_id)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
