# 🎫 Booking Record Keeper

A professional, production-ready Streamlit application for managing bookings for flights, hotels, trains, and buses with Excel as the database backend.

## 🌟 Features

- **Multi-Booking System**: Manage bookings for flights, hotels, trains, and buses in one place
- **Excel Database**: Persistent data storage in Excel format (.xlsx)
- **CRUD Operations**: Create, Read, Update, and Delete bookings
- **Search & Filter**: Find bookings quickly with powerful search and filtering
- **Data Validation**: Email, phone, cost, and date validation
- **Analytics Dashboard**: Real-time statistics and visual analytics
- **Export Functionality**: Download bookings as CSV files
- **Professional UI**: Clean, responsive interface with custom styling
- **Error Handling**: Comprehensive error messages and validation

## 📋 Booking Types

### ✈️ Flight Bookings

- Passenger information (name, email, phone)
- Flight details (airline, flight number, route)
- Schedule (departure/arrival dates and times)
- Seat assignment and class selection
- Pricing and booking status

### 🏨 Hotel Bookings

- Guest information
- Hotel details and location
- Check-in/check-out dates
- Room type and quantity
- Guest count and confirmation number
- Pricing and booking status

### 🚆 Train Bookings

- Passenger information
- Train details (name, number, route)
- Schedule (departure/arrival)
- Coach and seat assignment
- Class selection
- Pricing and booking status

### 🚌 Bus Bookings

- Passenger information
- Bus company and bus number
- Route (from/to cities)
- Schedule (departure/arrival)
- Seat assignment
- Pricing and booking status

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Booking-App
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 📁 Project Structure

```
Booking-App/
├── app.py                 # Main Streamlit application
├── config.py             # Configuration and constants
├── requirements.txt      # Python dependencies
├── .streamlit/
│   └── config.toml      # Streamlit configuration
├── utils/
│   ├── __init__.py
│   ├── excel_db.py      # Excel database operations
│   └── validators.py    # Data validation utilities
├── pages/
│   ├── 1_Flight.py      # Flight booking management
│   ├── 2_Hotel.py       # Hotel booking management
│   ├── 3_Train.py       # Train booking management
│   ├── 4_Bus.py         # Bus booking management
│   └── 5_Dashboard.py   # Analytics and statistics
└── data/
    └── bookings.xlsx    # Excel database (auto-created)
```

## 🎯 Usage Guide

### Adding a Booking

1. Navigate to the desired booking type (Flight, Hotel, Train, or Bus)
2. Click the **"➕ Add"** tab
3. Fill in all required fields (marked with \*)
4. Click **"Add [Booking Type]"** button
5. Booking ID is automatically generated

### Viewing Bookings

1. Go to the booking type page
2. Click the **"📋 View"** tab
3. Use the search field to find specific bookings
4. Filter by status using the status dropdown
5. Click **"📥 Download as CSV"** to export

### Editing a Booking

1. Navigate to the booking type
2. Click the **"✏️ Edit"** tab
3. Select the booking ID from dropdown
4. Modify the fields as needed
5. Click **"✏️ Update Booking"** to save

### Deleting a Booking

1. Go to the booking type
2. Click the **"🗑️ Delete"** tab
3. Select the booking ID to delete
4. Review the booking details
5. Click **"🗑️ Delete Booking"** (cannot be undone)

### Dashboard Analytics

- View total bookings and revenue
- See booking distribution by type
- Monitor booking status breakdown
- Access detailed statistics per booking type
- Export all data to CSV

## 📊 Database Structure

### Excel Sheets

The application creates an Excel file with separate sheets for each booking type:

- **Flight** - Flight booking records
- **Hotel** - Hotel booking records
- **Train** - Train booking records
- **Bus** - Bus booking records

### Common Fields

- **Booking ID** - Unique identifier (auto-generated)
- **Status** - Confirmed, Pending, Cancelled, Completed
- **Booking Date** - Date when booking was made
- **Notes** - Additional information

## ✅ Data Validation

The app validates:

- **Email**: Standard email format validation
- **Phone**: Minimum 10 digits required
- **Dates**: Valid date format (YYYY-MM-DD)
- **Costs**: Positive numbers only
- **Required Fields**: All marked fields must be filled
- **Date Logic**: Check-out after check-in for hotels

## 🔧 Configuration

Edit `config.py` to customize:

- Field names for each booking type
- Status options
- Class options for flights/trains
- Room types for hotels
- Database location

## 📦 Dependencies

- **streamlit** - Web app framework
- **pandas** - Data manipulation
- **openpyxl** - Excel file handling
- **python-dateutil** - Date utilities
- **plotly** - Interactive charts
- **pytz** - Timezone support

## 🎨 Customization

### Theme

Edit `.streamlit/config.toml` to customize:

- Primary color
- Font and styling
- Layout options

### Fields

Modify field lists in `config.py` for each booking type

### Validation Rules

Update `utils/validators.py` to add custom validation

## 🐛 Troubleshooting

**Q: Database not found**

- A: The database is created automatically on first run in the `data/` folder

**Q: Changes not saving**

- A: Ensure the `data/` folder exists and has write permissions

**Q: Import errors**

- A: Install dependencies with `pip install -r requirements.txt`

**Q: Validation errors**

- A: Check that all required fields (marked with \*) are filled correctly

## 📝 Best Practices

1. **Regular Backups**: Backup your `data/bookings.xlsx` file regularly
2. **Data Validation**: Always verify information before saving
3. **Status Management**: Keep status updated as bookings progress
4. **Export Reports**: Export data monthly for reporting
5. **Check Notes**: Use notes field for important booking information

## 🔒 Security Notes

- Store the Excel database file securely
- Backup data regularly
- Do not share booking files containing sensitive information
- Validate all user inputs before processing

## 📈 Performance

- Optimized for up to 10,000+ bookings
- Fast search and filter operations
- Efficient Excel I/O operations
- Responsive UI with no lag

## 🤝 Contributing

Feel free to extend the application:

- Add new booking types
- Implement additional validation rules
- Create custom reports
- Add notification features

## 📄 License

This project is provided as-is for booking management purposes.

## 📞 Support

For issues or questions:

1. Check the FAQ section in the app
2. Review the troubleshooting guide
3. Check Excel file for data integrity

## 🎓 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Openpyxl Documentation](https://openpyxl.readthedocs.io/)
- [Python Email Validation](https://docs.python.org/3/library/email.html)

## 🔄 Version History

### Version 1.0.0

- Initial release
- Support for Flight, Hotel, Train, Bus bookings
- Excel database backend
- Complete CRUD operations
- Search, filter, and export functionality
- Analytics dashboard

---

**Built with ❤️ using Streamlit | Last Updated: February 2026**
