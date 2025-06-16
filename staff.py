import streamlit as st
import mysql.connector
import json
import uuid 

def staff(staff_id):
    st.subheader("👷 Staff Portal")

    # Connect to MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="project"
    )
    cursor = conn.cursor()

    # Staff Details
    cursor.execute("SELECT * FROM STAFF WHERE Staff_id = %s", (staff_id,))
    staff_details = cursor.fetchone()

    if not staff_details:
        st.error("❌ Staff ID not found!")
        return

    staff_id, name, age, phone, address, role, shift, salary = staff_details

    cursor.execute("SELECT Password FROM LOGIN_INFO WHERE User_id = %s", (staff_id,))
    password = cursor.fetchone()[0]

    # Menu Selection - Conditional options based on role
    if role == "Ticketer":
        choice = st.selectbox("Choose an option:", 
                            ["Manage Profile", 
                             "Book Ticket for Non-Registered User", 
                             "View All Trains & Stops"])
    else:
        choice = st.selectbox("Choose an option:", 
                            ["Manage Profile", 
                             "View All Trains & Stops"])

    # Option 1: Manage Profile
    if choice == "Manage Profile":
        st.subheader("✏️ Update Your Details")
        new_password = st.text_input("Password", type="password", key="password", value=password)
        new_name = st.text_input("Name", value=name)
        new_age = st.number_input("Age", min_value=18, max_value=100, value=age)
        new_phone = st.text_input("Phone Number", value=phone)
        new_address = st.text_area("Address", value=address)

        if st.button("✅ Update Details"):
            cursor.execute(
                "UPDATE STAFF SET Name=%s, Age=%s, Phone_no=%s, Address=%s WHERE Staff_id=%s",
                (new_name, new_age, new_phone, new_address, staff_id)
            )
            cursor.execute(
                "UPDATE LOGIN_INFO SET Password=%s WHERE User_id=%s",
                (new_password, staff_id)
            )
            conn.commit()
            st.success("✅ Your details have been updated!")

        # Display assigned trains for staff who are not Ticketer or Station Master
        if role not in ["Ticketer", "Station Master"]:
            st.markdown("### 🚆 Assigned Trains (Read-Only)")
            cursor.execute("""
                SELECT Train_no, Name, Source_id, Destination_id
                FROM TRAIN
                WHERE Locopilot_id = %s OR TTE_id = %s
            """, (staff_id, staff_id))
            assigned_trains = cursor.fetchall()

            if not assigned_trains:
                st.info("No trains assigned to you.")
            else:
                for train in assigned_trains:
                    train_no, train_name, source_id, dest_id = train
                    cursor.execute("SELECT Name FROM STATION WHERE Station_id = %s", (source_id,))
                    source_result = cursor.fetchone()
                    source_name = source_result[0] if source_result else "Unknown"
                    cursor.fetchall() 

                    # Fetch destination name
                    cursor.execute("SELECT Name FROM STATION WHERE Station_id = %s", (dest_id,))
                    dest_result = cursor.fetchone()
                    dest_name = dest_result[0] if dest_result else "Unknown"
                    cursor.fetchall()  

                    st.write(f"**Train No:** {train_no} | **Name:** {train_name} | **Route:** {source_name} → {dest_name}")

    # Option 2: Book Ticket for Non-Registered User (Only for Ticketer)
    elif choice == "Book Ticket for Non-Registered User" and role == "Ticketer":
        st.subheader("🎫 Book Ticket for Non-Registered User")

        # Collect passenger details
        user_name = st.text_input("Passenger Name")
        user_age = st.number_input("Passenger Age", min_value=1, max_value=120)
        user_phone = st.text_input("Passenger Phone Number")  # Note: This won't be stored in BOOKING table

        # Fetch all stations for dropdown
        cursor.execute("SELECT Station_id, Name FROM STATION")
        stations = cursor.fetchall()
        station_options = {name: station_id for station_id, name in stations}
        station_names = list(station_options.keys())

        if not station_names:
            st.error("No stations available in the system.")
        else:
            # Select source station
            source_name = st.selectbox("Select Source Station:", options=station_names, key="source_station")
            user_source = station_options[source_name] if source_name else ""

            # Select destination station
            dest_name = st.selectbox("Select Destination Station:", options=station_names, key="dest_station")
            user_destination = station_options[dest_name] if dest_name else ""

            # Initialize session state variables if not already set
            if "train_results" not in st.session_state:
                st.session_state.train_results = None
            if "selected_train" not in st.session_state:
                st.session_state.selected_train = None
            if "selected_seat_type" not in st.session_state:
                st.session_state.selected_seat_type = "AC"
            if "available_seats" not in st.session_state:
                st.session_state.available_seats = 0

            # Search for trains
            if st.button("Search Trains"):
                if not user_source or not user_destination:
                    st.error("Please select both source and destination stations.")
                elif user_source == user_destination:
                    st.error("Source and destination stations cannot be the same.")
                else:
                    cursor.execute("""
                        SELECT Train_no, Name, Source_id, Destination_id, Stops, 
                               Avail_AC_seats, Avail_SL_seats, Avail_UR_seats 
                        FROM TRAIN
                    """)
                    all_trains = cursor.fetchall()
                    matching_trains = []

                    for train in all_trains:
                        train_no, name, source, destination, stops_json, ac_seats, sl_seats, ur_seats = train
                        stops_dict = json.loads(stops_json) if stops_json else {}
                        stops_list = list(stops_dict.keys())

                        # Check if source and destination are in the route
                        all_stops = [source] + stops_list + [destination]
                        try:
                            source_idx = all_stops.index(user_source)
                            dest_idx = all_stops.index(user_destination)
                            if source_idx < dest_idx:  # Validate source comes before destination
                                matching_trains.append((train_no, name, ac_seats, sl_seats, ur_seats))
                        except ValueError:
                            continue

                    if matching_trains:
                        st.session_state.train_results = matching_trains
                        st.success(f"Found {len(matching_trains)} matching trains!")
                    else:
                        st.error("❌ No trains found for this route!")
                        st.session_state.train_results = None

            # If trains are found, show selection
            if st.session_state.train_results:
                train_options = [f"{t[0]} - {t[1]}" for t in st.session_state.train_results]
                selected_train = st.selectbox("Select a train:", train_options, key="selected_train_option")

                # Update selected train
                train_no = selected_train.split(" - ")[0]
                if train_no != st.session_state.selected_train:
                    st.session_state.selected_train = train_no
                    st.session_state.available_seats = 0

                # Select seat type
                seat_type_map = {"AC": "AC", "Sleeper": "SL", "General": "UR"}
                st.session_state.selected_seat_type = st.radio("Choose seat type:", ["AC", "Sleeper", "General"])
                seat_column = {
                    "AC": "Avail_AC_seats",
                    "Sleeper": "Avail_SL_seats",
                    "General": "Avail_UR_seats"
                }[st.session_state.selected_seat_type]
                seat_prefix = seat_type_map[st.session_state.selected_seat_type]

                # Fetch seat availability and route details
                cursor.execute(f"""
                    SELECT {seat_column}, Stops, Source_id, Destination_id 
                    FROM TRAIN 
                    WHERE Train_no = %s
                """, (st.session_state.selected_train,))
                result = cursor.fetchone()
                if result:
                    st.session_state.available_seats, stops_json, source_id, dest_id = result
                    stops_dict = json.loads(stops_json) if stops_json else {}

                    # Fetch timing information
                    cursor.execute("SELECT Train_no FROM STATION WHERE Station_id = %s", (source_id,))
                    source_train_json = cursor.fetchone()[0]
                    source_train_dict = json.loads(source_train_json) if source_train_json else {}
                    source_time = source_train_dict.get(st.session_state.selected_train, "Not specified")

                    cursor.execute("SELECT Train_no FROM STATION WHERE Station_id = %s", (dest_id,))
                    dest_train_json = cursor.fetchone()[0]
                    dest_train_dict = json.loads(dest_train_json) if dest_train_json else {}
                    dest_time = dest_train_dict.get(st.session_state.selected_train, "Not specified")

                    # Display route information
                    st.markdown("### ⏳ Train Journey Timings")
                    cursor.execute("SELECT Name FROM STATION WHERE Station_id = %s", (source_id,))
                    source_name = cursor.fetchone()[0]
                    st.text(f"📍 {source_name} - Departure: {source_time}")

                    for stop_id, time in stops_dict.items():
                        cursor.execute("SELECT Name FROM STATION WHERE Station_id = %s", (stop_id,))
                        stop_name = cursor.fetchone()[0]
                        st.text(f"📍 {stop_name} - {time}")

                    cursor.execute("SELECT Name FROM STATION WHERE Station_id = %s", (dest_id,))
                    dest_name = cursor.fetchone()[0]
                    st.text(f"📍 {dest_name} - Arrival: {dest_time}")

                    # Display available seats
                    st.info(f"Available {st.session_state.selected_seat_type} seats: {st.session_state.available_seats}")

                    # Booking button
                    if st.session_state.available_seats > 0:
                        if st.button("📌 Book Ticket"):
                            if user_name and user_age and user_source and user_destination:
                                # Generate seat number
                                cursor.execute(f"SELECT COUNT(*) FROM BOOKING WHERE Train_no = %s AND Seat_no LIKE '{seat_prefix}%'", 
                                            (st.session_state.selected_train,))
                                booked_seats = cursor.fetchone()[0]
                                seat_no = f"{seat_prefix}{booked_seats + 1}"

                                # Generate a unique Booking_id
                                booking_id = str(uuid.uuid4())[:10]

                                # Insert booking into BOOKING table
                                cursor.execute(
                                    """
                                    INSERT INTO BOOKING (Booking_id, User_id, Train_no, Seat_no, Passenger_name, Source_id, Destination_id, Passenger_age) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    """,
                                    (booking_id, "s000", st.session_state.selected_train, seat_no, user_name, user_source, user_destination, user_age)
                                )

                                # Update seat availability
                                cursor.execute(
                                    f"UPDATE TRAIN SET {seat_column} = {seat_column} - 1 WHERE Train_no = %s",
                                    (st.session_state.selected_train,)
                                )
                                conn.commit()

                                # Update available seats in session state
                                cursor.execute(f"SELECT {seat_column} FROM TRAIN WHERE Train_no = %s", 
                                            (st.session_state.selected_train,))
                                st.session_state.available_seats = cursor.fetchone()[0]

                                st.success(f"✅ Ticket booked for {user_name}! Booking ID: {booking_id}, Seat: {seat_no}")
                            else:
                                st.error("❌ Please fill in all required details (Name, Age, Source, Destination).")
                    else:
                        st.error("❌ No seats available for the selected type!")

    # Option 3: View All Trains & Stops
    elif choice == "View All Trains & Stops":
        st.subheader("🚆 All Available Trains & Stops")

        # Fetch additional details including seat availability
        cursor.execute("""
            SELECT Train_no, Name, Source_id, Destination_id, Stops, 
                   Avail_AC_seats, Avail_SL_seats, Avail_UR_seats 
            FROM TRAIN
        """)
        all_trains = cursor.fetchall()

        if not all_trains:
            st.warning("No trains available.")
        else:
            for train in all_trains:
                train_no, name, source, destination, stops_json, ac_seats, sl_seats, ur_seats = train
                stops_dict = json.loads(stops_json) if stops_json else {}

                # Fetch station names
                cursor.execute("SELECT Name FROM STATION WHERE Station_id = %s", (source,))
                source_name = cursor.fetchone()[0]
                cursor.execute("SELECT Name FROM STATION WHERE Station_id = %s", (destination,))
                dest_name = cursor.fetchone()[0]

                # Display train details 
                with st.expander(f"🚆 {train_no} - {name} ({source_name} → {dest_name})"):
                    cursor.execute("SELECT Train_no FROM STATION WHERE Station_id = %s", (source,))
                    source_train_json = cursor.fetchone()[0]
                    source_train_dict = json.loads(source_train_json) if source_train_json else {}
                    source_time = source_train_dict.get(train_no, "Not specified")

                    cursor.execute("SELECT Train_no FROM STATION WHERE Station_id = %s", (destination,))
                    dest_train_json = cursor.fetchone()[0]
                    dest_train_dict = json.loads(dest_train_json) if dest_train_json else {}
                    dest_time = dest_train_dict.get(train_no, "Not specified")

                    st.write(f"**Source:** {source_name} - Departure: {source_time}")
                    st.markdown("### ⏳ Intermediate Stops")
                    if stops_dict:
                        for stop_id, time in stops_dict.items():
                            cursor.execute("SELECT Name FROM STATION WHERE Station_id = %s", (stop_id,))
                            stop_name = cursor.fetchone()[0]
                            st.text(f"📍 {stop_name} - {time}")
                    else:
                        st.text("No intermediate stops")
                    st.write(f"**Destination:** {dest_name} - Arrival: {dest_time}")
                    st.write(f"**Available Seats:** AC: {ac_seats}, Sleeper: {sl_seats}, General: {ur_seats}")

    cursor.close()
    conn.close()