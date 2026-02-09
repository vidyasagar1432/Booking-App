"""
Main Streamlit Application
Booking Record Keeper - Production Ready
"""

import streamlit as st
from config import BOOKING_TYPES

# Page configuration
st.set_page_config(
    page_title="Booking Record Keeper",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://github.com",
        "Report a bug": "https://github.com",
        "About": "## Booking Record Keeper\nA professional booking management system for flights, hotels, trains, and buses with Excel database.",
    },
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.markdown("## 🎫 Booking Record Keeper")
    st.divider()

    st.markdown("### Navigation")
    st.markdown(
        """
    - **📊 Dashboard** - Overview and analytics
    - **✈️ Flights** - Flight bookings
    - **🏨 Hotels** - Hotel bookings
    - **🚆 Trains** - Train bookings
    - **🚌 Buses** - Bus bookings
    """
    )

    st.divider()

    st.markdown("### About This App")
    st.info(
        """
    This is a production-ready booking management system built with Streamlit.
    
    **Features:**
    - ✅ Add, edit, delete bookings
    - 🔍 Search and filter functionality
    - 📊 Real-time analytics and statistics
    - 📥 CSV export capabilities
    - 💾 Excel database persistence
    - 📱 Responsive design
    
    **Database:** Excel (.xlsx)
    """
    )

    st.divider()

# Main content
st.markdown(
    """
<div class="main-header">
    <h1>🎫 Booking Record Keeper</h1>
    <p><em>Professional booking management for flights, hotels, trains, and buses</em></p>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# Introduction
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
    ### Welcome! 👋
    
    Manage all your travel and accommodation bookings in one place.
    
    **Quick Start:**
    1. Navigate using the left sidebar
    2. Select a booking type (Flight, Hotel, Train, or Bus)
    3. Use the tabs to view, add, edit, or delete bookings
    4. Check the Dashboard for analytics and insights
    """
    )

with col2:
    st.markdown(
        """
    ### Key Features 🌟
    
    - **Unified Management** - All booking types in one app
    - **Real-time Updates** - Changes saved instantly
    - **Data Validation** - Ensures accurate information
    - **Search & Filter** - Quickly find bookings
    - **Analytics** - View statistics and trends
    - **Export Data** - Download bookings as CSV
    """
    )

st.divider()

# Booking types overview
st.markdown("### 📝 Available Booking Types")

booking_cols = st.columns(4)

booking_info = {
    "flight": {
        "emoji": "✈️",
        "title": "Flights",
        "description": "Manage flight bookings with airline, route, and passenger details",
        "fields": ["Airline", "Flight Number", "Route", "Seat", "Class"],
    },
    "hotel": {
        "emoji": "🏨",
        "title": "Hotels",
        "description": "Track hotel reservations with guest info and room details",
        "fields": ["Hotel Name", "Check-in/out", "Room Type", "Guests", "Nights"],
    },
    "train": {
        "emoji": "🚆",
        "title": "Trains",
        "description": "Record train journeys with station and coach information",
        "fields": ["Train Name", "Route", "Coach", "Seat", "Class"],
    },
    "bus": {
        "emoji": "🚌",
        "title": "Buses",
        "description": "Organize bus bookings with company and route details",
        "fields": ["Bus Company", "Route", "Seat", "Departure", "Arrival"],
    },
}

for idx, (booking_type, info) in enumerate(booking_info.items()):
    with booking_cols[idx]:
        st.markdown(
            f"""
        ### {info['emoji']} {info['title']}
        
        {info['description']}
        """
        )

st.divider()

# Getting started section
st.markdown("### 🚀 Getting Started")

tab1, tab2, tab3 = st.tabs(["Add a Booking", "View Bookings", "FAQs"])

with tab1:
    st.markdown(
        """
    1. **Choose a booking type** from the sidebar
    2. **Click the "➕ Add" tab** in the selected page
    3. **Fill in the required fields** (marked with *)
    4. **Click "Add" button** to save
    5. Your booking will be saved to the Excel database
    
    **Tips:**
    - All required fields must be filled
    - Email and phone will be validated
    - Booking ID is generated automatically
    """
    )

with tab2:
    st.markdown(
        """
    1. **Select a booking type** from the sidebar
    2. **Click the "📋 View" tab**
    3. **Use search** to find specific bookings
    4. **Filter by status** using the filter dropdown
    5. **Export as CSV** using the download button
    
    **Columns available for search:**
    - Name, Email, Phone
    - Booking ID, Status
    - Airline/Hotel/Train/Bus name
    - Dates and costs
    """
    )

with tab3:
    with st.expander("❓ How do I edit a booking?"):
        st.write(
            """
        1. Go to the booking type you want to edit
        2. Click the "✏️ Edit" tab
        3. Select the booking ID from the dropdown
        4. Modify the fields as needed
        5. Click "Update Booking" to save
        """
        )

    with st.expander("❓ How do I delete a booking?"):
        st.write(
            """
        1. Go to the booking type you want to delete
        2. Click the "🗑️ Delete" tab
        3. Select the booking ID to delete
        4. Review the booking details
        5. Click "Delete Booking" (cannot be undone)
        """
        )

    with st.expander("❓ Where is my data stored?"):
        st.write(
            """
        All bookings are stored in an Excel file (bookings.xlsx) located in the 'data' folder.
        This is a persistent database that survives app restarts.
        """
        )

    with st.expander("❓ Can I export my data?"):
        st.write(
            """
        Yes! You can download bookings as CSV from the View tab of any booking type.
        You can also export all data from the Dashboard page.
        """
        )

    with st.expander("❓ What are the requirements?"):
        st.write(
            """
        **Required fields by booking type:**
        - **All:** Name, Email, Phone
        - **Flights:** Airline, Flight Number, Airports, Departure Date
        - **Hotels:** Hotel Name, City, Check-in/out Date
        - **Trains:** Train Name, Stations, Departure Date
        - **Buses:** Bus Company, Cities, Departure Date
        """
        )

st.divider()

# Footer
st.markdown(
    """
---
<div style='text-align: center'>
    <p><strong>Booking Record Keeper</strong></p>
    <p style='font-size: 0.8em; color: gray;'>
    Professional booking management system | Built with Streamlit | Excel Database
    </p>
</div>
""",
    unsafe_allow_html=True,
)
