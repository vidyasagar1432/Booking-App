import io
import csv
from datetime import datetime, date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.domain import Employee
from app.schemas.booking import EmployeeCreate, EmployeeUpdate, PaginatedResponse, EmployeeReadExtended
from app.crud import employee as crud_employee
from app.crud import booking as crud_booking
from app.crud import company as crud_company
from app.api.utils import booking_to_dict

router = APIRouter()

@router.get("", response_model=PaginatedResponse[EmployeeReadExtended])
async def list_employees(search: str = "", company_id: Optional[str] = Query(None), page: int = 1, size: int = 20, sort_by: str = "created_at", order: str = "desc", 
                         session: AsyncSession = Depends(get_session)):
    offset = (page - 1) * size
    cid = None
    if company_id and company_id.strip():
        try: cid = int(company_id)
        except ValueError: pass
            
    employees, total = await crud_employee.get_all_employees(
        session, search=search, company_id=cid, offset=offset, limit=size, 
        sort_by=sort_by, order=order, include_stats=True
    )
    
    return {
        "items": employees,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

@router.get("/export")
async def export_employees(search: str = "", company_id: Optional[str] = Query(None), sort_by: str = "created_at", order: str = "desc", 
                         session: AsyncSession = Depends(get_session)):
    cid = None
    if company_id and company_id.strip():
        try: cid = int(company_id)
        except ValueError: pass
            
    employees, _ = await crud_employee.get_all_employees(
        session, search=search, company_id=cid, offset=0, limit=100000, 
        sort_by=sort_by, order=order, include_stats=True
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Designation", "Phone", "Email", "ID Type", "ID Number", "Company", "Booking Count", "Total Spent", "Created At"])
    
    for e in employees:
        writer.writerow([
            e.name, e.designation or "", e.phone, e.email or "", 
            e.id_type or "", e.id_number or "", 
            getattr(e.company, "name", "Independent") if hasattr(e, "company") and getattr(e, "company", None) else "Independent",
            e.booking_count, e.total_spent,
            e.created_at.isoformat()
        ])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]), 
        media_type="text/csv", 
        headers={"Content-Disposition": f"attachment; filename=employees_export_{datetime.now().strftime('%Y%m%d')}.csv"}
    )

@router.post("", status_code=201)
async def create_employee(payload: EmployeeCreate, session: AsyncSession = Depends(get_session)):
    emp = await crud_employee.upsert_employee(
        session, name=payload.name, phone=payload.phone,
        company_name=payload.company_name, designation=payload.designation,
        email=payload.email
    )
    if payload.id_type: emp.id_type = payload.id_type
    if payload.id_number: emp.id_number = payload.id_number
    await session.commit()
    await session.refresh(emp)

    co = await crud_company.get_company_by_id(session, emp.company_id) if emp.company_id else None
    return {"id": emp.id, "name": emp.name, "phone": emp.phone,
            "company_id": emp.company_id, "company_name": co.name if co else None,
            "designation": emp.designation, "email": emp.email,
            "id_type": emp.id_type, "id_number": emp.id_number,
            "booking_count": 0, "total_spent": 0}

@router.post("/import", status_code=201)
async def import_employees_bulk(file: UploadFile = File(...), session: AsyncSession = Depends(get_session)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))
    
    new_employees = []
    for row in reader:
        name = row.get("name")
        phone = row.get("phone")
        if not name or not phone:
            continue
            
        emp = Employee(
            name=name,
            phone=phone,
            email=row.get("email"),
            designation=row.get("designation"),
            company_id=int(row["company_id"]) if row.get("company_id") and row["company_id"].isdigit() else None
        )
        new_employees.append(emp)
        
    if new_employees:
        await crud_employee.bulk_create_employees(session, new_employees)
        await session.commit()
        
    return {"message": f"Successfully imported {len(new_employees)} employees."}

@router.put("/{employee_id}")
async def update_employee(employee_id: int, payload: EmployeeUpdate, session: AsyncSession = Depends(get_session)):
    updated = await crud_employee.update_employee(session, employee_id, payload.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(404, "Employee not found.")
    await session.commit()
    co = updated.company
    return {"id": updated.id, "name": updated.name, "phone": updated.phone,
            "company_id": updated.company_id, "company_name": co.name if co else None,
            "designation": updated.designation, "email": updated.email,
            "id_type": updated.id_type, "id_number": updated.id_number}

@router.delete("/{employee_id}", status_code=204)
async def delete_employee(employee_id: int, session: AsyncSession = Depends(get_session)):
    if not await crud_employee.delete_employee(session, employee_id):
        raise HTTPException(404, "Employee not found.")
    await session.commit()

@router.get("/{employee_id}/bookings")
async def employee_bookings(employee_id: int, date_from: Optional[date] = None, date_to: Optional[date] = None, session: AsyncSession = Depends(get_session)):
    emp = await crud_employee.get_employee_by_id(session, employee_id)
    if not emp:
        raise HTTPException(404, "Employee not found.")
    emp_bks = await crud_booking.get_bookings_for_employee(session, employee_id)
    filtered_bks = []
    for b in emp_bks:
        if date_from and b.booking_date and b.booking_date.date() < date_from: continue
        if date_to and b.booking_date and b.booking_date.date() > date_to: continue
        filtered_bks.append(b)
    
    return {
        "employee_id": employee_id,
        "employee_name": emp.name,
        "phone": emp.phone,
        "email": emp.email,
        "designation": emp.designation,
        "id_type": emp.id_type,
        "id_number": emp.id_number,
        "company_id": emp.company_id,
        "company_name": emp.company.name if getattr(emp, "company", None) else None,
        "bookings": [booking_to_dict(b) for b in filtered_bks],
    }
