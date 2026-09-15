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

st.set_page_config(page_title="Soni AI", page_icon="🤖", layout="centered")

BG_IMAGE_URL = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"
UPI_QR_URL = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa=8307940340@ptyes&pn=Jatin%20Soni&cu=INR"
MY_WHATSAPP_NUMBER = "918307940340"
ADMIN_PIN = "2009"

ORDERS_FILE = "orders_database.json"
PRODUCTS_FILE = "products_database.json"
USERS_FILE = "users_database.json"

# --- CONFIG & SECRETS ---
try:
    SENDER_EMAIL = st.secrets.get("SENDER_EMAIL", "sonijatin177@gmail.com")
    SENDER_PASSWORD = st.secrets.get("SENDER_APP_PASSWORD", "")
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
        except:
            return default
    return default

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def send_otp_email(to_email, otp_code):
    if not SENDER_PASSWORD:
        return False, "SENDER_APP_PASSWORD set nahi hai Secrets mein!"
    try:
        msg = MIMEText(f"Hello,\n\nAapka Soni AI verification code hai: {otp_code}\n\nYeh code kisi ke sath share na karein.\n\nTeam Soni AI")
        msg['Subject'] = f"{otp_code} - Soni AI Verification Code"
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return True, "Code aapke Gmail par bhej diya gaya hai!"
    except Exception as e:
        return False, f"Email bhejne mein dikkat: {e}"

# --- AUTO LOGIN PERSISTENCE (Refresh safe) ---
users_db = load_json(USERS_FILE, {})
query_params = st.query_params

if "user" not in st.session_state:
    stored_user = query_params.get("user")
    if stored_user and stored_user in users_db:
        st.session_state.user = stored_user
    else:
        st.session_state.user = None

if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = None
if "pending_email" not in st.session_state:
    st.session_state.pending_email = None

def load_orders():
    return load_json(ORDERS_FILE, [])

def save_all_orders(orders_list):
    save_json(ORDERS_FILE, orders_list)

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
                except:
                    pass
        now_india = datetime.now(ZoneInfo("Asia/Kolkata"))
        return f"Abhi **India 🇮🇳** mein time **{now_india.strftime('%I:%M %p')}** ho raha hai.\n\nDusre desh ka time dekhne ke liye country ka naam likhein (jaise: *Dubai time*, *USA time*)."
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
        display: inline-block;
    }}

    .donate-box {{
        position: relative;
    }}
    .donate-btn {{
        background: rgba(0, 0, 0, 0.75);
        color: #ff69b4 !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid rgba(255, 105, 180, 0.4);
        backdrop-filter: blur(8px);
        cursor: pointer;
        display: inline-block;
        text-align: center;
    }}
    .donate-content {{
        display: none;
        position: absolute;
        right: 115% !important;
        top: 0;
        background: rgba(18, 18, 24, 0.96);
        border: 1px solid rgba(255, 105, 180, 0.4);
        border-radius: 16px;
        padding: 14px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.6);
        width: 210px;
        backdrop-filter: blur(12px);
    }}
    .donate-box:hover .donate-content {{
        display: block;
    }}
    .donate-content img {{
        width: 180px;
        border-radius: 10px;
        margin-bottom: 8px;
    }}
    .donate-content p {{
        font-size: 11px !important;
        color: #e0e0e0 !important;
        margin: 0 !important;
        line-height: 1.3;
    }}

    .shop-btn-link {{
        background: rgba(0, 0, 0, 0.75);
        color: #ffd700 !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none !important;
        border: 1px solid rgba(255, 215, 0, 0.5);
        backdrop-filter: blur(8px);
        display: inline-block;
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

    div[data-testid="stButton"] > button {{
        background: linear-gradient(135deg, #1e1e2f, #2c2d4a) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 8px 18px !important;
    }}
    div[data-testid="stButton"] > button p {{
        color: #ffffff !important;
    }}

    .auth-card-box {{
        background: rgba(18, 18, 28, 0.92);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 30px;
        max-width: 440px;
        margin: 40px auto;
        backdrop-filter: blur(15px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }}

    [data-testid="stChatInput"] {{
        background: rgba(255, 255, 255, 0.96) !important;
        border-radius: 35px !important;
    }}
    </style>

    <div class="top-right-stack">
        <a href="https://mail.google.com/mail/?view=cm&fs=1&to=sonijatin177@gmail.com" target="_blank" class="founder-badge">
            ⚡ Founder: Jatin Soni
        </a>
        <div class="donate-box">
            <div class="donate-btn">💖 Donate / Support</div>
            <div class="donate-content">
                <img src="{UPI_QR_URL}" alt="Paytm Scanner">
                <p><b>Scan with Paytm/PhonePe/GPay</b></p>
                <p style="color:#00e5ff !important; margin-top:4px;">UPI: 8307940340@ptyes</p>
            </div>
        </div>
        <a href="/?action=toggle_shop" target="_self" class="shop-btn-link">
            🛍️ Soni Shop
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🤖 Soni AI")

CREATOR_REPLY = "Mujhe Jatin Soni ne banaya hai! Woh 16 saal ke hain, 12th class mein padhte hain aur Haryana ke Sirsa district ke Rori gaon ke rehne wale hain."
CUSTOM_ANSWERS = {"what is skb": "Santosh kulcha bandar", "skb": "Santosh kulcha bandar"}
CURRENT_DATE_STR = datetime.now().strftime("%d %B %Y")
SYSTEM_PROMPT = f"""
You are Soni AI, an intelligent, helpful AI assistant created by Jatin Soni.
Creator: Jatin Soni (16 yrs, 12th class, Rori, Sirsa, Haryana).
Date: {CURRENT_DATE_STR}. Year: 2026.
Rules:
1. Always give direct answers without reasoning tokens, setup lines or fluff.
2. Reply in natural Hinglish or English based on user query.
3. If asked who made you, reply: "{CREATOR_REPLY}"
"""

def clean_model_output(text: str) -> str:
    if not text: return ""
    if "</think>" in text: text = text.split("</think>")[-1]
    elif "<think>" in text: text = re.sub(r'(?i)<think>.*', '', text, flags=re.DOTALL)
    text = re.sub(r'(?i)^\s*(analyze user input|identify key constraints|formulate response|draft response).*?\n\n', '', text, flags=re.DOTALL)
    return text.strip()

# --- AUTH / LOGIN FLOW (OTP Verification) ---
if not st.session_state.user:
    st.markdown('<div class="auth-card-box">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>🔐 Sign In to Soni AI</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:13px; color:#bbb;'>Apna Gmail daalein, verification code aapke inbox mein aayega</p>", unsafe_allow_html=True)

    if not st.session_state.otp_sent:
        with st.form("send_otp_form"):
            email_in = st.text_input("Enter Gmail Address*", placeholder="name@gmail.com").strip().lower()
            submit_email = st.form_submit_button("Send Verification Code 📩", use_container_width=True)

            if submit_email:
                if email_in and "@gmail.com" in email_in:
                    generated_otp = str(random.randint(100000, 999999))
                    success, msg = send_otp_email(email_in, generated_otp)
                    if success:
                        st.session_state.otp_sent = True
                        st.session_state.generated_otp = generated_otp
                        st.session_state.pending_email = email_in
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("Kripya ek valid Gmail address bharein (@gmail.com)!")
    else:
        st.info(f"Code sent to: **{st.session_state.pending_email}**")
        with st.form("verify_otp_form"):
            otp_entered = st.text_input("6-digit Code Daalein*", placeholder="Ex: 582194").strip()
            verify_btn = st.form_submit_button("Verify & Login 🚀", use_container_width=True)

            if verify_btn:
                if otp_entered == st.session_state.generated_otp:
                    user_email = st.session_state.pending_email
                    users_db[user_email] = {"joined": datetime.now().strftime("%d-%m-%Y")}
                    save_json(USERS_FILE, users_db)

                    # Persist session in state and URL query params (Refresh safe)
                    st.session_state.user = user_email
                    st.query_params["user"] = user_email
                    st.session_state.otp_sent = False
                    st.session_state.generated_otp = None
                    st.session_state.pending_email = None
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Galat code! Kripya apna Gmail check karke sahi code daalein.")

        if st.button("Change Email / Resend", key="btn_resend"):
            st.session_state.otp_sent = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- LOGGED IN USER INTERACTION ---
user_active = st.session_state.user
col_top_user, col_top_out = st.columns([7, 3])
with col_top_user:
    st.markdown(f"👤 Logged in as: **{user_active.split('@')[0].capitalize()}**")
with col_top_out:
    if st.button("🚪 Logout", key="btn_logout"):
        st.session_state.user = None
        st.query_params.clear()
        st.rerun()

# --- CHAT / STORE / ADMIN LOGIC ---
if st.session_state.lightbox_img:
    img_url = st.session_state.lightbox_img
    st.markdown(f"""
        <div class="lightbox-overlay" onclick="window.location.reload();">
            <div style="text-align: center; position: relative;">
                <img src="{img_url}" class="lightbox-content"><br>
                <span style="color: #bbb; font-size: 13px; display: block; margin-top: 12px;">(Band karne ke liye screen par click karein)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Admin Panel
if st.session_state.admin_authenticated:
    col_adm_title, col_adm_close = st.columns([7, 3])
    with col_adm_title:
        st.markdown("## 👑 Secret Owner Control Panel")
    with col_adm_close:
        if st.button("❌ Close Admin", key="btn_close_admin"):
            st.session_state.admin_authenticated = False
            st.rerun()

    tab_orders, tab_add_prod, tab_manage_prod = st.tabs(["📦 Manage Orders", "➕ List New Item", "🏷️ Current Store Items"])

    with tab_orders:
        all_orders = load_orders()
        if not all_orders:
            st.info("Abhi tak koi naya order nahi aaya hai.")
        else:
            st.success(f"Total Orders: {len(all_orders)}")
            if st.button("🗑️ Clear All Completed Orders", key="btn_clear_all_orders"):
                save_all_orders([])
                st.success("Saare orders clear ho gaye!")
                st.rerun()

            for idx, ord_data in enumerate(all_orders):
                st.markdown(f"""
                <div class="admin-card-box" style="background:rgba(18,18,28,0.88); border:1px solid #444; padding:12px; border-radius:10px; margin-bottom:8px;">
                    <b>Order #{idx + 1}</b><br>
                    📦 <b>Item:</b> {ord_data['item']} (₹{ord_data['price']})<br>
                    👤 <b>Customer:</b> {ord_data['name']} | 📞 <b>Phone:</b> {ord_data['phone']}<br>
                    🏠 <b>Address:</b> {ord_data['address']}<br>
                    💳 <b>Payment:</b> {ord_data['payment']}
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"🗑️ Delete Order #{idx + 1}", key=f"del_order_{idx}"):
                    all_orders.pop(idx)
                    save_all_orders(all_orders)
                    st.rerun()

    with tab_add_prod:
        st.markdown("### 🛒 Naya Item Shop Mein Add Karein")
        with st.form("form_add_new_product"):
            p_name = st.text_input("Product Name*", placeholder="Ex: Cotton Oversized T-Shirt")
            p_price = st.number_input("Price (in ₹)*", min_value=1, step=1, value=299)
            p_img = st.text_input("Product Image URL*", placeholder="https://example.com/image.jpg")
            submit_item = st.form_submit_button("Shop Mein List Karein 🚀")

            if submit_item:
                if not p_name.strip() or not p_img.strip():
                    st.error("Kripya Product Name aur Image URL dono daalein!")
                else:
                    cur_prods = load_products()
                    new_item = {
                        "id": int(os.urandom(3).hex(), 16),
                        "name": p_name.strip(),
                        "price": int(p_price),
                        "img": p_img.strip()
                    }
                    cur_prods.append(new_item)
                    save_all_products(cur_prods)
                    st.success(f"'{p_name}' successfully shop mein list ho gaya! 🎉")
                    st.rerun()

    with tab_manage_prod:
        st.markdown("### 🗑️ Store ke Items Hataein")
        cur_prods = load_products()
        for idx, item in enumerate(cur_prods):
            col_img, col_info, col_del = st.columns([2, 5, 3], vertical_alignment="center")
            with col_img:
                st.markdown(f'<img src="{item["img"]}" width="60" style="border-radius:8px; object-fit:cover; height:60px;">', unsafe_allow_html=True)
            with col_info:
                st.markdown(f"**{item['name']}**\n\n₹{item['price']}")
            with col_del:
                if st.button(f"Delete Product", key=f"del_prod_{item['id']}"):
                    cur_prods.pop(idx)
                    save_all_products(cur_prods)
                    st.rerun()

    st.markdown("---")

# Store Window
if st.session_state.show_shop:
    col_head, col_back = st.columns([7, 3])
    with col_head:
        st.markdown("## 🛍️ Soni Store")
    with col_back:
        if st.button("⬅️ Back to Chat", key="btn_back_to_chat"):
            st.session_state.show_shop = False
            st.session_state.lightbox_img = None
            st.rerun()

    st.markdown("---")
    products = load_products()

    if not products:
        st.info("Shop mein koi product nahi hai.")
    else:
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]

        for i, prod in enumerate(products):
            with cols[i % 3]:
                if st.button("", key=f"zoom_click_{prod['id']}", use_container_width=True, help="Click image to zoom"):
                    st.session_state.lightbox_img = prod["img"]
                    st.rerun()

                st.markdown(f"""
                <div style="background:rgba(0,0,0,0.55); border:1px solid rgba(255,255,255,0.15); border-radius:18px; padding:14px; text-align:center; margin-bottom:20px;">
                    <img src="{prod['img']}" style="width:100%; height:180px; object-fit:cover; border-radius:10px;">
                    <div style="font-size:15px; font-weight:700; color:#fff; margin-top:8px;">{prod['name']}</div>
                    <div style="font-size:16px; font-weight:800; color:#00e5ff; margin-bottom:10px;">₹{prod['price']}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"🛒 Buy Now", key=f"buy_btn_{prod['id']}", use_container_width=True):
                    st.session_state.selected_product = prod
                    st.session_state.lightbox_img = None
                    st.rerun()

    if "selected_product" in st.session_state and st.session_state.selected_product:
        item = st.session_state.selected_product
        st.markdown("---")
        st.markdown(f"### 📦 Checkout: {item['name']} (₹{item['price']})")

        with st.form("order_checkout_form"):
            cust_name = st.text_input("Aapka Naam*", placeholder="Apna pura naam likhein")
            cust_phone = st.text_input("Mobile Number*", placeholder="10-digit mobile number")
            cust_address = st.text_area("Delivery Address*", placeholder="House no, Gali/Ward, Gaon/City, District, Pincode")
            payment_mode = st.radio("Payment Mode*", ["Cash on Delivery (COD)", "Pay Online (UPI / QR)"])
            submit_order = st.form_submit_button("Confirm Order 🚀", use_container_width=True)

            if submit_order:
                if not cust_name.strip() or not cust_phone.strip() or not cust_address.strip():
                    st.error("Kripya saari details bharein!")
                else:
                    order_data = {
                        "item": item["name"],
                        "price": item["price"],
                        "name": cust_name.strip(),
                        "phone": cust_phone.strip(),
                        "address": cust_address.strip(),
                        "payment": payment_mode
                    }
                    orders = load_orders()
                    orders.append(order_data)
                    save_all_orders(orders)

                    msg = f"🛒 *NEW ORDER - SONI STORE*\n\n📦 Product: {item['name']}\n💰 Price: ₹{item['price']}\n👤 Customer: {cust_name}\n📞 Mobile: {cust_phone}\n🏠 Address: {cust_address}\n💳 Payment: {payment_mode}"
                    wa_url = f"https://wa.me/{MY_WHATSAPP_NUMBER}?text={urllib.parse.quote(msg)}"
                    st.success("Order Confirm ho gaya hai! 🎉")
                    if payment_mode == "Pay Online (UPI / QR)":
                        st.image(UPI_QR_URL, caption=f"Scan & Pay ₹{item['price']}", width=180)

                    st.markdown(f'<a href="{wa_url}" target="_blank" style="display:block; text-align:center; padding:12px 24px; background:#25D366; color:white; border-radius:25px; text-decoration:none; font-weight:bold; margin-top:10px;">📲 WhatsApp par Order Send Karein</a>', unsafe_allow_html=True)
                    st.session_state.selected_product = None

# Chat Area
else:
    col_c1, col_c2 = st.columns([7, 3])
    with col_c1:
        st.write("Aapka personal AI Assistant!")
    with col_c2:
        if st.button("🧹 Clear Chat", key="btn_clear_chat"):
            st.session_state.messages = []
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask Soni AI anything...")

    if user_input:
        clean_input = user_input.strip()

        if clean_input == f"/admin {ADMIN_PIN}":
            st.session_state.admin_authenticated = True
            st.rerun()

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
                    except:
                        continue

                bot_reply = clean_model_output(raw_reply) if raw_reply else "Main samajh gaya. Aage batayein?"
            except Exception as e:
                bot_reply = f"Error details: {e}"

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

        st.rerun()
