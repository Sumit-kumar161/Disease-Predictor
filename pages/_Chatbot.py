import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Logout button in sidebar
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

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("🔐 Please log in to access the chatbot.")
    st.stop()

# Configure API key
genai.configure(api_key=api_key)

# Initialize chat history in Streamlit state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🩺 Doctor's Assistant Chatbot")

# Display past messages
for msg in st.session_state.chat_history:
    role = "🧑‍⚕️ You" if msg["role"] == "user" else "🤖 AI Assistant"
    st.chat_message(role).markdown(msg["content"])

# Input from user
user_input = st.chat_input("Ask your medical question here...")

system_prompt = (
    "You are a highly professional medical assistant AI helping doctors. "
    "Provide accurate, concise, and evidence-based medical advice. "
    "If unsure, recommend consulting a specialist."
)

# Initialize the chat model
model = genai.GenerativeModel('gemini-2.0-flash')  # Updated model name

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    try:
        # Start a chat session if it doesn't exist
        if "chat_session" not in st.session_state:
            st.session_state.chat_session = model.start_chat(history=[])
        
        # Send the message with system prompt context
        response = st.session_state.chat_session.send_message(
            f"{system_prompt}\n\n{user_input}"
        )
        reply = response.text.strip()
    except Exception as e:
        reply = f"⚠️ Error generating response: {e}"

    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    st.rerun()

# Clear chat button
st.markdown("---")
if st.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []
    if "chat_session" in st.session_state:
        del st.session_state.chat_session
    st.rerun()
