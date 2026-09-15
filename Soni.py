import streamlit as st
from groq import Groq
import urllib.parse
import json
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Soni AI - Dashboard", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

CHATS_FILE = "chats_history_database.json"
USERS_FILE = "users_database.json"
PROJECTS_FILE = "projects_database.json"

# --- HELPER FUNCTIONS ---
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

# --- AUTH & NAVIGATION STATE ---
users_db = load_json(USERS_FILE, {})
chats_db = load_json(CHATS_FILE, {})
projects_db = load_json(PROJECTS_FILE, ["AI Assistant Bot", "E-Commerce Recommender", "Customer Support Workflow"])

query_params = st.query_params

if "user" not in st.session_state:
    stored_user = query_params.get("user")
    if stored_user:
        st.session_state.user = stored_user
    else:
        st.session_state.user = "jatinson8489@gmail.com"

if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Dashboard"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "user", "content": "hy", "time": "12:36 AM"},
        {"role": "assistant", "content": "Hi! How can I help you today?", "time": "12:36 AM"}
    ]

# --- CSS STYLING ---
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
        padding-top: 10px !important;
        padding-left: 12px !important;
        padding-right: 12px !important;
    }

    .brand-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 22px;
        font-weight: 700;
        color: #334155;
        margin-bottom: 22px;
    }

    /* Sidebar Button Overrides for Exact Pill Design */
    div[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: transparent !important;
        border: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 14px !important;
        padding: 9px 16px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #64748b !important;
        box-shadow: none !important;
        margin-bottom: 4px !important;
        width: 100% !important;
    }

    div[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: rgba(226, 232, 240, 0.7) !important;
        color: #1e293b !important;
    }

    div[data-testid="stSidebar"] .active-nav-btn > button {
        background: #e2e8f0 !important;
        color: #1e293b !important;
        font-weight: 600 !important;
        border-radius: 20px !important;
    }

    .sidebar-user-pill {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 6px;
        border-top: 1px solid #e2e8f0;
        margin-top: 40px;
    }

    .top-action-bar {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 10px;
        margin-bottom: 18px;
    }
    .top-action-btn {
        background: rgba(255, 255, 255, 0.85);
        color: #334155 !important;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 6px 14px;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none !important;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .welcome-card {
        background: rgba(255, 255, 255, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        padding: 18px 24px;
        margin-bottom: 14px;
        backdrop-filter: blur(10px);
    }

    .content-box-card {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 14px;
        backdrop-filter: blur(10px);
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

active_user = st.session_state.user
user_handle = active_user.split("@")[0]

# --- SIDEBAR (ALL TABS USABLE) ---
with st.sidebar:
    st.markdown("""
        <div class="brand-title">
            <span style="font-size:24px;">✨</span> Soni AI <span style="font-size:14px; margin-left:auto; color:#94a3b8;">«</span>
        </div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("Dashboard", "🏠 Dashboard"),
        ("History", "🕒 Chat History"),
        ("Projects", "📁 Projects"),
        ("Integrations", "⚡ Integrations"),
        ("Billing", "💳 Billing")
    ]

    for key, label in nav_items:
        is_active = (st.session_state.current_tab == key)
        wrapper_class = "active-nav-btn" if is_active else ""
        st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
        if st.button(label, key=f"nav_btn_{key}"):
            st.session_state.current_tab = key
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
        <div class="sidebar-user-pill">
            <div style="width:32px; height:32px; background:#e2e8f0; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:16px;">👤</div>
            <div style="line-height:1.2; overflow:hidden;">
                <div style="font-size:13px; font-weight:600; color:#1e293b;">User Settings</div>
                <div style="font-size:11px; color:#64748b; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">{active_user}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout", key="btn_logout_sidebar", use_container_width=True):
        st.session_state.user = None
        st.query_params.clear()
        st.rerun()

# --- TOP BAR ACTIONS ---
col_head, col_btns = st.columns([4, 6])
with col_head:
    st.markdown(f"<h2 style='margin:0; font-weight:700; color:#1e293b;'>{st.session_state.current_tab}</h2>", unsafe_allow_html=True)
with col_btns:
    st.markdown("""
        <div class="top-action-bar">
            <a href="https://mail.google.com/mail/?view=cm&fs=1&to=sonijatin177@gmail.com" target="_blank" class="top-action-btn">⚡ Founder: Jatin Soni</a>
            <a href="/?action=toggle_shop" target="_self" class="top-action-btn">🛒 Soni Shop</a>
            <a href="mailto:sonijatin177@gmail.com?subject=Help%20Support%20Soni%20AI" class="top-action-btn">❓ Help Center</a>
        </div>
    """, unsafe_allow_html=True)

# Welcome Banner
st.markdown(f"""
    <div class="welcome-card">
        <h3 style="margin:0 0 6px 0; font-size:22px; font-weight:700; color:#0f172a;">Welcome, {user_handle.capitalize()}!</h3>
        <div style="font-size:13px; font-weight:600; color:#475569;">
            Active Projects: <span style="color:#0f172a;">{len(projects_db)}</span> &nbsp;&nbsp;|&nbsp;&nbsp; Total Computes: <span style="color:#0f172a;">128</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# 4 Action Pills Row (Fully Clickable)
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
    if st.button("👤 Account Usage", use_container_width=True):
        st.session_state.current_tab = "Billing"
        st.rerun()

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# --- TAB 1: DASHBOARD (MAIN CHAT) ---
if st.session_state.current_tab == "Dashboard":
    for msg in st.session_state.messages:
        time_tag = msg.get("time", datetime.now().strftime("%I:%M %p"))
        if msg["role"] == "user":
            st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.7); border: 1px solid rgba(255, 255, 255, 0.8); border-radius: 14px; padding: 12px 16px; margin-bottom: 10px; backdrop-filter: blur(8px); display: flex; align-items: flex-start; justify-content: space-between;">
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
                <div style="background: rgba(255, 255, 255, 0.85); border: 1px solid rgba(255, 255, 255, 0.9); border-radius: 14px; padding: 12px 16px; margin-bottom: 10px; backdrop-filter: blur(8px); display: flex; align-items: flex-start; justify-content: space-between;">
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

    user_input = st.chat_input("Ask Soni AI anything...")

    if user_input:
        clean_input = user_input.strip()
        now_stamp = datetime.now().strftime("%I:%M %p")

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

# --- TAB 2: CHAT HISTORY ---
elif st.session_state.current_tab == "History":
    st.markdown('<div class="content-box-card">', unsafe_allow_html=True)
    st.markdown("### 🕒 Saved Chat Sessions")
    user_saved_chats = chats_db.get(active_user, {})

    if not user_saved_chats:
        st.info("Abhi koi purani saved chat nahi mili. Dashboard par jaakar nayi chat shuru karein!")
    else:
        for session_id, history in list(user_saved_chats.items()):
            col_info, col_load, col_del = st.columns([7, 1.5, 1.5])
            with col_info:
                first_query = history[0]['content'] if history else "Empty chat"
                st.markdown(f"**{session_id}** — *\"{first_query[:35]}...\"* ({len(history)} messages)")
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

# --- TAB 3: PROJECTS ---
elif st.session_state.current_tab == "Projects":
    st.markdown('<div class="content-box-card">', unsafe_allow_html=True)
    st.markdown("### 📁 My AI Projects")
    
    col_p1, col_p2 = st.columns([8, 2])
    with col_p1:
        new_proj_name = st.text_input("New Project Name", placeholder="Ex: AI Customer Helpdesk")
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

# --- TAB 4: INTEGRATIONS ---
elif st.session_state.current_tab == "Integrations":
    st.markdown('<div class="content-box-card">', unsafe_allow_html=True)
    st.markdown("### ⚡ API & Service Integrations")
    st.success("🟢 **Groq LLM API:** Connected & Active (High-Speed Engine)")
    st.info("🟢 **SMTP Email Engine:** Connected (`smtp.gmail.com`)")
    st.warning("🟡 **WhatsApp Business Bot:** Ready for Webhook configuration")
    st.markdown("---")
    st.markdown("**Active Webhook Endpoint:** `https://jatin-soni-ai.streamlit.app/api/webhook`")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 5: BILLING / ACCOUNT USAGE ---
elif st.session_state.current_tab == "Billing":
    st.markdown('<div class="content-box-card">', unsafe_allow_html=True)
    st.markdown("### 💳 Usage & Plan Overview")
    st.markdown(f"**Current Plan:** `Soni AI Pro Tier` (Unlimited Access)")
    st.markdown(f"**Logged Account:** `{active_user}`")

    st.progress(0.26)
    st.caption("Total Computes Used: 128 / 500 Compute Units (26%)")

    st.markdown("---")
    col_b1, col_b2, col_b3 = st.columns(3)
    col_b1.metric("Token Consumption", "42,850", "+12%")
    col_b2.metric("API Latency", "340 ms", "-25 ms")
    col_b3.metric("Uptime", "99.9%", "Optimal")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 6: MARKETPLACE (SHOP) ---
elif st.session_state.current_tab == "Marketplace":
    st.markdown('<div class="content-box-card">', unsafe_allow_html=True)
    st.markdown("### 🏛️ Soni Store & Marketplace")
    st.markdown("Shop par jaane ke liye top bar ke **🛒 Soni Shop** button par click karein ya direct order place karein.")
    if st.button("⬅️ Back to Chat"):
        st.session_state.current_tab = "Dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
