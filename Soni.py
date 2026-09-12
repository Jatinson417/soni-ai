import streamlit as st
from groq import Groq
import urllib.parse
import json
import os
from datetime import datetime

st.set_page_config(page_title="Soni AI", page_icon="🤖", layout="centered")

BG_IMAGE_URL = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"
UPI_QR_URL = "https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa=8307940340@ptyes&pn=Jatin%20Soni&cu=INR"
MY_WHATSAPP_NUMBER = "918307940340"
ADMIN_PIN = "2009"

ORDERS_FILE = "orders_database.json"
PRODUCTS_FILE = "products_database.json"

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

if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_shop" not in st.session_state:
    st.session_state.show_shop = False
if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "lightbox_img" not in st.session_state:
    st.session_state.lightbox_img = None

query_params = st.query_params
if query_params.get("action") == "toggle_shop":
    st.session_state.show_shop = not st.session_state.show_shop
    st.query_params.clear()
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
    .shop-btn-link:hover {{
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

    .lightbox-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.88);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 999999;
        backdrop-filter: blur(10px);
    }}
    .lightbox-content {{
        max-width: 90%;
        max-height: 85vh;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.8);
        border: 2px solid rgba(255,255,255,0.2);
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
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🤖 Soni AI")

client = Groq(api_key="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")

CREATOR_REPLY = (
    "Mujhe Jatin Soni ne banaya hai! Woh 16 saal ke hain, 12th class mein padhte hain "
    "aur Haryana ke Sirsa district ke Rori gaon ke rehne wale hain."
)

today_date_str = datetime.now().strftime("%d %B %Y")

SYSTEM_PROMPT = f"""
Aapka naam Soni AI hai.
Aap ek smart, accurate aur helpful AI assistant hain.
Current Real-Time Date: {today_date_str}
Current Year: 2026
Developer & Owner Info:
- Name: Jatin Soni
- Age: 16 saal
- Class: 12th class student
- Location: Rori village, District Sirsa, Haryana
Rules:
1. Agar koi pooche ki aapko kisne banaya ya developer kaun hai, batayein: "{CREATOR_REPLY}"
2. Agar koi aaj ki taareekh ya date pooche, batayein: "Aaj {today_date_str} hai."
3. Hamesha accurate, friendly aur Hinglish/Hindi mein seedha jawab dein.
"""

if st.session_state.lightbox_img:
    img_url = st.session_state.lightbox_img
    st.markdown(f"""
        <div class="lightbox-overlay" onclick="window.location.reload();">
            <div style="text-align: center; position: relative;">
                <img src="{img_url}" class="lightbox-content"><br>
                <span style="color: #bbb; font-size: 13px; display: block; margin-top: 12px;">(Band karne ke liye photo ya screen par kahin bhi click karein)</span>
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

            st.markdown("---")
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
        st.info("Shop mein filhal koi product nahi hai. Admin panel se add karein.")
    else:
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]

        for i, prod in enumerate(products):
            with cols[i % 3]:
                if st.button("", key=f"zoom_click_{prod['id']}", use_container_width=True, help="Click image to zoom"):
                    st.session_state.lightbox_img = prod["img"]
                    st.rerun()

                st.markdown(f"""
                <div class="shop-product-card" style="margin-top:-10px;">
                    <img src="{prod['img']}" style="width:100%; height:180px; object-fit:cover; border-radius:10px; cursor:pointer;">
                    <div class="shop-product-title">{prod['name']}</div>
                    <div class="shop-product-price">₹{prod['price']}</div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"🛒 Buy Now", key=f"buy_btn_{prod['id']}", use_container_width=True):
                    st.session_state.selected_product = prod
                    st.session_state.lightbox_img = None
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
            
            submit_order = st.form_submit_button("Confirm Order 🚀", use_container_width=True)

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
                    
                    orders = load_orders()
                    orders.append(order_data)
                    save_all_orders(orders)
                    
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
                        <a href="{wa_url}" target="_blank" style="display:block; text-align:center; padding:12px 24px; background:#25D366; color:white; border-radius:25px; text-decoration:none; font-weight:bold; margin-top:10px;">
                            📲 WhatsApp par Order Send Karein
                        </a>
                    ''', unsafe_allow_html=True)
                    st.session_state.selected_product = None

# Chat Area
else:
    st.write("Aapka personal AI Assistant!")
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
        creator_triggers = [
            "kisne banaya", "who made you", "developer", "creator", 
            "owner", "kaun banaya", "maker", "who created", "who is your developer"
        ]

        if any(trigger in input_lower for trigger in creator_triggers):
            bot_reply = CREATOR_REPLY
        else:
            try:
                conversation_payload = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[-10:]
                ]
                payload = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_payload

                # Auto-fallback mechanism: pehla fail hua to doosra chalega
                models_to_try = [
                    "llama-3.3-70b-versatile",
                    "llama-3.3-70b-specdec",
                    "qwen-2.5-32b",
                    "deepseek-r1-distill-llama-70b"
                ]

                bot_reply = None
                for m_name in models_to_try:
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=payload,
                            model=m_name,
                        )
                        bot_reply = chat_completion.choices[0].message.content
                        if bot_reply:
                            break
                    except Exception:
                        continue

                if not bot_reply:
                    bot_reply = "Service thodi busy hai, kripya 1 minute baad try karein."
            except Exception as e:
                bot_reply = f"Error aaya: {e}"

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)

        st.rerun()
