import streamlit as st
import mysql.connector

# Import pages
import customer
import staff
import admin

# Manage session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "customer_id" not in st.session_state:
    st.session_state.customer_id = None

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="project"
)

if conn.is_connected():
    print("Connected to MySQL!")
else:
    print("Connection failed!")

# Sidebar for Logout
def show_sidebar():
    with st.sidebar:
        st.title("Navigation")
        if st.button("🔄 Log Out"):
            st.session_state.page = "login"
            st.session_state.user_role = None
            st.session_state.customer_id = None
            st.rerun()

# Login Page
def login_page():
    st.title("🚅 THE RAILWAY RESERVATION 🚉")
    username = st.text_input("Username", placeholder="Enter your username") 
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    if st.button("Login"):
        cursor = conn.cursor()
        query = "SELECT * FROM login_info WHERE user_id = %s AND password = %s"
        cursor.execute(query, (username, password))
        
        if cursor.fetchone():
            st.success("Logged in!")
            st.session_state.id = username  

            if username == "admin":
                st.session_state.user_role = "admin"
                st.session_state.page = "admin"

            else:
                cursor.execute("SELECT * FROM STAFF WHERE Staff_id = %s", (username,))
                staff_exists = cursor.fetchone()
                if staff_exists:  
                    st.session_state.user_role = "staff"
                    st.session_state.page = "staff"
                else:
                    st.session_state.user_role = "customer"
                    st.session_state.page = "customer"

            st.rerun()
        else:
            st.error("❌ Invalid username or password")
        
        cursor.close()
    
    st.markdown("[👉 Don't have an account? Sign Up Here](?page=signup)")

# Sign-Up Page
def signup_page():
    st.title("🆕 Create an Account")
    new_username = st.text_input("Username", placeholder="Choose a username")
    new_password = st.text_input("Password", type="password", placeholder="Choose a password")
    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
    name = st.text_input("Full Name", placeholder="Enter your full name")
    phone_no = st.text_input("Phone Number", placeholder="Enter your phone number")
    age = st.number_input("Age", min_value=18, max_value=120, step=1, format="%d")

    if st.button("Sign Up"):
        if new_password != confirm_password:
            st.error("❌ Passwords do not match!")
        elif not name or not phone_no:
            st.error("❌ Name and Phone Number are required!")
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM login_info WHERE user_id = %s", (new_username,))
            
            if cursor.fetchone():
                st.error("❌ Username already taken! Please choose another.")
            else:
                cursor.execute("SELECT * FROM CUSTOMER WHERE Phone_no = %s", (phone_no,))
                if cursor.fetchone():
                    st.error("❌ Phone number already registered! Please use a different one.")
                else:
                    insert_login_query = "INSERT INTO login_info (user_id, password) VALUES (%s, %s)"
                    cursor.execute(insert_login_query, (new_username, new_password))
                    
                    insert_customer_query = "INSERT INTO CUSTOMER (Customer_id, Name, Phone_no, Age) VALUES (%s, %s, %s, %s)"
                    cursor.execute(insert_customer_query, (new_username, name, phone_no, age))
                    
                    conn.commit()
                    st.success("✅ Account created successfully! You can now log in.")
            
            cursor.close()
            
    st.markdown("[👉 Back to Login](?page=login)")

# Multi-page navigation
if st.query_params.get("page") == "signup":
    signup_page()
elif st.session_state.page == "login":
    login_page()
elif st.session_state.page == "admin":
    show_sidebar()
    admin.admin()
elif st.session_state.page == "staff":
    show_sidebar()
    staff.staff(st.session_state.id)
elif st.session_state.page == "customer":
    show_sidebar()
    customer.customer(st.session_state.id)
