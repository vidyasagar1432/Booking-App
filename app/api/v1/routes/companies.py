import io
import csv
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlmodel import select, func
from datetime import date, datetime

from app.db.session import get_session
from app.schemas.booking import CompanyCreate, CompanyUpdate, PaginatedResponse
from app.models.domain import Employee, Booking, BookingParticipant, Company
from sqlmodel import select, func, or_, and_
from app.crud import company as crud_company
from app.crud import employee as crud_employee
from app.crud import booking as crud_booking
from app.api.utils import booking_to_dict

router = APIRouter()

@router.get("", response_model=PaginatedResponse)
async def list_companies(search: str = "", page: int = 1, size: int = 20, sort_by: str = "created_at", order: str = "desc", session: AsyncSession = Depends(get_session)):
    offset = (page - 1) * size
    companies, total = await crud_company.get_all_companies(session, search=search, offset=offset, limit=size, sort_by=sort_by, order=order)
    
    company_ids = [c.id for c in companies]
    
    emp_counts = {}
    booking_stats = {}
    if company_ids:
        # 1. Employee counts per company
        counts_res = await session.execute(
            select(Employee.company_id, func.count(Employee.id))
            .where(Employee.company_id.in_(company_ids), Employee.is_active == True)
            .group_by(Employee.company_id)
        )
        emp_counts = {cid: cnt for cid, cnt in counts_res}

        # 2. Booking stats per company (Unified Join)
        b_stats_res = await session.execute(
            select(
                Employee.company_id, 
                func.count(func.distinct(Booking.booking_id)).label("count"), 
                func.sum(Booking.cost).label("spent")
            )
            .join(BookingParticipant, BookingParticipant.employee_id == Employee.id)
            .join(Booking, Booking.booking_id == BookingParticipant.booking_id)
            .where(Employee.company_id.in_(company_ids))
            .group_by(Employee.company_id)
        )
        for row in b_stats_res:
            booking_stats[row[0]] = {"count": row[1], "spent": float(row[2] or 0)}

    result_items = []
    for c in companies:
        stats = booking_stats.get(c.id, {"count": 0, "spent": 0.0})
        result_items.append({
            "id": c.id, "name": c.name, "industry": c.industry,
            "phone": c.phone, "email": c.email, "address": c.address,
            "gst_number": c.gst_number,
            "created_at": c.created_at.isoformat(),
            "is_active": c.is_active,
            "employee_count": emp_counts.get(c.id, 0),
            "booking_count": stats["count"],
            "total_spent": round(stats["spent"], 2) if stats["spent"] else 0.0,
        })
        
    return {
        "items": result_items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.get("/export")
async def export_companies(search: str = "", sort_by: str = "created_at", order: str = "desc", session: AsyncSession = Depends(get_session)):
    companies, _ = await crud_company.get_all_companies(session, search=search, offset=0, limit=100000, sort_by=sort_by, order=order)
    company_ids = [c.id for c in companies]
    
    emp_counts = {}
    booking_stats = {}
    if company_ids:
        counts_res = await session.execute(
            select(Employee.company_id, func.count(Employee.id))
            .where(Employee.company_id.in_(company_ids), Employee.is_active == True)
            .group_by(Employee.company_id)
        )
        emp_counts = {cid: cnt for cid, cnt in counts_res}

        b_stats_res = await session.execute(
            select(
                Employee.company_id, 
                func.count(func.distinct(Booking.booking_id)).label("count"), 
                func.sum(Booking.cost).label("spent")
            )
            .join(BookingParticipant, BookingParticipant.employee_id == Employee.id)
            .join(Booking, Booking.booking_id == BookingParticipant.booking_id)
            .where(Employee.company_id.in_(company_ids))
            .group_by(Employee.company_id)
        )
        for row in b_stats_res:
            booking_stats[row[0]] = {"count": row[1], "spent": float(row[2] or 0)}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Company Name", "Industry", "Phone", "Email", "Address", "GST Number", "Employee Count", "Booking Count", "Total Spent", "Created At"])
    
    for c in companies:
        stats = booking_stats.get(c.id, {"count": 0, "spent": 0.0})
        writer.writerow([
            c.name, c.industry or "", c.phone or "", c.email or "", 
            c.address or "", c.gst_number or "", 
            emp_counts.get(c.id, 0), stats["count"], stats["spent"],
            c.created_at.isoformat()
        ])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]), 
        media_type="text/csv", 
        headers={"Content-Disposition": f"attachment; filename=companies_export_{datetime.now().strftime('%Y%m%d')}.csv"}
    )

@router.post("", status_code=201)
async def create_company(payload: CompanyCreate, session: AsyncSession = Depends(get_session)):
    c = Company(**payload.model_dump())
    await crud_company.create_company(session, c)
    await session.commit()
    return {"id": c.id, "name": c.name, "industry": c.industry,
            "phone": c.phone, "email": c.email, "address": c.address,
            "gst_number": c.gst_number, "employee_count": 0,
            "booking_count": 0, "total_spent": 0}

@router.put("/{company_id}")
async def update_company(company_id: int, payload: CompanyUpdate, session: AsyncSession = Depends(get_session)):
    updated = await crud_company.update_company(session, company_id, payload.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(404, "Company not found.")
    await session.commit()
    return {"id": updated.id, "name": updated.name, "industry": updated.industry,
            "phone": updated.phone, "email": updated.email}

@router.delete("/{company_id}", status_code=204)
async def delete_company(company_id: int, session: AsyncSession = Depends(get_session)):
    if not await crud_company.delete_company(session, company_id):
        raise HTTPException(404, "Company not found.")
    await session.commit()

@router.get("/{company_id}/details")
async def company_details(company_id: int, date_from: Optional[date] = None, date_to: Optional[date] = None, session: AsyncSession = Depends(get_session)):
    company = await crud_company.get_company_by_id(session, company_id)
    if not company:
        raise HTTPException(404, "Company not found.")
        
    # Standardize dates for filter
    d_from = datetime.combine(date_from, datetime.min.time()) if date_from else None
    d_to = datetime.combine(date_to, datetime.max.time()) if date_to else None

    # Optimized fetch for employees with their stats in one go
    stmt = (
        select(
            Employee,
            func.count(func.distinct(Booking.booking_id)).label("b_count"),
            func.sum(Booking.cost).label("b_spent")
        )
        .outerjoin(BookingParticipant, BookingParticipant.employee_id == Employee.id)
        .outerjoin(Booking, Booking.booking_id == BookingParticipant.booking_id)
        .where(Employee.company_id == company_id)
    )
    
    if d_from: stmt = stmt.where(or_(Booking.booking_date == None, Booking.booking_date >= d_from))
    if d_to: stmt = stmt.where(or_(Booking.booking_date == None, Booking.booking_date <= d_to))
        
    stmt = stmt.group_by(Employee.id)
    res = await session.execute(stmt)
    
    employees_data = []
    for row in res.all():
        e, count, spent = row
        employees_data.append({
            "id": e.id, "name": e.name, "phone": e.phone,
            "email": e.email, "designation": e.designation,
            "id_type": e.id_type, "id_number": e.id_number,
            "created_at": e.created_at.isoformat(),
            "booking_count": count or 0,
            "total_spent": round(float(spent or 0), 2),
        })

    return {
        "id": company.id, "name": company.name,
        "industry": company.industry, "phone": company.phone,
        "email": company.email, "address": company.address,
        "gst_number": company.gst_number,
        "employee_count": len(employees_data),
        "employees": employees_data,
    }

@router.get("/{company_id}/ledger")
async def company_ledger(company_id: int, session: AsyncSession = Depends(get_session)):
    company = await crud_company.get_company_by_id(session, company_id)
    if not company:
        raise HTTPException(404, "Company not found.")
        
    # Fetch only bookings that belong to this company's employees
    stmt = (
        select(Booking)
        .join(BookingParticipant, BookingParticipant.booking_id == Booking.booking_id)
        .join(Employee, Employee.id == BookingParticipant.employee_id)
        .where(Employee.company_id == company_id)
        .distinct()
        .order_by(Booking.booking_date.desc())
    )
    res = await session.execute(stmt)
    bookings = res.scalars().all()
    
    return {"bookings": [booking_to_dict(b) for b in bookings]}
