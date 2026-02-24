import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.crud import booking as crud_booking
from app.models.domain import Company, Employee, Booking
from sqlmodel import select, or_, func, col
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter()

@router.get("/suggestions/{field}")
async def suggestions(field: str, q: str = "", session: AsyncSession = Depends(get_session)):
    return await crud_booking.get_suggestions(session, field, q)

@router.get("/search")
async def global_search(q: str = "", session: AsyncSession = Depends(get_session)):
    if not q or len(q) < 2:
        return {"companies": [], "employees": [], "bookings": []}
        
    term = f"%{q}%"
    
    # 1. Company matches
    comp_res = await session.execute(
        select(Company).where(or_(Company.name.ilike(term), Company.industry.ilike(term))).limit(5)
    )
    comp_matches = [
        {"id": c.id, "name": c.name, "type": "company", "desc": c.industry or "Company"}
        for c in comp_res.scalars()
    ]
    
    # 2. Employee matches
    emp_res = await session.execute(
        select(Employee).options(selectinload(Employee.company))
        .where(or_(Employee.name.ilike(term), Employee.phone.ilike(term), Employee.email.ilike(term)))
        .limit(5)
    )
    emp_matches = [
        {"id": e.id, "name": e.name, "type": "employee", 
         "desc": f"{e.designation or 'Employee'} - {e.company.name if e.company else 'Independent'}"}
        for e in emp_res.scalars()
    ]
    
    # 3. Booking matches
    bk_res = await session.execute(
        select(Booking).where(or_(Booking.booking_id.ilike(term), Booking.notes.ilike(term))).limit(5)
    )
    bk_matches = []
    for b in bk_res.scalars():
        # Quick route summary
        desc = f"{b.booking_type} | {b.booking_date.date() if b.booking_date else ''}"
        bk_matches.append({
            "id": b.booking_id, "name": f"{b.booking_type} ({b.booking_id})",
            "type": "booking", "desc": desc
        })
            
    return {"companies": comp_matches, "employees": emp_matches, "bookings": bk_matches}

@router.get("/notifications")
async def get_notifications(session: AsyncSession = Depends(get_session)):
    alerts = []
    now = datetime.utcnow()
    
    # 1. Pending Confirmations
    pending_count = (await session.execute(
        select(func.count(Booking.booking_id)).where(Booking.status == "Pending")
    )).scalar() or 0
    if pending_count > 0:
        alerts.append({
            "id": "alert_pending", "title": f"{pending_count} Pending Confirmations",
            "message": "Action required to finalize booking statuses.", "type": "warning",
            "icon": "bx-time-five", "link": "/bookings"
        })

    # 2. Departing Soon (next 48h)
    soon = now + timedelta(hours=48)
    upc_count = (await session.execute(
        select(func.count(Booking.booking_id))
        .where(Booking.status == "Confirmed", Booking.start_datetime > now, Booking.start_datetime < soon)
    )).scalar() or 0
    if upc_count > 0:
        alerts.append({
            "id": "alert_departures", "title": "Departing Soon",
            "message": f"{upc_count} confirmed trips depart in next 48h.", "type": "info",
            "icon": "bxs-plane-take-off", "link": "/tracker"
        })

    # 3. High Value (Pending + Cost > 50000)
    hv_count = (await session.execute(
        select(func.count(Booking.booking_id))
        .where(Booking.status == "Pending", Booking.cost > 50000)
    )).scalar() or 0
    if hv_count > 0:
        alerts.append({
            "id": "alert_highval", "title": "High Value Authorization",
            "message": f"{hv_count} bookings exceeding ₹50k require review.", "type": "error",
            "icon": "bx-money", "link": "/bookings"
        })

    return {"alerts": alerts, "unread_count": len(alerts)}

@router.get("/geocode")
async def proxy_geocode(q: str):
    # Proxy Nominatim to avoid CORS issues in frontend
    async with httpx.AsyncClient() as client:
        try:
            url = f"https://nominatim.openstreetmap.org/search?format=json&q={q}&limit=1"
            headers = {"User-Agent": "TravelAdmin/1.0"}
            resp = await client.get(url, headers=headers)
            return resp.json()
        except Exception:
            return []
