MAD-1 MODERN APPLICATION DEVELOPMENT-1 
PROJECT VEHICLE PARKING APP-V1
MAY TERM 2025

NAME: K RATNAGIRI MANIKANDAN
ROLL NO: 21F1002199


DESCRIPTION:

A full-stack Flask-based parking management system, named "Park Easy Go" with separate user & admin dashboards, spot reservation/release, historical summaries, and visual reports.


PROJECT STRUCTURE:

.
├── app/
│   ├── __init__.py         # Application factory
│   ├── config.py           # Flask settings
│   ├── extensions.py       # db, login_manager init
│   ├── models/             # SQLAlchemy models
│   │   └── models.py
│   ├── forms/              # Flask-WTF forms
│   │   └── forms.py
│   ├── views/              # Blueprint & routes
│   │   └── routes.py
│   ├── templates/          # Jinja2 templates
│   └── static/             # CSS, animations, chart images
├── instance/
│   ├── config.py           # Instance config
│   └── database.db
├── run.py                  # Entry point
├── README.md               # You are currently here
├── reset_db.py             # Drop & recreate schema
└── requirements.txt



🚀 KEY FEATURES

🔐 Authentication & Roles
Secure registration and login system using Flask-Login.

Two roles: Admin and User, with separate dashboards and permissions.




🚗 User Functionality
Reserve Spots: Real-time availability check and instant reservation.

Release Spots: Auto-calculates parking duration and cost.

View History: List of past reservations with duration and charges.

Summary Reports:

Filter by month and year.

Pie chart for expenditure per lot.

Bar chart showing reservations per lot.




🛠 Admin Functionality
Lot Management: Create, edit, and delete parking lots. Adjust spot count dynamically.

Spot Monitoring: View real-time status (Available/Occupied) of spots in each lot.

User Records: View detailed reservation history and active bookings of each user.

Search Tool: Locate users or lots by PIN code or address.

Summary Dashboard:

Monthly revenue per lot (bar chart).

Occupancy status (pie charts).

Reservation statistics.




📊 Dynamic Charts
Generated with Matplotlib and updated per selected month/year.

Stored and served from the static/ directory for efficient rendering.




TO RUN THE APPLICATION

STEP-1: DOWNLOAD THE APPLICATION ZIP FOLDER

STEP-2:  Prerequisite: Python 3.10+, Virtual Environment (optional)

STEP-3: pip install -r requirements.txt

STEP-4: Running the app:
	export FLASK_APP=run.py
	export FLASK_ENV=development   # optional: enables debug mode
	flask run

