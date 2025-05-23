import streamlit as st
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
from dotenv import load_dotenv
import time

# Load MongoDB connection
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["disease_predictor"]
users_collection = db["users"]

# Utility validators
def is_valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def is_strong_password(password):
    return len(password) >= 6 and re.search(r"[A-Za-z]", password) and re.search(r"[0-9]", password)

# User functions
def signup(email, password, doctor_id, org_id):
    if users_collection.find_one({"email": email}):
        st.error("Email already registered.")
        return False
    if users_collection.find_one({"doctor_id": doctor_id}):
        st.error("Doctor ID already in use.")
        return False
    if users_collection.find_one({"organization_id": org_id}):
        st.error("Organization ID already in use.")
        return False

    hashed_password = generate_password_hash(password)
    users_collection.insert_one({
        "email": email,
        "password": hashed_password,
        "doctor_id": doctor_id,
        "organization_id": org_id
    })
    st.success("Signup successful! Please login.")
    return True

def login(email, password):
    user = users_collection.find_one({"email": email})
    if user and check_password_hash(user["password"], password):
        st.session_state["authenticated"] = True
        st.session_state["email"] = email
        st.session_state["doctor_id"] = user.get("doctor_id", "")
        return True
    return False

# Main app
def main():
    st.set_page_config(page_title="Sumit HealthCare Login", layout="centered")

    st.markdown("""
        <div style='text-align: center;'>
            <h1 style='color: #0275d8;'>🏥 Sumit HealthCare</h1>
            <h3>Your AI-powered Diagnosis Partner</h3>
        </div>
        <hr style='margin-top: 0;'>
    """, unsafe_allow_html=True)

    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        with st.container():
            auth_mode = st.radio("🔐 Choose Action", ["Login", "Signup"], horizontal=True)

            if auth_mode == "Signup":
                st.subheader("📝 Create a New Account")
                email = st.text_input("📧 Email")
                password = st.text_input("🔑 Password", type="password")
                doctor_id = st.text_input("🆔 Doctor ID")
                org_id = st.text_input("🏢 Organization ID")

                if st.button("Sign Up"):
                    if not (email and password and doctor_id and org_id):
                        st.error("❗ Please fill in all the fields.")
                    elif not is_valid_email(email):
                        st.error("❗ Please enter a valid email address.")
                    elif not is_strong_password(password):
                        st.error("❗ Password must be at least 6 characters and contain both letters and numbers.")
                    else:
                        if signup(email, password, doctor_id, org_id):
                            st.session_state.authenticated = True
                            st.session_state.email = email
                            st.session_state.doctor_id = doctor_id
                            st.rerun()

            else:
                st.subheader("🔓 Login to Your Account")
                email = st.text_input("📧 Email", key="login_email")
                password = st.text_input("🔑 Password", type="password", key="login_password")

                if st.button("Login"):
                    if not email or not password:
                        st.error("❗ Please enter both email and password.")
                    elif not is_valid_email(email):
                        st.error("❗ Please enter a valid email address.")
                    elif login(email, password):
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password")

    else:
        st.success(f"Welcome Doctor!")
        with st.spinner("🔁 Redirecting to the Predictor..."):
            time.sleep(2)
            st.switch_page("pages/2_Predictor.py")

if __name__ == "__main__":
    main()
