# Railway Reservation System

Welcome to the Railway Reservation System, a Streamlit-based application for managing customer accounts, staff operations, train bookings, and station details. This app allows users to log in, sign up, and view booking progress with a custom green-white-orange gradient progress bar. The app connects to a MySQL database for data persistence.

## Features
- User authentication (login and signup for customers, staff, and admin).
- Role-based navigation (customer, staff, and admin pages).
- Real-time booking progress visualization with a custom gradient progress bar.
- Management of train schedules, station details, and bookings.

## Prerequisites
- Python 3.7 or higher
- Git (for cloning the repository)
- MySQL Server 8.0 or higher
- A code editor (e.g., VS Code, PyCharm)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/anaykrishna/Railway-Management-System.git
cd Railway-Management-System
```
###2. Install Dependencies

Install the required Python packages using pip:
```bash
pip install -r requirements.txt
```

###  3. Set Up the MySQL Database

    Ensure MySQL Server is installed and running on your system or a remote server.
    Use the provided create_database.sql script to create the project database and tables:
        Open MySQL (e.g., via MySQL Workbench or command line):
