from typing import Optional, List, Any, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from .user import UserRead

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

# --- Company Schmeas ---
class CompanyBase(BaseModel):
    name: str
    industry: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    is_active: Optional[bool] = None

class CompanyRead(CompanyBase):
    id: int
    created_at: datetime
    is_active: bool
    employee_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)

# --- Employee Schemas ---
class EmployeeBase(BaseModel):
    name: str
    designation: Optional[str] = None
    phone: str
    email: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    company_id: Optional[int] = None
    company_name: Optional[str] = None # Auto-create link support

class EmployeeUpdate(BaseModel):
    company_id: Optional[int] = None
    name: Optional[str] = None
    designation: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    is_active: Optional[bool] = None

class EmployeeRead(EmployeeBase):
    id: int
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    company: Optional[CompanyRead] = None
    created_at: datetime
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

class EmployeeReadExtended(EmployeeRead):
    booking_count: int = 0
    total_spent: float = 0.0

# --- Booking Sub-Schemas ---
class BookingFlightBase(BaseModel):
    flight_number: Optional[str] = None
    airline: Optional[str] = None
    pnr_status: Optional[str] = None
    seat_class: Optional[str] = None
    from_city: Optional[str] = None
    to_city: Optional[str] = None

class BookingTrainBase(BaseModel):
    train_number: Optional[str] = None
    coach_number: Optional[str] = None
    platform: Optional[str] = None
    from_city: Optional[str] = None
    to_city: Optional[str] = None
    pnr_status: Optional[str] = None
    seat_class: Optional[str] = None

class BookingBusBase(BaseModel):
    bus_operator: Optional[str] = None
    bus_pnr: Optional[str] = None
    pickup_point: Optional[str] = None
    drop_point: Optional[str] = None
    from_city: Optional[str] = None
    to_city: Optional[str] = None
    pnr_status: Optional[str] = None
    seat_class: Optional[str] = None

class BookingHotelBase(BaseModel):
    hotel_name: Optional[str] = None
    room_type: Optional[str] = None
    hotel_address: Optional[str] = None
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    city: Optional[str] = None

# --- Main Booking Schemas ---
class BookingBase(BaseModel):
    booking_type: str
    booking_date: Optional[datetime] = None
    start_datetime: datetime
    end_datetime: datetime
    cost: float = 0.0
    status: str = "Confirmed"
    notes: Optional[str] = None

class BookingCreate(BookingBase):
    # To assign custom IDs if provided by client/admin
    booking_id: Optional[str] = None
    
    # Needs at least one employee attached
    employees: List[EmployeeCreate] = []
    
    flight_details: Optional[BookingFlightBase] = None
    train_details: Optional[BookingTrainBase] = None
    bus_details: Optional[BookingBusBase] = None
    hotel_details: Optional[BookingHotelBase] = None

class BookingUpdate(BaseModel):
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    cost: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    
    flight_details: Optional[BookingFlightBase] = None
    train_details: Optional[BookingTrainBase] = None
    bus_details: Optional[BookingBusBase] = None
    hotel_details: Optional[BookingHotelBase] = None

class BookingRead(BookingBase):
    booking_id: str
    participants: List[EmployeeRead] = []
    
    flight_details: Optional[BookingFlightBase] = None
    train_details: Optional[BookingTrainBase] = None
    bus_details: Optional[BookingBusBase] = None
    hotel_details: Optional[BookingHotelBase] = None
    
    model_config = ConfigDict(from_attributes=True)

class StatusUpdate(BaseModel):
    status: str
