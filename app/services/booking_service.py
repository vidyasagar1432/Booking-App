from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.schemas.booking import BookingCreate, BookingUpdate
from app.models.domain import (
    Booking, BookingFlight, BookingTrain, BookingBus, BookingHotel
)
from app.crud.employee import upsert_employee
from app.crud.booking import create_booking

async def create_new_booking(db: AsyncSession, obj_in: BookingCreate) -> Booking:
    if not obj_in.employees:
        raise HTTPException(400, "Provide at least one traveling employee.")

    resolved_employees = []
    for emp_data in obj_in.employees:
        if not emp_data.name or not emp_data.phone:
            continue
        emp = await upsert_employee(
            db, 
            name=emp_data.name, 
            phone=emp_data.phone,
            company_name=emp_data.company_name, 
            designation=emp_data.designation,
            email=emp_data.email
        )
        if emp_data.id_type: emp.id_type = emp_data.id_type
        if emp_data.id_number: emp.id_number = emp_data.id_number
        resolved_employees.append(emp)

    if not resolved_employees:
        raise HTTPException(400, "Provide valid employees with name and phone.")

    # Create Base Booking
    b_data = obj_in.model_dump(exclude={
        "employees", "flight_details", "train_details", "bus_details", "hotel_details"
    }, exclude_none=True)
    
    bk = Booking(**b_data)
    bk.participants = resolved_employees

    # Parse appropriate child entity based on type
    b_type = bk.booking_type.lower()
    
    if b_type == "flight":
        if not obj_in.flight_details:
             raise HTTPException(400, "Flight details are required for flight tracking.")
        bk.flight_details = BookingFlight(**obj_in.flight_details.model_dump(exclude_none=True))
        
    elif b_type == "train":
        if not obj_in.train_details:
             raise HTTPException(400, "Train details are required")
        bk.train_details = BookingTrain(**obj_in.train_details.model_dump(exclude_none=True))
        
    elif b_type == "bus":
        if not obj_in.bus_details:
             raise HTTPException(400, "Bus details are required for this booking type.")
        bk.bus_details = BookingBus(**obj_in.bus_details.model_dump(exclude_none=True))
        
    elif b_type == "hotel":
        if not obj_in.hotel_details:
             raise HTTPException(400, "Hotel details are required")
        bk.hotel_details = BookingHotel(**obj_in.hotel_details.model_dump(exclude_none=True))
        
    else:
        raise HTTPException(400, f"Unsupported booking type: {b_type}")

    res = await create_booking(db, bk)
    # We moved commit to the boundary (API/Script), but for internal service calls it might be needed.
    # However, to support transactional testing, we should probably NOT commit here if we want to rollback.
    # Wait, if I'm calling this from a test that has a transaction, commit() will commit the transaction.
    # I should use session.commit() ONLY in the API routes.
    # Let's remove the commit() here.
    return res
