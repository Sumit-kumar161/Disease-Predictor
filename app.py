
import streamlit as st

# Set up the page
st.set_page_config(
    page_title="Sumit HealthCare",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "email" not in st.session_state:
    st.session_state.email = None
if "doctor_id" not in st.session_state:
    st.session_state.doctor_id = None

# Sidebar with logout (only if authenticated)
with st.sidebar:
    st.title("Sumit HealthCare 🏥")
    st.markdown("---")

    if st.session_state.authenticated:
        st.success(f"Logged in as **{st.session_state.email}**")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.email = None
            st.session_state.doctor_id = None
            st.success("You have been logged out.")
            st.rerun()
    else:
        st.info("🔐 Please log in to access the app features.")

# Main app header
st.markdown("""
    <div style='background-color: #0275d8; padding: 1.2rem; border-radius: 10px; margin-bottom: 1rem;'>
        <h2 style='color: white; text-align: center;'>🏥 Sumit HealthCare Portal</h2>
    </div>
""", unsafe_allow_html=True)

# Main content
st.markdown("## 👨‍⚕️ Welcome, Doctor!")
st.markdown("""
This AI-powered healthcare platform helps you:

- 🧪 Predict diseases like **Diabetes**, **Heart Disease**, **Parkinson’s**, and **Breast Cancer**  
- 📄 Generate professional, downloadable **PDF reports**  
- 💬 Use the **Gemini AI chatbot** for medical assistance  
""")

# Features section
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 🧠 Disease Predictor")
    st.markdown("Quick and accurate predictions using trained ML models.")

with col2:
    st.markdown("### 📑 Patient Reports")
    st.markdown("Personalized PDF summaries for each diagnosis.")

with col3:
    st.markdown("### 🤖 Health Chatbot")
    st.markdown("Integrated Gemini AI to answer your health queries.")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: grey; margin-top: 2rem; font-size: 0.9rem;'>
        &copy; 2025 Sumit HealthCare · All Rights Reserved.
    </div>
""", unsafe_allow_html=True)
