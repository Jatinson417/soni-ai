import streamlit as st
from groq import Groq
import urllib.parse
import json
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Soni AI", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

BG_IMAGE_URL = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"
UPI_QR_URL = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa=8307940340@ptyes&pn=Jatin%20Soni&cu=INR"
UPI_ID = "8307940340@ptyes"
UPI_NAME = "Jatin Soni"
MY_WHATSAPP_NUMBER = "918307940340"
ADMIN_PIN = "2009"
FREE_DAILY_LIMIT = 50
OWNER_EMAIL = "sonijatin177@gmail.com"

CHATS_FILE = "chats_history_database.json"
USERS_FILE = "users_database.json"
USAGE_FILE = "user_usage_database.json"
PAYMENTS_FILE = "pending_payments_database.json"
PRODUCTS_FILE = "products_database.json"
ORDERS_FILE = "orders_database.json"
SECRET_CHAT_FILE = "vip_secret_chat_room.json"

CUSTOM_REPLIES = {
    "what is skb": "Santosh Kulcha Bhandar",
    "skb kya hai": "Santosh Kulcha Bhandar",
    "skb": "Santosh Kulcha Bhandar"
}

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

# Persistent Login Check
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
    f"""
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background: url("{BG_IMAGE_URL}") no-repeat center center fixed !important;
        background-size: cover !important;
        height: 100vh !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important;
        color: #ffffff !important;
    }}

    [data-testid="stSidebar"] {{
        background: rgba(10, 10, 18, 0.88) !important;
        backdrop-filter: blur(14px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
        padding-top: 20px !important;
    }}

    header, [data-testid="stHeader"], footer, [data-testid="stBottom"], [data-testid="stBottom"] > div {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    .brand-title {{
        font-size: 24px;
        font-weight: 800;
        color: #00e5ff;
        margin-bottom: 24px;
        padding-left: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    div[data-testid="stSidebar"] div[data-testid="stButton"] > button {{
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        margin-bottom: 10px !important;
        width: 100% !important;
        backdrop-filter: blur(8px);
    }}
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {{
        background: rgba(0, 229, 255, 0.2) !important;
        border-color: #00e5ff !important;
        color: #00e5ff !important;
    }}

    .top-action-bar {{
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }}
    .founder-badge {{
        background: rgba(0, 0, 0, 0.75);
        color: #00e5ff !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none !important;
        border: 1px solid rgba(0, 229, 255, 0.4);
        backdrop-filter: blur(8px);
    }}

    .glass-card {{
        background: rgba(15, 15, 25, 0.78) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 18px;
        padding: 22px 26px;
        margin-bottom: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    }}

    [data-testid="stChatMessage"] {{
        background-color: rgba(255, 255, 255, 0.93) !important;
        border-radius: 14px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }}
    [data-testid="stChatMessage"] p {{
        color: #111111 !important;
    }}

    [data-testid="stChatInput"] {{
        background: rgba(255, 255, 255, 0.96) !important;
        border-radius: 35px !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
    }}

    .shop-product-card {{
        background: rgba(0, 0, 0, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(12px);
        border-radius: 18px;
        padding: 14px;
        text-align: center;
        margin-bottom: 20px;
    }}

    .secret-chat-box {{
        background: rgba(10, 10, 18, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 18px;
        max-height: 460px;
        overflow-y: auto;
        margin-bottom: 16px;
    }}
    .msg-bubble-owner {{
        background: rgba(255, 215, 0, 0.15);
        border-left: 4px solid #ffd700;
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 10px;
        color: #fff;
    }}
    .msg-bubble-member {{
        background: rgba(0, 229, 255, 0.15);
        border-left: 4px solid #00e5ff;
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 10px;
        color: #fff;
    }}
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
Rules: Direct, helpful, concise Hinglish/English answers without internal reasoning or thinking tags.
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
                temperature=0.5,
                max_tokens=550
            )
            raw = resp.choices[0].message.content
            if raw:
                return clean_model_output(raw)
        except Exception as e:
            last_error = e
            continue

    return f"Error: {last_error}" if last_error else "Server busy hai, kripya thodi der baad try karein."

# --- LOGIN MODAL (DARK THEME) ---
if not st.session_state.user:
    st.markdown("""
        <div style="max-width:440px; margin:70px auto; background:rgba(18, 18, 28, 0.9); border:1px solid rgba(255,255,255,0.15); border-radius:20px; padding:30px; backdrop-filter:blur(15px); text-align:center; box-shadow:0 10px 40px rgba(0,0,0,0.6);">
            <h2 style="color:#00e5ff; margin-bottom:4px;">🤖 Soni AI</h2>
            <p style="color:#bbb; font-size:14px; margin-bottom:20px;">Apna account choose karein</p>
        </div>
    """, unsafe_allow_html=True)

    c_pad1, c_box, c_pad2 = st.columns([1, 1.4, 1])
    with c_box:
        if st.button("🚀 Continue as Guest (Bina Login)", use_container_width=True):
            st.session_state.user = "guest@soniai.com"
            st.query_params["user"] = "guest@soniai.com"
            st.rerun()

        st.markdown("<div style='text-align:center; margin:15px 0; color:#888; font-size:12px;'>── YA ACCOUNT LOGIN KAREIN ──</div>", unsafe_allow_html=True)
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
                        st.error("Email nahi mila. Kripya Sign Up karein!")
        with auth_t2:
            with st.form("form_quick_signup"):
                reg_email = st.text_input("Email", placeholder="name@gmail.com").strip().lower()
                reg_pass = st.text_input("Password", type="password").strip()
                if st.form_submit_button("Create Account", use_container_width=True):
                    if reg_email and reg_pass:
                        users_db[reg_email] = {"password": reg_pass, "plan": "free", "date": datetime.now().strftime("%Y-%m-%d"), "post_allowed": False}
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

# --- SIDEBAR (DARK THEME) ---
with st.sidebar:
    st.markdown("""
        <div class="brand-title">
            <span>🤖</span> Soni AI
        </div>
    """, unsafe_allow_html=True)

    if st.button("🏠 AI Chat", key="btn_sb_dash"):
        st.session_state.current_tab = "Dashboard"
        st.rerun()

    if st.button("🔒 VIP Secret Room", key="btn_sb_secret"):
        st.session_state.current_tab = "SecretRoom"
        st.rerun()

    if st.button("👑 VIP Pro Tools", key="btn_sb_vip"):
        st.session_state.current_tab = "VIP Tools"
        st.rerun()

    if st.button("🛍️ Soni Shop", key="btn_sb_shop"):
        st.session_state.current_tab = "Shop"
        st.rerun()

    if st.button("💳 Upgrade to Pro", key="btn_sb_bill"):
        st.session_state.current_tab = "Billing"
        st.rerun()

    st.markdown(f"""
        <div style="padding:14px 8px; border-top:1px solid rgba(255,255,255,0.15); margin-top:50px;">
            <div style="font-size:14px; font-weight:700; color:#00e5ff;">👤 {user_handle}</div>
            <div style="font-size:12px; color:#aaa; margin-top:3px;">Status: <b style="color:{'#ffd700' if is_pro_user else '#00e5ff'};">{'PRO MEMBER' if is_pro_user else f'{chats_used_today}/{FREE_DAILY_LIMIT} Used'}</b></div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout", key="btn_logout_sb"):
        st.session_state.user = None
        st.query_params.clear()
        st.rerun()

# --- TOP ACTION BAR ---
col_head, col_btns = st.columns([5, 5])
with col_head:
    st.markdown(f"<h2 style='margin:0; font-weight:700; color:#ffffff;'>{st.session_state.current_tab}</h2>", unsafe_allow_html=True)
with col_btns:
    st.markdown("""
        <div class="top-action-bar">
            <a href="https://mail.google.com/mail/?view=cm&fs=1&to=sonijatin177@gmail.com" target="_blank" class="founder-badge">⚡ Founder: Jatin Soni</a>
        </div>
    """, unsafe_allow_html=True)

# --- TAB: DASHBOARD (ORIGINAL DARK AI CHAT) ---
if st.session_state.current_tab == "Dashboard":
    col_c1, col_c2 = st.columns([7, 3])
    with col_c1:
        st.markdown(f"**Welcome, {user_handle.capitalize()}!** {'💎 (Pro Member)' if is_pro_user else ''}")
    with col_c2:
        if st.button("🧹 Clear Chat", key="btn_clear_chat"):
            st.session_state.messages = []
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if not is_pro_user and chats_used_today >= FREE_DAILY_LIMIT:
        st.error(f"Daily free limit ({FREE_DAILY_LIMIT} messages) poori ho gayi hai!")
        if st.button("💎 Upgrade to Pro for Unlimited Chats", use_container_width=True):
            st.session_state.current_tab = "Billing"
            st.rerun()
    else:
        user_input = st.chat_input("Ask Soni AI anything...")
        if user_input:
            clean_input = user_input.strip()
            if clean_input == f"/admin {ADMIN_PIN}":
                st.session_state.current_tab = "AdminPanel"
                st.rerun()

            if not is_pro_user:
                increment_user_chat_count(active_user, usage_db)

            st.session_state.messages.append({"role": "user", "content": clean_input})
            with st.chat_message("user"):
                st.markdown(clean_input)

            input_clean_norm = re.sub(r'[^\w\s]', '', clean_input.lower()).strip()
            matched_custom = None
            for trigger_k, trigger_v in CUSTOM_REPLIES.items():
                norm_trig = re.sub(r'[^\w\s]', '', trigger_k.lower()).strip()
                if norm_trig in input_clean_norm or input_clean_norm in norm_trig:
                    matched_custom = trigger_v
                    break

            creator_triggers = ["kisne banaya", "who made you", "developer", "creator", "owner", "kaun banaya", "maker"]

            if matched_custom:
                bot_reply = matched_custom
            elif any(trig in input_clean_norm for trig in creator_triggers):
                bot_reply = CREATOR_REPLY
            else:
                messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-6:]
                ]
                bot_reply = generate_ai_response(messages_payload)

            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            with st.chat_message("assistant"):
                st.markdown(bot_reply)

            st.rerun()

# --- TAB: VIP SECRET ROOM (DARK GLASSROOM) ---
elif st.session_state.current_tab == "SecretRoom":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🔒 VIP Secret Room (Private Channel)")

    if not is_pro_user:
        st.error("🚫 **Access Denied!** Yeh room sirf Paid/Pro members ke liye hai. Free users iski chats nahi dekh sakte.")
        st.write("VIP chats dekhne ke liye account upgrade karein:")
        if st.button("💎 Upgrade to Pro & Unlock Room", use_container_width=True):
            st.session_state.current_tab = "Billing"
            st.rerun()
    else:
        st.caption("✅ Paid Member Verified: Aap sabhi private messages padh sakte hain.")

        st.markdown('<div class="secret-chat-box">', unsafe_allow_html=True)
        if not secret_chat_db:
            st.markdown("<p style='text-align:center; color:#888;'>Abhi koi messages nahi hain.</p>", unsafe_allow_html=True)
        for msg in secret_chat_db:
            s_name = msg.get("sender_name", "Member")
            text = msg.get("text", "")
            t_str = msg.get("time", "")
            is_adm = msg.get("is_owner", False)

            b_class = "msg-bubble-owner" if is_adm else "msg-bubble-member"
            b_label = "👑 Owner (Jatin Soni)" if is_adm else f"👤 {s_name}"

            st.markdown(f"""
                <div class="{b_class}">
                    <b>{b_label}</b><br>
                    {text}<br>
                    <span style="font-size:10px; color:#aaa; float:right;">{t_str}</span>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if has_post_permission:
            with st.form("form_secret_chat_msg", clear_on_submit=True):
                s_input = st.text_input("Secret message type karein:", placeholder="Type here...")
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
            st.info("👀 **Read-Only Mode:** Aap sabhi messages padh sakte hain. Message bhej sirf Owner ya permitted members hi sakte hain. Permission ke liye Owner ko WhatsApp karein:")
            wa_url = f"https://wa.me/{MY_WHATSAPP_NUMBER}?text={urllib.parse.quote(f'Hi Jatin, maine Pro liya hai ({active_user}). Please mujhe VIP Secret Room mein message permission dedo.')}"
            st.markdown(f'<a href="{wa_url}" target="_blank" style="padding:8px 16px; background:#25D366; color:white; border-radius:10px; text-decoration:none; font-weight:bold;">📲 Request Permission on WhatsApp</a>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: VIP PRO TOOLS ---
elif st.session_state.current_tab == "VIP Tools":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 👑 VIP AI Writing Tools")

    if not is_pro_user:
        st.warning("🔒 **Locked:** Yeh tools sirf Pro members ke liye hain.")
        if st.button("💎 Upgrade to Pro", use_container_width=True):
            st.session_state.current_tab = "Billing"
            st.rerun()
    else:
        tool_choice = st.selectbox("Tool select karein:", [
            "🎬 Viral Instagram Reels Script & Hooks",
            "📦 E-commerce Product Description Generator",
            "✍️ Viral Bio & Captions Writer"
        ])

        if "Reels" in tool_choice:
            st.markdown("#### 🎬 Instagram Reels Script")
            topic = st.text_input("Reel ka topic:", placeholder="Ex: Fast bowling technique / Business tips")
            if st.button("Generate Viral Script 🚀"):
                if topic:
                    with st.spinner("AI likh raha hai..."):
                        p = f"Write a high converting 30-second viral Instagram Reel script on '{topic}'. Include a strong opening hook and CTA in Hinglish."
                        out = generate_ai_response([{"role": "user", "content": p}])
                        st.markdown(out)

        elif "E-commerce" in tool_choice:
            st.markdown("#### 📦 E-Commerce Description")
            item_name = st.text_input("Product details:", placeholder="Ex: Cotton short kurti, breathable fabric")
            if st.button("Generate Professional Listing 🚀"):
                if item_name:
                    with st.spinner("AI listing create kar raha hai..."):
                        p = f"Write a Meesho/Amazon product title, 5 bullet points, and description for: '{item_name}' in Hinglish."
                        out = generate_ai_response([{"role": "user", "content": p}])
                        st.markdown(out)

        elif "Bio" in tool_choice:
            st.markdown("#### ✍️ Viral Bio Generator")
            niche = st.text_input("Aapki niche/category:", placeholder="Ex: Cricket / Fitness")
            if st.button("Generate Bios 🚀"):
                if niche:
                    with st.spinner("Bios create ho rahe hain..."):
                        p = f"Generate 5 viral Instagram bios with emojis and CTA for niche: '{niche}'."
                        out = generate_ai_response([{"role": "user", "content": p}])
                        st.markdown(out)

    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: SHOP ---
elif st.session_state.current_tab == "Shop":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🛍️ Soni Store")
    if is_pro_user:
        st.success("💎 **VIP Active:** Har product par flat ₹100 instant VIP discount!")
    else:
        st.info("💡 **Tip:** Pro members ko har item par flat ₹100 direct discount milta hai.")

    products = load_products()
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]

    for i, prod in enumerate(products):
        final_p = max(1, prod["price"] - 100) if is_pro_user else prod["price"]
        with cols[i % 3]:
            st.markdown(f"""
            <div class="shop-product-card">
                <img src="{prod['img']}" style="width:100%; height:180px; object-fit:cover; border-radius:12px;">
                <div style="font-weight:700; margin-top:8px; color:#fff;">{prod['name']}</div>
                <div style="color:#00e5ff; font-weight:800; font-size:16px;">
                    {f'<s style="color:#888; font-size:13px;">₹{prod["price"]}</s> ₹{final_p}' if is_pro_user else f'₹{final_p}'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🛒 Buy Now", key=f"shop_buy_{prod['id']}", use_container_width=True):
                st.session_state.selected_product = {"name": prod["name"], "price": final_p}
                st.rerun()

    if "selected_product" in st.session_state and st.session_state.selected_product:
        sel = st.session_state.selected_product
        st.markdown("---")
        st.markdown(f"#### 📦 Checkout: {sel['name']} (₹{sel['price']})")
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

# --- TAB: BILLING (PRO UPGRADE) ---
elif st.session_state.current_tab == "Billing":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 💳 Upgrade to Soni AI Pro")
    st.write("Unlimited Chats + VIP Secret Room Access + ₹100 Store Discount:")

    final_price = 49.00
    qr_img_url, direct_upi_link = generate_upi_qr(final_price, f"Soni AI Pro - {active_user}")

    col_qr, col_pay_form = st.columns([4, 6])
    with col_qr:
        st.image(qr_img_url, caption=f"Scan & Pay ₹{final_price:.2f}", width=220)
        st.markdown(f"**Amount:** `₹{final_price:.2f}` | **UPI:** `{UPI_ID}`")
    with col_pay_form:
        if is_pro_user:
            st.success("🎉 **Pro Active Hai!** Aap unlimited chat aur Secret Room use kar sakte hain.")
        else:
            with st.form("pro_utr_form"):
                utr = st.text_input("12-digit UTR / UPI Ref ID*", placeholder="Ex: 421098492019").strip()
                if st.form_submit_button("Submit For Verification 📩", use_container_width=True):
                    if len(utr) >= 8 and utr.isdigit():
                        payments_db[active_user] = {"utr": utr, "amount": final_price, "status": "pending"}
                        save_json(PAYMENTS_FILE, payments_db)
                        st.success("UTR submit ho gaya! Admin jald verify karke activate kar dega.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: ADMIN (/admin 2009) ---
elif st.session_state.current_tab == "AdminPanel":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 👑 Owner Verification & Control Panel")

    tab_adm_pay, tab_adm_feed = st.tabs(["💳 Approve Payments", "🔒 Manage Secret Room Permissions"])

    with tab_adm_pay:
        st.markdown("#### Pending Payment Requests")
        if not payments_db:
            st.info("Koi pending payment nahi hai.")
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
        st.markdown("#### ⚙️ Secret Room Member Permissions")
        registered_users = [u for u in users_db.keys() if u not in ["guest@soniai.com", OWNER_EMAIL]]
        if not registered_users:
            st.info("Koi registered member nahi hai.")
        else:
            for mem_email in registered_users:
                mem_data = users_db.get(mem_email, {})
                has_perm = mem_data.get("post_allowed", False)
                mem_plan = mem_data.get("plan", "free")

                c_m1, c_m2 = st.columns([6, 4])
                with c_m1:
                    st.write(f"👤 **{mem_email}** ({mem_plan.upper()}) — Post: `{'ALLOWED' if has_perm else 'READ ONLY'}`")
                with c_m2:
                    if has_perm:
                        if st.button(f"🚫 Revoke", key=f"rev_{mem_email}"):
                            users_db[mem_email]["post_allowed"] = False
                            save_json(USERS_FILE, users_db)
                            st.rerun()
                    else:
                        if st.button(f"✅ Allow", key=f"alw_{mem_email}"):
                            users_db[mem_email]["post_allowed"] = True
                            save_json(USERS_FILE, users_db)
                            st.rerun()

        st.markdown("---")
        if st.button("Clear Secret Room Chat"):
            save_json(SECRET_CHAT_FILE, [])
            st.success("Chat clear ho gayi!")
            st.rerun()

    st.markdown("---")
    if st.button("⬅️ Back to AI Chat"):
        st.session_state.current_tab = "Dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
