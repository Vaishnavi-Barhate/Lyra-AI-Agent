import streamlit as st
import requests

st.set_page_config(
    page_title="Lyra AI",
    layout="centered"
)

# Inject your purple styling
st.markdown("""
    <style>
    body {
        background-color: #ffffff;
        color: #333333;
        font-family: 'Segoe UI', sans-serif;
    }
    .main {
        background-color: #ffffff;
    }
    h1, h2, h3, h4 {
        color: #5D3FD3;
        font-weight: 700;
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 10px;
        background-color: #f3f0ff;
        color: #2c215d;
        font-size: 16px;
    }
    .user-message {
        background-color: #ede4ff;
        color: #5D3FD3;
        border-left: 4px solid #5D3FD3;
    }
    .bot-message {
        background-color: #f5f3fe;
        color: #3d2d99;
        border-left: 4px solid #3d2d99;
    }
    .stTextInput > div > div > input {
        border: 2px solid #5D3FD3;
        border-radius: 8px;
        padding: 10px;
    }
    .stButton>button {
        background-color: #5D3FD3;
        color: white;
        border-radius: 5px;
        font-weight: bold;
        padding: 10px 20px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #4b30b3;
        color: #ffffff;
    }
    .block-container {
        padding-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h2 style="text-align: center;">
        Lyra AI - Conversations Meet Calendars
    </h2>
    <p style="text-align: center; color: #666666; font-size: 18px;">
        Your Smart Scheduling Companion. Let’s book your meeting now.
    </p>
""", unsafe_allow_html=True)

# Track conversation history and state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "conversation_state" not in st.session_state:
    st.session_state.conversation_state = {}

def send_message(message):
    try:
        with st.spinner("Lyra is thinking..."):
            response = requests.post(
                "https://lyra-ai-agent.onrender.com/",
                json={
                    "message": message,
                    "conversation_state": st.session_state.conversation_state
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # Update conversation state
            st.session_state.conversation_state = data.get("conversation_state", {})
            
            reply = data.get("reply", "⚠️ No reply from backend.")
    except Exception as e:
        reply = f"⚠️ Backend error: {str(e)}"
    return reply

user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.chat_history.append(("user", user_input))
    bot_reply = send_message(user_input)
    st.session_state.chat_history.append(("bot", bot_reply))

for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(
            f"""
            <div class="stChatMessage user-message">
                <b>You:</b> {msg}
            </div>
            """, unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="stChatMessage bot-message">
                <b>Lyra:</b> {msg}
            </div>
            """, unsafe_allow_html=True
        )
