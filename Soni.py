import streamlit as st
from groq import Groq
import urllib.parse
import json
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Soni AI", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

CHATS_FILE = "chats_history_database.json"
USERS_FILE = "users_database.json"
USAGE_FILE = "user_usage_database.json"
PAYMENTS_FILE = "pending_payments_database.json"
PRODUCTS_FILE = "products_database.json"
ORDERS_FILE = "orders_database.json"
SECRET_CHAT_FILE = "vip_secret_chat_room.json"
COUPONS_FILE = "coupons_database.json"

UPI_ID = "8307940340@ptyes"
UPI_NAME = "Jatin Soni"
MY_WHATSAPP_NUMBER = "918307940340"
ADMIN_PIN = "2009"
FREE_DAILY_LIMIT = 50
OWNER_EMAIL = "sonijatin177@gmail.com"
PREMIUM_PRICE = 99.00

EXACT_CUSTOM_REPLIES = {
    "what is skb": "Santosh Kulcha Bhandar",
    "skb kya hai": "Santosh Kulcha Bhandar",
    "skb": "Santosh Kulcha Bhandar"
}

TIMEZONE_MAP = {
    "india": ("Asia/Kolkata", "India 🇮🇳"),
    "bharat": ("Asia/Kolkata", "India 🇮🇳"),
    "dubai": ("Asia/Dubai", "Dubai (UAE) 🇦🇪"),
    "uae": ("Asia/Dubai", "UAE 🇦🇪"),
    "usa": ("America/New_York", "USA (New York) 🇺🇸"),
    "america": ("America/New_York", "USA (New York) 🇺🇸"),
    "new york": ("America/New_York", "New York 🇺🇸"),
    "london": ("Europe/London", "London (UK) 🇬🇧"),
    "uk": ("Europe/London", "UK 🇬🇧"),
    "canada": ("America/Toronto", "Canada (Toronto) 🇨🇦"),
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
                now = datetime.now(ZoneInfo(tz_name))
                return f"Abhi **{label}** mein live time **{now.strftime('%I:%M %p')}** ho raha hai ({now.strftime('%d %b %Y')})."
        now_india = datetime.now(ZoneInfo("Asia/Kolkata"))
        return f"Abhi **India 🇮🇳** mein time **{now_india.strftime('%I:%M %p')}** ho raha hai."
    return None

def generate_upi_qr(amount: float, note: str = "Soni AI Pro Plan"):
    upi_url = f"upi://pay?pa={UPI_ID}&pn={urllib.parse.quote(UPI_NAME)}&am={amount:.2f}&mam={amount:.2f}&cu=INR&tn={urllib.parse.quote(note)}"
    qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(upi_url)}"
    return qr_api, upi_url

def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(filepath, data):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except:
        pass

def load_products():
    default_items = [
        {"id": 1, "name": "Women's Stylish Short Kurti", "price": 299, "img": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=400"},
        {"id": 2, "name": "Adjustable Aluminum Laptop Stand", "price": 449, "img": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400"},
        {"id": 3, "name": "Premium Handbag For Women", "price": 399, "img": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400"}
    ]
    prods = load_json(PRODUCTS_FILE, None)
    if not prods:
        save_json(PRODUCTS_FILE, default_items)
        return default_items
    return prods

users_db = load_json(USERS_FILE, {})
DEFAULT_USERS = {
    "sonijatin177@gmail.com": {"password": "admin", "plan": "pro"},
    "jatinson8489@gmail.com": {"password": "admin", "plan": "pro"},
    "jatinsoni32459@gmail.com": {"password": "admin", "plan": "pro"}
}
for u_k, u_v in DEFAULT_USERS.items():
    if u_k not in users_db:
        users_db[u_k] = u_v
save_json(USERS_FILE, users_db)

usage_db = load_json(USAGE_FILE, {})
payments_db = load_json(PAYMENTS_FILE, {})
orders_db = load_json(ORDERS_FILE, [])
secret_chat_db = load_json(SECRET_CHAT_FILE, [])
coupons_db = load_json(COUPONS_FILE, {"SONI": {"discount_percent": 50}})

url_user = st.query_params.get("user")
if url_user and url_user.strip().lower() in users_db:
    st.session_state.user = url_user.strip().lower()
elif url_user == "guest@soniai.com":
    st.session_state.user = "guest@soniai.com"
elif "user" not in st.session_state:
    st.session_state.user = None

if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Dashboard"
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_user_chat_count(email, users_dict, usage_dict):
    clean_email = email.strip().lower()
    user_info = users_dict.get(clean_email, {})
    if isinstance(user_info, dict) and user_info.get("plan") == "pro":
        return 0, True
    today_str = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
    user_usage = usage_dict.get(clean_email, {})
    if user_usage.get("date") != today_str:
        return 0, False
    return user_usage.get("count", 0), False

def increment_user_chat_count(email, usage_dict):
    clean_email = email.strip().lower()
    today_str = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
    user_usage = usage_dict.get(clean_email, {})
    if user_usage.get("date") != today_str:
        usage_dict[clean_email] = {"date": today_str, "count": 1}
    else:
        usage_dict[clean_email]["count"] = user_usage.get("count", 0) + 1
    save_json(USAGE_FILE, usage_dict)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: linear-gradient(120deg, #ffd9d6 0%, #ecd9fc 35%, #cfe4ff 70%, #d4f4ff 100%) !important;
        background-attachment: fixed !important;
        font-family: 'Inter', sans-serif !important;
        color: #1e293b !important;
    }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stSidebar"] {
        background: #f1f3f7 !important;
        border-right: 1px solid #e2e8f0 !important;
        padding-top: 15px !important;
        padding-left: 14px !important;
        padding-right: 14px !important;
    }
    .brand-title {
        display: flex; align-items: center; gap: 8px; font-size: 22px; font-weight: 700; color: #1e293b; margin-bottom: 24px; padding-left: 6px;
    }
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: #ffffff !important; border: 1px solid #cbd5e1 !important; text-align: left !important; justify-content: flex-start !important; border-radius: 12px !important; padding: 10px 16px !important; font-size: 14px !important; font-weight: 600 !important; color: #1e293b !important; box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important; margin-bottom: 12px !important; width: 100% !important;
    }
    .welcome-card {
        background: rgba(255, 255, 255, 0.95) !important; border: 1px solid #ffffff !important; border-radius: 16px; padding: 22px 26px; margin-bottom: 16px; box-shadow: 0 4px 15px rgba(0,0,0,0.04);
    }
    .pro-badge {
        background: linear-gradient(135deg, #f59e0b, #ef4444); color: white; font-weight: 700; font-size: 11px; padding: 3px 8px; border-radius: 8px; margin-left: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

HARDCODED_KEY = "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".strip()
client = Groq(api_key=HARDCODED_KEY, timeout=25.0)

CREATOR_REPLY = "Mujhe Jatin Soni ne banaya hai! Woh 16 saal ke hain, 12th class mein padhte hain aur Haryana ke Sirsa district ke Rori gaon ke rehne wale hain."
SYSTEM_PROMPT = "You are Soni AI, created by Jatin Soni. Direct, helpful, smart Hinglish/English answers."

def generate_ai_response(messages_list):
    try:
        resp = client.chat.completions.create(
            messages=messages_list,
            model="llama-3.1-8b-instant",
            temperature=0.6,
            max_tokens=650
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"

# Login
if not st.session_state.user:
    st.markdown("<div style='max-width:400px; margin:80px auto; background:white; padding:30px; border-radius:16px; text-align:center;'><h2>✨ Soni AI Login</h2></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            in_email = st.text_input("Email", placeholder="name@gmail.com").strip().lower()
            in_pass = st.text_input("Password", type="password").strip()
            if st.form_submit_button("Log In / Sign Up", use_container_width=True):
                if in_email:
                    if in_email not in users_db:
                        users_db[in_email] = {"password": in_pass, "plan": "free"}
                        save_json(USERS_FILE, users_db)
                    st.session_state.user = in_email
                    st.query_params["user"] = in_email
                    st.rerun()
    st.stop()

active_user = st.session_state.get("user", "guest@soniai.com").strip().lower()
user_handle = active_user.split("@")[0]
chats_used_today, is_pro_user = get_user_chat_count(active_user, users_db, usage_db)

# Sidebar
with st.sidebar:
    st.markdown('<div class="brand-title">✨ Soni AI</div>', unsafe_allow_html=True)
    if st.button("🏠 Dashboard"): st.session_state.current_tab = "Dashboard"; st.rerun()
    if st.button("🔒 VIP Room"): st.session_state.current_tab = "SecretRoom"; st.rerun()
    if st.button("👑 VIP Pro Tools"): st.session_state.current_tab = "VIP Tools"; st.rerun()
    if st.button("🛍️ Soni Shop"): st.session_state.current_tab = "Shop"; st.rerun()
    if st.button("💳 Billing / Upgrade"): st.session_state.current_tab = "Billing"; st.rerun()
    
    st.markdown(f"""
        <div style="padding:12px 6px; border-top:1px solid #cbd5e1; margin-top:30px;">
            <b>{user_handle}</b> <span class="pro-badge">{'PRO' if is_pro_user else 'FREE'}</span>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Logout"): st.session_state.user = None; st.query_params.clear(); st.rerun()

# Tabs
tab = st.session_state.current_tab
st.markdown(f"<h2 style='font-weight:700;'>{tab}</h2>", unsafe_allow_html=True)

if tab == "Dashboard":
    st.markdown(f'<div class="welcome-card"><h3>Welcome, {user_handle.capitalize()}!</h3></div>', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        st.write(f"**{msg['role'].capitalize()}**: {msg['content']}")
    
    user_input = st.chat_input("Ask Soni AI anything...")
    if user_input:
        if user_input.strip() == f"/admin {ADMIN_PIN}":
            st.session_state.current_tab = "AdminPanel"
            st.rerun()
        st.session_state.messages.append({"role": "user", "content": user_input})
        ans = generate_ai_response([{"role": "user", "content": user_input}])
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()

elif tab == "Billing":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 💳 Upgrade to Soni AI Pro (₹99)")
    
    qr_url, _ = generate_upi_qr(PREMIUM_PRICE, f"Pro - {active_user}")
    col_q, col_f = st.columns([4, 6])
    with col_q:
        st.image(qr_url, width=220, caption="Scan & Pay ₹99 via GPay/PhonePe/Paytm")
        st.markdown(f"**UPI ID:** `{UPI_ID}`")
    with col_f:
        with st.form("utr_form_direct"):
            st.markdown("#### 📝 UTR Number Dalein")
            utr_input = st.text_input("12-digit UTR / UPI Reference ID*", placeholder="Ex: 421098492019").strip()
            if st.form_submit_button("Submit UTR for Verification 📩", use_container_width=True):
                if len(utr_input) >= 8 and utr_input.isdigit():
                    payments_db[active_user] = {"utr": utr_input, "amount": PREMIUM_PRICE, "status": "pending"}
                    save_json(PAYMENTS_FILE, payments_db)
                    st.success("✅ UTR successfully submit ho gaya! Admin verify karke aapko Pro access dega.")
                else:
                    st.error("❌ Kripya valid 12-digit UTR number daalein!")
    st.markdown('</div>', unsafe_allow_html=True)

elif tab == "AdminPanel":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 👑 Admin Payment Approvals")
    if not payments_db:
        st.info("Koi pending UTR nahi hai.")
    for u_mail, p_info in list(payments_db.items()):
        st.write(f"👤 **{u_mail}** | UTR: `{p_info.get('utr')}`")
        if st.button(f"Approve {u_mail}", key=f"app_{u_mail}"):
            if u_mail in users_db:
                users_db[u_mail]["plan"] = "pro"
                save_json(USERS_FILE, users_db)
            del payments_db[u_mail]
            save_json(PAYMENTS_FILE, payments_db)
            st.success(f"{u_mail} approved as Pro!")
            st.rerun()
    if st.button("⬅️ Back"): st.session_state.current_tab = "Dashboard"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="welcome-card"><h3>Other sections available soon!</h3></div>', unsafe_allow_html=True)
