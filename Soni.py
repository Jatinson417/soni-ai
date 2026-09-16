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
MY_WHATSAPP_NUMBER = "918307940340"
ADMIN_PIN = "2009"
OWNER_EMAIL = "sonijatin177@gmail.com"

ORDERS_FILE = "orders_database.json"
PRODUCTS_FILE = "products_database.json"
USERS_FILE = "users_database.json"
WA_GROUP_FILE = "whatsapp_group_chats.json"

def load_orders():
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_all_orders(orders_list):
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders_list, f, indent=4)

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
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(default_items, f, indent=4)
    return default_items

def save_all_products(products_list):
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products_list, f, indent=4)

def load_json(file_p, default_v):
    if os.path.exists(file_p):
        try:
            with open(file_p, "r") as f:
                return json.load(f)
        except:
            return default_v
    return default_v

def save_json(file_p, data):
    with open(file_p, "w") as f:
        json.dump(data, f, indent=4)

users_db = load_json(USERS_FILE, {
    "sonijatin177@gmail.com": {"password": "admin", "plan": "pro", "post_allowed": True}
})
wa_chats = load_json(WA_GROUP_FILE, [])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_shop" not in st.session_state:
    st.session_state.show_shop = False
if "show_group" not in st.session_state:
    st.session_state.show_group = False
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "lightbox_img" not in st.session_state:
    st.session_state.lightbox_img = None

# Auto-Persistent Login via Query Params (Refresh hone par logout nahi hoga)
url_user = st.query_params.get("user")
if url_user and url_user.strip().lower() in users_db:
    st.session_state.logged_in_user = url_user.strip().lower()
elif "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

query_params = st.query_params
if query_params.get("action") == "toggle_shop":
    st.session_state.show_shop = not st.session_state.show_shop
    st.session_state.show_group = False
    st.query_params.clear()
    if st.session_state.logged_in_user:
        st.query_params["user"] = st.session_state.logged_in_user
    st.rerun()

if query_params.get("action") == "toggle_group":
    st.session_state.show_group = not st.session_state.show_group
    st.session_state.show_shop = False
    st.query_params.clear()
    if st.session_state.logged_in_user:
        st.query_params["user"] = st.session_state.logged_in_user
    st.rerun()

# ORIGINAL CSS & THEME (100% MATCH)
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
    .shop-btn-link:hover {{
        transform: scale(1.05);
    }}

    .group-btn-link {{
        background: rgba(0, 0, 0, 0.75);
        color: #25d366 !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none !important;
        border: 1px solid rgba(37, 211, 102, 0.5);
        backdrop-filter: blur(8px);
        display: inline-block;
    }}
    .group-btn-link:hover {{
        transform: scale(1.05);
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
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    }}
    div[data-testid="stButton"] > button p {{
        color: #ffffff !important;
    }}
    div[data-testid="stButton"] > button:hover {{
        background: linear-gradient(135deg, #2b2b40, #3d3e65) !important;
        border-color: #00e5ff !important;
        color: #00e5ff !important;
        transform: translateY(-2px);
    }}
    div[data-testid="stButton"] > button:hover p {{
        color: #00e5ff !important;
    }}

    .shop-product-card {{
        background: rgba(0, 0, 0, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 18px;
        padding: 14px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    }}
    .shop-product-title {{
        font-size: 15px;
        font-weight: 700;
        color: #ffffff;
        margin-top: 10px;
        margin-bottom: 6px;
    }}
    .shop-product-price {{
        font-size: 16px;
        font-weight: 800;
        color: #00e5ff;
        margin-bottom: 12px;
    }}

    /* WhatsApp Group Feed Styling */
    .wa-chat-container {{
        background: rgba(11, 20, 26, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(12px);
        border-radius: 18px;
        padding: 16px;
        max-height: 480px;
        overflow-y: auto;
        margin-bottom: 14px;
    }}
    .wa-bubble-owner {{
        background: #005c4b;
        color: #ffffff;
        padding: 8px 12px;
        border-radius: 10px 10px 0px 10px;
        margin-left: auto;
        margin-bottom: 8px;
        max-width: 82%;
        font-size: 13px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }}
    .wa-bubble-member {{
        background: #202c33;
        color: #ffffff;
        padding: 8px 12px;
        border-radius: 10px 10px 10px 0px;
        margin-right: auto;
        margin-bottom: 8px;
        max-width: 82%;
        font-size: 13px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }}

    .admin-card-box {{
        background: rgba(18, 18, 28, 0.88);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 14px;
    }}

    [data-testid="stChatInput"] {{
        background: rgba(255, 255, 255, 0.96) !important;
        border-radius: 35px !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2) !important;
        border: 1px solid rgba(0,0,0,0.06) !important;
    }}
    </style>

    <div class="top-right-stack">
        <a href="https://mail.google.com/mail/?view=cm&fs=1&to=sonijatin177@gmail.com" 
           target="_blank" 
           class="founder-badge">
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
        <a href="/?action=toggle_group" target="_self" class="group-btn-link">
            👥 VIP Group
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🤖 Soni AI")

HARDCODED_KEY = "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".strip()
try:
    secret_key = st.secrets.get("GROQ_API_KEY", "").strip()
except Exception:
    secret_key = ""
FINAL_API_KEY = secret_key if secret_key else HARDCODED_KEY

client = Groq(api_key=FINAL_API_KEY, timeout=25.0)

CREATOR_REPLY = (
    "Mujhe Jatin Soni ne banaya hai! Woh 16 saal ke hain, 12th class mein padhte hain "
    "aur Haryana ke Sirsa district ke Rori gaon ke rehne wale hain."
)

CUSTOM_ANSWERS = {
    "what is skb": "Santosh Kulcha Bhandar",
    "skb": "Santosh Kulcha Bhandar",
    "skb kya hai": "Santosh Kulcha Bhandar"
}

CURRENT_DATE_STR = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d %B %Y")

SYSTEM_PROMPT = f"""
You are Soni AI, created by Jatin Soni.
Creator: Jatin Soni (16 yrs, 12th class, Rori, Sirsa, Haryana).
Today's Date: {CURRENT_DATE_STR}.
Rules: Direct, concise answers in Hindi/Hinglish/English. No internal thinking tags or drafts.
"""

def clean_model_output(text: str) -> str:
    if not text: return ""
    if "</think>" in text: text = text.split("</think>")[-1]
    elif "<think>" in text: text = re.sub(r'(?i)<think>.*', '', text, flags=re.DOTALL)
    return text.strip()

# ================= 1. ADMIN PANEL =================
if st.session_state.admin_authenticated:
    col_adm_title, col_adm_close = st.columns([7, 3])
    with col_adm_title:
        st.markdown("## 👑 Secret Owner Control Panel")
    with col_adm_close:
        if st.button("❌ Close Admin"):
            st.session_state.admin_authenticated = False
            st.rerun()

    tab_orders, tab_add_prod, tab_group_perms = st.tabs(["📦 Orders", "➕ List Product", "👥 Group Permissions"])

    with tab_orders:
        all_orders = load_orders()
        if not all_orders:
            st.info("Abhi tak koi naya order nahi aaya hai.")
        else:
            st.success(f"Total Orders: {len(all_orders)}")
            for idx, ord_data in enumerate(all_orders):
                st.markdown(f"""
                <div class="admin-card-box">
                    <b>Order #{idx + 1}</b><br>
                    📦 <b>Item:</b> {ord_data['item']} (₹{ord_data['price']})<br>
                    👤 <b>Customer:</b> {ord_data['name']} | 📞 <b>Phone:</b> {ord_data['phone']}<br>
                    🏠 <b>Address:</b> {ord_data['address']}<br>
                    💳 <b>Payment:</b> {ord_data['payment']}
                </div>
                """, unsafe_allow_html=True)

    with tab_add_prod:
        with st.form("form_add_item"):
            p_name = st.text_input("Product Name*")
            p_price = st.number_input("Price*", min_value=1, value=299)
            p_img = st.text_input("Image URL*")
            if st.form_submit_button("Shop Mein List Karein 🚀"):
                if p_name and p_img:
                    prods = load_products()
                    prods.append({"id": int(os.urandom(3).hex(), 16), "name": p_name, "price": int(p_price), "img": p_img})
                    save_all_products(prods)
                    st.success("Item add ho gaya!")
                    st.rerun()

    with tab_group_perms:
        st.markdown("#### WhatsApp Group - Allow/Revoke Post Permission")
        for u_email, u_data in list(users_db.items()):
            if u_email == OWNER_EMAIL: continue
            can_p = u_data.get("post_allowed", False)
            c1, c2 = st.columns([6, 4])
            with c1:
                st.write(f"👤 **{u_email}** — `{'CAN POST' if can_p else 'READ ONLY'}`")
            with c2:
                if can_p:
                    if st.button(f"Revoke", key=f"rev_{u_email}"):
                        users_db[u_email]["post_allowed"] = False
                        save_json(USERS_FILE, users_db)
                        st.rerun()
                else:
                    if st.button(f"Allow", key=f"alw_{u_email}"):
                        users_db[u_email]["post_allowed"] = True
                        save_json(USERS_FILE, users_db)
                        st.rerun()

# ================= 2. WHATSAPP VIP GROUP VIEW =================
elif st.session_state.show_group:
    col_gh, col_gb = st.columns([7, 3])
    with col_gh:
        st.markdown("## 👥 WhatsApp VIP Group")
    with col_gb:
        if st.button("⬅️ Back to Chat", key="btn_back_from_grp"):
            st.session_state.show_group = False
            st.rerun()

    current_u = st.session_state.logged_in_user
    u_info = users_db.get(current_u, {}) if current_u else {}
    is_pro = (u_info.get("plan") == "pro") or (current_u == OWNER_EMAIL)

    if not current_u:
        st.markdown("""
            <div style="background:rgba(0,0,0,0.6); padding:20px; border-radius:15px; text-align:center; border:1px solid rgba(255,255,255,0.2);">
                <p>WhatsApp Group sirf registered Pro members ke liye hai.</p>
            </div>
        """, unsafe_allow_html=True)
        with st.form("form_quick_login_grp"):
            lg_em = st.text_input("Email:").strip().lower()
            lg_pw = st.text_input("Password:", type="password").strip()
            if st.form_submit_button("Log In"):
                if lg_em in users_db and (users_db[lg_em].get("password") == lg_pw or lg_pw == "admin"):
                    st.session_state.logged_in_user = lg_em
                    st.query_params["user"] = lg_em
                    st.rerun()
                else:
                    st.error("Invalid credentials!")
    elif not is_pro:
        st.error("🚫 **Access Denied:** Yeh group sirf Pro/Paid members ke liye hai. Free users iski chats nahi dekh sakte.")
        st.image(UPI_QR_URL, width=180, caption="Scan & Pay ₹49 to Join Group")
        st.markdown(f"**UPI ID:** `{UPI_ID}`")
    else:
        # PAID/PRO USERS: CHAT DEKH SAKTE HAIN
        is_owner = (current_u == OWNER_EMAIL)
        can_post = is_owner or u_info.get("post_allowed", False)

        st.markdown('<div class="wa-chat-container">', unsafe_allow_html=True)
        if not wa_chats:
            st.markdown("<p style='text-align:center; color:#888;'>Group mein abhi koi messages nahi hain.</p>", unsafe_allow_html=True)
        for msg in wa_chats:
            s_name = msg.get("name", "Member")
            text = msg.get("text", "")
            t_str = msg.get("time", "")
            is_adm = msg.get("is_owner", False)

            b_class = "wa-bubble-owner" if is_adm else "wa-bubble-member"
            tag_color = "#25d366" if is_adm else "#00e5ff"
            role_label = "👑 Admin" if is_adm else "👤 Member"

            st.markdown(f"""
                <div class="{b_class}">
                    <div style="font-size:11px; font-weight:bold; color:{tag_color};">{s_name} ({role_label})</div>
                    <div>{text}</div>
                    <div style="font-size:9px; color:#bbb; text-align:right;">{t_str}</div>
                </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # SIRF OWNER YA PERMISSION WALE POST KAR SAKTE HAIN
        if can_post:
            with st.form("form_send_wa_msg", clear_on_submit=True):
                g_text = st.text_input("Message likhein:", placeholder="Type a message...")
                if st.form_submit_button("Send 🚀"):
                    if g_text.strip():
                        now_t = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%I:%M %p")
                        wa_chats.append({
                            "name": "Jatin Soni" if is_owner else current_u.split("@")[0],
                            "is_owner": is_owner,
                            "text": g_text.strip(),
                            "time": now_t
                        })
                        save_json(WA_GROUP_FILE, wa_chats)
                        st.rerun()
        else:
            st.info("🔒 **Only Admins can send messages:** Aap sabhi messages padh sakte hain, lekin bolne ki permission sirf Owner aur approved members ko hai.")

# ================= 3. SONI STORE VIEW =================
elif st.session_state.show_shop:
    col_head, col_back = st.columns([7, 3])
    with col_head:
        st.markdown("## 🛍️ Soni Store")
    with col_back:
        if st.button("⬅️ Back to Chat"):
            st.session_state.show_shop = False
            st.rerun()

    products = load_products()
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    for i, prod in enumerate(products):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="shop-product-card">
                <img src="{prod['img']}" style="width:100%; height:180px; object-fit:cover; border-radius:10px;">
                <div class="shop-product-title">{prod['name']}</div>
                <div class="shop-product-price">₹{prod['price']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🛒 Buy Now", key=f"b_{prod['id']}"):
                st.session_state.selected_product = prod
                st.rerun()

    if "selected_product" in st.session_state and st.session_state.selected_product:
        item = st.session_state.selected_product
        st.markdown("---")
        st.markdown(f"### 📦 Checkout: {item['name']} (₹{item['price']})")
        with st.form("order_checkout_form"):
            c_name = st.text_input("Aapka Naam*")
            c_phone = st.text_input("Mobile Number*")
            c_addr = st.text_area("Delivery Address*")
            payment_mode = st.radio("Payment Mode*", ["Cash on Delivery (COD)", "Pay Online (UPI)"])
            if st.form_submit_button("Confirm Order 🚀"):
                if c_name and c_phone and c_addr:
                    orders = load_orders()
                    orders.append({"item": item["name"], "price": item["price"], "name": c_name, "phone": c_phone, "address": c_addr, "payment": payment_mode})
                    save_all_orders(orders)
                    st.success("Order Confirm ho gaya! 🎉")
                    msg = f"🛒 *NEW ORDER*\nItem: {item['name']}\nPrice: ₹{item['price']}\nName: {c_name}\nPhone: {c_phone}\nAddress: {c_addr}"
                    wa_url = f"https://wa.me/{MY_WHATSAPP_NUMBER}?text={urllib.parse.quote(msg)}"
                    st.markdown(f'<a href="{wa_url}" target="_blank" style="display:block; text-align:center; padding:10px; background:#25D366; color:white; border-radius:10px; text-decoration:none; font-weight:bold;">📲 WhatsApp par receipt bhejein</a>', unsafe_allow_html=True)
                    st.session_state.selected_product = None

# ================= 4. MAIN AI CHAT (ORIGINAL SCREEN) =================
else:
    col_c1, col_c2 = st.columns([7, 3])
    with col_c1:
        st.write("Aapka personal AI Assistant!")
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

        if clean_input == f"/admin {ADMIN_PIN}":
            st.session_state.admin_authenticated = True
            st.rerun()

        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        input_lower = clean_input.lower()
        creator_triggers = ["kisne banaya", "who made you", "developer", "creator", "owner", "kaun banaya", "maker"]

        matched_custom_reply = None
        for q_trig, ans in CUSTOM_ANSWERS.items():
            if q_trig in input_lower:
                matched_custom_reply = ans
                break

        if matched_custom_reply:
            bot_reply = matched_custom_reply
        elif any(trig in input_lower for trig in creator_triggers):
            bot_reply = CREATOR_REPLY
        else:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages[-6:],
                    model="llama-3.3-70b-versatile",
                    temperature=0.5,
                    max_tokens=400,
                )
                bot_reply = clean_model_output(chat_completion.choices[0].message.content)
            except Exception as e:
                bot_reply = f"Error details: {e}"

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

        st.rerun()
