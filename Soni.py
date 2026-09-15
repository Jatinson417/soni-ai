import streamlit as st
from groq import Groq
import urllib.parse
import json
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Soni AI", page_icon="🤖", layout="wide")

BG_IMAGE_URL = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"
UPI_QR_URL = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa=8307940340@ptyes&pn=Jatin%20Soni&cu=INR"
MY_WHATSAPP_NUMBER = "918307940340"
ADMIN_PIN = "2009"

ORDERS_FILE = "orders_database.json"
PRODUCTS_FILE = "products_database.json"
USERS_FILE = "users_database.json"
CHATS_FILE = "chats_history_database.json"

# --- DATABASE HELPERS ---
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

def load_products():
    if os.path.exists(PRODUCTS_FILE):
        try:
            with open(PRODUCTS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    default_items = [
        {"id": 1, "name": "Women's Stylish Short Kurti", "price": 299, "img": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=400"},
        {"id": 2, "name": "Adjustable Aluminum Laptop Stand", "price": 449, "img": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400"},
        {"id": 3, "name": "Premium Handbag For Women", "price": 399, "img": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400"}
    ]
    save_json(PRODUCTS_FILE, default_items)
    return default_items

# --- WORLD CLOCK ---
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
    "england": ("Europe/London", "England 🇬🇧"),
    "canada": ("America/Toronto", "Canada 🇨🇦"),
    "australia": ("Australia/Sydney", "Australia (Sydney) 🇦🇺"),
    "sydney": ("Australia/Sydney", "Sydney 🇦🇺"),
    "japan": ("Asia/Tokyo", "Japan 🇯🇵"),
    "tokyo": ("Asia/Tokyo", "Tokyo 🇯🇵"),
    "germany": ("Europe/Berlin", "Germany 🇩🇪"),
    "berlin": ("Europe/Berlin", "Berlin 🇩🇪"),
    "singapore": ("Asia/Singapore", "Singapore 🇸🇬"),
    "pakistan": ("Asia/Karachi", "Pakistan 🇵🇰"),
    "saudi": ("Asia/Riyadh", "Saudi Arabia 🇸🇦"),
    "france": ("Europe/Paris", "France 🇫🇷"),
    "paris": ("Europe/Paris", "Paris 🇫🇷"),
    "russia": ("Europe/Moscow", "Russia 🇷🇺"),
    "moscow": ("Europe/Moscow", "Moscow 🇷🇺"),
    "china": ("Asia/Shanghai", "China 🇨🇳"),
    "qatar": ("Asia/Qatar", "Qatar 🇶🇦"),
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
        return f"Abhi **India 🇮🇳** mein time **{now_india.strftime('%I:%M %p')}** ho raha hai.\n\nDusre desh ka time dekhne ke liye desh ka naam likhein (jaise: *Dubai time*, *USA time*)."
    return None

# --- SESSION INITIALIZATION ---
if "logged_user" not in st.session_state:
    st.session_state.logged_user = None
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "show_shop" not in st.session_state:
    st.session_state.show_shop = False
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "lightbox_img" not in st.session_state:
    st.session_state.lightbox_img = None

# Custom CSS
st.markdown(
    f"""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background: url("{BG_IMAGE_URL}") no-repeat center center fixed !important;
        background-size: cover !important;
        height: 100vh !important;
    }}

    [data-testid="stSidebar"] {{
        background: rgba(12, 12, 18, 0.90) !important;
        backdrop-filter: blur(14px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
    }}

    .top-right-stack {{
        position: fixed;
        top: 25px;
        right: 25px;
        display: flex;
        flex-direction: row;
        gap: 10px;
        z-index: 99999;
    }}

    .badge-btn {{
        background: rgba(0, 0, 0, 0.75);
        color: #00e5ff !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none !important;
        border: 1px solid rgba(0, 229, 255, 0.4);
        backdrop-filter: blur(8px);
        display: inline-block;
    }}

    [data-testid="stChatMessage"] {{
        background-color: rgba(255, 255, 255, 0.94) !important;
        border-radius: 14px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }}
    [data-testid="stChatMessage"] p {{
        color: #111111 !important;
    }}

    .auth-container {{
        max-width: 420px;
        margin: 60px auto;
        padding: 30px;
        background: rgba(15, 15, 25, 0.92);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        backdrop-filter: blur(15px);
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    </style>

    <div class="top-right-stack">
        <a href="https://mail.google.com/mail/?view=cm&fs=1&to=sonijatin177@gmail.com" target="_blank" class="badge-btn">⚡ Founder: Jatin Soni</a>
        <a href="/?action=toggle_shop" target="_self" class="badge-btn" style="color: #ffd700 !important; border-color: rgba(255,215,0,0.4);">🛍️ Soni Shop</a>
    </div>
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

CREATOR_REPLY = (
    "Mujhe Jatin Soni ne banaya hai! Woh 16 saal ke hain, 12th class mein padhte hain "
    "aur Haryana ke Sirsa district ke Rori gaon ke rehne wale hain."
)
CUSTOM_ANSWERS = {
    "what is skb": "Santosh kulcha bandar",
    "skb": "Santosh kulcha bandar",
}
CURRENT_DATE_STR = datetime.now().strftime("%d %B %Y")
SYSTEM_PROMPT = f"""
You are Soni AI, a natural, highly intelligent assistant created by Jatin Soni.
Creator: Jatin Soni (16 yrs, 12th class, Rori, Sirsa, Haryana).
Today's Date: {CURRENT_DATE_STR}. Year: 2026.
Rules:
1. Direct answers without preface, planning, or reasoning tokens.
2. Reply in Hinglish if asked in Hindi/Hinglish, else English.
3. If asked who made you, reply: "{CREATOR_REPLY}"
"""

def clean_model_output(text: str) -> str:
    if not text: return ""
    if "</think>" in text: text = text.split("</think>")[-1]
    elif "<think>" in text: text = re.sub(r'(?i)<think>.*', '', text, flags=re.DOTALL)
    text = re.sub(r'(?i)^\s*(analyze user input|identify key constraints|formulate response|draft response).*?\n\n', '', text, flags=re.DOTALL)
    text = re.sub(r'(?i)Here\'s a thinking process:?.*?(?=\n\n|\Z)', '', text, flags=re.DOTALL)
    return text.strip()

# --- AUTHENTICATION SCREEN ---
if not st.session_state.logged_user:
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>🤖 Soni AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00e5ff;'>Apna account login ya register karein taaki chat history save rahe</p>", unsafe_allow_html=True)

    auth_tab1, auth_tab2 = st.tabs(["🔑 Login", "📝 Sign Up (Naya Account)"])
    users_db = load_json(USERS_FILE, {})

    with auth_tab1:
        with st.form("login_form"):
            l_user = st.text_input("Username").strip().lower()
            l_pass = st.text_input("Password", type="password")
            btn_login = st.form_submit_button("Login Karein 🚀", use_container_width=True)

            if btn_login:
                if l_user in users_db and users_db[l_user] == l_pass:
                    st.session_state.logged_user = l_user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Galat Username ya Password!")

    with auth_tab2:
        with st.form("signup_form"):
            s_user = st.text_input("Choose Username").strip().lower()
            s_pass = st.text_input("Choose Password", type="password")
            btn_signup = st.form_submit_button("Account Banayein ✨", use_container_width=True)

            if btn_signup:
                if not s_user or not s_pass:
                    st.error("Username aur password dono bharein!")
                elif s_user in users_db:
                    st.error("Yeh Username pehle se kisi aur ka hai!")
                else:
                    users_db[s_user] = s_pass
                    save_json(USERS_FILE, users_db)
                    st.session_state.logged_user = s_user
                    st.success("Account ban gaya! Logging in...")
                    st.rerun()

    st.stop()

# --- LOGGED IN USER INTERFACE ---
user = st.session_state.logged_user
chats_db = load_json(CHATS_FILE, {})

if user not in chats_db:
    chats_db[user] = {}

# Ensure an active chat session
if not st.session_state.current_chat_id or st.session_state.current_chat_id not in chats_db[user]:
    if len(chats_db[user]) > 0:
        st.session_state.current_chat_id = list(chats_db[user].keys())[0]
    else:
        new_id = datetime.now().strftime("Chat %d %b, %I:%M %p")
        chats_db[user][new_id] = []
        save_json(CHATS_FILE, chats_db)
        st.session_state.current_chat_id = new_id

# --- SIDEBAR (Gemini Style History) ---
with st.sidebar:
    st.markdown(f"### 👤 `{user.capitalize()}`")
    
    if st.button("➕ New Chat", use_container_width=True):
        new_id = datetime.now().strftime("Chat %d %b, %I:%M %p")
        chats_db[user][new_id] = []
        save_json(CHATS_FILE, chats_db)
        st.session_state.current_chat_id = new_id
        st.rerun()

    st.markdown("---")
    st.markdown("**📜 Chat History**")

    # List chats
    for chat_title in list(chats_db[user].keys()):
        col_c, col_d = st.columns([8, 2])
        with col_c:
            is_active = "👉 " if chat_title == st.session_state.current_chat_id else ""
            if st.button(f"{is_active}{chat_title}", key=f"sel_{chat_title}", use_container_width=True):
                st.session_state.current_chat_id = chat_title
                st.rerun()
        with col_d:
            if st.button("✕", key=f"del_{chat_title}", help="Delete chat"):
                del chats_db[user][chat_title]
                save_json(CHATS_FILE, chats_db)
                st.session_state.current_chat_id = None
                st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_user = None
        st.session_state.current_chat_id = None
        st.rerun()

# --- MAIN CHAT WINDOW ---
curr_id = st.session_state.current_chat_id
current_messages = chats_db[user].get(curr_id, [])

st.title(f"🤖 Soni AI")

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input(f"Ask Soni AI anything, {user.capitalize()}...")

if user_input:
    clean_input = user_input.strip()

    if clean_input == f"/admin {ADMIN_PIN}":
        st.session_state.admin_authenticated = True
        st.rerun()

    current_messages.append({"role": "user", "content": user_input})
    chats_db[user][curr_id] = current_messages
    save_json(CHATS_FILE, chats_db)

    with st.chat_message("user"):
        st.markdown(user_input)

    input_lower = clean_input.lower()
    creator_triggers = ["kisne banaya", "who made you", "developer", "creator", "owner", "kaun banaya", "who created"]

    matched_custom = None
    for q_t, ans in CUSTOM_ANSWERS.items():
        if q_t in input_lower:
            matched_custom = ans
            break

    time_reply = get_country_time(clean_input)

    if matched_custom:
        bot_reply = matched_custom
    elif time_reply:
        bot_reply = time_reply
    elif any(t in input_lower for t in creator_triggers):
        bot_reply = CREATOR_REPLY
    else:
        try:
            sanitized = []
            for m in current_messages[-6:]:
                cleaned = clean_model_output(m["content"])
                if cleaned:
                    sanitized.append({"role": m["role"], "content": cleaned})

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

            bot_reply = clean_model_output(raw_reply) if raw_reply else "Kuch dikkat aayi, dobara try karein."
        except Exception as e:
            bot_reply = f"Error details: {e}"

    current_messages.append({"role": "assistant", "content": bot_reply})
    chats_db[user][curr_id] = current_messages
    save_json(CHATS_FILE, chats_db)

    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.rerun()
