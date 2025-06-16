import streamlit as st
import mysql.connector
import json  
import bookings  

def customer(customer_id):
    st.subheader("👤 Customer Portal")

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="project"
    )
    cursor = conn.cursor()

    cursor.execute("SELECT Station_id, Name FROM STATION")
    station_map = {station_id: name for station_id, name in cursor.fetchall()}

    cursor.execute("SELECT Name, Phone_no, Age FROM CUSTOMER WHERE Customer_id = %s", (customer_id,))
    name, phone_no, age = cursor.fetchone()

    cursor.execute("SELECT Password FROM LOGIN_INFO WHERE User_id = %s", (customer_id,))
    password = cursor.fetchone()[0]

    session_vars = ["train_results", "selected_train", "seat_type", "available_seats",
                    "source", "destination", "selected_seat_type"]
    defaults = [None, None, "AC", 0, "", "", "AC"]

    for var, default in zip(session_vars, defaults):
        if var not in st.session_state:
            st.session_state[var] = default

    # Option selection
    choice = st.selectbox("Choose an option:", ["Search & Book Train", "View All Trains & Stops", "View My Tickets", "Update Details"])

    # Option 1: Search & Book Train
    if choice == "Search & Book Train":
        st.subheader("🚆 Search Available Trains")

        # Use cached station names for dropdown
        station_options = {name: station_id for station_id, name in station_map.items()}
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

            # Update session state
            st.session_state.source = user_source
            st.session_state.destination = user_destination

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

            # Display train results and booking options
            if st.session_state.train_results:
                train_options = [f"{t[0]} - {t[1]}" for t in st.session_state.train_results]
                selected_train = st.selectbox("Select a train:", train_options, key="selected_train_option")

                # Update selected train
                train_no = selected_train.split(" - ")[0]
                if train_no != st.session_state.selected_train:
                    st.session_state.selected_train = train_no
                    st.session_state.available_seats = 0

                st.session_state.selected_seat_type = st.radio("Choose seat type:", ["AC", "SL", "UR"])

                # Fetch seat availability and stops
                seat_column = {
                    "AC": "Avail_AC_seats",
                    "SL": "Avail_SL_seats",
                    "UR": "Avail_UR_seats"
                }[st.session_state.selected_seat_type]

                cursor.execute(f"""
                    SELECT {seat_column}, Stops, Source_id, Destination_id 
                    FROM TRAIN 
                    WHERE Train_no = %s
                """, (st.session_state.selected_train,))
                result = cursor.fetchone()
                if result:
                    st.session_state.available_seats, stops_json, source_id, dest_id = result
                    stops_dict = json.loads(stops_json) if stops_json else {}

                    # Fetch timing information from STATION table
                    cursor.execute("SELECT Train_no FROM STATION WHERE Station_id = %s", (source_id,))
                    source_result = cursor.fetchone()
                    source_train_json = source_result[0] if source_result else None
                    source_train_dict = json.loads(source_train_json) if source_train_json else {}
                    source_time = source_train_dict.get(st.session_state.selected_train, "Not specified")
                    cursor.fetchall() 

                    cursor.execute("SELECT Train_no FROM STATION WHERE Station_id = %s", (dest_id,))
                    dest_result = cursor.fetchone()
                    dest_train_json = dest_result[0] if dest_result else None
                    dest_train_dict = json.loads(dest_train_json) if dest_train_json else {}
                    dest_time = dest_train_dict.get(st.session_state.selected_train, "Not specified")
                    cursor.fetchall()  

                    # Display route information 
                    st.markdown("### ⏳ Train Journey Timings")
                    
                    # Train's Source
                    source_name = station_map.get(source_id, "Unknown")
                    user_source_name = station_map.get(user_source, "Unknown")
                    user_dest_name = station_map.get(user_destination, "Unknown")
                    st.text(f"📍 {source_name} - Departure: {source_time}")

                    # All intermediate stops
                    for stop_id, stop_time in stops_dict.items():
                        stop_name = station_map.get(stop_id, "Unknown")
                        st.text(f"📍 {stop_name} - {stop_time}")

                    # Train's Destination 
                    dest_name = station_map.get(dest_id, "Unknown")
                    marker = " (Your Destination)" if dest_id == user_destination else ""
                    st.text(f"📍 {dest_name} - Arrival: {dest_time}{marker}")

                    # Display available seats
                    st.info(f"Available {st.session_state.selected_seat_type} seats: {st.session_state.available_seats}")

                    # Booking button
                    if st.session_state.available_seats > 0:
                        if st.button("Book Now"):
                            success, message = bookings.book_seat(
                                user_id=customer_id,
                                train_no=st.session_state.selected_train,
                                source_id=st.session_state.source,
                                destination_id=st.session_state.destination,
                                seat_type=st.session_state.selected_seat_type
                            )

                            if success:
                                st.success(message)
                                # Refresh available seats
                                cursor.execute(f"SELECT {seat_column} FROM TRAIN WHERE Train_no = %s", 
                                            (st.session_state.selected_train,))
                                st.session_state.available_seats = cursor.fetchone()[0]
                                cursor.fetchall()  # Clear any remaining results
                            else:
                                st.error(message)
                    else:
                        st.error("❌ No seats available for the selected type!")

    # Option 2: View All Trains & Stops
    elif choice == "View All Trains & Stops":
        st.subheader("🚆 All Available Trains & Stops")

        cursor.execute("SELECT Train_no, Name, Source_id, Destination_id, Stops FROM TRAIN")
        all_trains = cursor.fetchall()

        if not all_trains:
            st.warning("No trains available.")
        else:
            for train in all_trains:
                train_no, name, source_id, destination_id, stops_json = train

                # Fetch source and destination
                source_name = station_map.get(source_id, "Unknown")
                dest_name = station_map.get(destination_id, "Unknown")

                # Fetch source and destination timings
                cursor.execute("SELECT Train_no FROM STATION WHERE Station_id = %s", (source_id,))
                source_result = cursor.fetchone()
                source_train_json = source_result[0] if source_result else None
                source_train_dict = json.loads(source_train_json) if source_train_json else {}
                source_time = source_train_dict.get(train_no, "Not specified")
                cursor.fetchall() 

                cursor.execute("SELECT Train_no FROM STATION WHERE Station_id = %s", (destination_id,))
                dest_result = cursor.fetchone()
                dest_train_json = dest_result[0] if dest_result else None
                dest_train_dict = json.loads(dest_train_json) if dest_train_json else {}
                dest_time = dest_train_dict.get(train_no, "Not specified")
                cursor.fetchall()  

                # Parse stop timings and fetch stop names
                if stops_json:
                    stop_timings = json.loads(stops_json)
                    stop_details = []
                    for stop_id, time in stop_timings.items():
                        stop_name = station_map.get(stop_id, "Unknown")
                        stop_details.append(f"📍 {stop_name} - {time}")
                    stop_details_text = "\n".join(stop_details)
                else:
                    stop_details_text = "No intermediate stops available."

                # Display train details
                with st.expander(f"🚆 {train_no} - {name} ({source_name} → {dest_name})"):
                    st.text(f"Source: {source_name}")
                    st.text(f"Destination: {dest_name}")
                    st.markdown("### ⏳ Train Journey Timings")
                    st.text(f"📍 {source_name} - Departure: {source_time}")
                    st.text(stop_details_text)
                    st.text(f"📍 {dest_name} - Arrival: {dest_time}")

    # Option 3: View My Tickets
    elif choice == "View My Tickets":
        st.subheader("🎟️ My Booked Tickets")

        # Query the BOOKING table for tickets booked by this customer
        cursor.execute(
            """
            SELECT b.Booking_id, b.Train_no, t.Name, b.Passenger_name, b.Source_id, b.Destination_id, b.Seat_no
            FROM BOOKING b
            JOIN TRAIN t ON b.Train_no = t.Train_no
            WHERE b.User_id = %s
            """,
            (customer_id,)
        )
        tickets = cursor.fetchall()

        if not tickets:
            st.warning("You have not booked any tickets yet.")
        else:
            for ticket in tickets:
                booking_id, train_no, train_name, passenger_name, source_id, destination_id, seat_no = ticket
                
                # Fetch source and destination names 
                source_name = station_map.get(source_id, "Unknown")
                dest_name = station_map.get(destination_id, "Unknown")

                with st.expander(f"🎟️ Ticket ID: {booking_id} - {train_name} ({train_no})"):
                    st.text(f"Passenger Name: {passenger_name}")
                    st.text(f"Source: {source_name}")
                    st.text(f"Destination: {dest_name}")
                    st.text(f"Seat: {seat_no}")

    # Option 4: Update Customer Details
    elif choice == "Update Details":
        st.subheader("Update Your Details")
        new_password = st.text_input("Enter new password:", type="password", value=password)
        new_name = st.text_input("Enter new name:", value=name)
        new_phone = st.text_input("Enter new phone number:", value=phone_no)
        new_age = st.number_input("Age", min_value=18, max_value=120, step=1, format="%d", value=age)

        if st.button("Update Details"):
            cursor.execute("UPDATE CUSTOMER SET Name = %s WHERE Customer_id = %s", (new_name, customer_id))
            cursor.execute("UPDATE CUSTOMER SET Phone_no = %s WHERE Customer_id = %s", (new_phone, customer_id))
            cursor.execute("UPDATE CUSTOMER SET Age = %s WHERE Customer_id = %s", (new_age, customer_id))
            cursor.execute("UPDATE LOGIN_INFO SET Password = %s WHERE User_id = %s", (new_password, customer_id))
            
            conn.commit()
            st.success("✅ Details updated successfully!")

    cursor.close()
    conn.close()