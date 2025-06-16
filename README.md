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

- Ensure MySQL Server is installed and running on your system or a remote server.
- Use the provided create_database.sql script to create the project database and tables:
```bash
mysql -u root -p
SOURCE create_database.sql;

CREATE DATABASE IF NOT EXISTS project;
USE project;

CREATE TABLE login_info (
    user_id VARCHAR(30) NOT NULL,
    password VARCHAR(15),
    PRIMARY KEY (user_id)
);

CREATE TABLE customer (
    Customer_id VARCHAR(20) NOT NULL,
    Name VARCHAR(30) NOT NULL,
    Phone_no VARCHAR(11) NOT NULL,
    Age INT NOT NULL,
    PRIMARY KEY (Customer_id),
    UNIQUE (Phone_no)
);

CREATE TABLE staff (
    Staff_id VARCHAR(20) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Age INT,
    Phone_no VARCHAR(15),
    Address VARCHAR(255),
    Role VARCHAR(50) NOT NULL,
    Shift VARCHAR(20),
    Salary FLOAT,
    PRIMARY KEY (Staff_id),
    UNIQUE (Phone_no)
);

CREATE TABLE station (
    Station_id VARCHAR(50) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Train_no JSON,
    Station_master_id VARCHAR(50),
    PRIMARY KEY (Station_id)
);

CREATE TABLE train (
    Train_no VARCHAR(255) NOT NULL,
    Name VARCHAR(255) NOT NULL,
    Locopilot_id VARCHAR(255),
    TTE_id VARCHAR(255),
    Source_id VARCHAR(255),
    Destination_id VARCHAR(255),
    Avail_AC_seats INT DEFAULT 0,
    Avail_SL_seats INT DEFAULT 0,
    Avail_UR_seats INT DEFAULT 0,
    Stops JSON,
    PRIMARY KEY (Train_no)
);

CREATE TABLE booking (
    Booking_id VARCHAR(10) NOT NULL,
    User_id VARCHAR(10),
    Train_no VARCHAR(10),
    Seat_no VARCHAR(5),
    Passenger_name VARCHAR(50),
    Source_id VARCHAR(10),
    Destination_id VARCHAR(10),
    Passenger_age INT,
    PRIMARY KEY (Booking_id)
);

INSERT INTO login_info (user_id, password) VALUES
    ('admin', 'adminpass'),
    ('cust1', 'custpass'),
    ('staff1', 'staffpass');

INSERT INTO customer (Customer_id, Name, Phone_no, Age) VALUES
    ('cust1', 'John Doe', '1234567890', 25);

INSERT INTO staff (Staff_id, Name, Age, Phone_no, Address, Role, Shift, Salary) VALUES
    ('staff1', 'Jane Smith', 30, '0987654321', '123 Main St', 'Manager', 'Day', 50000.00);

INSERT INTO station (Station_id, Name, Train_no, Station_master_id) VALUES
    ('S001', 'Central Station', '{"T001"}', 'SM001');

INSERT INTO train (Train_no, Name, Locopilot_id, TTE_id, Source_id, Destination_id, Avail_AC_seats, Avail_SL_seats, Avail_UR_seats, Stops) VALUES
    ('T001', 'Express Train', 'L001', 'TTE001', 'S001', 'S002', 50, 100, 50, '{"S003", "S004"}');

INSERT INTO booking (Booking_id, User_id, Train_no, Seat_no, Passenger_name, Source_id, Destination_id, Passenger_age) VALUES
    ('B001', 'cust1', 'T001', 'A01', 'John Doe', 'S001', 'S002', 25);
```
- Change this in all the files
```bash
    conn = mysql.connector.connect(
    host="your-server-ip",  # e.g., "192.168.1.100" for remote access
    user="remote_user",
    password="secure_password",
    database="project"
```
- For remote access, ensure the MySQL server’s bind-address is set to 0.0.0.0 in my.ini (e.g., C:\ProgramData\MySQL\MySQL Server 8.0\my.ini) and port 3306 is open in your firewall.

### 4. Run the Application

- Start the Streamlit app locally:
```bash
streamlit run app.py
```
- Open your browser and navigate to http://localhost:8501 (local)

## Usage

1. Login: Use the login page to access the app with an existing user_id and password from the login_info table.
2. Sign Up: Create a new customer account with a unique Customer_id, password, Name, Phone_no, and Age, which will be added to the customer and login_info tables.
3. Navigation: After logging in, use the sidebar to navigate between customer, staff, or admin pages (based on your role).
4. Booking Progress: On the customer page, enter a Train_no to view the booking progress with a green-white-orange gradient progress bar, calculated from the booking and train tables.

## Configuration

- Database Credentials: Update the host, user, password, and database in app.py to match your MySQL setup.
- Firewall: Ensure ports 3306 (MySQL) and 8501 (Streamlit) are open if using remote access.
- Security: For internet access, enable SSL in MySQL (my.ini) and update the app to use SSL

## Acknowledgements

- Built with Streamlit for the frontend.
- Powered by MySQL for data management.
- Gradient progress bar inspired by user customization requests.
- Last updated: 01:06 PM +04, Monday, June 16, 2025
