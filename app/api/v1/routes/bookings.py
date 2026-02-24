import io
import csv
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime

from app.db.session import get_session
from app.schemas.booking import BookingCreate, BookingUpdate, StatusUpdate, PaginatedResponse
from app.models.domain import Booking
from app.crud import booking as crud_booking
from app.services.booking_service import create_new_booking
from app.api.utils import booking_to_dict
from app.api.websockets import manager

router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def list_bookings(search: str = "", 
                  type: Optional[List[str]] = Query(None), 
                  status: Optional[List[str]] = Query(None), 
                  date_from: Optional[str] = None, 
                  date_to: Optional[str] = None,
                  min_cost: Optional[str] = Query(None),
                  max_cost: Optional[str] = Query(None),
                  page: int = 1, size: int = 20, sort_by: str = "booking_date", order: str = "desc", 
                  session: AsyncSession = Depends(get_session)):
    
    # Safely parse dates
    dt_from = None
    if date_from and date_from.strip() and date_from != 'null':
        try:
            # Handle both ISO with Z and without
            clean_date = date_from.replace('Z', '+00:00')
            dt_from = datetime.fromisoformat(clean_date)
        except ValueError:
            pass

    dt_to = None
    if date_to and date_to.strip() and date_to != 'null':
        try:
            clean_date = date_to.replace('Z', '+00:00')
            dt_to = datetime.fromisoformat(clean_date)
        except ValueError:
            pass
    
    # Safely parse costs
    f_min_cost = None
    if min_cost and min_cost.strip() and min_cost != 'null':
        try:
            f_min_cost = float(min_cost)
        except ValueError:
            pass
            
    f_max_cost = None
    if max_cost and max_cost.strip() and max_cost != 'null':
        try:
            f_max_cost = float(max_cost)
        except ValueError:
            pass

    # Filter out empty strings from lists
    types = [t for t in type if t and t != 'null'] if type else None
    statuses = [s for s in status if s and s != 'null'] if status else None

    offset = (page - 1) * size
    bookings, total = await crud_booking.get_all_bookings(
        session, search=search, types=types, statuses=statuses, 
        date_from=dt_from, date_to=dt_to, 
        min_cost=f_min_cost, max_cost=f_max_cost,
        offset=offset, limit=size, sort_by=sort_by, order=order
    )
    result_items = [booking_to_dict(b) for b in bookings]
    return {
        "items": result_items, "total": total, "page": page, "size": size,
        "pages": (total + size - 1) // size
    }

@router.get("/export")
async def export_bookings(search: str = "", 
                  type: Optional[List[str]] = Query(None), 
                  status: Optional[List[str]] = Query(None), 
                  date_from: Optional[datetime] = None, 
                  date_to: Optional[datetime] = None,
                  min_cost: Optional[float] = Query(None),
                  max_cost: Optional[float] = Query(None),
                  sort_by: str = "booking_date", order: str = "desc", 
                  session: AsyncSession = Depends(get_session)):
    bookings, _ = await crud_booking.get_all_bookings(
        session, search=search, types=type, statuses=status, 
        date_from=date_from, date_to=date_to, 
        min_cost=min_cost, max_cost=max_cost,
        offset=0, limit=100000, sort_by=sort_by, order=order
    )
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Booking ID", "Type", "Status", "Booking Date", "Start Time", "End Time", "Cost", "Notes", "Participants"])
    
    for b in bookings:
        participants = ", ".join([f"{emp.name} ({getattr(emp.company, 'name', 'Independent') if hasattr(emp, 'company') else 'Independent'})" for emp in b.participants])
        writer.writerow([
            b.booking_id, b.booking_type, b.status, 
            b.booking_date.date() if b.booking_date else "", 
            b.start_datetime.isoformat() if b.start_datetime else "",
            b.end_datetime.isoformat() if b.end_datetime else "", 
            b.cost, b.notes or "", participants
        ])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]), 
        media_type="text/csv", 
        headers={"Content-Disposition": f"attachment; filename=bookings_export_{datetime.now().strftime('%Y%m%d')}.csv"}
    )

@router.get("/{booking_id}")
async def get_booking(booking_id: str, session: AsyncSession = Depends(get_session)):
    b = await crud_booking.get_booking_by_id(session, booking_id)
    if not b:
        raise HTTPException(404, "Booking not found.")
    return booking_to_dict(b)

@router.post("", status_code=201)
async def create_booking_api(payload: BookingCreate, bg_tasks: BackgroundTasks, 
                             session: AsyncSession = Depends(get_session)):
    bk = await create_new_booking(session, payload)

    bg_tasks.add_task(manager.broadcast, {"type": "booking_created", "id": bk.booking_id})
    return booking_to_dict(bk)

@router.put("/{booking_id}")
async def update_booking(booking_id: str, payload: BookingUpdate, bg_tasks: BackgroundTasks, 
                         session: AsyncSession = Depends(get_session)):
    b = await crud_booking.update_booking(session, booking_id, payload.model_dump(exclude_none=True))
    if not b:
        raise HTTPException(404, "Booking not found.")
    await session.commit()
    bg_tasks.add_task(manager.broadcast, {"type": "booking_updated", "id": b.booking_id})
    return booking_to_dict(b)

@router.patch("/{booking_id}/status")
async def update_booking_status(booking_id: str, payload: StatusUpdate, bg_tasks: BackgroundTasks, 
                                session: AsyncSession = Depends(get_session)):
    b = await crud_booking.update_booking(session, booking_id, {"status": payload.status})
    if not b:
        raise HTTPException(404, "Booking not found.")
    await session.commit()
    bg_tasks.add_task(manager.broadcast, {"type": "status_updated", "id": b.booking_id})
    return {"booking_id": b.booking_id, "status": b.status}

@router.delete("/{booking_id}", status_code=204)
async def delete_booking(booking_id: str, bg_tasks: BackgroundTasks, 
                         session: AsyncSession = Depends(get_session)):
    success = await crud_booking.delete_booking(session, booking_id)
    if not success:
        raise HTTPException(404, "Booking not found")
    await session.commit()
    bg_tasks.add_task(manager.broadcast, {"type": "booking_deleted", "id": booking_id})
