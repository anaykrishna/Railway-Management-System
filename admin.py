import streamlit as st
import mysql.connector
import json

def admin():
    st.subheader("🛠️ Admin Portal")

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="project"
    )
    cursor = conn.cursor()

    # Admin options
    choice = st.selectbox("Choose an option:", ["Manage Users", "Manage Trains", "Manage Staff", "Manage Stations", "View Reports"])

    # Option 1: Manage Users
    if choice == "Manage Users":
        st.subheader("👥 Manage Users")
        cursor.execute("SELECT Customer_id, Name, Phone_no, Age FROM CUSTOMER")
        users = cursor.fetchall()

        if not users:
            st.warning("No users found.")
        else:
            for user in users:
                user_id, name, phone, age = user
                with st.expander(f"👤 {name} (ID: {user_id})"):
                    st.text(f"📞 Phone: {phone}")
                    st.text(f"🎂 Age: {age}")

                    if st.button(f"❌ Delete {name}", key=f"delete_{user_id}"):
                        cursor.execute("DELETE FROM BOOKING WHERE User_id = %s", (user_id,))
                        cursor.execute("DELETE FROM LOGIN_INFO WHERE User_id = %s", (user_id,))
                        cursor.execute("DELETE FROM CUSTOMER WHERE Customer_id = %s", (user_id,))
                        conn.commit()
                        st.success(f"✅ User {name} deleted!")

    # Option 2: Manage Trains
    elif choice == "Manage Trains":
        st.subheader("🚆 Manage Trains")
        action = st.selectbox("Select Action:", ["Add New Train", "Update Existing Train"])

        # Fetch all stations for mapping and selection
        cursor.execute("SELECT Station_id, Name FROM STATION")
        stations = cursor.fetchall()
        station_map = {station_id: name for station_id, name in stations}  
        station_options = {name: station_id for station_id, name in stations} 
        station_names = list(station_options.keys())

        if action == "Update Existing Train":
            cursor.execute("SELECT Train_no, Name, Source_id, Destination_id, Avail_AC_seats, Avail_SL_seats, Avail_UR_seats, Locopilot_id, TTE_id FROM TRAIN")
            trains = cursor.fetchall()

            if not trains:
                st.warning("No trains available.")
            else:
                # Locopilots and TTEs for selection
                cursor.execute("SELECT Staff_id, Name FROM STAFF WHERE Role = 'Locopilot'")
                locopilots = cursor.fetchall()
                locopilot_options = {f"{name} (ID: {staff_id})": staff_id for staff_id, name in locopilots}
                locopilot_options["None"] = None  

                cursor.execute("SELECT Staff_id, Name FROM STAFF WHERE Role = 'TTE'")
                ttes = cursor.fetchall()
                tte_options = {f"{name} (ID: {staff_id})": staff_id for staff_id, name in ttes}
                tte_options["None"] = None 

                for train in trains:
                    train_no, name, source_id, destination_id, ac_seats, sl_seats, ur_seats, locopilot_id, tte_id = train
                    source_name = station_map.get(source_id, "Unknown")
                    dest_name = station_map.get(destination_id, "Unknown")

                    with st.expander(f"🚆 {train_no} - {name} ({source_name} → {dest_name})"):
                        new_name = st.text_input(f"Edit Name ({name})", value=name, key=f"name_{train_no}")

                        # Selection box for Source
                        new_source_name = st.selectbox(
                            f"Edit Source ({source_name})",
                            options=station_names,
                            index=station_names.index(source_name) if source_name in station_names else 0,
                            key=f"source_{train_no}"
                        )
                        new_source = station_options[new_source_name] if new_source_name else source_id

                        # Selection box for Destination
                        new_dest_name = st.selectbox(
                            f"Edit Destination ({dest_name})",
                            options=station_names,
                            index=station_names.index(dest_name) if dest_name in station_names else 0,
                            key=f"dest_{train_no}"
                        )
                        new_destination = station_options[new_dest_name] if new_dest_name else destination_id

                        new_ac_seats = st.number_input(f"AC Seats ({ac_seats})", min_value=0, value=ac_seats, key=f"ac_{train_no}")
                        new_sl_seats = st.number_input(f"SL Seats ({sl_seats})", min_value=0, value=sl_seats, key=f"sl_{train_no}")
                        new_ur_seats = st.number_input(f"UR Seats ({ur_seats})", min_value=0, value=ur_seats, key=f"ur_{train_no}")

                        # Display current Locopilot and TTE
                        current_locopilot = locopilot_id if locopilot_id else "None"
                        current_tte = tte_id if tte_id else "None"
                        
                        # Selection box for Locopilot
                        selected_locopilot = st.selectbox(
                            f"Assign Locopilot (Current: {current_locopilot})",
                            options=list(locopilot_options.keys()),
                            index=list(locopilot_options.values()).index(locopilot_id) if locopilot_id in locopilot_options.values() else 0,
                            key=f"locopilot_{train_no}"
                        )
                        new_locopilot_id = locopilot_options[selected_locopilot]

                        # Selection box for TTE
                        selected_tte = st.selectbox(
                            f"Assign TTE (Current: {current_tte})",
                            options=list(tte_options.keys()),
                            index=list(tte_options.values()).index(tte_id) if tte_id in tte_options.values() else 0,
                            key=f"tte_{train_no}"
                        )
                        new_tte_id = tte_options[selected_tte]

                        if st.button(f"✅ Update {name}", key=f"update_{train_no}"):
                            cursor.execute(
                                """UPDATE TRAIN 
                                SET Name=%s, Source_id=%s, Destination_id=%s, Avail_AC_seats=%s, 
                                Avail_SL_seats=%s, Avail_UR_seats=%s, Locopilot_id=%s, TTE_id=%s 
                                WHERE Train_no=%s""",
                                (new_name, new_source, new_destination, new_ac_seats, new_sl_seats, new_ur_seats, new_locopilot_id, new_tte_id, train_no)
                            )
                            conn.commit()
                            st.success(f"✅ Train {train_no} updated!")

                        if st.button(f"❌ Delete {name}", key=f"delete_{train_no}"):
                            cursor.execute("SELECT Station_id, Train_no FROM STATION")
                            stations = cursor.fetchall()
                            for station in stations:
                                station_id, train_json = station
                                if train_json:
                                    train_dict = json.loads(train_json)
                                    if train_no in train_dict:
                                        del train_dict[train_no]
                                        new_train_json = json.dumps(train_dict)
                                        cursor.execute(
                                            "UPDATE STATION SET Train_no = %s WHERE Station_id = %s",
                                            (new_train_json, station_id)
                                        )
                            cursor.execute("DELETE FROM TRAIN WHERE Train_no = %s", (train_no,))
                            conn.commit()
                            st.success(f"✅ Train {name} deleted!")

        elif action == "Add New Train":
            st.subheader("➕ Add New Train")
            new_train_no = st.text_input("Enter Train No (Unique):")
            new_train_name = st.text_input("Enter Train Name:")
            
            if not station_names:
                st.error("No stations available. Please add stations first.")
            else:
                # Select source station
                new_source_name = st.selectbox("Select Source Station:", options=station_names, key="source_station")
                new_source = station_options[new_source_name] if new_source_name else None

                # Select destination station
                new_destination_name = st.selectbox("Select Destination Station:", options=station_names, key="dest_station")
                new_destination = station_options[new_destination_name] if new_destination_name else None

                new_ac_seats = st.number_input("Enter AC Seats:", min_value=0)
                new_sl_seats = st.number_input("Enter SL Seats:", min_value=0)
                new_ur_seats = st.number_input("Enter UR Seats:", min_value=0)
                new_max_seats = new_ac_seats + new_sl_seats + new_ur_seats

                # Locopilots and TTEs for selection
                cursor.execute("SELECT Staff_id, Name FROM STAFF WHERE Role = 'Locopilot'")
                locopilots = cursor.fetchall()
                locopilot_options = {f"{name} (ID: {staff_id})": staff_id for staff_id, name in locopilots}
                locopilot_options["None"] = None  

                cursor.execute("SELECT Staff_id, Name FROM STAFF WHERE Role = 'TTE'")
                ttes = cursor.fetchall()
                tte_options = {f"{name} (ID: {staff_id})": staff_id for staff_id, name in ttes}
                tte_options["None"] = None  

                # Selection box for Locopilot
                selected_locopilot = st.selectbox(
                    "Assign Locopilot:",
                    options=list(locopilot_options.keys()),
                    key="new_locopilot"
                )
                new_locopilot_id = locopilot_options[selected_locopilot]

                # Selection box for TTE
                selected_tte = st.selectbox(
                    "Assign TTE:",
                    options=list(tte_options.keys()),
                    key="new_tte"
                )
                new_tte_id = tte_options[selected_tte]

                st.subheader("🚉 Add Route for the Train")
                route = {}  # Dictionary to store the full route (Station_id: arrival_time), including source and destination
                stops = {}  # Dictionary to store intermediate stops only (Station_id: arrival_time)

                # Add source time
                source_time = st.text_input("Enter Departure Time from Source (HH:MM AM/PM):", key="source_time")
                if new_source and source_time:
                    route[new_source] = source_time

                # Add intermediate stops
                stop_count = st.number_input("Number of Intermediate Stops (excluding Source and Destination):", min_value=0, step=1)
                for i in range(int(stop_count)):
                    st.write(f"### Stop {i+1}")
                    stop_name = st.selectbox(f"Select Station for Stop {i+1}:", options=station_names, key=f"stop_name_{i}")
                    arrival_time = st.text_input(f"Arrival Time for Stop {i+1} (HH:MM AM/PM):", key=f"arrival_{i}")
                    if stop_name and arrival_time:
                        stop_id = station_options[stop_name]
                        stops[stop_id] = arrival_time
                        route[stop_id] = arrival_time

                # Add destination time
                destination_time = st.text_input("Enter Arrival Time at Destination (HH:MM AM/PM):", key="dest_time")
                if new_destination and destination_time:
                    route[new_destination] = destination_time

                if st.button("Add Train"):
                    if all([new_train_no, new_train_name, new_source, new_destination, new_max_seats, source_time, destination_time]):
                        if new_source == new_destination:
                            st.error("Source and destination stations cannot be the same.")
                        else:
                            invalid_stops = [stop_id for stop_id in stops.keys() if stop_id in (new_source, new_destination)]
                            if invalid_stops:
                                invalid_stop_names = [name for name, sid in station_options.items() if sid in invalid_stops]
                                st.error(f"Intermediate stops cannot include source or destination stations: {', '.join(invalid_stop_names)}")
                            else:
                                stops_json = json.dumps(stops) 

                                # Insert the new train into the TRAIN table
                                cursor.execute(
                                    """INSERT INTO TRAIN 
                                    (Train_no, Name, Source_id, Destination_id, Max_seats, Avail_AC_seats, 
                                    Avail_SL_seats, Avail_UR_seats, Stops, Locopilot_id, TTE_id) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                    (new_train_no, new_train_name, new_source, new_destination, new_max_seats, 
                                    new_ac_seats, new_sl_seats, new_ur_seats, stops_json, new_locopilot_id, new_tte_id)
                                )

                                # Update the STATION table: Append the new train and its time to the Train_no JSON field
                                for station_id, arrival_time in route.items():
                                    cursor.execute("SELECT Train_no FROM STATION WHERE Station_id = %s", (station_id,))
                                    result = cursor.fetchone()
                                    train_dict = json.loads(result[0]) if result and result[0] else {}

                                    train_dict[new_train_no] = arrival_time

                                    new_train_json = json.dumps(train_dict)
                                    cursor.execute(
                                        "UPDATE STATION SET Train_no = %s WHERE Station_id = %s",
                                        (new_train_json, station_id)
                                    )

                                conn.commit()
                                st.success(f"✅ New train {new_train_name} added and linked to stations!")
                    else:
                        st.error("Please fill in all required fields!")
                else:
                    st.warning("Please select source and destination stations.")

    # Option 3: Manage Staff
    elif choice == "Manage Staff":
        st.subheader("👷 Manage Staff")
        action = st.selectbox("Select Action:", ["Add New Staff", "Update or Delete Staff"])

        if action == "Update or Delete Staff":
            cursor.execute("SELECT Staff_id, Name, Age, Phone_no, Address, Role, Shift, Salary FROM STAFF")
            staff_members = cursor.fetchall()

            if not staff_members:
                st.warning("No staff members found.")
            else:
                for staff in staff_members:
                    staff_id, name, age, phone, address, role, shift, salary = staff
                    with st.expander(f"👷 {name} (ID: {staff_id})"):
                        new_name = st.text_input(f"Edit Name ({name})", value=name, key=f"staff_name_{staff_id}")
                        new_age = st.number_input(f"Edit Age ({age})", min_value=18, max_value=80, value=age, key=f"staff_age_{staff_id}")
                        new_phone = st.text_input(f"Edit Phone No ({phone})", value=phone, key=f"staff_phone_{staff_id}")
                        new_address = st.text_input(f"Edit Address ({address})", value=address, key=f"staff_address_{staff_id}")
                        new_role = st.text_input(f"Edit Role ({role})", value=role, key=f"staff_role_{staff_id}")
                        new_shift = st.text_input(f"Edit Shift ({shift})", value=shift, key=f"staff_shift_{staff_id}")
                        new_salary = st.number_input(f"Edit Salary ({salary})", min_value=0.0, value=salary, key=f"staff_salary_{staff_id}")

                        if st.button(f"✅ Update {name}", key=f"update_staff_{staff_id}"):
                            cursor.execute(
                                "UPDATE STAFF SET Name=%s, Age=%s, Phone_no=%s, Address=%s, Role=%s, Shift=%s, Salary=%s WHERE Staff_id=%s",
                                (new_name, new_age, new_phone, new_address, new_role, new_shift, new_salary, staff_id)
                            )
                            conn.commit()
                            st.success(f"✅ Staff {name} updated!")

                        if st.button(f"❌ Delete {name}", key=f"delete_staff_{staff_id}"):
                            cursor.execute("DELETE FROM STAFF WHERE Staff_id = %s", (staff_id,))
                            cursor.execute("DELETE FROM LOGIN_INFO WHERE user_id = %s", (staff_id,))
                            conn.commit()
                            st.success(f"✅ Staff {name} deleted!")

        elif action == "Add New Staff":
            st.subheader("➕ Add New Staff Member")
            new_staff_id = st.text_input("Enter Staff ID (Unique):", key="new_staff_id")
            new_staff_name = st.text_input("Enter Name:", key="new_staff_name")
            new_staff_age = st.number_input("Enter Age:", min_value=18, max_value=80, key="new_staff_age")
            new_staff_phone = st.text_input("Enter Phone No:", key="new_staff_phone")
            new_staff_address = st.text_input("Enter Address:", key="new_staff_address")
            new_staff_role = st.text_input("Enter Role:", key="new_staff_role")
            new_staff_shift = st.text_input("Enter Shift:", key="new_staff_shift")
            new_staff_salary = st.number_input("Enter Salary:", min_value=0.0, key="new_staff_salary")
            new_staff_password = st.text_input("Enter Password:", type="password", key="new_staff_password")

            if st.button("Add Staff", key="add_staff_button"):
                if all([new_staff_id, new_staff_name, new_staff_age, new_staff_phone, new_staff_address, new_staff_role, new_staff_shift, new_staff_salary, new_staff_password]):
                    cursor.execute("INSERT INTO STAFF (Staff_id, Name, Age, Phone_no, Address, Role, Shift, Salary) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                        (new_staff_id, new_staff_name, new_staff_age, new_staff_phone, new_staff_address, new_staff_role, new_staff_shift, new_staff_salary))
                    cursor.execute("INSERT INTO login_info (user_id, password) VALUES (%s, %s)", (new_staff_id, new_staff_password))
                    conn.commit()
                    st.success(f"✅ New staff {new_staff_name} added!")

    # Option 4: Manage Stations
    elif choice == "Manage Stations":
        st.subheader("🚉 Manage Stations")
        action = st.selectbox("Select Action:", ["Add New Station", "Update or Delete Station"])

        if action == "Update or Delete Station":
            cursor.execute("SELECT Station_id, Name, Train_no, Station_master_id FROM STATION")
            stations = cursor.fetchall()

            if not stations:
                st.warning("No stations found.")
            else:
                # Fetch Station Masters 
                cursor.execute("SELECT Staff_id, Name FROM STAFF WHERE Role = 'Station Master'")
                station_masters = cursor.fetchall()
                station_master_options = {f"{name} (ID: {staff_id})": staff_id for staff_id, name in station_masters}
                station_master_options["None"] = None 

                for station in stations:
                    station_id, name, train_json, station_master_id = station
                    train_dict = json.loads(train_json) if train_json else {}
                    with st.expander(f"🚉 {name} (ID: {station_id})"):
                        new_name = st.text_input(f"Edit Name ({name})", value=name, key=f"station_name_{station_id}")

                        # Display current trains and times
                        st.write("### Trains and Arrival Times")
                        updated_train_dict = train_dict.copy()
                        for train_no, arrival_time in train_dict.items():
                            new_time = st.text_input(
                                f"Arrival Time for {train_no} ({arrival_time})",
                                value=arrival_time,
                                key=f"time_{station_id}_{train_no}"
                            )
                            updated_train_dict[train_no] = new_time
                            if st.button(f"Remove {train_no}", key=f"remove_{station_id}_{train_no}"):
                                del updated_train_dict[train_no]

                        # Add a new train to this station
                        new_train_no = st.text_input("Add New Train No:", key=f"new_train_{station_id}")
                        new_train_time = st.text_input("Arrival Time for New Train (HH:MM AM/PM):", key=f"new_time_{station_id}")
                        if st.button("Add Train to Station", key=f"add_train_{station_id}"):
                            if new_train_no and new_train_time:
                                updated_train_dict[new_train_no] = new_train_time

                        # Display Station Master
                        current_station_master = station_master_id if station_master_id else "None"
                        selected_station_master = st.selectbox(
                            f"Assign Station Master (Current: {current_station_master})",
                            options=list(station_master_options.keys()),
                            index=list(station_master_options.values()).index(station_master_id) if station_master_id in station_master_options.values() else 0,
                            key=f"station_master_{station_id}"
                        )
                        new_station_master_id = station_master_options[selected_station_master]

                        if st.button(f"✅ Update {name}", key=f"update_station_{station_id}"):
                            new_train_json = json.dumps(updated_train_dict)
                            cursor.execute(
                                "UPDATE STATION SET Name=%s, Train_no=%s, Station_master_id=%s WHERE Station_id=%s",
                                (new_name, new_train_json, new_station_master_id, station_id)
                            )
                            conn.commit()
                            st.success(f"✅ Station {name} updated!")

                        if st.button(f"❌ Delete {name}", key=f"delete_station_{station_id}"):
                            cursor.execute("DELETE FROM STATION WHERE Station_id = %s", (station_id,))
                            conn.commit()
                            st.success(f"✅ Station {name} deleted!")

        elif action == "Add New Station":
            st.subheader("➕ Add New Station")
            new_station_id = st.text_input("Enter Station ID (Unique):")
            new_station_name = st.text_input("Enter Station Name:")

            # Adding trains and times for the new station
            train_dict = {}
            train_count = st.number_input("Number of Trains for this Station:", min_value=0, step=1)
            for i in range(int(train_count)):
                st.write(f"### Train {i+1}")
                train_no = st.text_input(f"Train No {i+1}:", key=f"new_station_train_{i}")
                arrival_time = st.text_input(f"Arrival Time for Train {i+1} (HH:MM AM/PM):", key=f"new_station_time_{i}")
                if train_no and arrival_time:
                    train_dict[train_no] = arrival_time

            # Fetch Station Masters 
            cursor.execute("SELECT Staff_id, Name FROM STAFF WHERE Role = 'Station Master'")
            station_masters = cursor.fetchall()
            station_master_options = {f"{name} (ID: {staff_id})": staff_id for staff_id, name in station_masters}
            station_master_options["None"] = None  

            selected_station_master = st.selectbox(
                "Assign Station Master:",
                options=list(station_master_options.keys()),
                key="new_station_master"
            )
            new_station_master_id = station_master_options[selected_station_master]

            if st.button("Add Station"):
                if all([new_station_id, new_station_name]):
                    train_json = json.dumps(train_dict) if train_dict else json.dumps({})
                    cursor.execute(
                        "INSERT INTO STATION (Station_id, Name, Train_no, Station_master_id) VALUES (%s, %s, %s, %s)",
                        (new_station_id, new_station_name, train_json, new_station_master_id)
                    )
                    conn.commit()
                    st.success(f"✅ New station {new_station_name} added!")
                else:
                    st.error("Please fill in all required fields (Station ID and Name).")

    # Option 5: View Reports
    elif choice == "View Reports":
        st.subheader("📊 View Reports")
        cursor.execute("SELECT COUNT(*) FROM BOOKING")
        total_bookings = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM CUSTOMER")
        total_customers = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM STAFF")
        total_staff = cursor.fetchone()[0]

        st.metric("Total Bookings", total_bookings)
        st.metric("Total Customers", total_customers)
        st.metric("Total Staff", total_staff)

    cursor.close()
    conn.close()