import streamlit as st
from groq import Groq
import urllib.parse
import json
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Soni AI", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

BG_IMAGE_URL = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"
UPI_QR_URL = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa=8307940340@ptyes&pn=Jatin%20Soni&cu=INR"
MY_WHATSAPP_NUMBER = "918307940340"
ADMIN_PIN = "2009"

CHATS_FILE = "chats_history_database.json"
PRODUCTS_FILE = "products_database.json"
ORDERS_FILE = "orders_database.json"

# --- HELPER FUNCTIONS ---
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

# --- STATE MANAGEMENT ---
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# Custom Gemini Dark-Minimal CSS
st.markdown(
    f"""
    <style>
    [data-testid="stSidebar"] {{
        background-color: #1e1f20 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding-top: 15px !important;
    }}
    [data-testid="stSidebar"] * {{
        color: #e3e3e3 !important;
    }}
    .gemini-brand {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 20px;
        color: #ffffff !important;
    }}
    .recents-label {{
        font-size: 12px;
        color: #8e918f !important;
        margin-top: 25px;
        margin-bottom: 8px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    .user-profile-bar {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 6px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        margin-top: 30px;
    }}
    .user-avatar {{
        width: 36px;
        height: 36px;
        background: #ea4335;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: #ffffff !important;
        font-size: 16px;
    }}
    .auth-card {{
        max-width: 440px;
        margin: 80px auto;
        padding: 35px;
        background: #1e1f20;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 12px 40px rgba(0,0,0,0.6);
    }}
    [data-testid="stChatMessage"] {{
        background: rgba(30, 31, 32, 0.85) !important;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 12px;
    }}
    [data-testid="stChatMessage"] p {{
        color: #e3e3e3 !important;
    }}
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
You are Soni AI, styled cleanly like Gemini, created by Jatin Soni.
Creator: Jatin Soni (16 yrs, 12th class, Rori, Sirsa, Haryana).
Today: {CURRENT_DATE_STR}. Year: 2026.
Rules:
1. Always start directly with the actual answer. No drafts or thinking process.
2. Reply in concise natural Hinglish or English.
3. If asked who made you, reply: "{CREATOR_REPLY}"
"""

def clean_model_output(text: str) -> str:
    if not text: return ""
    if "</think>" in text: text = text.split("</think>")[-1]
    elif "<think>" in text: text = re.sub(r'(?i)<think>.*', '', text, flags=re.DOTALL)
    text = re.sub(r'(?i)^\s*(analyze user input|identify key constraints|formulate response|draft response).*?\n\n', '', text, flags=re.DOTALL)
    return text.strip()

# --- GOOGLE SIGN IN SCREEN ---
if not st.session_state.user_email:
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div class="auth-card">
            <h2 style="color: #ffffff; margin-bottom: 6px;">✨ Soni AI</h2>
            <p style="color: #8e918f; font-size: 14px; margin-bottom: 25px;">Sign in with your Google account to save chat history</p>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        col_pad1, col_form, col_pad2 = st.columns([1, 1.2, 1])
        with col_form:
            with st.form("google_login_form"):
                user_gmail = st.text_input("Enter your Gmail address", placeholder="name@gmail.com").strip().lower()
                submit_google = st.form_submit_button("🔴 Sign in with Google", use_container_width=True)

                if submit_google:
                    if user_gmail and "@" in user_gmail:
                        name_extracted = user_gmail.split("@")[0].replace(".", " ").title()
                        st.session_state.user_email = user_gmail
                        st.session_state.user_name = name_extracted
                        st.rerun()
                    else:
                        st.error("Kripya valid Gmail address daalein!")
    st.stop()

# --- LOGGED IN GEMINI-STYLE DASHBOARD ---
u_email = st.session_state.user_email
u_name = st.session_state.user_name
chats_db = load_json(CHATS_FILE, {})

if u_email not in chats_db:
    chats_db[u_email] = {}

if not st.session_state.current_chat_id or st.session_state.current_chat_id not in chats_db[u_email]:
    if len(chats_db[u_email]) > 0:
        st.session_state.current_chat_id = list(chats_db[u_email].keys())[0]
    else:
        init_id = "New chat"
        chats_db[u_email][init_id] = []
        save_json(CHATS_FILE, chats_db)
        st.session_state.current_chat_id = init_id

# --- SIDEBAR (Gemini UI Layout) ---
with st.sidebar:
    st.markdown("""
        <div class="gemini-brand">
            <span>✨</span> Soni AI
        </div>
    """, unsafe_allow_html=True)

    if st.button("✏️ New chat", use_container_width=True):
        fresh_title = f"Chat {len(chats_db[u_email]) + 1}"
        chats_db[u_email][fresh_title] = []
        save_json(CHATS_FILE, chats_db)
        st.session_state.current_chat_id = fresh_title
        st.rerun()

    st.markdown('<div class="recents-label">Recents</div>', unsafe_allow_html=True)

    # Recents List
    for c_title in list(chats_db[u_email].keys()):
        is_current = (c_title == st.session_state.current_chat_id)
        btn_label = f"💬 {c_title}" if not is_current else f"🔹 {c_title}"
        
        col_t, col_x = st.columns([8, 2])
        with col_t:
            if st.button(btn_label, key=f"btn_{c_title}", use_container_width=True):
                st.session_state.current_chat_id = c_title
                st.rerun()
        with col_x:
            if st.button("✕", key=f"del_{c_title}"):
                del chats_db[u_email][c_title]
                save_json(CHATS_FILE, chats_db)
                st.session_state.current_chat_id = None
                st.rerun()

    # User Profile Pill at Bottom
    initial_char = u_name[0].upper() if u_name else "U"
    st.markdown(f"""
        <div class="user-profile-bar">
            <div class="user-avatar">{initial_char}</div>
            <div style="line-height: 1.2;">
                <div style="font-weight: 600; font-size: 14px; color: #ffffff;">{u_name}</div>
                <div style="font-size: 11px; color: #8e918f;">Pro</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.session_state.current_chat_id = None
        st.rerun()

# --- MAIN CHAT PANEL ---
curr_id = st.session_state.current_chat_id
current_history = chats_db[u_email].get(curr_id, [])

st.markdown(f"### {curr_id}")

for msg in current_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask Soni AI...")

if user_input:
    clean_input = user_input.strip()

    # If first message in "New chat", rename chat title like Gemini
    active_key = curr_id
    if curr_id.startswith("Chat ") or curr_id == "New chat":
        new_title = clean_input[:28] + ("..." if len(clean_input) > 28 else "")
        chats_db[u_email][new_title] = chats_db[u_email].pop(curr_id)
        active_key = new_title
        st.session_state.current_chat_id = new_title

    current_history.append({"role": "user", "content": clean_input})
    chats_db[u_email][active_key] = current_history
    save_json(CHATS_FILE, chats_db)

    with st.chat_message("user"):
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

    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.rerun()
