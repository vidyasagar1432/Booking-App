import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import engine, init_db
from app.models.domain import Company, Employee, Booking, BookingParticipant, BookingFlight, BookingTrain, BookingHotel
from app.crud import company as crud_company
from app.crud import employee as crud_employee
from app.crud import booking as crud_booking

async def seed_data():
    print("Seeding dummy data...")
    async with engine.begin() as conn:
        session = AsyncSession(conn)
        
        # 1. Create Companies
        companies = [
            Company(name="TechCorp Solutions", industry="Technology", phone="9876543210", email="info@techcorp.com", address="Bangalore, KA"),
            Company(name="Global Finance Inc", industry="Finance", phone="9876543211", email="hr@globalfinance.com", address="Mumbai, MH"),
            Company(name="Green Energy Ltd", industry="Energy", phone="9876543212", email="contact@greenenergy.in", address="Delhi, NCR"),
            Company(name="Creative Minds Agency", industry="Marketing", phone="9876543213", email="hello@creativeminds.com", address="Pune, MH")
        ]
        session.add_all(companies)
        await session.flush()
        
        # 2. Create Employees
        names = ["Amit Sharma", "Priya Patel", "Vikram Singh", "Anjali Rao", "Rahul Verma", "Sneha Gupta", "Karan Malhotra", "Riya Sen"]
        employees = []
        for name in names:
            emp = Employee(
                name=name,
                phone=f"90000{random.randint(10000, 99999)}",
                email=f"{name.lower().replace(' ', '.')}@example.com",
                company_id=random.choice(companies).id,
                designation=random.choice(["Lead Engineer", "Senior Analyst", "Manager", "Consultant", "Director"]),
                id_type="Aadhar",
                id_number=str(random.randint(100000000000, 999999999999))
            )
            employees.append(emp)
        session.add_all(employees)
        await session.flush()
        
        # 3. Create Bookings
        booking_types = ["Flight", "Train", "Hotel"]
        statuses = ["Confirmed", "Completed", "Pending", "Cancelled"]
        cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune"]
        
        for i in range(20):
            b_type = random.choice(booking_types)
            b_date = datetime.now() - timedelta(days=random.randint(0, 60))
            cost = random.randint(2000, 25000)
            
            b = Booking(
                booking_id=f"BKN-{random.randint(10000, 99999)}",
                booking_type=b_type,
                booking_date=b_date,
                start_datetime=b_date + timedelta(hours=2),
                end_datetime=b_date + timedelta(hours=5),
                cost=cost,
                status=random.choice(statuses),
                notes="Automatic dummy entry"
            )
            session.add(b)
            await session.flush()
            
            # Link passenger
            participant = BookingParticipant(booking_id=b.booking_id, employee_id=random.choice(employees).id)
            session.add(participant)
            
            # Add specific details
            if b_type == "Flight":
                details = BookingFlight(
                    booking_id=b.booking_id,
                    airline=random.choice(["IndiGo", "Air India", "Vistara", "SpiceJet"]),
                    flight_number=f"6E-{random.randint(100, 999)}",
                    from_city=random.choice(cities),
                    to_city=random.choice(cities),
                    pnr_status="HK1",
                    seat_class="Economy"
                )
                session.add(details)
            elif b_type == "Train":
                details = BookingTrain(
                    booking_id=b.booking_id,
                    train_number=str(random.randint(12000, 13000)),
                    coach_number=f"B{random.randint(1, 4)}",
                    from_city=random.choice(cities),
                    to_city=random.choice(cities),
                    platform=str(random.randint(1, 10))
                )
                session.add(details)
            elif b_type == "Hotel":
                details = BookingHotel(
                    booking_id=b.booking_id,
                    hotel_name=random.choice(["Taj Mahal Palace", "JW Marriott", "The Oberoi", "ITC Maurya"]),
                    room_type="Deluxe Suite",
                    city=random.choice(cities),
                    hotel_address="Downtown Square",
                    check_in_time=(b_date + timedelta(hours=14)).isoformat(),
                    check_out_time=(b_date + timedelta(days=2, hours=11)).isoformat()
                )
                session.add(details)

        
        await session.commit()
        print("Successfully seeded 4 companies, 8 employees, and 20 bookings.")

if __name__ == "__main__":
    asyncio.run(seed_data())
