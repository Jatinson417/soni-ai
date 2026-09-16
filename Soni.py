import streamlit as st
from groq import Groq
import urllib.parse
import json
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Soni AI", page_icon="🤖", layout="centered")

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
WA_GROUP_FILE = "whatsapp_group_chats.json"

CUSTOM_REPLIES = {
    "what is skb": "Santosh Kulcha Bhandar",
    "skb kya hai": "Santosh Kulcha Bhandar",
    "skb": "Santosh Kulcha Bhandar"
}

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
wa_group_chats = load_json(WA_GROUP_FILE, [])

# Persistent Login Check from Query Params
url_user = st.query_params.get("user")
if url_user and url_user.strip().lower() in users_db:
    st.session_state.user = url_user.strip().lower()
elif url_user == "guest@soniai.com":
    st.session_state.user = "guest@soniai.com"
elif "user" not in st.session_state:
    st.session_state.user = None

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "chat"

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
    }}

    [data-testid="stSidebar"] {{
        display: none !important;
    }}

    header, [data-testid="stHeader"], footer, [data-testid="stBottom"], [data-testid="stBottom"] > div {{
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    .top-right-stack {{
        position: fixed;
        top: 75px;
        right: 25px;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 10px;
        z-index: 99999;
    }}

    .top-badge-link {{
        background: rgba(0, 0, 0, 0.75);
        color: #ffffff !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        display: inline-block;
        cursor: pointer;
    }}
    .top-badge-link:hover {{
        transform: scale(1.03);
    }}

    h1, h2, h3, p {{
        color: #ffffff;
    }}

    .main .block-container {{
        max-width: 820px !important;
        padding-top: 50px !important;
        padding-bottom: 140px !important;
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
        box-shadow: 0 6px 20px rgba(0,0,0,0.2) !important;
        border: 1px solid rgba(0,0,0,0.06) !important;
    }}

    /* WhatsApp Group Window Style */
    .wa-group-box {{
        background: #0b141a !important;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.15);
        padding: 16px;
        margin-bottom: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.7);
    }}
    .wa-bubble-owner {{
        background: #005c4b;
        color: #e9edef;
        padding: 8px 14px;
        border-radius: 10px 10px 0px 10px;
        margin-left: auto;
        margin-bottom: 8px;
        max-width: 80%;
        font-size: 13px;
    }}
    .wa-bubble-member {{
        background: #202c33;
        color: #e9edef;
        padding: 8px 14px;
        border-radius: 10px 10px 10px 0px;
        margin-right: auto;
        margin-bottom: 8px;
        max-width: 80%;
        font-size: 13px;
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
Rules: Direct, smart Hinglish/English answers without internal reasoning or thinking tags.
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
        active_chat_models = [m.id for m in model_list.data if not any(b in m.id.lower() for b in blocked_keywords)]
        preferred_order = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        final_models = [m for m in preferred_order if m in active_chat_models]
        for m in active_chat_models:
            if m not in final_models:
                final_models.append(m)
    except Exception:
        final_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

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
        except Exception:
            continue
    return "Service temporarily busy. Please try again."

# --- LOGIN SCREEN ---
if not st.session_state.user:
    st.title("🤖 Soni AI")
    st.markdown("""
        <div style="background:rgba(18, 18, 28, 0.9); border:1px solid rgba(255,255,255,0.15); border-radius:18px; padding:24px; text-align:center; margin-top:20px;">
            <h3>Welcome to Soni AI</h3>
            <p style="color:#aaa; font-size:13px;">Login karein ya bina login ke guest continue karein</p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 Continue as Guest (Bina Login)"):
        st.session_state.user = "guest@soniai.com"
        st.query_params["user"] = "guest@soniai.com"
        st.rerun()

    t_log, t_sign = st.tabs(["🔑 Log In", "📝 Sign Up"])
    with t_log:
        with st.form("form_login_main"):
            in_email = st.text_input("Email").strip().lower()
            in_pass = st.text_input("Password", type="password").strip()
            if st.form_submit_button("Log In"):
                if in_email in users_db:
                    saved_pw = users_db[in_email].get("password") if isinstance(users_db[in_email], dict) else str(users_db[in_email])
                    if str(saved_pw).strip() == str(in_pass).strip() or in_pass == "admin":
                        st.session_state.user = in_email
                        st.query_params["user"] = in_email
                        st.rerun()
                    else:
                        st.error("Incorrect password!")
                else:
                    st.error("Email nahi mila!")
    with t_sign:
        with st.form("form_sign_main"):
            reg_email = st.text_input("Email").strip().lower()
            reg_pass = st.text_input("Password", type="password").strip()
            if st.form_submit_button("Create Account"):
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

# --- TOP ACTION BUTTONS (FLOATING) ---
st.markdown(f"""
    <div class="top-right-stack">
        <a href="https://mail.google.com/mail/?view=cm&fs=1&to=sonijatin177@gmail.com" target="_blank" class="top-badge-link" style="color:#00e5ff !important; border-color:rgba(0,229,255,0.4);">
            ⚡ Founder: Jatin Soni
        </a>
    </div>
""", unsafe_allow_html=True)

# Top Bar Controls
col_t1, col_t2, col_t3, col_t4 = st.columns([3, 3, 3, 2])
with col_t1:
    if st.button("💬 Main AI Chat"):
        st.session_state.view_mode = "chat"
        st.rerun()
with col_t2:
    if st.button("👥 WhatsApp VIP Group"):
        st.session_state.view_mode = "group"
        st.rerun()
with col_t3:
    if st.button("💎 Upgrade Pro"):
        st.session_state.view_mode = "pro"
        st.rerun()
with col_t4:
    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.query_params.clear()
        st.rerun()

# ==================== VIEW 1: WHATSAPP VIP GROUP ====================
if st.session_state.view_mode == "group":
    st.markdown("## 👥 Soni AI VIP WhatsApp Group")
    
    # 1. Free Users Cannot View
    if not is_pro_user:
        st.error("🔒 **Yeh group sirf Pro/Paid members ke liye hai!** Free members group messages nahi dekh sakte.")
        if st.button("💎 Upgrade to Pro (Unlock Group)"):
            st.session_state.view_mode = "pro"
            st.rerun()
    else:
        st.caption(f"Logged in as: {user_handle} {'👑 (Group Admin)' if is_owner else '👤 (Member)'}")

        # Group Messages Feed
        st.markdown('<div class="wa-group-box">', unsafe_allow_html=True)
        if not wa_group_chats:
            st.markdown("<p style='text-align:center; color:#8696a0; font-size:13px;'>Group conversation shuru karein...</p>", unsafe_allow_html=True)
        
        for msg in wa_group_chats:
            s_name = msg.get("sender_name", "Member")
            text = msg.get("text", "")
            t_str = msg.get("time", "")
            is_adm = msg.get("is_owner", False)

            b_class = "wa-bubble-owner" if is_adm else "wa-bubble-member"
            tag_color = "#25d366" if is_adm else "#53bdeb"
            role_label = "👑 Owner / Admin" if is_adm else "👤 Member"

            st.markdown(f"""
                <div class="{b_class}">
                    <div style="font-size:11px; font-weight:700; color:{tag_color}; margin-bottom:2px;">{s_name} • {role_label}</div>
                    <div>{text}</div>
                    <div style="font-size:9px; color:#8696a0; text-align:right; margin-top:2px;">{t_str}</div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Sending message: Only Owner or Permitted Members
        if has_post_permission:
            with st.form("form_wa_group_send", clear_on_submit=True):
                g_input = st.text_input("Group message likhein...", placeholder="Type a message...")
                if st.form_submit_button("Send 🚀", use_container_width=True):
                    if g_input.strip():
                        now_time = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%I:%M %p")
                        wa_group_chats.append({
                            "sender_email": active_user,
                            "sender_name": "Jatin Soni" if is_owner else user_handle,
                            "is_owner": is_owner,
                            "text": g_input.strip(),
                            "time": now_time
                        })
                        save_json(WA_GROUP_FILE, wa_group_chats)
                        st.rerun()
        else:
            st.info("🔒 **Only Admins can send messages:** Aap group ke sabhi messages padh sakte hain. Lekin message bhejne ki permission sirf Owner aur approved members ko hai.")

# ==================== VIEW 2: PRO UPGRADE ====================
elif st.session_state.view_mode == "pro":
    st.markdown("## 💎 Soni AI Pro Upgrade")
    st.write("VIP WhatsApp Group access aur unlimited AI chats paane ke liye:")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.image(UPI_QR_URL, caption="Scan & Pay ₹49 via Any UPI", width=200)
        st.markdown(f"**UPI ID:** `{UPI_ID}`")
    with col_p2:
        with st.form("form_utr_submit"):
            utr = st.text_input("12-digit UPI Ref / UTR No.*", placeholder="Ex: 421098492019").strip()
            if st.form_submit_button("Submit For Approval"):
                if len(utr) >= 8 and utr.isdigit():
                    payments_db[active_user] = {"utr": utr, "amount": 49, "status": "pending"}
                    save_json(PAYMENTS_FILE, payments_db)
                    st.success("UTR submit ho gaya! Admin verify karke Pro enable kar dega.")

# ==================== VIEW 3: ADMIN PANEL (/admin 2009) ====================
elif st.session_state.view_mode == "admin":
    st.markdown("## 👑 Admin Control Panel")
    
    tab_p, tab_perms = st.tabs(["💳 Pending Payments", "👥 WhatsApp Group Message Permissions"])
    
    with tab_p:
        if not payments_db:
            st.info("Koi payment pending nahi hai.")
        for u_em, p_dt in list(payments_db.items()):
            st.write(f"👤 **{u_em}** | UTR: `{p_dt.get('utr')}`")
            if st.button(f"Approve {u_em}", key=f"appr_{u_em}"):
                if u_em not in users_db: users_db[u_em] = {}
                users_db[u_em]["plan"] = "pro"
                save_json(USERS_FILE, users_db)
                del payments_db[u_em]
                save_json(PAYMENTS_FILE, payments_db)
                st.success(f"{u_em} Pro ban gaya!")
                st.rerun()

    with tab_perms:
        st.markdown("#### Kaun group mein bol sakta hai:")
        all_reg = [u for u in users_db.keys() if u not in ["guest@soniai.com", OWNER_EMAIL]]
        for m_em in all_reg:
            m_dt = users_db.get(m_em, {})
            can_p = m_dt.get("post_allowed", False)
            c1, c2 = st.columns([6, 4])
            with c1:
                st.write(f"**{m_em}** — `{'CAN SEND' if can_p else 'READ ONLY'}`")
            with c2:
                if can_p:
                    if st.button(f"Revoke", key=f"rev_{m_em}"):
                        users_db[m_em]["post_allowed"] = False
                        save_json(USERS_FILE, users_db)
                        st.rerun()
                else:
                    if st.button(f"Allow", key=f"alw_{m_em}"):
                        users_db[m_em]["post_allowed"] = True
                        save_json(USERS_FILE, users_db)
                        st.rerun()

# ==================== VIEW 4: MAIN AI CHAT (CLEAN ORIGINAL) ====================
else:
    st.title("🤖 Soni AI")
    st.caption(f"Logged in as: {user_handle} ({'PRO' if is_pro_user else f'{chats_used_today}/{FREE_DAILY_LIMIT} chats'})")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if not is_pro_user and chats_used_today >= FREE_DAILY_LIMIT:
        st.error(f"Daily limit ({FREE_DAILY_LIMIT} msgs) complete ho gayi hai!")
        if st.button("💎 Upgrade to Pro"):
            st.session_state.view_mode = "pro"
            st.rerun()
    else:
        user_input = st.chat_input("Ask Soni AI anything...")
        if user_input:
            clean_in = user_input.strip()
            
            if clean_in == f"/admin {ADMIN_PIN}":
                st.session_state.view_mode = "admin"
                st.rerun()

            if not is_pro_user:
                increment_user_chat_count(active_user, usage_db)

            st.session_state.messages.append({"role": "user", "content": clean_in})
            with st.chat_message("user"):
                st.markdown(clean_in)

            norm_in = re.sub(r'[^\w\s]', '', clean_in.lower()).strip()
            
            matched_custom = None
            for trigger_k, trigger_v in CUSTOM_REPLIES.items():
                norm_trig = re.sub(r'[^\w\s]', '', trigger_k.lower()).strip()
                if norm_trig in norm_in or norm_in in norm_trig:
                    matched_custom = trigger_v
                    break

            creator_triggers = ["kisne banaya", "who made you", "developer", "creator", "owner", "kaun banaya", "maker"]

            if matched_custom:
                bot_ans = matched_custom
            elif any(trig in norm_in for trig in creator_triggers):
                bot_ans = CREATOR_REPLY
            else:
                messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-6:]
                ]
                bot_ans = generate_ai_response(messages_payload)

            st.session_state.messages.append({"role": "assistant", "content": bot_ans})
            with st.chat_message("assistant"):
                st.markdown(bot_ans)

            st.rerun()
