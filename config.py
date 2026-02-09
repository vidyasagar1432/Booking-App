"""
Configuration file for Booking App
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
DB_FILE = DATA_DIR / "bookings.xlsx"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# Booking types
BOOKING_TYPES = {
    "flight": "✈️ Flight",
    "hotel": "🏨 Hotel",
    "train": "🚆 Train",
    "bus": "🚌 Bus",
}

# Flight fields
FLIGHT_FIELDS = [
    "Booking ID",
    "Passenger Name",
    "Email",
    "Phone",
    "Airline",
    "Company Name",
    "Flight Number",
    "Departure Date",
    "Departure Time",
    "Arrival Date",
    "Arrival Time",
    "From Airport",
    "To Airport",
    "Seat Number",
    "Class",
    "Total Cost",
    "Booking Date",
    "Status",
    "Notes",
]

# Hotel fields
HOTEL_FIELDS = [
    "Booking ID",
    "Guest Name",
    "Email",
    "Phone",
    "Hotel Name",
    "Company Name",
    "City",
    "Check-in Date",
    "Check-out Date",
    "Number of Nights",
    "Room Type",
    "Number of Rooms",
    "Total Guests",
    "Total Cost",
    "Booking Date",
    "Status",
    "Confirmation Number",
    "Notes",
]

# Train fields
TRAIN_FIELDS = [
    "Booking ID",
    "Passenger Name",
    "Email",
    "Phone",
    "Train Name",
    "Company Name",
    "Train Number",
    "Departure Date",
    "Departure Time",
    "Arrival Date",
    "Arrival Time",
    "From Station",
    "To Station",
    "Coach",
    "Seat Number",
    "Class",
    "Total Cost",
    "Booking Date",
    "Status",
    "Notes",
]

# Bus fields
BUS_FIELDS = [
    "Booking ID",
    "Passenger Name",
    "Email",
    "Phone",
    "Bus Company",
    "Company Name",
    "Bus Number",
    "Departure Date",
    "Departure Time",
    "Arrival Date",
    "Arrival Time",
    "From City",
    "To City",
    "Seat Number",
    "Total Cost",
    "Booking Date",
    "Status",
    "Notes",
]

# Status options
STATUS_OPTIONS = ["Confirmed", "Pending", "Cancelled", "Completed"]

# Class options for flights and trains
CLASS_OPTIONS = ["Economy", "Premium Economy", "Business", "First Class"]

# Room types
ROOM_TYPES = ["Single", "Double", "Twin", "Suite", "Standard", "Deluxe"]

# Default values
DEFAULT_STATUS = "Confirmed"
