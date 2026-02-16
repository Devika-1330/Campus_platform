# Campus Platform

A college-based integrated web platform for **Lost & Found** and **Campus Complaints** management. Students can report lost/found items and raise complaints; college authorities manage and resolve them from a centralized admin dashboard.

## Tech Stack

- **UI:** HTML / CSS
- **Backend:** Flask (Python)
- **Database:** MySQL

## Features

### User Module
- **Registration & Login** — Create account with email and password
- **Lost & Found** — Report lost or found items (item name, description, location, date, contact); view all listings
- **Complaints** — Raise complaints with category (Hostel, Classroom, Canteen, Infrastructure, Library, Other), title, description, location; default status **Pending**
- **Dashboard** — View recent complaints and counts; track complaint status and admin remarks

### Admin Module
- **Admin Login** — Predefined admin account (see below)
- **Complaint Management** — View all complaints; update status: **Pending** → **In Progress** → **Resolved**; add admin remark (visible to student)
- **Lost & Found Management** — View all lost/found reports; verify entries; remove invalid entries

## Database

MySQL database **campus_platform** with tables:

- **users** — User details (email, password, name)
- **lost_items** — Lost item reports
- **found_items** — Found item reports  
- **complaints** — Complaints with category, title, description, location, status, admin_remark

The database and tables are created automatically on first run.

## Setup

1. **Install Python 3.8+** and **MySQL Server** (e.g. XAMPP, WAMP, or standalone MySQL).

2. **Create a virtual environment (recommended):**
   ```bash
   cd campus-platform
   python -m venv venv
   venv\Scripts\activate   # Windows
   # source venv/bin/activate   # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MySQL** (optional — defaults work for local MySQL):
   - Create a database named `campus_platform` in MySQL, or let the app create it.
   - Set environment variables if your MySQL differs:
     - `MYSQL_HOST` (default: localhost)
     - `MYSQL_USER` (default: root)
     - `MYSQL_PASSWORD` (default: empty)
     - `MYSQL_DB` (default: campus_platform)

5. **Run the application:**
   ```bash
   python app.py
   ```
   Open **http://127.0.0.1:5000** in your browser.

## Default Admin Credentials

- **Email:** `admin@campus.edu`  
- **Password:** `admin123`  

*(Change these in production and use a strong `SECRET_KEY` in config.)*

## Workflow

1. Student registers and logs in.
2. Student reports a lost/found item or raises a complaint → data is saved in MySQL.
3. Admin logs in and sees all submissions on the dashboard.
4. Admin updates complaint status (Pending / In Progress / Resolved) and can add remarks.
5. Student sees status and remarks in **My Complaints** and dashboard.

## Project Structure

```
campus-platform/
├── app.py              # Flask app, routes, auth
├── config.py           # Configuration
├── database.py         # MySQL init, table creation
├── requirements.txt
├── static/
│   └── style.css       # Main styles
└── templates/          # HTML templates
    ├── base.html
    ├── index.html
    ├── login.html, register.html
    ├── user_dashboard.html
    ├── lost_found.html, report_lost.html, report_found.html
    ├── complaints_list.html, raise_complaint.html
    ├── admin_dashboard.html
    ├── admin_complaints.html
    └── admin_lost_found.html
```

## License

MIT (or as per your college project guidelines).
