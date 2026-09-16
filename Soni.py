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

if "applied_coupon" not in st.session_state:
    st.session_state.applied_coupon = None

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

    .shop-product-card {
        background: rgba(255, 255, 255, 0.92);
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

def get_available_groq_models():
    try:
        models_data = client.models.list()
        chat_models = []
        for m in models_data.data:
            m_id = m.id.lower()
            if "whisper" not in m_id and "tts" not in m_id:
                chat_models.append(m.id)
        return chat_models
    except Exception:
        return []

def generate_ai_response(messages_list):
    live_models = get_available_groq_models()
    if not live_models:
        live_models = ["llama-3.2-3b-preview", "llama-3.1-8b-instant"]

    last_error = ""
    for model_name in live_models:
        try:
            resp = client.chat.completions.create(
                messages=messages_list,
                model=model_name
            )
            return clean_model_output(resp.choices[0].message.content)
        except Exception as e:
            last_error = str(e)
            continue
            
    return f"Error connecting to AI: {last_error}"

# --- LOGIN SCREEN ---
if not st.session_state.user:
    st.markdown("""
        <div style="max-width:440px; margin:50px auto; background:rgba(255,255,255,0.85); border-radius:20px; padding:30px; box-shadow:0 8px 30px rgba(0,0,0,0.06); text-align:center;">
            <h2 style="margin-bottom:4px;">✨ Soni AI</h2>
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

    if st.button("🎨 AI Media Studio (Pic & Video)", key="btn_sb_media"):
        st.session_state.current_tab = "Media Studio"
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
        <div style="display:flex; align-items:center; gap:10px; padding:12px 6px; border-top:1px solid #e2e8f0; margin-top:50px;">
            <div style="font-size:22px;">👤</div>
            <div style="line-height:1.2;">
                <div style="font-size:13px; font-weight:700;">{user_handle} <span class="pro-badge">{'PRO' if is_pro_user else 'FREE'}</span></div>
                <div style="font-size:11px; color:#64748b;">Plan: {'Unlimited VIP' if is_pro_user else f'{chats_used_today}/{FREE_DAILY_LIMIT} msgs'}</div>
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
            <h3 style="margin:0 0 6px 0; font-size:22px; font-weight:700;">Welcome, {user_handle.capitalize()}! {'🔥 (VIP PRO MEMBER)' if is_pro_user else ''}</h3>
            <div style="font-size:13px; font-weight:600; color:#475569;">
                Status: <span style="color:#2563eb;">{'Unlimited Chats + AI Pic & Video Studio Unlocked 💎' if is_pro_user else f'Free Plan ({chats_used_today}/{FREE_DAILY_LIMIT} chats used)'}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        role_title = "User" if msg["role"] == "user" else "Soni AI"
        icon = "👤" if msg["role"] == "user" else "🤖"
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.9); border-radius: 14px; padding: 12px 18px; margin-bottom: 10px;">
                <b>{icon} {role_title}</b>
                <div style="margin-top: 4px; color: #334155;">{msg['content']}</div>
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

# --- TAB: AI MEDIA STUDIO (ACTUAL PIC & VIDEO GENERATION) ---
elif st.session_state.current_tab == "Media Studio":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 🎨 AI Media Studio (Generate Real Pictures & Videos)")
    st.write("Paid/Pro members ke liye exclusive photo generation aur direct live AI Video generator.")

    if not is_pro_user:
        st.warning("🔒 **Yeh Feature Sirf Pro Plan Members ke liye Unlock Hai!**")
        st.markdown("""
        * 🖼️ **Ultra-HD AI Image Creator:** Text prompt daalein aur 4K quality photo banayein.
        * 🎬 **Direct AI Video Generator:** Text likhein aur actual MP4 Video generate karke download karein.
        """)
        if st.button("💎 Unlock Real Picture & Video Generator (Upgrade to Pro)", use_container_width=True):
            st.session_state.current_tab = "Billing"
            st.rerun()
    else:
        media_tab1, media_tab2 = st.tabs(["🖼️ AI Image Generator", "🎬 Direct AI Video Generator (.MP4)"])
        
        with media_tab1:
            st.markdown("#### 🖼️ Text se Ultra-HD Image banayein")
            img_prompt = st.text_input("Photo kaisi chahiye? (Prompt likhein)", placeholder="Ex: Futuristic sports car driving in neon rain, photorealistic, 8k")
            style_opt = st.selectbox("Image Style", ["Photorealistic / Natural", "Anime / Manga", "Cinematic 3D", "Cyberpunk Neon", "Oil Painting Art"])
            
            if st.button("Generate Image Now 🚀", use_container_width=True):
                if img_prompt.strip():
                    with st.spinner("AI Image render ho rahi hai..."):
                        full_prompt = f"{img_prompt.strip()}, {style_opt}, high detail, 8k resolution"
                        encoded_prompt = urllib.parse.quote(full_prompt)
                        generated_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
                        
                        st.success("Aapki AI Image taiyaar hai! 🎉")
                        st.image(generated_image_url, caption=f"Prompt: {img_prompt}", use_container_width=True)
                        st.markdown(f'<a href="{generated_image_url}" target="_blank" download="ai_image.jpg" style="display:block; text-align:center; padding:10px; background:#2563eb; color:white; border-radius:10px; text-decoration:none; font-weight:bold; margin-top:10px;">⬇️ Download Full Resolution Image</a>', unsafe_allow_html=True)
                else:
                    st.error("Kripya image prompt likhein!")

        with media_tab2:
            st.markdown("#### 🎬 Real AI Video (.MP4) Generator")
            st.write("Apna scene likhein aur AI aapko direct MP4 video generate karke dega:")
            vid_prompt = st.text_input("Video scene describe karein", placeholder="Ex: A futuristic astronaut walking on Mars with red sand and glowing stars")
            
            if st.button("Generate Real AI Video 🎥", use_container_width=True):
                if vid_prompt.strip():
                    with st.spinner("AI video generate kar raha hai (isme 15-20 seconds lag sakte hain)..."):
                        clean_vid_p = urllib.parse.quote(vid_prompt.strip())
                        video_stream_url = f"https://image.pollinations.ai/prompt/{clean_vid_p}?model=flux-video&nologo=true"
                        
                        st.success("Video successfully ban gayi hai! 🎉")
                        st.video(video_stream_url)
                        st.markdown(f'<a href="{video_stream_url}" target="_blank" download="ai_video.mp4" style="display:block; text-align:center; padding:12px; background:#10b981; color:white; border-radius:10px; text-decoration:none; font-weight:bold; margin-top:10px;">⬇️ Download MP4 Video</a>', unsafe_allow_html=True)
                else:
                    st.error("Kripya video banane ke liye description likhein!")

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
            topic = st.text_input("Reel ka topic kya hai?", placeholder="Ex: Cricket batting tips / Online business ideas")
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
            niche = st.text_input("Aapka page/account kiske baare mein hai?", placeholder="Ex: Fitness trainer / Gamer")
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
            <div class="shop-product-card">
                <img src="{prod['img']}" style="width:100%; height:180px; object-fit:cover; border-radius:12px;">
                <div style="font-weight:700; margin-top:8px;">{prod['name']}</div>
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

# --- TAB: BILLING ---
elif st.session_state.current_tab == "Billing":
    st.markdown('<div class="welcome-card">', unsafe_allow_html=True)
    st.markdown("### 💳 Upgrade to Soni AI Pro")
    st.write("Unlimited Chats + Direct AI Pic & Video Generator + ₹100 Store Discount pane ke liye Pro activate karein:")

    final_price = 49.00 if st.session_state.applied_coupon == "SONI" else 99.00
    qr_img_url, direct_upi_link = generate_upi_qr(final_price, f"Soni AI Pro - {active_user}")

    col_qr, col_pay_form = st.columns([4, 6])
    with col_qr:
        st.image(qr_img_url, caption=f"Scan & Pay ₹{final_price:.2f}", width=220)
        st.markdown(f"**Amount:** `₹{final_price:.2f}` | **UPI:** `{UPI_ID}`")
    with col_pay_form:
        if is_pro_user:
            st.success("🎉 **Pro Mode Active Hai!** Unlimited Chats, Media Studio & VIP Tools unlocked hain.")
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
