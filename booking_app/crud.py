import streamlit as st
import pandas as pd

from .storage import (
    load_sheet,
    save_sheet,
    generate_new_id,
    get_sheet_name_from_booking_type,
    initialize_excel_file,
)
from .forms import (
    common_fields,
    flight_fields,
    hotel_fields,
    train_fields,
    bus_fields,
)
from .views import render_summary_metrics, filtered_dataframe_ui, download_buttons


def create_booking(booking_type: str):
    sheet_name = get_sheet_name_from_booking_type(booking_type)
    df = load_sheet(sheet_name)

    st.subheader(f"Create new {booking_type} booking")

    with st.form(f"create_{booking_type}_form"):
        common_data = common_fields(booking_type)
        if booking_type == "Flight":
            specific_data = flight_fields()
        elif booking_type == "Hotel":
            specific_data = hotel_fields()
        elif booking_type == "Train":
            specific_data = train_fields()
        elif booking_type == "Bus":
            specific_data = bus_fields()
        else:
            specific_data = {}

        submitted = st.form_submit_button("Create booking")

        if submitted:
            errors = []
            if not common_data["client_name"]:
                errors.append("Client name is required.")
            if common_data["total_amount"] < 0:
                errors.append("Total amount cannot be negative.")

            if errors:
                st.error("\n".join(errors))
            else:
                new_id = generate_new_id(df)
                new_record = {"id": new_id}
                new_record.update(common_data)
                new_record.update(specific_data)

                df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
                save_sheet(sheet_name, df)
                st.success(
                    f"{booking_type} booking created successfully with ID: {new_id}"
                )


def view_bookings(booking_type: str):
    sheet_name = get_sheet_name_from_booking_type(booking_type)
    df = load_sheet(sheet_name)

    st.subheader(f"View {booking_type} bookings")

    if df.empty:
        st.info(f"No {booking_type} bookings found.")
        return

    render_summary_metrics(df)
    filtered = filtered_dataframe_ui(df, booking_type)
    st.write("### Results")
    st.dataframe(filtered, use_container_width=True)

    download_buttons(filtered, label_prefix=f"{booking_type}_bookings")


def edit_booking(booking_type: str):
    sheet_name = get_sheet_name_from_booking_type(booking_type)
    df = load_sheet(sheet_name)

    st.subheader(f"Edit {booking_type} booking")

    if df.empty:
        st.info(f"No {booking_type} bookings found to edit.")
        return

    pnr_filter = ""
    if booking_type in ["Flight", "Train", "Bus"] and "pnr" in df.columns:
        pnr_filter = st.text_input("Filter by PNR (optional)")

    df_filtered = df.copy()
    if pnr_filter and "pnr" in df.columns:
        df_filtered = df_filtered[df_filtered["pnr"].astype(str) == pnr_filter]

    if df_filtered.empty:
        st.info("No records found with the given filter.")
        return

    df_filtered["id_display"] = (
        df_filtered["id"].astype(str) + " | " + df_filtered["client_name"].astype(str)
    )
    id_options = df_filtered["id"].tolist()
    id_display_options = df_filtered["id_display"].tolist()

    selected_display = st.selectbox(
        "Select booking to edit (ID | Client name)", id_display_options
    )
    selected_index = id_display_options.index(selected_display)
    selected_id = id_options[selected_index]

    record = df[df["id"] == selected_id]
    if record.empty:
        st.error("Selected booking ID not found.")
        return

    record_series = record.iloc[0]

    with st.form(f"edit_{booking_type}_form"):
        st.markdown(f"**Editing ID:** {selected_id}")
        common_data = common_fields(booking_type, existing=record_series)

        if booking_type == "Flight":
            specific_data = flight_fields(existing=record_series)
        elif booking_type == "Hotel":
            specific_data = hotel_fields(existing=record_series)
        elif booking_type == "Train":
            specific_data = train_fields(existing=record_series)
        elif booking_type == "Bus":
            specific_data = bus_fields(existing=record_series)
        else:
            specific_data = {}

        submitted = st.form_submit_button("Save changes")

        if submitted:
            errors = []
            if not common_data["client_name"]:
                errors.append("Client name is required.")
            if common_data["total_amount"] < 0:
                errors.append("Total amount cannot be negative.")

            if errors:
                st.error("\n".join(errors))
            else:
                for key, val in common_data.items():
                    df.loc[df["id"] == selected_id, key] = val
                for key, val in specific_data.items():
                    if key in df.columns:
                        df.loc[df["id"] == selected_id, key] = val

                save_sheet(sheet_name, df)
                st.success(
                    f"{booking_type} booking with ID {selected_id} updated successfully."
                )


def delete_booking(booking_type: str):
    sheet_name = get_sheet_name_from_booking_type(booking_type)
    df = load_sheet(sheet_name)

    st.subheader(f"Delete {booking_type} booking")

    if df.empty:
        st.info(f"No {booking_type} bookings found to delete.")
        return

    df["id_display"] = df["id"].astype(str) + " | " + df["client_name"].astype(str)
    id_options = df["id"].tolist()
    id_display_options = df["id_display"].tolist()

    selected_display = st.selectbox(
        "Select booking to delete (ID | Client name)", id_display_options
    )
    selected_index = id_display_options.index(selected_display)
    selected_id = id_options[selected_index]

    record = df[df["id"] == selected_id]
    if record.empty:
        st.error("Selected booking ID not found.")
        return

    st.write("### Booking details")
    st.dataframe(
        record.drop(columns=["id_display"], errors="ignore"), use_container_width=True
    )

    st.warning("This action cannot be undone.")

    confirm = st.checkbox("Yes, I really want to delete this booking.")
    if st.button("Delete booking", disabled=not confirm):
        if not confirm:
            st.info("Please confirm deletion by ticking the checkbox.")
            return

        df = df[df["id"] != selected_id]
        if "id_display" in df.columns:
            df = df.drop(columns=["id_display"])
        save_sheet(sheet_name, df)
        st.success(
            f"{booking_type} booking with ID {selected_id} deleted successfully."
        )


__all__ = ["create_booking", "view_bookings", "edit_booking", "delete_booking"]
