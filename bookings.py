import random
import string
import mysql.connector

def generate_random_id(length=8):
    """Generate a random alphanumeric Booking ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_available_seat(cursor, train_no, seat_type):
    """Fetch an available seat number from the TRAIN table with seat type prefix."""
    seat_column = {
        "AC": "Avail_AC_seats",
        "SL": "Avail_SL_seats",
        "UR": "Avail_UR_seats"
    }[seat_type]

    # Fetch available seats count
    cursor.execute(f"SELECT {seat_column} FROM TRAIN WHERE Train_no = %s", (train_no,))
    available_seats = cursor.fetchone()

    if available_seats and available_seats[0] > 0:
        seat_no = str(random.randint(1, available_seats[0]))  # Random seat number
        return f"{seat_type}{seat_no}"  # Prefix seat type (e.g., AC12, SL5, UR8)
    
    return None

def book_seat(user_id, train_no, source_id, destination_id, seat_type):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="project"
    )
    cursor = conn.cursor()

    # Generate random Booking ID
    booking_id = generate_random_id()

    # Fetch user details
    cursor.execute("SELECT Name, Age FROM CUSTOMER WHERE Customer_id = %s", (user_id,))
    result = cursor.fetchone()
    if not result:
        cursor.close()
        conn.close()
        return False, "❌ User not found!"

    passenger_name, passenger_age = result

    # Validate seat type
    seat_no = get_available_seat(cursor, train_no, seat_type)
    if not seat_no:
        cursor.close()
        conn.close()
        return False, "❌ No seats available!"

    try:
        # Insert booking into BOOKING table
        cursor.execute("""
            INSERT INTO BOOKING (Booking_id, User_id, Train_no, Seat_no, Passenger_name, Source_id, Destination_id, Passenger_age)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (booking_id, user_id, train_no, seat_no, passenger_name, source_id, destination_id, passenger_age))

        seat_column = {
            "AC": "Avail_AC_seats",
            "SL": "Avail_SL_seats",
            "UR": "Avail_UR_seats"
        }[seat_type]
        cursor.execute(f"UPDATE TRAIN SET {seat_column} = {seat_column} - 1 WHERE Train_no = %s", (train_no,))

        conn.commit()
        message = f"✅ Booking Successful! Booking ID: {booking_id}, Seat No: {seat_no}"
        success = True

    except Exception as e:
        conn.rollback()  
        message = f"❌ Booking failed: {e}"
        success = False

    cursor.close()
    conn.close()
    return success, message  # Return status and message
