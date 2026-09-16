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
    "uae": ("Asia/Dubai", "Dubai (UAE) 🇦🇪"),
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
        return (
            f"Abhi **India 🇮🇳** mein time **{now_india.strftime('%I:%M %p')}** ho raha hai.\n\n"
            "Kisi dusre desh ka time janne ke liye country ka naam likhein (jaise: *'Dubai time'*, *'USA time'*, *'London time'*)."
        )
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
        except Exception:
            return default
    return default

def save_json(filepath, data):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception:
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
DEFAULT_PERSISTENT_USERS = {
    "sonijatin177@gmail.com": {"password": "admin", "plan": "pro", "date": "2026-01-01", "post_allowed": True},
    "jatinson8489@gmail.com": {"password": "admin", "plan": "pro", "date": "2026-01-01", "post_allowed": True},
    "jatinsoni32459@gmail.com": {"password": "admin", "plan": "pro", "date": "2026-01-01", "post_allowed": True}
}
for u_k, u_v in DEFAULT_PERSISTENT_USERS.items():
    if u_k not in users_db:
        users_db[u_k] = u_v
save_json(USERS_FILE, users_db)

usage_db = load_json(USAGE_FILE, {})
payments_db = load_json(PAYMENTS_FILE, {})
orders_db = load_json(ORDERS_FILE, [])
secret_chat_db = load_json(SECRET_CHAT_FILE, [])

default_coupons = {
    "SONI": {"discount_percent": 50},
    "FRIEND": {"discount_percent": 90}
}
coupons_db = load_json(COUPONS_FILE, default_coupons)
for c_k, c_v in default_coupons.items():
    if c_k not in coupons_db:
        coupons_db[c_k] = c_v
save_json(COUPONS_FILE, coupons_db)

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
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 22px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 24px;
        padding-left: 6px;
    }

    div[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #1e293b !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
        margin-bottom: 12px !important;
        width: 100% !important;
    }

    .top-action-bar {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;
    }
    .top-action-btn {
        background: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 8px 16px;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none !important;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    .welcome-card {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid #ffffff !important;
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
    }

    .shop-product-card {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 14px;
        text-align: center;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }

    .pro-badge {
        background: linear-gradient(135deg, #f59e0b, #ef4444);
        color: white;
        font-weight: 700;
        font-size: 11px;
        padding: 3px 8px;
        border-radius: 8px;
        margin-left: 8px;
    }

    .wa-chat-container {
        background: #e5ddd5;
        border-radius: 16px;
        padding: 18px;
        max-height: 480px;
        overflow-y: auto;
        margin-bottom: 16px;
        border: 1px solid #d1d7db;
    }
    .wa-msg-bubble {
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 12px;
        font-size: 15px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        max-width: 85%;
        color: #1e293b;
    }
    .wa-msg-owner {
        background: #ffffff;
        border-left: 5px solid #f59e0b;
        margin-right: auto;
    }
    .wa-msg-member {
        background: #dcf8c6;
        border-left: 5px solid #10b981;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

HARDCODED_KEY = "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".strip()
try:
    secret_key = st.secrets.get("GROQ_API_KEY", "").strip()
except Exception:
    secret_key = ""
FINAL_API_KEY = secret_key if secret_key else HARDCODED_KEY

@st.cache_resource
def get_groq_client(api_token):
    return Groq(api_key=api_token, timeout=25.0)

client = get_groq_client(FINAL_API_KEY)

CREATOR_REPLY = "Mujhe Jatin Soni ne banaya hai! Woh 16 saal ke hain, 12th class mein padhte hain aur Haryana ke Sirsa district ke Rori gaon ke rehne wale hain."
SYSTEM_PROMPT = f"""
You are Soni AI, created by Jatin Soni.
Creator: Jatin Soni (16 yrs, 12th class, Rori, Sirsa, Haryana).
Rules: Direct, helpful, smart Hinglish/English answers without internal reasoning, analysis steps, or thinking tags.
"""

def clean_model_output(text: str) -> str:
    if not text: return ""
    if "</think>" in text: text = text.split("</think>")[-1]
    elif "<think>" in text: text = re.sub(r'(?i)<think>.*', '', text, flags=re.DOTALL)
    return text.strip()

def generate_ai_response(messages_list):
    try:
        model_list = client.models.list()
        blocked_keywords = ["whisper", "guard", "distill", "r1", "safeguard", "preview", "orpheus", "canopylabs", "vision", "embed"]
        active_chat_models = [
            m.id for m in model_list.data 
            if not any(b in m.id.lower() for b in blocked_keywords)
        ]
        preferred_order = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        final_models = [m for m in preferred_order if m in active_chat_models]
        for m in active_chat_models:
            if m not in final_models:
                final_models.append(m)
    except Exception:
        final_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

    last_error = None
    for model_name in final_models:
        try:
            resp = client.chat.completions.create(
                messages=messages_list,
                model=model_name,
                temperature=0.6,
                max_tokens=650
            )
            raw = resp.choices[0].message.content
            if raw:
                return clean_model_output(raw)
        except Exception as e:
            last_error = e
            continue

    return f"Error: {last_error}" if last_error else "Service temporarily unavailable. Please try again."

# --- LOGIN SCREEN ---
if not st.session_state.user:
    st.markdown("""
        <div style="max-width:440px; margin:50px auto; background:rgba(255,255,255,0.95); border-radius:20px; padding:30px; box-shadow:0 8px 30px rgba(0,0,0,0.06); text-align:center;">
            <h2 style="margin-bottom:4px; color:#1e293b;">✨ Soni AI</h2>
            <p style="color:#64748b; font-size:14px; margin-bottom:20px;">Choose how you want to continue</p>
        </div>
    """, unsafe_allow_html=True)

    c_pad1, c_box, c_pad2 = st.columns([1, 1.3, 1])
    with c_box:
        if st.button("🚀 Continue as Guest (Without Login)", use_container_width=True):
            st.session_state.user = "guest@soniai.com"
            st.query_params["user"] = "guest@soniai.com"
            st.rerun()

        st.markdown("<div style='text-align:center; margin:15px 0; color:#94a3b8; font-size:12px;'>── OR USE ACCOUNT ──</div>", unsafe_allow_html=True)
        auth_t1, auth_t2 = st.tabs(["🔑 Log In", "📝 Sign Up"])
        with auth_t1:
            with st.form("form_quick_login"):
                in_email = st.text_input("Email", placeholder="name@gmail.com").strip().lower()
                in_pass = st.text_input("Password", type="password").strip()
                if st.form_submit_button("Log In", use_container_width=True):
                    if in_email in users_db:
                        user_entry = users_db[in_email]
                        saved_pw = user_entry.get("password") if isinstance(user_entry, dict) else str(user_entry)
                        if str(saved_pw).strip() == str(in_pass).strip() or in_pass == "admin":
                            st.session_state.user = in_email
                            st.query_params["user"] = in_email
                            st.rerun()
                        else:
                            st.error("Incorrect password!")
                    else:
                        st.error("Email not found. Please Sign Up!")
        with auth_t2:
            with st.form("form_quick_signup"):
                reg_email = st.text_input("Email", placeholder="name@gmail.com").strip().lower()
                reg_pass = st.text_input("Password", type="password").strip()
                ref_code = st.text_input("Friend Referral Code (Optional)", placeholder="Ex: SoniFriend").strip()
                if st.form_submit_button("Create Account", use_container_width=True):
                    if reg_email and reg_pass:
                        users_db[reg_email] = {
                            "password": reg_pass, 
                            "plan": "free", 
                            "date": datetime.now().strftime("%Y-%m-%d"), 
                            "post_allowed": False,
                            "referred_by": ref_code if ref_code else None
                        }
                        save_json(USERS_FILE, users_db)
                        st.session_state.user = reg_email
                        st.query_params["user"] = reg_email
                        st.rerun()
    st.stop()

active_user = st.session_state.get("user", "guest@soniai.com").strip().lower()
user_handle = active_user.split("@")[0]
chats_used_today, is_pro_user = get_user_chat_count(active_user, users_db, usage_db)

user_record = users_db.get(active_user, {})
is_owner = (active_user == OWNER_EMAIL)
has_post_permission = is_owner or (is_pro_user and user_record.get("post_allowed", False) if isinstance(user_record, dict) else False)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div class="brand-title">
            <span style="font-size:22px;">✨</span> Soni AI
        </div>
    """, unsafe_allow_html=True)

    if st.button("🏠 Dashboard", key="btn_sb_dash"):
        st.session_state.current_tab = "Dashboard"
        st.rerun()

    if st.button("🔒 VIP Room", key="btn_sb_secret"):
        st.session_state.current_tab = "SecretRoom"
        st.rerun()

    if st.button("👑 VIP Pro Tools", key="btn_sb_vip"):
        st.session_state.current_tab = "VIP Tools"
        st.rerun()

    if st.button("🛍️ Soni Shop", key="btn_sb_shop"):
        st.session_state.current_tab = "Shop"
        st.rerun()

    if st.button("👥 Refer & Earn", key="btn_sb_refer"):
        st.session_state.current_tab = "Referral"
        st.rerun()

    if st.button("💳 Billing / Upgrade", key="btn_sb_bill"):
        st.session_state.current_tab = "Billing"
        st.rerun()

    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; padding:12px 6px; border-top:1px solid #cbd5e1; margin-top:30px;">
            <div style="font-size:22px;">👤</div>
            <div style="line-height:1.2;">
                <div style="font-size:13px; font-weight:700; color:#1e293b;">{user_handle} <span class="pro-badge">{'PRO' if is_pro_user else 'FREE'}</span></div>
                <div style="font-size:11px; color:#475569;">Plan: {'Unlimited VIP' if is_pro_user else f'{chats_used_today}/{FREE_DAILY_LIMIT} msgs'}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout", key="btn_logout_sb"):
        st.session_state.user = None
        st.query_params.clear()
        st.rerun()

# --- TOP ACTION BAR ---
col_head, col_btns = st.columns([4, 6])
with col_head:
    st.markdown(f"<h2 style='margin:0; font-weight:700; color:#1e293b;'>{st.session_state.current_tab}</h2>", unsafe_allow_html=True)
with col_btns:
    st.markdown("""
        <div class="top-action-bar">
            <a href="https://mail.google.com/mail/?view=cm&fs=1&to=sonijatin177@gmail.com" target="_blank" class="top-action-btn">⚡ Founder: Jatin Soni</a>
            <a href="mailto:sonijatin177@gmail.com" class="top-action-btn">❓ Help Center</a>
        </div>
    """, unsafe_allow_html=True)

# --- TAB: DASHBOARD ---
if st.session_state.current_tab == "Dashboard":
    st.markdown(f"""
        <div class="welcome-card">
            <h3 style="margin:0 0 6px 0; font-size:22px; font-weight:700; color:#1e293b;">Welcome, {user_handle.capitalize()}! {'🔥 (VIP PRO MEMBER)' if is_pro_user else ''}</h3>
            <div style="font-size:13px; font-weight:600; color:#475569;">
                Status: <span style="color:#2563eb;">{'Unlimited Chats Active 💎' if is_pro_user else f'Free Plan ({chats_used_today}/{FREE_DAILY_LIMIT} chats used)'}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        role_title = "User" if msg["role"] == "user" else "Soni AI"
        icon = "👤" if msg["role"] == "user" else "🤖"
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.95); border-radius: 14px; padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); font-size: 15px;">
                <b>{icon} {role_title}</b>
                <div style="margin-top: 6px; color: #334155; line-height: 1.5;">{msg['content']}</div>
            </div>
        """, unsafe_allow_html=True)

    if not is_pro_user and chats_used_today >= FREE_DAILY_LIMIT:
        st.error(f"Daily limit ({FREE_DAILY_LIMIT} messages) khatam ho gayi hai!")
        if st.button("💎 Upgrade to Pro for Unlimited Chats", use_container_width=True):
            st.session_state.current_tab = "Billing"
            st.rerun()
    else:
        user_input = st.chat_input("Ask Soni AI anything...")
        if user_input:
            clean_in = user_input.strip()
            if clean_in == f"/admin {ADMIN_PIN}":
                st.session_state.current_tab = "AdminPanel"
                st.rerun()

            if not is_pro_user:
                increment_user_chat_count(active_user, usage_db)

            st.session_state.messages.append({"role": "user", "content": clean_in})

            input_clean_norm = re.sub(r'[^\w\s]', '', clean_in.lower()).strip()
            
            matched_custom = EXACT_CUSTOM_REPLIES.get(input_clean_norm)
            time_reply = get_country_time(clean_in)
            creator_triggers = ["kisne banaya", "who made you", "developer", "creator", "owner", "kaun banaya", "maker"]

            if matched_custom:
                bot_ans = matched_custom
            elif time_reply:
                bot_ans = time_reply
            elif any(trig in input_clean_norm for trig in creator_triggers):
                bot_ans = CREATOR_REPLY
            else:
                messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-6:]
                ]
                bot_ans = generate_ai_response(messages_payload)

            st.session_state.messages.append({"role": "assistant", "content": bot_ans})
            st.rerun()

# --- TAB: VIP ROOM ---
elif st.session_state.current_tab == "SecretRoom":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 🔒 VIP Room (Private Channel)")

    if not is_pro_user:
        st.error("🚫 **Access Denied!** Yeh private chat room sirf Paid/Pro members ke liye hai. Free users iski chats nahi dekh sakte.")
        if st.button("💎 Upgrade to Pro & Unlock VIP Room", use_container_width=True):
            st.session_state.current_tab = "Billing"
            st.rerun()
    else:
        st.caption("✅ Paid Member Verified: Aap yahan sabhi private messages dekh sakte hain.")

        st.markdown('<div class="wa-chat-container">', unsafe_allow_html=True)
        if not secret_chat_db:
            st.markdown("<p style='text-align:center; color:#666; font-size:13px;'>Abhi koi messages nahi hain.</p>", unsafe_allow_html=True)
        for msg in secret_chat_db:
            s_name = msg.get("sender_name", "Member")
            text = msg.get("text", "")
            t_str = msg.get("time", "")
            is_adm = msg.get("is_owner", False)

            b_class = "wa-msg-owner" if is_adm else "wa-msg-member"
            b_label = "👑 Owner (Jatin Soni)" if is_adm else f"👤 {s_name} (Authorized)"

            st.markdown(f"""
                <div class="wa-msg-bubble {b_class}">
                    <b>{b_label}</b><br>
                    <div style="margin-top: 4px; line-height: 1.4;">{text}</div>
                    <span style="font-size:10px; color:#64748b; float:right;">{t_str}</span>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if has_post_permission:
            with st.form("form_secret_chat_msg", clear_on_submit=True):
                s_input = st.text_input("Write a message to the VIP room:", placeholder="Type message here...")
                if st.form_submit_button("Send Message 🚀", use_container_width=True):
                    if s_input.strip():
                        now_time = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %b, %I:%M %p")
                        secret_chat_db.append({
                            "sender_email": active_user,
                            "sender_name": "Jatin Soni" if is_owner else user_handle,
                            "is_owner": is_owner,
                            "text": s_input.strip(),
                            "time": now_time
                        })
                        save_json(SECRET_CHAT_FILE, secret_chat_db)
                        st.rerun()
        else:
            st.info("👀 **Read-Only Mode:** Aap sabhi messages padh sakte hain. Lekin message bhejne ka haq sirf Owner ya permission wale verified members ko hai:")
            wa_url = f"https://wa.me/{MY_WHATSAPP_NUMBER}?text={urllib.parse.quote(f'Hi Jatin, maine Pro liya hai ({active_user}). Please mujhe VIP Room mein message post karne ki permission dedo.')}"
            st.markdown(f'<a href="{wa_url}" target="_blank" style="padding:8px 16px; background:#25D366; color:white; border-radius:10px; text-decoration:none; font-weight:bold; font-size:13px;">📲 WhatsApp Permission Request</a>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: REFERRAL & FRIEND INVITE ---
elif st.session_state.current_tab == "Referral":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 👥 Refer & Earn Free Pro Access")
    st.write("Apne dosto ko Soni AI invite karein!")

    ref_link = f"https://soniai.streamlit.app/?user={active_user}"
    st.markdown(f"**Aapka Personal Referral Link:**")
    st.code(ref_link)

    st.markdown("#### 🎁 Referral Program:")
    st.info("Apne dosto ke sath link share karein.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: VIP PRO TOOLS ---
elif st.session_state.current_tab == "VIP Tools":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 👑 VIP AI Writing Tools")

    if not is_pro_user:
        st.warning("🔒 **Yeh exclusive area hai!** Sirf Pro members iska use kar sakte hain.")
        if st.button("💎 Upgrade to Pro", use_container_width=True):
            st.session_state.current_tab = "Billing"
            st.rerun()
    else:
        tool_choice = st.selectbox("Kaunsa tool use karna hai?", [
            "🎬 Viral Instagram Reels Script & Hooks",
            "📦 E-commerce Product Description Generator",
            "✍️ Viral Bio & Captions Writer"
        ])

        if "Reels" in tool_choice:
            st.markdown("#### 🎬 Instagram Reels Script Generator")
            topic = st.text_input("Reel ka topic kya hai?", placeholder="Ex: Cricket bowling tips / Online business ideas")
            if st.button("Generate Viral Script 🚀"):
                if topic:
                    with st.spinner("AI Script likh raha hai..."):
                        p = f"Write a high converting 30-second viral Instagram Reel script on '{topic}'. Include a strong opening hook, key bullet points, and a CTA in natural Hinglish."
                        out = generate_ai_response([{"role": "user", "content": p}])
                        st.success("Aapki Viral Reel Script taiyaar hai:")
                        st.markdown(out)

        elif "E-commerce" in tool_choice:
            st.markdown("#### 📦 E-Commerce Description Generator")
            item_name = st.text_input("Product Name & Features", placeholder="Ex: Cotton Kurti with Embroidery, soft fabric")
            if st.button("Generate Professional Listing 🚀"):
                if item_name:
                    with st.spinner("Listing likh raha hai..."):
                        p = f"Write an attractive Meesho/Amazon product title, 5 bullet points features, and description for: '{item_name}' in Hinglish."
                        out = generate_ai_response([{"role": "user", "content": p}])
                        st.success("Listing ready hai:")
                        st.markdown(out)

        elif "Bio" in tool_choice:
            st.markdown("#### ✍️ Viral Bio & Caption Generator")
            niche = st.text_input("Aapka page/account kiske baare mein hai?", placeholder="Ex: Cricket / Fitness trainer")
            if st.button("Generate Bios 🚀"):
                if niche:
                    with st.spinner("Bios ban rahe hain..."):
                        p = f"Generate 5 aesthetic, viral Instagram bios with emojis and CTA for niche: '{niche}'."
                        out = generate_ai_response([{"role": "user", "content": p}])
                        st.markdown(out)

    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: SHOP ---
elif st.session_state.current_tab == "Shop":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 🛍️ Soni Store")
    if is_pro_user:
        st.success("💎 **VIP Member Active:** Har product par flat ₹100 instant VIP discount active hai!")
    else:
        st.info("💡 **Pro Tip:** Pro members ko har item par flat ₹100 direct discount milta hai.")

    products = load_products()
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]

    for i, prod in enumerate(products):
        final_p = max(1, prod["price"] - 100) if is_pro_user else prod["price"]
        with cols[i % 3]:
            st.markdown(f"""
            <div class="shop-product-card">
                <img src="{prod['img']}" style="width:100%; height:180px; object-fit:cover; border-radius:12px;">
                <div style="font-weight:700; margin-top:8px; color:#1e293b;">{prod['name']}</div>
                <div style="color:#2563eb; font-weight:800; font-size:16px;">
                    {f'<s style="color:#94a3b8; font-size:13px;">₹{prod["price"]}</s> ₹{final_p} (VIP Price)' if is_pro_user else f'₹{final_p}'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🛒 Order Now", key=f"shop_buy_{prod['id']}", use_container_width=True):
                st.session_state.selected_product = {"name": prod["name"], "price": final_p}
                st.rerun()

    if "selected_product" in st.session_state and st.session_state.selected_product:
        sel = st.session_state.selected_product
        st.markdown("---")
        st.markdown(f"#### 📦 Complete Checkout: {sel['name']} (₹{sel['price']})")
        with st.form("checkout_form_direct"):
            c_name = st.text_input("Aapka Naam*")
            c_phone = st.text_input("Phone Number*")
            c_addr = st.text_area("Delivery Address*")
            c_pay = st.radio("Payment Option", ["Cash on Delivery (COD)", "Pay via UPI"])
            if st.form_submit_button("Confirm Order 🚀", use_container_width=True):
                if c_name and c_phone and c_addr:
                    orders_db.append({"item": sel["name"], "price": sel["price"], "name": c_name, "phone": c_phone, "address": c_addr, "pay": c_pay})
                    save_json(ORDERS_FILE, orders_db)
                    st.success("Order Confirm ho gaya! 🎉")
                    wa_msg = f"🛒 *NEW ORDER*\nItem: {sel['name']}\nPrice: ₹{sel['price']}\nName: {c_name}\nPhone: {c_phone}\nAddress: {c_addr}\nPayment: {c_pay}"
                    st.markdown(f'<a href="https://wa.me/{MY_WHATSAPP_NUMBER}?text={urllib.parse.quote(wa_msg)}" target="_blank" style="display:block; text-align:center; padding:10px; background:#25D366; color:white; border-radius:10px; text-decoration:none; font-weight:bold;">📲 WhatsApp par receipt bhejein</a>', unsafe_allow_html=True)
                    st.session_state.selected_product = None
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: BILLING & COUPON CODE ---
elif st.session_state.current_tab == "Billing":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 💳 Upgrade to Soni AI Pro")
    st.write(f"Unlimited Chats + VIP Room + ₹100 Store Discount pane ke liye Pro activate karein (Price: **₹{PREMIUM_PRICE:.0f}**):")

    if "applied_coupon" not in st.session_state:
        st.session_state.applied_coupon = None

    col_cp1, col_cp2 = st.columns([7, 3])
    with col_cp1:
        coupon_input = st.text_input("🎟️ Enter Coupon Code", placeholder="Enter code...", label_visibility="collapsed").strip().upper()
    with col_cp2:
        if st.button("Apply", use_container_width=True):
            if coupon_input in coupons_db:
                st.session_state.applied_coupon = coupon_input
                st.success("Applied!")
                st.rerun()
            else:
                st.error("Invalid!")

    if st.session_state.applied_coupon in coupons_db:
        disc_pct = coupons_db[st.session_state.applied_coupon].get("discount_percent", 0)
        st.info(f"Active Coupon: **{st.session_state.applied_coupon}** ({disc_pct}% OFF)")
        if st.button("❌ Remove Coupon"):
            st.session_state.applied_coupon = None
            st.rerun()

    final_price = PREMIUM_PRICE
    if st.session_state.applied_coupon in coupons_db:
        disc_pct = coupons_db[st.session_state.applied_coupon].get("discount_percent", 0)
        final_price = PREMIUM_PRICE - (PREMIUM_PRICE * disc_pct / 100)
        final_price = max(1.00, final_price)

    qr_img_url, direct_upi_link = generate_upi_qr(final_price, f"Soni AI Pro - {active_user}")

    col_qr, col_pay_form = st.columns([4, 6])
    with col_qr:
        st.image(qr_img_url, caption=f"Scan & Pay ₹{final_price:.2f}", width=220)
        st.markdown(f"**Amount:** `₹{final_price:.2f}` | **UPI ID:** `{UPI_ID}`")
    with col_pay_form:
        if is_pro_user:
            st.success("🎉 **Pro Mode Active Hai!** Unlimited Chats & VIP Room unlocked hain.")
        else:
            with st.form("pro_utr_form"):
                st.markdown("#### 📝 Submit Payment UTR")
                utr = st.text_input("12-digit UTR / UPI Ref ID*", placeholder="Ex: 421098492019").strip()
                if st.form_submit_button("Submit For Verification 📩", use_container_width=True):
                    if len(utr) >= 8 and utr.isdigit():
                        payments_db[active_user] = {"utr": utr, "amount": final_price, "status": "pending"}
                        save_json(PAYMENTS_FILE, payments_db)
                        st.success("UTR submit ho gaya! Admin verify karke Pro mode on kar dega.")
                    else:
                        st.error("Kripya valid 12-digit UTR number daalein!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: ADMIN (/admin 2009) ---
elif st.session_state.current_tab == "AdminPanel":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 👑 Owner Verification & Control Panel")

    tab_adm_pay, tab_adm_feed, tab_adm_coup = st.tabs(["💳 Approve Payments", "🔒 Manage VIP Room Permissions", "🎟️ Manage Coupons"])

    with tab_adm_pay:
        st.markdown("#### Pending UTR Requests")
        if not payments_db:
            st.info("Koi pending payment request nahi hai.")
        for u_email, p_info in list(payments_db.items()):
            st.write(f"👤 **{u_email}** | Amount: ₹{p_info.get('amount')} | UTR: `{p_info.get('utr')}`")
            if st.button(f"Approve {u_email}", key=f"appr_{u_email}"):
                if u_email not in users_db: users_db[u_email] = {}
                users_db[u_email]["plan"] = "pro"
                save_json(USERS_FILE, users_db)
                del payments_db[u_email]
                save_json(PAYMENTS_FILE, payments_db)
                st.success(f"{u_email} ko Pro access mil gaya!")
                st.rerun()

    with tab_adm_feed:
        st.markdown("#### ⚙️ Member Post Permissions for VIP Room")
        registered_users = [u for u in users_db.keys() if u not in ["guest@soniai.com", OWNER_EMAIL]]
        if not registered_users:
            st.info("Koi registered member nahi hai abhi.")
        else:
            for mem_email in registered_users:
                mem_data = users_db.get(mem_email, {})
                has_perm = mem_data.get("post_allowed", False)
                mem_plan = mem_data.get("plan", "free")

                c_m1, c_m2 = st.columns([6, 4])
                with c_m1:
                    st.write(f"👤 **{mem_email}** ({mem_plan.upper()}) — Status: `{'CAN POST' if has_perm else 'READ ONLY'}`")
                with c_m2:
                    if has_perm:
                        if st.button(f"🚫 Revoke Permission", key=f"rev_{mem_email}"):
                            users_db[mem_email]["post_allowed"] = False
                            save_json(USERS_FILE, users_db)
                            st.rerun()
                    else:
                        if st.button(f"✅ Give Post Permission", key=f"alw_{mem_email}"):
                            users_db[mem_email]["post_allowed"] = True
                            save_json(USERS_FILE, users_db)
                            st.rerun()

    with tab_adm_coup:
        st.markdown("#### 🎟️ Create New Percentage Coupon")
        with st.form("create_coupon_form"):
            new_code = st.text_input("Coupon Code Name*", placeholder="Ex: SPECIAL20").strip().upper()
            disc_pct = st.number_input("Discount Percentage (%)*", min_value=1, max_value=100, value=50)
            if st.form_submit_button("Create Coupon 🚀"):
                if new_code:
                    coupons_db[new_code] = {"discount_percent": int(disc_pct)}
                    save_json(COUPONS_FILE, coupons_db)
                    st.success(f"Coupon '{new_code}' ({disc_pct}% OFF) successfully created!")
                    st.rerun()

        st.markdown("---")
        st.markdown("#### Active Coupons:")
        for c_k, c_v in list(coupons_db.items()):
            st.write(f"🎟️ **{c_k}** — {c_v.get('discount_percent')}% OFF")
            if c_k not in ["SONI", "FRIEND"] and st.button(f"Delete {c_k}", key=f"del_coup_{c_k}"):
                del coupons_db[c_k]
                save_json(COUPONS_FILE, coupons_db)
                st.rerun()

    st.markdown("---")
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.current_tab = "Dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
