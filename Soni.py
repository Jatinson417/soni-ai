import streamlit as st
from groq import Groq
import json
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Gemini", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

CHATS_FILE = "chats_history_database.json"

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

TIMEZONE_MAP = {
    "india": ("Asia/Kolkata", "India 🇮🇳"),
    "bharat": ("Asia/Kolkata", "India 🇮🇳"),
    "dubai": ("Asia/Dubai", "Dubai (UAE) 🇦🇪"),
    "uae": ("Asia/Dubai", "UAE 🇦🇪"),
    "usa": ("America/New_York", "USA (New York) 🇺🇸"),
    "america": ("America/New_York", "USA 🇺🇸"),
    "new york": ("America/New_York", "New York 🇺🇸"),
    "london": ("Europe/London", "London (UK) 🇬🇧"),
    "uk": ("Europe/London", "UK 🇬🇧"),
    "canada": ("America/Toronto", "Canada 🇨🇦"),
    "australia": ("Australia/Sydney", "Australia (Sydney) 🇦🇺"),
    "japan": ("Asia/Tokyo", "Japan 🇯🇵"),
    "tokyo": ("Asia/Tokyo", "Tokyo 🇯🇵"),
    "germany": ("Europe/Berlin", "Germany 🇩🇪"),
    "singapore": ("Asia/Singapore", "Singapore 🇸🇬"),
    "pakistan": ("Asia/Karachi", "Pakistan 🇵🇰"),
    "saudi": ("Asia/Riyadh", "Saudi Arabia 🇸🇦"),
}

def get_country_time(text: str):
    text_low = text.lower()
    time_keywords = ["time", "samay", "baje", "waqt", "ghadi", "clock", "kitne baje"]
    if any(k in text_low for k in time_keywords):
        for place, (tz_name, label) in TIMEZONE_MAP.items():
            if place in text_low:
                try:
                    now = datetime.now(ZoneInfo(tz_name))
                    return f"Abhi **{label}** mein live time **{now.strftime('%I:%M %p')}** ho raha hai ({now.strftime('%d %b %Y')})."
                except:
                    pass
        now_india = datetime.now(ZoneInfo("Asia/Kolkata"))
        return f"Abhi **India 🇮🇳** mein time **{now_india.strftime('%I:%M %p')}** ho raha hai."
    return None

if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- EXACT GEMINI LIGHT THEME CSS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600&display=swap');

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #ffffff !important;
        font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #1f1f1f !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Sidebar Exact Gemini Theme */
    [data-testid="stSidebar"] {
        background-color: #f0f4f9 !important;
        border-right: 1px solid #e1e5ea !important;
        padding-top: 14px !important;
        padding-left: 12px !important;
        padding-right: 12px !important;
    }

    [data-testid="stSidebar"] * {
        font-family: 'Google Sans', sans-serif !important;
    }

    .gemini-top-brand {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 4px 6px 14px 6px;
    }
    .brand-left {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 19px;
        font-weight: 500;
        color: #1f1f1f;
    }

    .chat-spark-toggle {
        display: flex;
        background: #e3e8ef;
        border-radius: 20px;
        padding: 3px;
        margin-bottom: 14px;
    }
    .toggle-pill-active {
        background: #ffffff;
        border-radius: 16px;
        flex: 1;
        text-align: center;
        padding: 4px 0;
        font-size: 13px;
        font-weight: 500;
        color: #1f1f1f;
        box-shadow: 0 1px 2px rgba(0,0,0,0.06);
    }
    .toggle-pill-inactive {
        flex: 1;
        text-align: center;
        padding: 4px 0;
        font-size: 13px;
        color: #5f6368;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
    }
    .beta-badge {
        font-size: 9px;
        background: #d3d8df;
        padding: 1px 4px;
        border-radius: 4px;
        color: #444746;
        font-weight: 600;
    }

    .nav-item-mock {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 7px 10px;
        font-size: 13px;
        color: #444746;
        cursor: default;
        border-radius: 8px;
    }
    .section-muted-heading {
        font-size: 12px;
        color: #72777d;
        font-weight: 500;
        margin-top: 18px;
        margin-bottom: 6px;
        padding-left: 8px;
    }

    /* Recents Chat Buttons List */
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: transparent !important;
        border: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 18px !important;
        padding: 6px 14px !important;
        font-size: 13px !important;
        font-weight: 400 !important;
        color: #1f1f1f !important;
        box-shadow: none !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        margin-bottom: 2px !important;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: #e3e8ef !important;
    }

    /* Exact Active Chat Pill */
    div[data-testid="stSidebar"] .active-recents-pill > button {
        background-color: #e8eaed !important;
        color: #1f1f1f !important;
        font-weight: 600 !important;
    }

    .bottom-profile-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 6px;
        border-top: 1px solid #e1e5ea;
        margin-top: 24px;
    }
    .profile-info {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .avatar-circle {
        width: 32px;
        height: 32px;
        background-color: #e1552f;
        color: #ffffff !important;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 14px;
    }

    /* Chat Messages Light Styling */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        padding: 10px 0 !important;
    }
    [data-testid="stChatMessage"] p {
        color: #1f1f1f !important;
        font-size: 15px !important;
        line-height: 1.6 !important;
    }

    /* Gemini Pill Chat Input */
    [data-testid="stChatInput"] {
        border-radius: 28px !important;
        border: 1px solid #e1e5ea !important;
        background-color: #f0f4f9 !important;
        box-shadow: none !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #0b57d0 !important;
        background-color: #ffffff !important;
    }

    .disclaimer-text {
        text-align: center;
        font-size: 11px;
        color: #72777d;
        margin-top: 8px;
    }

    .auth-box {
        max-width: 420px;
        margin: 100px auto;
        padding: 36px;
        background: #f0f4f9;
        border-radius: 24px;
        text-align: center;
        border: 1px solid #e1e5ea;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# API setup
HARDCODED_KEY = "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".strip()
try:
    secret_key = st.secrets.get("GROQ_API_KEY", "").strip()
except Exception:
    secret_key = ""
FINAL_API_KEY = secret_key if secret_key else HARDCODED_KEY
client = Groq(api_key=FINAL_API_KEY, timeout=25.0)

CREATOR_REPLY = "Mujhe Jatin Soni ne banaya hai! Woh 16 saal ke hain, 12th class mein padhte hain aur Haryana ke Sirsa district ke Rori gaon ke rehne wale hain."
CUSTOM_ANSWERS = {"what is skb": "Santosh kulcha bandar", "skb": "Santosh kulcha bandar"}
CURRENT_DATE_STR = datetime.now().strftime("%d %B %Y")
SYSTEM_PROMPT = f"""
You are Gemini, created by Jatin Soni.
Creator: Jatin Soni (16 yrs, 12th class, Rori, Sirsa, Haryana).
Today: {CURRENT_DATE_STR}. Year: 2026.
Rules:
1. Always give clear, concise, direct answers without meta-announcements or setup text.
2. Reply in natural Hinglish or English based on user query.
3. If asked who made you, reply: "{CREATOR_REPLY}"
"""

def clean_model_output(text: str) -> str:
    if not text: return ""
    if "</think>" in text: text = text.split("</think>")[-1]
    elif "<think>" in text: text = re.sub(r'(?i)<think>.*', '', text, flags=re.DOTALL)
    text = re.sub(r'(?i)^\s*(analyze user input|identify key constraints|formulate response|draft response).*?\n\n', '', text, flags=re.DOTALL)
    return text.strip()

# --- SIGN IN SCREEN ---
if not st.session_state.user_email:
    st.markdown("""
        <div class="auth-box">
            <h2 style="color:#1f1f1f; margin-bottom:8px;">✨ Gemini</h2>
            <p style="color:#5f6368; font-size:14px; margin-bottom:24px;">Sign in with your Google Account to continue</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("google_login"):
            email_in = st.text_input("Email", placeholder="example@gmail.com").strip().lower()
            submitted = st.form_submit_button("Sign in with Google", use_container_width=True)
            if submitted:
                if email_in and "@" in email_in:
                    name_part = email_in.split("@")[0].replace(".", " ").title()
                    st.session_state.user_email = email_in
                    st.session_state.user_name = name_part
                    st.rerun()
                else:
                    st.error("Kripya valid Gmail address likhein.")
    st.stop()

# --- DATABASE SETUP ---
u_email = st.session_state.user_email
u_name = st.session_state.user_name
chats_db = load_json(CHATS_FILE, {})

if u_email not in chats_db:
    chats_db[u_email] = {}

if not st.session_state.current_chat_id or st.session_state.current_chat_id not in chats_db[u_email]:
    if len(chats_db[u_email]) > 0:
        st.session_state.current_chat_id = list(chats_db[u_email].keys())[0]
    else:
        initial_title = "Python Me Gemini Jaisa AI Banayein"
        chats_db[u_email][initial_title] = []
        save_json(CHATS_FILE, chats_db)
        st.session_state.current_chat_id = initial_title

# --- EXACT GEMINI SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div class="gemini-top-brand">
            <div class="brand-left">
                <span style="font-size:20px;">✦</span> Gemini
            </div>
            <div style="color:#5f6368; font-size:16px;">🗖</div>
        </div>
        <div class="chat-spark-toggle">
            <div class="toggle-pill-active">Chat</div>
            <div class="toggle-pill-inactive">Spark <span class="beta-badge">BETA</span></div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("✏️  New chat", use_container_width=True):
        new_name = f"New chat {len(chats_db[u_email]) + 1}"
        chats_db[u_email][new_name] = []
        save_json(CHATS_FILE, chats_db)
        st.session_state.current_chat_id = new_name
        st.rerun()

    st.markdown("""
        <div class="nav-item-mock">🔍 Search chats</div>
        <div class="nav-item-mock">🌄 Images</div>
        <div class="nav-item-mock">📹 Videos</div>
        <div class="nav-item-mock">⚏ Library</div>
        <div class="section-muted-heading">Notebooks</div>
        <div class="nav-item-mock">➕ New notebook</div>
        <div class="section-muted-heading">Recents</div>
    """, unsafe_allow_html=True)

    # Recents List (Exact Screenshot Matching)
    for c_title in list(chats_db[u_email].keys()):
        is_active = (c_title == st.session_state.current_chat_id)
        pill_class = "active-recents-pill" if is_active else ""

        col_text, col_del = st.columns([8.8, 1.2])
        with col_text:
            st.markdown(f'<div class="{pill_class}">', unsafe_allow_html=True)
            if st.button(c_title, key=f"rcnt_{c_title}", use_container_width=True):
                st.session_state.current_chat_id = c_title
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with col_del:
            if st.button("×", key=f"del_{c_title}", help="Delete"):
                del chats_db[u_email][c_title]
                save_json(CHATS_FILE, chats_db)
                st.session_state.current_chat_id = None
                st.rerun()

    # User Profile Pill (Exact Screenshot bottom)
    initial_letter = u_name[0].upper() if u_name else "J"
    st.markdown(f"""
        <div class="bottom-profile-container">
            <div class="profile-info">
                <div class="avatar-circle">{initial_letter}</div>
                <div style="line-height:1.2;">
                    <div style="font-size:13px; font-weight:500; color:#1f1f1f;">{u_name}</div>
                    <div style="font-size:11px; color:#72777d;">Pro</div>
                </div>
            </div>
            <div style="color:#5f6368; font-size:16px;">⚙</div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Log out", use_container_width=True):
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.session_state.current_chat_id = None
        st.rerun()

# --- MAIN CHAT PANEL ---
curr_id = st.session_state.current_chat_id
current_history = chats_db[u_email].get(curr_id, [])

col_m1, col_m2 = st.columns([8.5, 1.5])
with col_m1:
    st.markdown(f"<h3 style='font-weight:500; margin-bottom:20px;'>{curr_id}</h3>", unsafe_allow_html=True)
with col_m2:
    if st.button("Clear Chat", use_container_width=True):
        chats_db[u_email][curr_id] = []
        save_json(CHATS_FILE, chats_db)
        st.rerun()

for msg in current_history:
    avatar_char = "👤" if msg["role"] == "user" else "✦"
    with st.chat_message(msg["role"], avatar=avatar_char):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask Gemini...")

if user_input:
    clean_input = user_input.strip()

    # Gemini Auto-Rename on first message
    active_key = curr_id
    if curr_id.startswith("New chat") or curr_id == "Python Me Gemini Jaisa AI Banayein":
        if not current_history:
            renamed = clean_input[:32].strip()
            chats_db[u_email][renamed] = chats_db[u_email].pop(curr_id)
            active_key = renamed
            st.session_state.current_chat_id = renamed

    current_history.append({"role": "user", "content": clean_input})
    chats_db[u_email][active_key] = current_history
    save_json(CHATS_FILE, chats_db)

    with st.chat_message("user", avatar="👤"):
        st.markdown(clean_input)

    input_lower = clean_input.lower()
    matched_custom = next((ans for q_t, ans in CUSTOM_ANSWERS.items() if q_t in input_lower), None)
    time_reply = get_country_time(clean_input)

    if matched_custom:
        bot_reply = matched_custom
    elif time_reply:
        bot_reply = time_reply
    elif any(t in input_lower for t in ["kisne banaya", "who made you", "developer", "creator", "owner"]):
        bot_reply = CREATOR_REPLY
    else:
        try:
            sanitized = [{"role": m["role"], "content": clean_model_output(m["content"])} for m in current_history[-6:] if clean_model_output(m["content"])]
            payload = [{"role": "system", "content": SYSTEM_PROMPT}] + sanitized

            model_data = client.models.list()
            BLACKLIST = ["whisper", "guard", "distill", "safeguard", "vision", "embed", "tts", "r1"]
            active_models = [m.id for m in model_data.data if not any(b in m.id.lower() for b in BLACKLIST)]
            active_models.sort(key=lambda n: 0 if "llama-3.1-8b" in n.lower() else 1)

            raw_reply = None
            for m_cand in active_models:
                try:
                    chat_comp = client.chat.completions.create(
                        messages=payload,
                        model=m_cand,
                        temperature=0.5,
                        max_tokens=350,
                    )
                    raw_reply = chat_comp.choices[0].message.content
                    if raw_reply: break
                except:
                    continue

            bot_reply = clean_model_output(raw_reply) if raw_reply else "Main samajh gaya. Aage batayein?"
        except Exception as e:
            bot_reply = f"Error details: {e}"

    current_history.append({"role": "assistant", "content": bot_reply})
    chats_db[u_email][active_key] = current_history
    save_json(CHATS_FILE, chats_db)

    with st.chat_message("assistant", avatar="✦"):
        st.markdown(bot_reply)

    st.rerun()

st.markdown('<div class="disclaimer-text">Gemini is AI and can make mistakes.</div>', unsafe_allow_html=True)
