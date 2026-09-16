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
CRICKET_FILE = "cricket_matches_database.json"

UPI_ID = "8307940340@ptyes"
UPI_NAME = "Jatin Soni"
MY_WHATSAPP_NUMBER = "918307940340"
ADMIN_PIN = "2009"
FREE_DAILY_LIMIT = 50

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
    "sonijatin177@gmail.com": {"password": "admin", "plan": "pro", "date": "2026-01-01"},
    "jatinson8489@gmail.com": {"password": "admin", "plan": "pro", "date": "2026-01-01"},
    "jatinsoni32459@gmail.com": {"password": "admin", "plan": "pro", "date": "2026-01-01"}
}
for u_k, u_v in DEFAULT_PERSISTENT_USERS.items():
    if u_k not in users_db:
        users_db[u_k] = u_v
save_json(USERS_FILE, users_db)

usage_db = load_json(USAGE_FILE, {})
payments_db = load_json(PAYMENTS_FILE, {})
orders_db = load_json(ORDERS_FILE, [])
matches_db = load_json(CRICKET_FILE, {})

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

query_params = st.query_params

if "user" not in st.session_state:
    stored_user = query_params.get("user")
    if stored_user and stored_user.strip().lower() in users_db:
        st.session_state.user = stored_user.strip().lower()
    else:
        st.session_state.user = None

if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Dashboard"

if "messages" not in st.session_state:
    st.session_state.messages = []

def reset_cricket_match():
    return {
        "team_1": "Team A",
        "team_2": "Team B",
        "batting_team": "Team A",
        "bowling_team": "Team B",
        "total_overs": 5,
        "innings": 1,
        "runs": 0,
        "wickets": 0,
        "balls_bowled": 0,
        "striker_name": "Striker",
        "striker_runs": 0,
        "striker_balls": 0,
        "non_striker_name": "Non-Striker",
        "non_striker_runs": 0,
        "non_striker_balls": 0,
        "bowler_name": "Bowler 1",
        "bowler_wickets": 0,
        "bowler_runs": 0,
        "bowler_balls": 0,
        "this_over": [],
        "target": 0,
        "status": "Ongoing",
        "winner": "",
        "awaiting_wicket": False,
        "first_inn_summary": ""
    }

if "match_state" not in st.session_state or not isinstance(st.session_state.match_state, dict) or "status" not in st.session_state.match_state:
    st.session_state.match_state = reset_cricket_match()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: linear-gradient(135deg, #0b1120 0%, #0f172a 40%, #1e1b4b 100%) !important;
        background-attachment: fixed !important;
        font-family: 'Inter', sans-serif !important;
        color: #f8fafc !important;
    }

    [data-testid="stHeader"] { background: transparent !important; }

    [data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding-top: 15px !important;
        padding-left: 14px !important;
        padding-right: 14px !important;
    }

    .brand-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 20px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 24px;
        padding-left: 6px;
    }

    div[data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #cbd5e1 !important;
        margin-bottom: 8px !important;
        width: 100% !important;
    }

    .top-action-bar {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 10px;
        margin-bottom: 14px;
    }
    .top-action-btn {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #cbd5e1 !important;
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 10px;
        padding: 6px 14px;
        font-size: 12px;
        font-weight: 600;
        text-decoration: none !important;
    }

    .welcome-card {
        background: rgba(15, 23, 42, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 18px;
        padding: 20px 24px;
        margin-bottom: 16px;
        backdrop-filter: blur(12px);
    }

    /* EXACT 3-PANEL CRICKET BROADCAST LAYOUT */
    .cricket-broadcast-shell {
        background: #0d1527;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        padding: 18px;
        display: grid;
        grid-template-columns: 1.2fr 1fr 1fr;
        gap: 14px;
        box-shadow: 0 16px 36px rgba(0,0,0,0.55);
        margin-bottom: 20px;
    }

    .broadcast-subcard {
        background: #131c31;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 14px 16px;
    }

    .card-top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        font-weight: 700;
        color: #94a3b8;
        letter-spacing: 0.6px;
        margin-bottom: 10px;
    }

    .striker-active-box {
        border: 1.5px solid #22c55e !important;
        border-radius: 12px;
        padding: 10px 12px;
        background: rgba(34, 197, 94, 0.06);
        margin-bottom: 8px;
    }

    .non-striker-box {
        border: 1px solid transparent;
        border-radius: 12px;
        padding: 8px 12px;
    }

    .player-row-main {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 15px;
        font-weight: 700;
        color: #ffffff;
    }

    .player-sub-sr {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 3px;
        font-weight: 500;
    }

    .ball-icon-circle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        font-size: 13px;
        font-weight: 700;
        color: #ffffff;
    }
    .ball-dot { background: #334155; color: #94a3b8; }
    .ball-run { background: #1e3a8a; border: 1px solid #3b82f6; }
    .ball-four { background: #0284c7; }
    .ball-six { background: #9333ea; }
    .ball-wicket { background: #dc2626; font-weight: 800; }

    div.telecast-btn button {
        background: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        padding: 10px !important;
    }
    div.telecast-btn-run button {
        background: #0f172a !important;
        border: 1px solid #334155 !important;
    }
    div.telecast-btn-boundary button {
        background: #eab308 !important;
        color: #422006 !important;
    }
    div.telecast-btn-six button {
        background: #9333ea !important;
        color: #ffffff !important;
    }
    div.telecast-btn-out button {
        background: #ef4444 !important;
        color: #ffffff !important;
    }

    .saved-card {
        background: #131c31;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
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
SYSTEM_PROMPT = f"""
You are Soni AI, created by Jatin Soni.
Creator: Jatin Soni (16 yrs, 12th class, Rori, Sirsa, Haryana).
Rules: Direct, helpful, smart Hinglish/English answers.
"""

def clean_model_output(text: str) -> str:
    if not text: return ""
    if "</think>" in text: text = text.split("</think>")[-1]
    elif "<think>" in text: text = re.sub(r'(?i)<think>.*', '', text, flags=re.DOTALL)
    return text.strip()

def generate_ai_response(messages_list):
    try:
        resp = client.chat.completions.create(
            messages=messages_list,
            model="llama-3.1-8b-instant"
        )
        return clean_model_output(resp.choices[0].message.content)
    except Exception:
        try:
            resp = client.chat.completions.create(
                messages=messages_list,
                model="llama-3.2-3b-preview"
            )
            return clean_model_output(resp.choices[0].message.content)
        except Exception as e:
            return f"Error: {e}"

# --- LOGIN SCREEN ---
if not st.session_state.user:
    st.markdown("""
        <div style="max-width:440px; margin:50px auto; background:#131c31; border:1px solid rgba(255,255,255,0.1); border-radius:20px; padding:30px; text-align:center;">
            <h2 style="margin-bottom:4px; color:#fff;">✨ Soni AI</h2>
            <p style="color:#94a3b8; font-size:14px; margin-bottom:20px;">Sign in to save match stats and access Pro features</p>
        </div>
    """, unsafe_allow_html=True)

    c_pad1, c_box, c_pad2 = st.columns([1, 1.3, 1])
    with c_box:
        if st.button("🚀 Continue as Guest (Matches Won't Auto-Save)", use_container_width=True):
            st.session_state.user = "guest@soniai.com"
            st.query_params["user"] = "guest@soniai.com"
            st.rerun()

        st.markdown("<div style='text-align:center; margin:15px 0; color:#94a3b8; font-size:12px;'>── OR LOG IN TO SAVE STATS ──</div>", unsafe_allow_html=True)
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
                if st.form_submit_button("Create Account", use_container_width=True):
                    if reg_email and reg_pass:
                        users_db[reg_email] = {"password": reg_pass, "plan": "free", "date": datetime.now().strftime("%Y-%m-%d")}
                        save_json(USERS_FILE, users_db)
                        st.session_state.user = reg_email
                        st.query_params["user"] = reg_email
                        st.rerun()
    st.stop()

active_user = st.session_state.get("user", "guest@soniai.com").strip().lower()
user_handle = active_user.split("@")[0]
chats_used_today, is_pro_user = get_user_chat_count(active_user, users_db, usage_db)

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

    if st.button("🏏 Pro Cricket Scorer", key="btn_sb_cricket"):
        st.session_state.current_tab = "Cricket Scorer"
        st.rerun()

    if st.button("👑 VIP Pro Tools", key="btn_sb_vip"):
        st.session_state.current_tab = "VIP Tools"
        st.rerun()

    if st.button("🛍️ Soni Shop", key="btn_sb_shop"):
        st.session_state.current_tab = "Shop"
        st.rerun()

    if st.button("💳 Billing / Upgrade", key="btn_sb_bill"):
        st.session_state.current_tab = "Billing"
        st.rerun()

    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; padding:12px 6px; border-top:1px solid rgba(255,255,255,0.08); margin-top:50px;">
            <div style="font-size:22px;">👤</div>
            <div style="line-height:1.2;">
                <div style="font-size:13px; font-weight:700; color:#fff;">{user_handle} <span style="background:#2563eb; color:white; font-size:10px; padding:2px 6px; border-radius:6px;">{'PRO' if is_pro_user else 'FREE'}</span></div>
                <div style="font-size:11px; color:#94a3b8;">Plan: {'Unlimited VIP' if is_pro_user else f'{chats_used_today}/{FREE_DAILY_LIMIT} msgs'}</div>
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
    st.markdown(f"<h2 style='margin:0; font-weight:700; color:#ffffff;'>{st.session_state.current_tab}</h2>", unsafe_allow_html=True)
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
            <h3 style="margin:0 0 6px 0; font-size:22px; font-weight:700; color:#fff;">Welcome, {user_handle.capitalize()}! {'🔥 (VIP PRO MEMBER)' if is_pro_user else ''}</h3>
            <div style="font-size:13px; font-weight:600; color:#cbd5e1;">
                Status: <span style="color:#38bdf8;">{'Unlimited Chats + Pro Cricket Scorer Active 💎' if is_pro_user else f'Free Plan ({chats_used_today}/{FREE_DAILY_LIMIT} chats used)'}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        role_title = "User" if msg["role"] == "user" else "Soni AI"
        icon = "👤" if msg["role"] == "user" else "🤖"
        st.markdown(f"""
            <div style="background: #131c31; border:1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 12px 18px; margin-bottom: 10px;">
                <b style="color:#38bdf8;">{icon} {role_title}</b>
                <div style="margin-top: 4px; color: #f1f5f9;">{msg['content']}</div>
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

            input_lower = clean_in.lower()
            creator_triggers = ["kisne banaya", "who made you", "developer", "creator", "owner", "kaun banaya", "maker"]
            if any(trig in input_lower for trig in creator_triggers):
                bot_ans = CREATOR_REPLY
            else:
                messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-5:]
                ]
                bot_ans = generate_ai_response(messages_payload)

            st.session_state.messages.append({"role": "assistant", "content": bot_ans})
            st.rerun()

# --- TAB: PRO CRICKET SCORER (PHOTO MATCH: BATSMEN / BOWLER / THIS OVER) ---
elif st.session_state.current_tab == "Cricket Scorer":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 🏏 Soni Pro Cricket Live Scorer")

    if not is_pro_user:
        st.warning("🔒 **Yeh Feature Sirf Pro Plan Members ke liye Unlock Hai!**")
        st.markdown("""
        * 🏆 **3-Panel Broadcast Scoreboard:** Live TV graphics, Striker highlight, Bowler economy & ball tracker.
        * 🎯 **Permanent Scorecard Storage:** Match finish hote hi saara scorecard aapke profile mein save ho jayega.
        """)
        if st.button("💎 Unlock Pro Cricket Scorer (Upgrade to Pro)", use_container_width=True):
            st.session_state.current_tab = "Billing"
            st.rerun()
    else:
        ms = st.session_state.match_state

        def save_finished_match():
            if active_user != "guest@soniai.com":
                if active_user not in matches_db:
                    matches_db[active_user] = []
                
                match_record = {
                    "id": f"M-{int(datetime.now().timestamp())}",
                    "date": datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %b %Y, %I:%M %p"),
                    "team_1": ms.get("team_1"),
                    "team_2": ms.get("team_2"),
                    "winner": ms.get("winner"),
                    "first_inn": ms.get("first_inn_summary"),
                    "second_inn": f"{ms.get('batting_team')}: {ms.get('runs')}/{ms.get('wickets')} in {ms.get('balls_bowled')//6}.{ms.get('balls_bowled')%6} ov",
                    "target": ms.get("target")
                }
                matches_db[active_user].insert(0, match_record)
                save_json(CRICKET_FILE, matches_db)

        def check_match_status():
            status = ms.get("status", "Ongoing")
            if status == "Finished": return
            
            inn = ms.get("innings", 1)
            t_overs = ms.get("total_overs", 5)
            balls = ms.get("balls_bowled", 0)
            wkts = ms.get("wickets", 0)
            r = ms.get("runs", 0)
            tgt = ms.get("target", 0)

            if inn == 1:
                if balls >= t_overs * 6 or wkts >= 10:
                    ms["status"] = "Innings Break"
                    ms["target"] = r + 1
                    ms["first_inn_summary"] = f"{ms.get('batting_team')}: {r}/{wkts} in {balls//6}.{balls%6} ov"
            elif inn == 2:
                if r >= tgt:
                    ms["status"] = "Finished"
                    ms["winner"] = ms.get("batting_team")
                    save_finished_match()
                elif balls >= t_overs * 6 or wkts >= 10:
                    ms["status"] = "Finished"
                    if r == tgt - 1:
                        ms["winner"] = "Tie"
                    else:
                        ms["winner"] = ms.get("bowling_team")
                    save_finished_match()

        current_status = ms.get("status", "Ongoing")

        # WINNER CUP ANNOUNCEMENT
        if current_status == "Finished":
            win_team = ms.get("winner", "")
            win_text = "Match Tied! 🤝" if win_team == "Tie" else f"🏆 {win_team} Won the Match! 🎉"
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f59e0b, #fbbf24); border-radius:18px; padding:24px; text-align:center; color:#000; margin-bottom:16px;">
                    <h1 style="font-size:45px; margin:0;">🏆</h1>
                    <h2 style="font-weight:800; margin:6px 0;">{win_text}</h2>
                    <div style="font-size:13px; font-weight:600;">Match scorecard has been permanently saved to your profile!</div>
                </div>
            """, unsafe_allow_html=True)

        elif current_status == "Innings Break":
            st.info(f"**Innings Break!** {ms.get('first_inn_summary')}")
            st.success(f"🎯 **Target for {ms.get('bowling_team')}: {ms.get('target')} Runs in {ms.get('total_overs')} Overs.**")
            if st.button("▶️ Start 2nd Innings", use_container_width=True):
                ms["batting_team"], ms["bowling_team"] = ms.get("bowling_team"), ms.get("batting_team")
                ms["runs"] = 0
                ms["wickets"] = 0
                ms["balls_bowled"] = 0
                ms["striker_name"] = "Striker"
                ms["striker_runs"] = 0
                ms["striker_balls"] = 0
                ms["non_striker_name"] = "Non-Striker"
                ms["non_striker_runs"] = 0
                ms["non_striker_balls"] = 0
                ms["bowler_wickets"] = 0
                ms["bowler_runs"] = 0
                ms["bowler_balls"] = 0
                ms["this_over"] = []
                ms["innings"] = 2
                ms["status"] = "Ongoing"
                st.rerun()

        # LIVE NUMBERS
        b_balls = ms.get("balls_bowled", 0)
        bw_balls = ms.get("bowler_balls", 0)
        bw_overs_str = f"{bw_balls // 6}.{bw_balls % 6}"
        bw_economy = (ms.get("bowler_runs", 0) / max(1, bw_balls)) * 6 if bw_balls > 0 else 0.0

        s_b = ms.get("striker_balls", 0)
        s_sr = (ms.get("striker_runs", 0) / max(1, s_b)) * 100 if s_b > 0 else 0.0

        ns_b = ms.get("non_striker_balls", 0)
        ns_sr = (ms.get("non_striker_runs", 0) / max(1, ns_b)) * 100 if ns_b > 0 else 0.0

        # BUILD 3-PANEL SHELL (BATSMEN / BOWLER / THIS OVER)
        over_balls_html = ""
        current_over_list = ms.get("this_over", [])
        if not current_over_list:
            over_balls_html = '<div style="color:#64748b; font-size:13px; margin-top:14px;">Over just started</div>'
        else:
            chips = []
            labels = []
            for b_info in current_over_list:
                val = b_info["val"]
                cls = b_info["cls"]
                chips.append(f'<span class="ball-icon-circle {cls}">{val}</span>')
                labels.append(f'<span style="font-size:11px; color:#64748b; display:inline-block; width:32px; text-align:center;">[{val}]</span>')

            chips_html = " ".join(chips)
            labels_html = " ".join(labels)
            over_balls_html = f'<div style="display:flex; gap:8px; margin-top:8px;">{chips_html}</div><div style="display:flex; gap:8px; margin-top:4px;">{labels_html}</div>'

        scoreboard_html = (
            '<div class="cricket-broadcast-shell">'
            # CARD 1: BATSMEN
            '<div class="broadcast-subcard">'
            '<div class="card-top-header">'
            '<span>BATSMEN</span>'
            f'<span style="color:#fff; font-size:13px;">{ms.get("batting_team")} {ms.get("runs")}/{ms.get("wickets")}</span>'
            '</div>'
            '<div class="striker-active-box">'
            '<div class="player-row-main">'
            f'<span>🏏 {ms.get("striker_name")}*</span>'
            f'<span>{ms.get("striker_runs")} <span style="font-size:12px; color:#94a3b8;">({s_b})</span></span>'
            '</div>'
            f'<div class="player-sub-sr">SR: {s_sr:.1f}</div>'
            '</div>'
            '<div class="non-striker-box">'
            '<div class="player-row-main">'
            f'<span style="color:#cbd5e1;">{ms.get("non_striker_name")}</span>'
            f'<span style="color:#cbd5e1;">{ms.get("non_striker_runs")} <span style="font-size:12px; color:#64748b;">({ns_b})</span></span>'
            '</div>'
            f'<div class="player-sub-sr">SR: {ns_sr:.1f}</div>'
            '</div>'
            '</div>'
            # CARD 2: BOWLER
            '<div class="broadcast-subcard">'
            '<div class="card-top-header">'
            '<span>BOWLER</span>'
            '<span>#1</span>'
            '</div>'
            '<div style="display:flex; align-items:center; gap:8px; font-size:16px; font-weight:700; color:#fff; margin-top:4px;">'
            f'<span>⚾</span> <span>{ms.get("bowler_name")}</span>'
            '</div>'
            f'<div style="font-size:24px; font-weight:800; color:#fff; margin-top:8px;">{ms.get("bowler_wickets")}/{ms.get("bowler_runs")} <span style="font-size:14px; color:#94a3b8; font-weight:500;">({bw_overs_str} ov)</span></div>'
            f'<div style="font-size:12px; color:#94a3b8; margin-top:3px;">ER: {bw_economy:.1f}</div>'
            '</div>'
            # CARD 3: THIS OVER
            '<div class="broadcast-subcard">'
            '<div class="card-top-header">'
            '<span>THIS OVER</span>'
            '</div>'
            f'{over_balls_html}'
            '</div>'
            '</div>'
        )

        st.markdown(scoreboard_html, unsafe_allow_html=True)

        # SCORING CONTROLS
        def record_ball(val_str, cls_str):
            ms["this_over"].append({"val": val_str, "cls": cls_str})
            if len(ms["this_over"]) > 6:
                ms["this_over"] = ms["this_over"][-6:]

        if current_status == "Ongoing":
            if ms.get("awaiting_wicket", False):
                st.warning("⚠️ **Select Wicket Type:**")
                cw1, cw2, cw3, cw4, cw5 = st.columns(5)
                w_types = ["🎯 Bowled", "🧤 Catch", "🦵 LBW", "🏃 Run Out", "⚡ Stumped"]
                cols = [cw1, cw2, cw3, cw4, cw5]
                for i, w_type in enumerate(w_types):
                    if cols[i].button(w_type, use_container_width=True):
                        ms["wickets"] = ms.get("wickets", 0) + 1
                        if "Run Out" not in w_type:
                            ms["bowler_wickets"] = ms.get("bowler_wickets", 0) + 1
                        ms["balls_bowled"] = ms.get("balls_bowled", 0) + 1
                        ms["bowler_balls"] = ms.get("bowler_balls", 0) + 1
                        ms["striker_balls"] = ms.get("striker_balls", 0) + 1
                        record_ball("W", "ball-wicket")
                        ms["awaiting_wicket"] = False
                        
                        # Reset out batsman to next generic name
                        ms["striker_name"] = f"Player {ms.get('wickets')+2}"
                        ms["striker_runs"] = 0
                        ms["striker_balls"] = 0
                            
                        check_match_status()
                        st.rerun()
            else:
                col_b1, col_b2, col_b3, col_b4, col_b5, col_b6 = st.columns(6)
                with col_b1:
                    st.markdown('<div class="telecast-btn telecast-btn-run">', unsafe_allow_html=True)
                    if st.button("➕ 1 Run", use_container_width=True):
                        ms["runs"] += 1
                        ms["bowler_runs"] += 1
                        ms["balls_bowled"] += 1
                        ms["bowler_balls"] += 1
                        ms["striker_runs"] += 1
                        ms["striker_balls"] += 1
                        record_ball("1", "ball-run")
                        # Strike rotation on 1 run
                        ms["striker_name"], ms["non_striker_name"] = ms["non_striker_name"], ms["striker_name"]
                        ms["striker_runs"], ms["non_striker_runs"] = ms["non_striker_runs"], ms["striker_runs"]
                        ms["striker_balls"], ms["non_striker_balls"] = ms["non_striker_balls"], ms["striker_balls"]
                        check_match_status()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_b2:
                    st.markdown('<div class="telecast-btn telecast-btn-run">', unsafe_allow_html=True)
                    if st.button("➕ 2 Runs", use_container_width=True):
                        ms["runs"] += 2
                        ms["bowler_runs"] += 2
                        ms["balls_bowled"] += 1
                        ms["bowler_balls"] += 1
                        ms["striker_runs"] += 2
                        ms["striker_balls"] += 1
                        record_ball("2", "ball-run")
                        check_match_status()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_b3:
                    st.markdown('<div class="telecast-btn telecast-btn-boundary">', unsafe_allow_html=True)
                    if st.button("FOUR (4)", use_container_width=True):
                        ms["runs"] += 4
                        ms["bowler_runs"] += 4
                        ms["balls_bowled"] += 1
                        ms["bowler_balls"] += 1
                        ms["striker_runs"] += 4
                        ms["striker_balls"] += 1
                        record_ball("4", "ball-four")
                        check_match_status()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_b4:
                    st.markdown('<div class="telecast-btn telecast-btn-six">', unsafe_allow_html=True)
                    if st.button("SIX (6)", use_container_width=True):
                        ms["runs"] += 6
                        ms["bowler_runs"] += 6
                        ms["balls_bowled"] += 1
                        ms["bowler_balls"] += 1
                        ms["striker_runs"] += 6
                        ms["striker_balls"] += 1
                        record_ball("6", "ball-six")
                        check_match_status()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_b5:
                    st.markdown('<div class="telecast-btn telecast-btn-out">', unsafe_allow_html=True)
                    if st.button("🔴 OUT (W)", use_container_width=True):
                        ms["awaiting_wicket"] = True
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_b6:
                    st.markdown('<div class="telecast-btn telecast-btn-run">', unsafe_allow_html=True)
                    if st.button("⚪ Dot Ball", use_container_width=True):
                        ms["balls_bowled"] += 1
                        ms["bowler_balls"] += 1
                        ms["striker_balls"] += 1
                        record_ball("•", "ball-dot")
                        check_match_status()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")

        # EDIT TEAMS & PLAYERS (CUSTOM NAMES ENTERED HERE DISPLAY IN CARDS)
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("#### ⚙️ Edit Teams & Players")
            with st.form("form_edit_match"):
                team1 = st.text_input("Team 1 Name", value=ms.get("team_1", "Team A"))
                team2 = st.text_input("Team 2 Name", value=ms.get("team_2", "Team B"))
                t_overs = st.number_input("Total Match Overs", min_value=1, max_value=50, value=ms.get("total_overs", 5))
                st_name = st.text_input("Striker Name", value=ms.get("striker_name", "Striker"))
                nst_name = st.text_input("Non-Striker Name", value=ms.get("non_striker_name", "Non-Striker"))
                bw_name = st.text_input("Bowler Name", value=ms.get("bowler_name", "Bowler 1"))

                if st.form_submit_button("Update Details 🔄", use_container_width=True):
                    ms["team_1"], ms["team_2"], ms["total_overs"] = team1, team2, t_overs
                    if ms.get("balls_bowled", 0) == 0 and ms.get("innings", 1) == 1:
                        ms["batting_team"], ms["bowling_team"] = team1, team2
                    ms["striker_name"], ms["non_striker_name"], ms["bowler_name"] = st_name, nst_name, bw_name
                    st.success("Details updated!")
                    st.rerun()

        with col_m2:
            st.markdown("#### 📲 Share Scorecard")
            target_str = f"🎯 Target: {ms.get('target', 0)}\n" if ms.get("innings", 1) == 2 else ""
            win_str = f"\n🏆 *{ms.get('winner')} Won The Match!*" if current_status == "Finished" else ""
            
            overs_disp = f"{b_balls // 6}.{b_balls % 6}"
            wa_score_text = (
                f"🏏 *LIVE CRICKET TELECAST*\n"
                f"⚔️ *{ms.get('team_1')} vs {ms.get('team_2')}*\n\n"
                f"Batting: *{ms.get('batting_team')}*\n"
                f"📊 *Score:* {ms.get('runs', 0)}/{ms.get('wickets', 0)} ({overs_disp} ov)\n"
                f"🏏 *Striker:* {ms.get('striker_name')} - {ms.get('striker_runs')} ({s_b})\n"
                f"🏏 *Non-Striker:* {ms.get('non_striker_name')} - {ms.get('non_striker_runs')} ({ns_b})\n"
                f"⚾ *Bowler:* {ms.get('bowler_name')} - {ms.get('bowler_wickets')}/{ms.get('bowler_runs')}\n"
                f"{target_str}"
                f"{win_str}\n\n"
                f"⚡ *Scored via Soni AI*"
            )
            share_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(wa_score_text)}"
            st.markdown(f'<a href="{share_url}" target="_blank" style="display:block; text-align:center; padding:12px; background:#25D366; color:white; border-radius:12px; text-decoration:none; font-weight:bold; margin-top:20px;">📲 Share on WhatsApp</a>', unsafe_allow_html=True)

            if st.button("🔄 Start New Match (Reset Board)", use_container_width=True):
                st.session_state.match_state = reset_cricket_match()
                st.rerun()

        # PERMANENT SCORECARD HISTORY SECTION
        st.markdown("---")
        st.markdown("### 📋 Saved Matches & Permanent Scorecards")

        user_matches = matches_db.get(active_user, [])
        if active_user == "guest@soniai.com":
            st.info("💡 You are currently browsing as a Guest. Log in or Sign up to permanently preserve your match records!")
        elif not user_matches:
            st.write("Abhi tak koi match finish nahi hua hai. Complete a match to view its archived scorecard here.")
        else:
            with st.expander(f"📁 View Saved Match History ({len(user_matches)} Matches)", expanded=True):
                for m in user_matches:
                    saved_html = (
                        '<div class="saved-card">'
                        '<div style="display:flex; justify-content:space-between; align-items:center;">'
                        f'<span style="font-weight:700; font-size:15px; color:#fff;">⚔️ {m["team_1"]} vs {m["team_2"]}</span>'
                        f'<span style="font-size:12px; color:#94a3b8;">📅 {m["date"]}</span>'
                        '</div>'
                        f'<div style="margin-top:6px; font-size:13px; color:#cbd5e1;"><b>1st Inn:</b> {m["first_inn"]} <br><b>2nd Inn:</b> {m["second_inn"]}</div>'
                        f'<div style="margin-top:8px; font-weight:700; color:#38bdf8; font-size:14px;">🏆 Winner: {m["winner"]}</div>'
                        '</div>'
                    )
                    st.markdown(saved_html, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: VIP PRO TOOLS ---
elif st.session_state.current_tab == "VIP Tools":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 👑 Exclusive VIP AI Tools")

    if not is_pro_user:
        st.warning("🔒 **Yeh feature locked hai!** Sirf Pro Plan members ise use kar sakte hain.")
        if st.button("💎 Unlock VIP Tools (Upgrade to Pro)", use_container_width=True):
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

# --- TAB: SHOP (WITH VIP DISCOUNT) ---
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
            <div style="background:#131c31; border:1px solid rgba(255,255,255,0.08); border-radius:14px; padding:12px; text-align:center; margin-bottom:12px;">
                <img src="{prod['img']}" style="width:100%; height:180px; object-fit:cover; border-radius:10px;">
                <div style="font-weight:700; margin-top:8px; color:#fff;">{prod['name']}</div>
                <div style="color:#38bdf8; font-weight:800; font-size:16px;">
                    {f'<s style="color:#64748b; font-size:13px;">₹{prod["price"]}</s> ₹{final_p} (VIP Price)' if is_pro_user else f'₹{final_p}'}
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

# --- TAB: BILLING ---
elif st.session_state.current_tab == "Billing":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 💳 Upgrade to Soni AI Pro")
    st.write("Unlimited Chats + Pro Cricket Live Scorer + VIP Tools + ₹100 Store Discount pane ke liye Pro activate karein:")

    final_price = 49.00
    qr_img_url, direct_upi_link = generate_upi_qr(final_price, f"Soni AI Pro - {active_user}")

    col_qr, col_pay_form = st.columns([4, 6])
    with col_qr:
        st.image(qr_img_url, caption=f"Scan & Pay ₹{final_price:.2f}", width=220)
        st.markdown(f"**Amount:** `₹{final_price:.2f}` | **UPI:** `{UPI_ID}`")
    with col_pay_form:
        if is_pro_user:
            st.success("🎉 **Pro Mode Active Hai!** Unlimited Chats, Pro Cricket Scorer & VIP Tools unlocked hain.")
        else:
            with st.form("pro_utr_form"):
                utr = st.text_input("12-digit UTR / UPI Ref ID*", placeholder="Ex: 421098492019").strip()
                if st.form_submit_button("Submit For Verification 📩", use_container_width=True):
                    if len(utr) >= 8 and utr.isdigit():
                        payments_db[active_user] = {"utr": utr, "amount": final_price, "status": "pending"}
                        save_json(PAYMENTS_FILE, payments_db)
                        st.success("UTR submit ho gaya! Admin verify karke Pro mode on kar dega.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: ADMIN (/admin 2009) ---
elif st.session_state.current_tab == "AdminPanel":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 👑 Owner Verification Panel")
    for u_email, p_info in list(payments_db.items()):
        st.write(f"👤 **{u_email}** | Amount: ₹{p_info.get('amount')} | UTR: `{p_info.get('utr')}`")
        if st.button(f"Approve {u_email}", key=f"appr_{u_email}"):
            if u_email not in users_db: users_db[u_email] = {}
            users_db[u_email]["plan"] = "pro"
            save_json(USERS_FILE, users_db)
            del payments_db[u_email]
            save_json(PAYMENTS_FILE, payments_db)
            st.rerun()
    if st.button("Back to Dashboard"):
        st.session_state.current_tab = "Dashboard"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
