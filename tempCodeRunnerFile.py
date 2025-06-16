import streamlit as st
import mysql.connector

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

st.text("Enter your username and password")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
if st.button("Login"):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM login_info WHERE user_name='{username}' AND password='{password}'")
    if cursor.fetchone():
        st.success("Logged in!")
    else:
        st.error("Invalid username or password")
    cursor.close()