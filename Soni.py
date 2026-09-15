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
PROJECTS_FILE = "projects_database.json"
USAGE_FILE = "user_usage_database.json"

UPI_QR_URL = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa=8307940340@ptyes&pn=Jatin%20Soni&am=1.00&cu=INR"
MY_WHATSAPP_NUMBER = "918307940340"

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

# --- USAGE TRACKER (100 CHATS / DAY) ---
def get_user_chat_count(email, users_dict, usage_dict):
    # Check if Pro Mode
    user_info = users_dict.get(email, {})
    if isinstance(user_info, dict) and user_info.get("plan") == "pro":
        return 0, True  # (Count, is_pro)

    today_str = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
    user_usage = usage_dict.get(email, {})
    
    if user_usage.get("date") != today_str:
        return 0, False
    return user_usage.get("count", 0), False

def increment_user_chat_count(email, usage_dict):
    today_str = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
    user_usage = usage_dict.get(email, {})
    if user_usage.get("date") != today_str:
        usage_dict[email] = {"date": today_str, "count": 1}
    else:
        usage_dict[email]["count"] = user_usage.get("count", 0) + 1
    save_json(USAGE_FILE, usage_dict)

users_db = load_json(USERS_FILE, {})
chats_db = load_json(CHATS_FILE, {})
projects_db = load_json(PROJECTS_FILE, ["AI Assistant Bot", "E-Commerce Recommender", "Customer Support Workflow"])
usage_db = load_json(USAGE_FILE, {})

query_params = st.query_params

if "user" not in st.session_state:
    stored_user = query_params.get("user")
    if stored_user:
        st.session_state.user = stored_user
    else:
        st.session_state.user = None

if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Dashboard"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "user", "content": "hy", "time": "12:36 AM"},
        {"role": "assistant", "content": "Hi! How can I help you today?", "time": "12:36 AM"}
    ]

# --- THEME STYLING ---
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

    [data-testid="stHeader"] {
        background: transparent !important;
    }

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
        border: 1px solid #e2e8f0 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #334155 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
        margin-bottom: 12px !important;
        width: 100% !important;
    }

    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: #f8fafc !important;
        border-color: #cbd5e1 !important;
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
        color: #334155 !important;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 8px 16px;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none !important;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }

    .welcome-card {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid #ffffff !important;
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }

    div.stButton > button {
        background: #ffffff !important;
        color: #334155 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
    }

    .avatar-red {
        width: 36px;
        height: 36px;
        background: #ef4444;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 16px;
    }
    .avatar-ai {
        width: 36px;
        height: 36px;
        background: #f59e0b;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    }

    div[data-testid="stChatInput"] {
        border-radius: 14px !important;
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04) !important;
    }

    .login-glass-card {
        max-width: 460px;
        margin: 50px auto;
        background: rgba(255, 255, 255, 0.75);
        border: 1px solid #ffffff;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.06);
        backdrop-filter: blur(15px);
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
client = Groq(api_key=FINAL_API_KEY, timeout=25.0)

CREATOR_REPLY = "Mujhe Jatin Soni ne banaya hai! Woh 16 saal ke hain, 12th class mein padhte hain aur Haryana ke Sirsa district ke Rori gaon ke rehne wale hain."
CUSTOM_ANSWERS = {"what is skb": "Santosh kulcha bandar", "skb": "Santosh kulcha bandar"}
CURRENT_DATE_STR = datetime.now().strftime("%d %B %Y")
SYSTEM_PROMPT = f"""
You are Soni AI, created by Jatin Soni.
Creator: Jatin Soni (16 yrs, 12th class, Rori, Sirsa, Haryana).
Today: {CURRENT_DATE_STR}. Year: 2026.
Rules:
1. Direct, clear answers without meta text or thinking tokens.
2. Reply in concise natural Hinglish or English.
3. If asked who made you, reply: "{CREATOR_REPLY}"
"""

def clean_model_output(text: str) -> str:
    if not text: return ""
    if "</think>" in text: text = text.split("</think>")[-1]
    elif "<think>" in text: text = re.sub(r'(?i)<think>.*', '', text, flags=re.DOTALL)
    text = re.sub(r'(?i)^\s*(analyze user input|identify key constraints|formulate response|draft response).*?\n\n', '', text, flags=re.DOTALL)
    return text.strip()

# --- LOGIN / GUEST SCREEN ---
if not st.session_state.user:
    st.markdown("""
        <div class="login-glass-card">
            <h2 style="text-align:center; margin-bottom:4px;">✨ Soni AI</h2>
            <p style="text-align:center; color:#64748b; font-size:14px; margin-bottom:20px;">Welcome! Choose how you want to continue</p>
        </div>
    """, unsafe_allow_html=True)

    c_pad1, c_box, c_pad2 = st.columns([1, 1.3, 1])
    with c_box:
        if st.button("🚀 Continue as Guest (Without Login)", use_container_width=True):
            st.session_state.user = "guest@soniai.com"
            st.query_params["user"] = "guest@soniai.com"
            st.rerun()

        st.markdown("<div style='text-align:center; margin:15px 0; color:#94a3b8; font-size:12px;'>── OR USE EMAIL ACCOUNT ──</div>", unsafe_allow_html=True)

        auth_t1, auth_t2 = st.tabs(["🔑 Log In", "📝 Sign Up"])
        with auth_t1:
            with st.form("form_quick_login"):
                in_email = st.text_input("Email", placeholder="name@gmail.com").strip().lower()
                in_pass = st.text_input("Password", type="password").strip()
                if st.form_submit_button("Log In", use_container_width=True):
                    users_db = load_json(USERS_FILE, {})
                    if not in_email or not in_pass:
                        st.error("Please enter both email and password.")
                    elif in_email not in users_db:
                        st.error("This email is not registered. Please sign up first.")
                    else:
                        user_entry = users_db[in_email]
                        saved_pw = user_entry.get("password") if isinstance(user_entry, dict) else str(user_entry)
                        if str(saved_pw).strip() == str(in_pass).strip():
                            st.session_state.user = in_email
                            st.query_params["user"] = in_email
                            st.success("Login Successful!")
                            st.rerun()
                        else:
                            st.error("Incorrect password! Please re-check your password.")

        with auth_t2:
            with st.form("form_quick_signup"):
                reg_email = st.text_input("Your Email", placeholder="name@gmail.com").strip().lower()
                reg_pass = st.text_input("Create Password", type="password").strip()
                if st.form_submit_button("Create Account", use_container_width=True):
                    users_db = load_json(USERS_FILE, {})
                    if not reg_email or not reg_pass:
                        st.error("Please fill all details.")
                    elif reg_email in users_db:
                        st.error("Email already registered! Log in instead.")
                    else:
                        users_db[reg_email] = {
                            "password": reg_pass,
                            "plan": "free",
                            "date": datetime.now().strftime("%Y-%m-%d")
                        }
                        save_json(USERS_FILE, users_db)
                        st.session_state.user = reg_email
                        st.query_params["user"] = reg_email
                        st.success("Account created successfully!")
                        st.rerun()

    st.stop()

active_user = st.session_state.get("user", "guest@soniai.com")
user_handle = active_user.split("@")[0]

# Compute current limits
chats_used_today, is_pro_user = get_user_chat_count(active_user, users_db, usage_db)
plan_badge = "PRO" if is_pro_user else f"{chats_used_today}/100 Free"

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div class="brand-title">
            <span style="font-size:22px;">✨</span> Soni AI <span style="font-size:14px; margin-left:auto; color:#94a3b8;">«</span>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🏠 Dashboard", key="btn_sb_dash"):
        st.session_state.current_tab = "Dashboard"
        st.rerun()

    if st.button("🕒 Chat History", key="btn_sb_hist"):
        st.session_state.current_tab = "History"
        st.rerun()

    if st.button("📁 Projects", key="btn_sb_proj"):
        st.session_state.current_tab = "Projects"
        st.rerun()

    if st.button("⚡ Integrations", key="btn_sb_int"):
        st.session_state.current_tab = "Integrations"
        st.rerun()

    if st.button("💳 Billing / Upgrade", key="btn_sb_bill"):
        st.session_state.current_tab = "Billing"
        st.rerun()

    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; padding:12px 6px; border-top:1px solid #e2e8f0; margin-top:50px;">
            <div style="width:34px; height:34px; background:#e2e8f0; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:16px;">👤</div>
            <div style="line-height:1.2; overflow:hidden;">
                <div style="font-size:13px; font-weight:600; color:#1e293b;">
                    {active_user}
                    <span class="pro-badge">{plan_badge}</span>
                </div>
                <div style="font-size:11px; color:#64748b;">Plan: {'Unlimited Pro' if is_pro_user else 'Free (100 chats/day)'}</div>
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
            <a href="/?action=toggle_shop" target="_self" class="top-action-btn">🛒 Soni Shop</a>
            <a href="mailto:sonijatin177@gmail.com?subject=Help%20Soni%20AI" class="top-action-btn">❓ Help Center</a>
        </div>
    """, unsafe_allow_html=True)

# Welcome Card
st.markdown(f"""
    <div class="welcome-card">
        <h3 style="margin:0 0 6px 0; font-size:22px; font-weight:700; color:#0f172a;">
            Welcome, {user_handle.capitalize()}! {'🔥 (PRO ACTIVE)' if is_pro_user else ''}
        </h3>
        <div style="font-size:13px; font-weight:600; color:#475569;">
            Today's Usage: <span style="color:#0f172a;">{'Unlimited' if is_pro_user else f'{chats_used_today}/100 chats'}</span> &nbsp;&nbsp;|&nbsp;&nbsp; 
            Plan Status: <span style="color:#2563eb;">{'VIP Pro Tier 💎' if is_pro_user else 'Free Tier (₹1 to Unlock Pro)'}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# 4 Action Buttons
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("💬 Start New Chat", use_container_width=True):
        if len(st.session_state.messages) > 1:
            timestamp_id = datetime.now().strftime("Chat - %d %b, %I:%M %p")
            if active_user not in chats_db:
                chats_db[active_user] = {}
            chats_db[active_user][timestamp_id] = st.session_state.messages
            save_json(CHATS_FILE, chats_db)
        st.session_state.messages = []
        st.session_state.current_tab = "Dashboard"
        st.rerun()

with c2:
    if st.button("🕒 Review History", use_container_width=True):
        st.session_state.current_tab = "History"
        st.rerun()

with c3:
    if st.button("🏛️ Browse Marketplace", use_container_width=True):
        st.session_state.current_tab = "Marketplace"
        st.rerun()

with c4:
    if st.button("⚡ Upgrade to Pro (₹1)", use_container_width=True):
        st.session_state.current_tab = "Billing"
        st.rerun()

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# --- TAB 1: DASHBOARD ---
if st.session_state.current_tab == "Dashboard":
    for msg in st.session_state.messages:
        time_tag = msg.get("time", datetime.now().strftime("%I:%M %p"))
        if msg["role"] == "user":
            st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.8); border: 1px solid #ffffff; border-radius: 14px; padding: 12px 18px; margin-bottom: 10px; display: flex; align-items: flex-start; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; align-items: flex-start; gap: 12px;">
                        <div class="avatar-red">👤</div>
                        <div>
                            <div style="font-weight: 700; font-size: 14px; color: #0f172a;">User</div>
                            <div style="font-size: 14px; color: #334155; margin-top: 2px;">{msg['content']}</div>
                        </div>
                    </div>
                    <div style="font-size: 11px; color: #94a3b8;">{time_tag} ↩</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.95); border: 1px solid #ffffff; border-radius: 14px; padding: 12px 18px; margin-bottom: 10px; display: flex; align-items: flex-start; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,0,0,0.02);">
                    <div style="display: flex; align-items: flex-start; gap: 12px;">
                        <div class="avatar-ai">🤖</div>
                        <div>
                            <div style="font-weight: 700; font-size: 14px; color: #0f172a;">Soni AI</div>
                            <div style="font-size: 14px; color: #334155; margin-top: 2px;">{msg['content']}</div>
                        </div>
                    </div>
                    <div style="font-size: 11px; color: #94a3b8;">{time_tag} ↩</div>
                </div>
            """, unsafe_allow_html=True)

    # Check limit before showing chat input
    if not is_pro_user and chats_used_today >= 100:
        st.error("🚫 **Aaj ki 100 free chats limit poori ho chuki hai!**")
        st.info("💡 Unlimited chats use karne ke liye sirf **₹1 mein Pro Mode** activate karein.")
        if st.button("💎 Unlock Unlimited Pro Now (₹1)", use_container_width=True):
            st.session_state.current_tab = "Billing"
            st.rerun()
    else:
        user_input = st.chat_input(f"Ask Soni AI anything... ({'Unlimited' if is_pro_user else f'{100 - chats_used_today} left today'})")

        if user_input:
            clean_input = user_input.strip()
            now_stamp = datetime.now().strftime("%I:%M %p")

            # Increment count for free tier
            if not is_pro_user:
                increment_user_chat_count(active_user, usage_db)

            st.session_state.messages.append({"role": "user", "content": clean_input, "time": now_stamp})

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
                    sanitized = [{"role": m["role"], "content": clean_model_output(m["content"])} for m in st.session_state.messages[-6:] if clean_model_output(m["content"])]
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
                        except Exception:
                            continue

                    bot_reply = clean_model_output(raw_reply) if raw_reply else "Main samajh gaya. Aage batayein?"
                except Exception as e:
                    bot_reply = f"Error details: {e}"

            st.session_state.messages.append({"role": "assistant", "content": bot_reply, "time": datetime.now().strftime("%I:%M %p")})
            st.rerun()

# --- TAB 2: BILLING & ₹1 PRO PLAN WITH SCANNER ---
elif st.session_state.current_tab == "Billing":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 💳 Upgrade to Soni AI Pro Tier (₹1 Only)")
    st.markdown("Rozana ki 100 chat limit hatane aur **Unlimited Pro Mode** activate karne ke liye QR scan karein:")

    col_qr, col_pay_form = st.columns([4, 6])
    with col_qr:
        st.image(UPI_QR_URL, caption="Scan with PhonePe / Paytm / GPay (₹1)", width=220)
        st.markdown("**UPI ID:** `8307940340@ptyes`")
        st.markdown("**Amount:** ₹1 (One-Time / Lifetime)")

    with col_pay_form:
        st.markdown("#### ✅ Payment Verification")
        if is_pro_user:
            st.success("🎉 **Aapka Pro Mode pehle se active hai!** Aap unlimited chats use kar sakte hain.")
        else:
            st.write("QR par ₹1 pay karne ke baad transaction details enter karein:")
            with st.form("form_activate_pro"):
                utr_number = st.text_input("12-digit UTR / UPI Ref ID*", placeholder="Ex: 421098492019").strip()
                pay_app = st.selectbox("Kaunse app se pay kiya?", ["PhonePe", "Paytm", "Google Pay (GPay)", "Other UPI"])
                submit_pro = st.form_submit_button("🚀 Activate Pro Mode Now", use_container_width=True)

                if submit_pro:
                    if len(utr_number) >= 4:
                        # Activate Pro in database
                        if active_user not in users_db:
                            users_db[active_user] = {}
                        if isinstance(users_db[active_user], dict):
                            users_db[active_user]["plan"] = "pro"
                            users_db[active_user]["utr"] = utr_number
                        else:
                            users_db[active_user] = {"password": str(users_db[active_user]), "plan": "pro", "utr": utr_number}
                        
                        save_json(USERS_FILE, users_db)

                        # WhatsApp notification link
                        wa_msg = f"⚡ *NEW PRO SUBSCRIPTION*\nUser: {active_user}\nUTR: {utr_number}\nApp: {pay_app}\nAmount: ₹1"
                        wa_link = f"https://wa.me/{MY_WHATSAPP_NUMBER}?text={urllib.parse.quote(wa_msg)}"

                        st.success("🎉 Mubarak! Aapka Pro Mode successfully activate ho gaya hai!")
                        st.markdown(f'<a href="{wa_link}" target="_blank" style="display:inline-block; margin-top:8px; padding:8px 16px; background:#25D366; color:white; border-radius:10px; text-decoration:none; font-weight:bold;">📲 WhatsApp par receipt confirm karein</a>', unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error("Kripya valid Transaction / UTR number daalein.")

    st.markdown("---")
    st.markdown("#### 📊 Account Usage Stats")
    st.write(f"Account: **{active_user}** | Plan: **{'PRO UNLIMITED' if is_pro_user else 'FREE (100/day)'}**")
    st.progress(1.0 if is_pro_user else min(chats_used_today / 100.0, 1.0))
    st.caption(f"Today's Chats Used: {'Unlimited' if is_pro_user else f'{chats_used_today} / 100'}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: HISTORY ---
elif st.session_state.current_tab == "History":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 🕒 Saved Chat History")
    user_saved_chats = chats_db.get(active_user, {})

    if not user_saved_chats:
        st.info("Abhi tak koi purani chat save nahi hui hai. Nayi chat karein!")
    else:
        for session_id, history in list(user_saved_chats.items()):
            col_info, col_load, col_del = st.columns([7, 1.5, 1.5])
            with col_info:
                first_query = history[0]['content'] if history else "Chat"
                st.markdown(f"**{session_id}** — *\"{first_query[:35]}...\"*")
            with col_load:
                if st.button("Load Chat", key=f"load_{session_id}"):
                    st.session_state.messages = history
                    st.session_state.current_tab = "Dashboard"
                    st.rerun()
            with col_del:
                if st.button("Delete", key=f"del_{session_id}"):
                    del chats_db[active_user][session_id]
                    save_json(CHATS_FILE, chats_db)
                    st.rerun()
            st.markdown("---")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 4: PROJECTS ---
elif st.session_state.current_tab == "Projects":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 📁 My AI Projects")
    
    col_p1, col_p2 = st.columns([8, 2])
    with col_p1:
        new_proj_name = st.text_input("New Project Name", placeholder="Ex: Voice Assistant")
    with col_p2:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        if st.button("➕ Add Project", use_container_width=True):
            if new_proj_name.strip():
                projects_db.append(new_proj_name.strip())
                save_json(PROJECTS_FILE, projects_db)
                st.rerun()

    st.markdown("---")
    for idx, p_name in enumerate(projects_db):
        col_item, col_action = st.columns([8.5, 1.5])
        with col_item:
            st.markdown(f"🔹 **{p_name}** `Active`")
        with col_action:
            if st.button("Remove", key=f"del_proj_{idx}"):
                projects_db.pop(idx)
                save_json(PROJECTS_FILE, projects_db)
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 5: INTEGRATIONS ---
elif st.session_state.current_tab == "Integrations":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### ⚡ Integrations")
    st.success("🟢 **Groq LLM Engine:** Connected & Active")
    st.info("🟢 **SMTP Email Engine:** Connected (`smtp.gmail.com`)")
    st.warning("🟡 **UPI Auto-Pay Webhook:** Active")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 6: MARKETPLACE ---
elif st.session_state.current_tab == "Marketplace":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 🏛️ Soni Store & Marketplace")
    st.markdown("Shop kholne ke liye top bar ke **🛒 Soni Shop** button par click karein.")
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.current_tab = "Dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
