import io
import pandas as pd
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.crud import booking as crud_booking
from app.crud import employee as crud_employee
from app.crud import company as crud_company
from app.api.utils import booking_to_dict

router = APIRouter()

@router.post("/reset-db", status_code=200)
async def admin_reset_db():
    from app.db.session import init_db, engine
    from sqlmodel import SQLModel
    # Note: For SQLite, drop_all might need syncing context, but we will do a basic approach
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    return {"message": "Database reset successfully."}

@router.get("/export")
async def admin_export_db(
    entity_bookings: bool = True,
    entity_employees: bool = True,
    entity_companies: bool = True,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    booking_type: Optional[str] = None,
    booking_status: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if entity_bookings:
            all_bookings, _ = await crud_booking.get_all_bookings(
                session, limit=100000, 
                types=[booking_type] if booking_type else None, 
                statuses=[booking_status] if booking_status else None,
                date_from=date_from, date_to=date_to
            )
            
            # Group bookings by type
            bookings_by_type = {}
            for b in all_bookings:
                d = booking_to_dict(b)
                # Format passengers list
                d['passengers'] = ", ".join([e['name'] for e in d.get('employees', [])])
                d.pop('employees', None)
                
                b_type = d.get('booking_type', 'Other')
                if b_type not in bookings_by_type:
                    bookings_by_type[b_type] = []
                bookings_by_type[b_type].append(d)
            
            if not bookings_by_type:
                df_empty = pd.DataFrame(columns=["booking_id", "booking_type", "booking_date", "cost", "status"])
                df_empty.to_excel(writer, sheet_name='Bookings', index=False)
            else:
                for b_type, items in bookings_by_type.items():
                    df = pd.DataFrame(items)
                    # Remove columns that are completely empty for this specific type to keep it clean
                    df = df.dropna(axis=1, how='all')
                    
                    # Name the sheet pluralized (e.g., Flights, Hotels)
                    sheet_name = f"{b_type}s" if b_type != "Bus" else "Buses"
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        if entity_employees:
            all_employees, _ = await crud_employee.get_all_employees(session, limit=100000)
            emp_list = []
            for e in all_employees:
                emp_list.append({
                    "ID": e.get("id"), 
                    "Name": e.get("name"), 
                    "Phone": e.get("phone"), 
                    "Email": e.get("email"),
                    "Company ID": e.get("company_id"), 
                    "Company Name": e.get("company_name"),
                    "Designation": e.get("designation"),
                    "ID Type": e.get("id_type"), 
                    "ID Number": e.get("id_number"),
                    "Created At": e.get("created_at").isoformat() if e.get("created_at") and hasattr(e.get("created_at"), "isoformat") else str(e.get("created_at")),
                    "Is Active": e.get("is_active")
                })
            df_employees = pd.DataFrame(emp_list) if emp_list else pd.DataFrame(columns=["ID", "Name", "Phone", "Email"])
            df_employees.to_excel(writer, sheet_name='Employees', index=False)
            
        if entity_companies:
            all_companies, _ = await crud_company.get_all_companies(session, limit=100000)
            comp_list = []
            for c in all_companies:
                comp_list.append({
                    "ID": c.id, "Name": c.name, "Industry": c.industry,
                    "Phone": c.phone, "Email": c.email, "Address": c.address,
                    "GST Number": c.gst_number,
                    "Created At": c.created_at.isoformat() if c.created_at else None,
                    "Is Active": c.is_active
                })
            df_companies = pd.DataFrame(comp_list) if comp_list else pd.DataFrame(columns=["ID", "Name", "Industry", "Phone"])
            df_companies.to_excel(writer, sheet_name='Companies', index=False)

        if not entity_bookings and not entity_employees and not entity_companies:
            df_empty = pd.DataFrame(["No entities selected"])
            df_empty.to_excel(writer, sheet_name='Export', index=False, header=False)

    output.seek(0)
    headers = {
        'Content-Disposition': 'attachment; filename="TravelAdmin_Export.xlsx"'
    }
    return StreamingResponse(
        output, 
        headers=headers, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
