import streamlit as st
from groq import Groq
import urllib.parse
import json
import os

st.set_page_config(page_title="Soni AI", page_icon="🤖", layout="centered")

BG_IMAGE_URL = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"
UPI_QR_URL = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa=8307940340@ptyes&pn=Jatin%20Soni&cu=INR"
MY_WHATSAPP_NUMBER = "918307940340"
ADMIN_PIN = "1770"  # Aapka secret password orders dekhne ke liye
ORDERS_FILE = "orders_database.json"

# Permanent File Storage for Orders
def load_orders():
    if os.path.exists(ORDERS_FILE):
        try:
            with open(ORDERS_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_order_to_file(order_dict):
    orders = load_orders()
    orders.append(order_dict)
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=4)

st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: url("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe") no-repeat center center fixed !important;
        background-size: cover !important;
        height: 100vh !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important;
    }

    [data-testid="stSidebar"] {
        display: none !important;
    }

    header, [data-testid="stHeader"], footer, [data-testid="stBottom"], [data-testid="stBottom"] > div {
        background: transparent !important;
        border: none !important;
    }

    /* Founder Badge */
    .founder-badge {
        position: fixed;
        top: 40px;
        right: 25px;
        background: rgba(0, 0, 0, 0.75);
        color: #00e5ff !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none !important;
        border: 1px solid rgba(0, 229, 255, 0.4);
        backdrop-filter: blur(8px);
        z-index: 9999;
        display: block;
    }

    /* Donate Dropdown */
    .donate-box {
        position: fixed;
        top: 80px;
        right: 25px;
        z-index: 9999;
    }
    .donate-btn {
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
    }
    .donate-content {
        display: none;
        position: absolute;
        right: 0;
        top: 36px;
        background: rgba(18, 18, 24, 0.96);
        border: 1px solid rgba(255, 105, 180, 0.4);
        border-radius: 16px;
        padding: 14px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.6);
        width: 210px;
        backdrop-filter: blur(12px);
    }
    .donate-box:hover .donate-content {
        display: block;
    }
    .donate-content img {
        width: 180px;
        border-radius: 10px;
        margin-bottom: 8px;
    }
    .donate-content p {
        font-size: 11px !important;
        color: #e0e0e0 !important;
        margin: 0 !important;
        line-height: 1.3;
    }

    /* Shop Button */
    .shop-trigger-box {
        position: fixed;
        top: 120px;
        right: 25px;
        z-index: 9999;
    }
    .shop-trigger-btn button {
        background: rgba(0, 0, 0, 0.75) !important;
        color: #ffd700 !important;
        border: 1px solid rgba(255, 215, 0, 0.5) !important;
        border-radius: 20px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 6px 14px !important;
        backdrop-filter: blur(8px) !important;
    }

    /* Secret Orders View Button (Top-Left) */
    .admin-badge-box {
        position: fixed;
        top: 40px;
        left: 20px;
        z-index: 9999;
    }
    .admin-badge-box button {
        background: rgba(0, 0, 0, 0.6) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        font-size: 12px !important;
        padding: 4px 12px !important;
    }

    h1, h2, h3, p {
        color: #ffffff;
    }

    .main .block-container {
        max-width: 760px !important;
        padding-top: 40px !important;
        padding-bottom: 140px !important;
    }

    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.93) !important;
        border-radius: 14px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }
    [data-testid="stChatMessage"] p {
        color: #111111 !important;
    }

    [data-testid="stChatInput"] {
        background: rgba(255, 255, 255, 0.96) !important;
        border-radius: 35px !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2) !important;
        border: 1px solid rgba(0,0,0,0.06) !important;
    }
    </style>

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
    """,
    unsafe_allow_html=True
)

# Admin Trigger (Top Left)
st.markdown('<div class="admin-badge-box">', unsafe_allow_html=True)
if st.button("🔒 Admin Orders", key="btn_admin_toggle"):
    st.session_state.show_admin = not st.session_state.get("show_admin", False)
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Shop Trigger (Top Right)
st.markdown('<div class="shop-trigger-box shop-trigger-btn">', unsafe_allow_html=True)
if st.button("🛍️ Soni Shop", key="btn_open_shop"):
    st.session_state.show_shop = not st.session_state.get("show_shop", False)
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.title("🤖 Soni AI")
st.write("Aapka personal AI Assistant!")

client = Groq(api_key="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")

CREATOR_REPLY = (
    "Mujhe Jatin Soni ne banaya hai! Woh 16 saal ke hain, 12th class mein padhte hain "
    "aur Haryana ke Sirsa district ke Rori gaon ke rehne wale hain."
)

SYSTEM_PROMPT = f"""
Aapka naam Soni AI hai.
Aap ek smart aur helpful AI assistant hain.
Aapko Jatin Soni ne banaya aur develop kiya hai.
Jatin Soni ke baare mein details:
- Name: Jatin Soni
- Age: 16 saal
- Class: 12th class student
- Location: Rori village, District Sirsa, Haryana
Agar koi bhi aapse pooche ki aapko kisne banaya, creator/owner kaun hai, ya developer kaun hai, toh hamesha yahi batayein:
"{CREATOR_REPLY}"
Hamesha friendly, respectful aur natural Hinglish/Hindi/English mein jawab dein.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_shop" not in st.session_state:
    st.session_state.show_shop = False
if "show_admin" not in st.session_state:
    st.session_state.show_admin = False

# --- 1. ADMIN ORDERS DASHBOARD (Sirf aapke dekhne ke liye) ---
if st.session_state.show_admin:
    with st.expander("🔒 Owner Dashboard - Received Orders", expanded=True):
        admin_pass = st.text_input("Enter Secret PIN to view orders:", type="password", placeholder="PIN likhein...")
        if admin_pass == ADMIN_PIN:
            all_orders = load_orders()
            if not all_orders:
                st.info("Abhi tak koi naya order nahi aaya hai.")
            else:
                st.success(f"Kul {len(all_orders)} orders mile hain:")
                for idx, ord_data in enumerate(reversed(all_orders)):
                    st.markdown(f"""
                    ---
                    **Order #{len(all_orders) - idx}**
                    * **Product:** `{ord_data['item']}` (₹{ord_data['price']})
                    * **Customer:** **{ord_data['name']}**
                    * **Mobile:** `{ord_data['phone']}`
                    * **Delivery Address:** {ord_data['address']}
                    * **Payment Method:** `{ord_data['payment']}`
                    """)
        elif admin_pass:
            st.error("Galat PIN! Access denied.")

# --- 2. USER SHOPPING WINDOW ---
if st.session_state.show_shop:
    with st.expander("🛍️ Soni Store - Buy Products", expanded=True):
        st.markdown("### 🛒 Hamare Products")
        
        products = [
            {"id": 1, "name": "Women's Stylish Short Kurti", "price": 299, "img": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=400"},
            {"id": 2, "name": "Adjustable Aluminum Laptop Stand", "price": 449, "img": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400"},
            {"id": 3, "name": "Premium Handbag For Women", "price": 399, "img": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400"}
        ]

        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]

        for i, prod in enumerate(products):
            with cols[i % 3]:
                st.image(prod["img"], use_container_width=True)
                st.markdown(f"**{prod['name']}**")
                st.markdown(f"Price: **₹{prod['price']}**")
                if st.button(f"Buy Now", key=f"buy_btn_{prod['id']}"):
                    st.session_state.selected_product = prod
                    st.rerun()

        # Checkout Form
        if "selected_product" in st.session_state and st.session_state.selected_product:
            item = st.session_state.selected_product
            st.markdown("---")
            st.markdown(f"### 📦 Checkout: {item['name']} (₹{item['price']})")
            
            with st.form("order_checkout_form"):
                cust_name = st.text_input("Aapka Naam*", placeholder="Apna pura naam likhein")
                cust_phone = st.text_input("Mobile Number*", placeholder="10-digit mobile number")
                cust_address = st.text_area("Delivery Address*", placeholder="House no, Gali/Ward, Gaon/City, District, Pincode")
                payment_mode = st.radio("Payment Mode*", ["Cash on Delivery (COD)", "Pay Online (UPI / QR)"])
                
                submit_order = st.form_submit_button("Confirm Order 🚀")

                if submit_order:
                    if not cust_name.strip() or not cust_phone.strip() or not cust_address.strip():
                        st.error("Kripya saari details (Naam, Mobile, Address) bharein!")
                    else:
                        order_data = {
                            "item": item["name"],
                            "price": item["price"],
                            "name": cust_name.strip(),
                            "phone": cust_phone.strip(),
                            "address": cust_address.strip(),
                            "payment": payment_mode
                        }
                        
                        # File mein permanent save
                        save_order_to_file(order_data)
                        
                        # WhatsApp URL ready
                        msg = (
                            f"🛒 *NEW ORDER - SONI STORE*\n\n"
                            f"📦 *Product:* {item['name']}\n"
                            f"💰 *Price:* ₹{item['price']}\n"
                            f"👤 *Customer:* {cust_name}\n"
                            f"📞 *Mobile:* {cust_phone}\n"
                            f"🏠 *Address:* {cust_address}\n"
                            f"💳 *Payment Mode:* {payment_mode}\n"
                        )
                        wa_url = f"https://wa.me/{MY_WHATSAPP_NUMBER}?text={urllib.parse.quote(msg)}"
                        
                        st.success("Order Confirm ho gaya hai! 🎉")
                        
                        if payment_mode == "Pay Online (UPI / QR)":
                            st.image(UPI_QR_URL, caption=f"Scan & Pay ₹{item['price']}", width=180)
                        
                        st.markdown(f'''
                            <a href="{wa_url}" target="_blank" style="display:inline-block; padding:12px 24px; background:#25D366; color:white; border-radius:25px; text-decoration:none; font-weight:bold; margin-top:10px;">
                                📲 WhatsApp par Order Send Karein
                            </a>
                        ''', unsafe_allow_html=True)
                        st.session_state.selected_product = None

# Chat messages display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask Soni AI anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    input_lower = user_input.lower()
    creator_triggers = [
        "kisne banaya", "who made you", "developer", "creator", 
        "owner", "kaun banaya", "maker", "who created", "who is your developer"
    ]

    if any(trigger in input_lower for trigger in creator_triggers):
        bot_reply = CREATOR_REPLY
    else:
        try:
            conversation_history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[-10:]
            ]
            payload = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

            chat_completion = client.chat.completions.create(
                messages=payload,
                model="openai/gpt-oss-20b",
            )
            bot_reply = chat_completion.choices[0].message.content
        except Exception as e:
            bot_reply = f"Error aaya: {e}"

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)

    st.rerun()
