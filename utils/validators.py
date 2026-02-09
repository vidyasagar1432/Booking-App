"""
Data validation utilities
"""

import re
from datetime import datetime
from typing import Tuple


class Validators:
    """Data validation methods"""

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email format"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if re.match(pattern, email):
            return True, ""
        return False, "Invalid email format"

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """Validate phone number"""
        # Remove common formatting characters
        cleaned = re.sub(r"[\s\-\+\(\)]", "", phone)
        if len(cleaned) >= 10 and cleaned.isdigit():
            return True, ""
        return False, "Phone number should contain at least 10 digits"

    @staticmethod
    def validate_date(date_str: str, format: str = "%Y-%m-%d") -> Tuple[bool, str]:
        """Validate date format"""
        try:
            datetime.strptime(date_str, format)
            return True, ""
        except ValueError:
            return False, f"Invalid date format. Expected {format}"

    @staticmethod
    def validate_time(time_str: str, format: str = "%H:%M") -> Tuple[bool, str]:
        """Validate time format"""
        try:
            datetime.strptime(time_str, format)
            return True, ""
        except ValueError:
            return False, f"Invalid time format. Expected {format}"

    @staticmethod
    def validate_cost(cost: str) -> Tuple[bool, str]:
        """Validate cost is a positive number"""
        try:
            cost_float = float(cost)
            if cost_float >= 0:
                return True, ""
            return False, "Cost must be positive"
        except ValueError:
            return False, "Cost must be a valid number"

    @staticmethod
    def validate_required_field(
        value: str, field_name: str = "Field"
    ) -> Tuple[bool, str]:
        """Validate that field is not empty"""
        if isinstance(value, str) and value.strip():
            return True, ""
        return False, f"{field_name} is required"

    @staticmethod
    def validate_flight_data(data: dict) -> Tuple[bool, str]:
        """Validate flight booking data"""
        required_fields = [
            "Passenger Name",
            "Email",
            "Phone",
            "Airline",
            "Flight Number",
            "Departure Date",
            "From Airport",
            "To Airport",
        ]

        for field in required_fields:
            is_valid, msg = Validators.validate_required_field(
                data.get(field, ""), field
            )
            if not is_valid:
                return False, msg

        # Validate email
        is_valid, msg = Validators.validate_email(data.get("Email", ""))
        if not is_valid:
            return False, msg

        # Validate phone
        is_valid, msg = Validators.validate_phone(data.get("Phone", ""))
        if not is_valid:
            return False, msg

        # Validate cost if provided
        if data.get("Total Cost"):
            is_valid, msg = Validators.validate_cost(str(data["Total Cost"]))
            if not is_valid:
                return False, msg

        return True, ""

    @staticmethod
    def validate_hotel_data(data: dict) -> Tuple[bool, str]:
        """Validate hotel booking data"""
        required_fields = [
            "Guest Name",
            "Email",
            "Phone",
            "Hotel Name",
            "City",
            "Check-in Date",
            "Check-out Date",
        ]

        for field in required_fields:
            is_valid, msg = Validators.validate_required_field(
                data.get(field, ""), field
            )
            if not is_valid:
                return False, msg

        # Validate email
        is_valid, msg = Validators.validate_email(data.get("Email", ""))
        if not is_valid:
            return False, msg

        # Validate phone
        is_valid, msg = Validators.validate_phone(data.get("Phone", ""))
        if not is_valid:
            return False, msg

        # Validate cost if provided
        if data.get("Total Cost"):
            is_valid, msg = Validators.validate_cost(str(data["Total Cost"]))
            if not is_valid:
                return False, msg

        return True, ""

    @staticmethod
    def validate_train_data(data: dict) -> Tuple[bool, str]:
        """Validate train booking data"""
        required_fields = [
            "Passenger Name",
            "Email",
            "Phone",
            "Train Name",
            "Departure Date",
            "From Station",
            "To Station",
        ]

        for field in required_fields:
            is_valid, msg = Validators.validate_required_field(
                data.get(field, ""), field
            )
            if not is_valid:
                return False, msg

        # Validate email
        is_valid, msg = Validators.validate_email(data.get("Email", ""))
        if not is_valid:
            return False, msg

        # Validate phone
        is_valid, msg = Validators.validate_phone(data.get("Phone", ""))
        if not is_valid:
            return False, msg

        # Validate cost if provided
        if data.get("Total Cost"):
            is_valid, msg = Validators.validate_cost(str(data["Total Cost"]))
            if not is_valid:
                return False, msg

        return True, ""

    @staticmethod
    def validate_bus_data(data: dict) -> Tuple[bool, str]:
        """Validate bus booking data"""
        required_fields = [
            "Passenger Name",
            "Email",
            "Phone",
            "Bus Company",
            "Departure Date",
            "From City",
            "To City",
        ]

        for field in required_fields:
            is_valid, msg = Validators.validate_required_field(
                data.get(field, ""), field
            )
            if not is_valid:
                return False, msg

        # Validate email
        is_valid, msg = Validators.validate_email(data.get("Email", ""))
        if not is_valid:
            return False, msg

        # Validate phone
        is_valid, msg = Validators.validate_phone(data.get("Phone", ""))
        if not is_valid:
            return False, msg

        # Validate cost if provided
        if data.get("Total Cost"):
            is_valid, msg = Validators.validate_cost(str(data["Total Cost"]))
            if not is_valid:
                return False, msg

        return True, ""
