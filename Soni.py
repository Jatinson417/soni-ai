import streamlit as st
from groq import Groq
import urllib.parse
import json
import os
import re
import random
import smtplib
from email.mime.text import MIMEText
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
VERIFY_FILE = "pending_verifications.json"

# --- CREDENTIALS & SECRETS ---
try:
    SENDER_EMAIL = st.secrets.get("SENDER_EMAIL", "sonijatin177@gmail.com").strip()
    SENDER_PASSWORD = st.secrets.get("SENDER_APP_PASSWORD", "").strip().replace(" ", "")
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "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").strip()
except Exception:
    SENDER_EMAIL = "sonijatin177@gmail.com"
    SENDER_PASSWORD = ""
    GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY, timeout=25.0)

# --- DATABASE HELPERS ---
def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def send_verification_email(to_email, otp_code):
    if not SENDER_PASSWORD:
        return False, "Secrets mein SENDER_APP_PASSWORD set nahi hai!"
    try:
        msg = MIMEText(
            f"Namaste!\n\n"
            f"Aapka unique Soni AI verification code yeh hai:\n\n"
            f"👉 {otp_code}\n\n"
            f"Yeh code sirf aapke account verification ke liye hai.\n\n"
            f"- Team Soni AI"
        )
        msg['Subject'] = f"{otp_code} - Soni AI Verification Code"
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return True, "Unique verification code aapki Gmail par bhej diya gaya hai!"
    except Exception as e:
        return False, f"Email error: {e}"

# --- USER PERSISTENCE ---
users_db = load_json(USERS_FILE, {})
pending_verifications = load_json(VERIFY_FILE, {})
query_params = st.query_params

if "user" not in st.session_state:
    stored_user = query_params.get("user")
    if stored_user and stored_user in users_db:
        st.session_state.user = stored_user
    else:
        st.session_state.user = None

if "signup_stage" not in st.session_state:
    st.session_state.signup_stage = "form"
if "verifying_email" not in st.session_state:
    st.session_state.verifying_email = None

def load_orders():
    return load_json(ORDERS_FILE, [])

def save_all_orders(orders_list):
    save_json(ORDERS_FILE, orders_list)

def load_products():
    if os.path.exists(PRODUCTS_FILE):
        try:
            with open(PRODUCTS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    default_items = [
        {"id": 1, "name": "Women's Stylish Short Kurti", "price": 299, "img": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=400"},
        {"id": 2, "name": "Adjustable Aluminum Laptop Stand", "price": 449, "img": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400"},
        {"id": 3, "name": "Premium Handbag For Women", "price": 399, "img": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400"}
    ]
    save_json(PRODUCTS_FILE, default_items)
    return default_items

def save_all_products(products_list):
    save_json(PRODUCTS_FILE, products_list)

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
                except Exception:
                    pass
        now_india = datetime.now(ZoneInfo("Asia/Kolkata"))
        return f"Abhi **India 🇮🇳** mein time **{now_india.strftime('%I:%M %p')}** ho raha hai."
    return None

if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_shop" not in st.session_state:
    st.session_state.show_shop = False
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "lightbox_img" not in st.session_state:
    st.session_state.lightbox_img = None

if query_params.get("action") == "toggle_shop":
    st.session_state.show_shop = not st.session_state.show_shop
    st.query_params["action"] = ""
    st.rerun()

# --- CSS STYLING ---
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 50%, #c471ed 100%) !important;
        background-attachment: fixed !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        min-height: 100vh !important;
    }}

    [data-testid="stSidebar"] {{
        display: none !important;
    }}

    header, [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    .top-nav-bar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 15px 30px;
        width: 100%;
    }}
    .brand-logo {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 26px;
        font-weight: 800;
        color: #1f1f2e;
    }}
    .top-actions {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .action-pill {{
        background: rgba(255, 255, 255, 0.75);
        color: #1f1f2e !important;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none !important;
        border: 1px solid rgba(255, 255, 255, 0.4);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}

    .auth-glass-container {{
        max-width: 480px;
        margin: 30px auto;
        background: rgba(255, 255, 255, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 28px;
        padding: 36px;
        backdrop-filter: blur(25px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
    }}

    div[data-testid="stTextInput"] input {{
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.8) !important;
        border-radius: 14px !important;
        padding: 12px 16px !important;
        color: #1f1f2e !important;
        font-size: 14px !important;
    }}

    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button {{
        background: linear-gradient(90deg, #ff7e5f, #feb47b) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        box-shadow: 0 8px 20px rgba(254, 180, 123, 0.4) !important;
    }}
    </style>

    <div class="top-nav-bar">
        <div class="brand-logo">
            <span>✨</span> Soni AI
        </div>
        <div class="top-actions">
            <a href="https://mail.google.com/mail/?view=cm&fs=1&to=sonijatin177@gmail.com" target="_blank" class="action-pill">
                ⚡ Founder: Jatin Soni
            </a>
            <a href="/?action=toggle_shop" target="_self" class="action-pill" style="color:#e65c00 !important;">
                🛒 Soni Shop
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

CREATOR_REPLY = "Mujhe Jatin Soni ne banaya hai! Woh 16 saal ke hain, 12th class mein padhte hain aur Haryana ke Sirsa district ke Rori gaon ke rehne wale hain."
CUSTOM_ANSWERS = {"what is skb": "Santosh kulcha bandar", "skb": "Santosh kulcha bandar"}
CURRENT_DATE_STR = datetime.now().strftime("%d %B %Y")
SYSTEM_PROMPT = f"""
You are Soni AI, created by Jatin Soni.
Creator: Jatin Soni (16 yrs, 12th class, Rori, Sirsa, Haryana).
Date: {CURRENT_DATE_STR}. Year: 2026.
Rules:
1. Direct, clear answers without meta text or thinking tokens.
2. If asked who made you: "{CREATOR_REPLY}"
"""

def clean_model_output(text: str) -> str:
    if not text: return ""
    if "</think>" in text: text = text.split("</think>")[-1]
    elif "<think>" in text: text = re.sub(r'(?i)<think>.*', '', text, flags=re.DOTALL)
    return text.strip()

# --- SIGN IN & SIGN UP (INDIVIDUAL OTP PER USER) ---
if not st.session_state.user:
    st.markdown('<div class="auth-glass-container">', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;">
            <div>
                <h3 style="margin:0; font-size:22px; font-weight:700; color:#1f1f2e;">Soni AI: Access</h3>
                <p style="margin:4px 0 0 0; font-size:13px; color:#555;">Apna Gmail dalein aur unique code se verify karein</p>
            </div>
            <div style="font-size:32px;">🔐</div>
        </div>
    """, unsafe_allow_html=True)

    # Verification stage
    if st.session_state.signup_stage == "verify":
        active_email = st.session_state.verifying_email
        all_pendings = load_json(VERIFY_FILE, {})
        user_pending_data = all_pendings.get(active_email, {})

        st.info(f"Verification code sent to:\n**{active_email}**")

        with st.form("verify_form"):
            code_in = st.text_input("Enter 6-digit Verification Code*", placeholder="Ex: 481920").strip()
            submit_verify = st.form_submit_button("Sign In / Explore Soni AI ➔", use_container_width=True)

            if submit_verify:
                expected_otp = str(user_pending_data.get("otp", "")).strip()
                entered_otp = str(code_in).strip()

                if entered_otp and expected_otp and entered_otp == expected_otp:
                    users_db[active_email] = {
                        "password": user_pending_data.get("password", ""),
                        "joined": datetime.now().strftime("%d-%m-%Y")
                    }
                    save_json(USERS_FILE, users_db)

                    # Saaf karein pending entry
                    if active_email in all_pendings:
                        del all_pendings[active_email]
                        save_json(VERIFY_FILE, all_pendings)

                    st.session_state.user = active_email
                    st.query_params["user"] = active_email
                    st.session_state.signup_stage = "form"
                    st.session_state.verifying_email = None
                    st.success("Verification successful! Welcome to Soni AI.")
                    st.rerun()
                else:
                    st.error("Invalid verification code! Kripya apni Gmail par aaya hua naya code dalein.")

        if st.button("⬅️ Change Email / Resend"):
            st.session_state.signup_stage = "form"
            st.rerun()

    # Form stage
    else:
        tab_login, tab_signup = st.tabs(["🔑 Log In", "📝 Sign Up"])

        with tab_login:
            with st.form("login_box_form"):
                l_email = st.text_input("Enter Gmail Address*", placeholder="your_email@gmail.com").strip().lower()
                l_pass = st.text_input("Password*", type="password", placeholder="Enter your password")
                btn_l = st.form_submit_button("Log In ➔", use_container_width=True)

                if btn_l:
                    if not l_email or not l_pass:
                        st.error("Email aur Password dono bharein!")
                    elif l_email not in users_db:
                        st.error("Yeh email registered nahi hai! Pehle Sign Up karein.")
                    elif users_db[l_email].get("password") != l_pass:
                        st.error("Incorrect password!")
                    else:
                        st.session_state.user = l_email
                        st.query_params["user"] = l_email
                        st.rerun()

        with tab_signup:
            with st.form("signup_box_form"):
                s_email = st.text_input("Enter Gmail Address*", placeholder="your_email@gmail.com").strip().lower()
                s_pass = st.text_input("Create Password*", type="password", placeholder="Choose a password")
                btn_s = st.form_submit_button("🔑 Get Verification Code", use_container_width=True)

                if btn_s:
                    if not s_email or not s_pass:
                        st.error("Email aur Password dono bharein!")
                    elif "@gmail.com" not in s_email:
                        st.error("Kripya valid @gmail.com address dalein!")
                    elif s_email in users_db:
                        st.error("Yeh email pehle se registered hai! 'Log In' tab use karein.")
                    else:
                        # Har request par 100% alag aur fresh 6-digit random code
                        unique_otp = f"{random.randint(100000, 999999)}"
                        ok, msg = send_verification_email(s_email, unique_otp)
                        if ok:
                            all_pendings = load_json(VERIFY_FILE, {})
                            all_pendings[s_email] = {
                                "password": s_pass,
                                "otp": unique_otp,
                                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            save_json(VERIFY_FILE, all_pendings)

                            st.session_state.verifying_email = s_email
                            st.session_state.signup_stage = "verify"
                            st.rerun()
                        else:
                            st.error(msg)

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- MAIN APP (AFTER LOGIN) ---
current_user = st.session_state.user

col_u1, col_u2 = st.columns([8, 2])
with col_u1:
    st.markdown(f"👋 Welcome, **{current_user.split('@')[0].capitalize()}**!")
with col_u2:
    if st.button("🚪 Logout", key="btn_logout_main"):
        st.session_state.user = None
        st.query_params.clear()
        st.rerun()

col_c1, col_c2 = st.columns([8.5, 1.5])
with col_c2:
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask Soni AI anything...")

if user_input:
    clean_input = user_input.strip()

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    input_lower = clean_input.lower()
    creator_triggers = ["kisne banaya", "who made you", "developer", "creator", "owner", "kaun banaya", "who created"]

    matched_custom_reply = next((ans for q_t, ans in CUSTOM_ANSWERS.items() if q_t in input_lower), None)
    time_reply = get_country_time(clean_input)

    if matched_custom_reply:
        bot_reply = matched_custom_reply
    elif time_reply:
        bot_reply = time_reply
    elif any(trigger in input_lower for trigger in creator_triggers):
        bot_reply = CREATOR_REPLY
    else:
        try:
            sanitized_history = [{"role": m["role"], "content": clean_model_output(m["content"])} for m in st.session_state.messages[-6:] if clean_model_output(m["content"])]
            payload = [{"role": "system", "content": SYSTEM_PROMPT}] + sanitized_history

            model_data = client.models.list()
            BLACKLIST = ["whisper", "guard", "distill", "safeguard", "vision", "embed", "tts", "r1"]
            active_models = [m.id for m in model_data.data if not any(b in m.id.lower() for b in BLACKLIST)]
            active_models.sort(key=lambda n: 0 if "llama-3.1-8b" in n.lower() else 1)

            raw_reply = None
            for m_candidate in active_models:
                try:
                    chat_completion = client.chat.completions.create(
                        messages=payload,
                        model=m_candidate,
                        temperature=0.5,
                        max_tokens=350,
                    )
                    raw_reply = chat_completion.choices[0].message.content
                    if raw_reply: break
                except Exception:
                    continue

            bot_reply = clean_model_output(raw_reply) if raw_reply else "Main samajh gaya. Aage batayein?"
        except Exception as e:
            bot_reply = f"Error details: {e}"

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.rerun()
