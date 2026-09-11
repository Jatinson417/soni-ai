import streamlit as st
from groq import Groq
import base64

st.set_page_config(page_title="Soni AI", page_icon="🤖", layout="centered")

st.markdown(
    """
    <style>
    /* Full Page Background */
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

    header, [data-testid="stHeader"], footer {
        background: transparent !important;
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

    h1, h2, h3, p {
        color: #ffffff;
    }

    /* Chat Messages scrolling container */
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

    /* Bottom Input Container */
    [data-testid="stBottom"] {
        background: transparent !important;
        padding-bottom: 20px !important;
    }
    [data-testid="stBottom"] > div {
        background: transparent !important;
    }

    /* Gemini Pill Bar */
    [data-testid="stChatInput"] {
        background: rgba(255, 255, 255, 0.96) !important;
        border-radius: 35px !important;
        padding-left: 52px !important;
        padding-right: 52px !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2) !important;
        border: 1px solid rgba(0,0,0,0.06) !important;
    }

    /* Left ➕ Icon embedded inside bar */
    .dock-pill-left {
        position: fixed !important;
        bottom: 30px !important;
        left: calc(50% - 360px) !important;
        z-index: 10001 !important;
    }

    /* Right 🎙️ Icon embedded inside bar (beside send arrow) */
    .dock-pill-right {
        position: fixed !important;
        bottom: 30px !important;
        right: calc(50% - 315px) !important;
        z-index: 10001 !important;
    }

    @media (max-width: 820px) {
        .dock-pill-left { left: 24px !important; }
        .dock-pill-right { right: 65px !important; }
    }

    .pill-icon-btn div[data-testid="stButton"] button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 20px !important;
        width: 32px !important;
        height: 32px !important;
        min-width: 32px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: #444444 !important;
        cursor: pointer !important;
    }
    .pill-icon-btn div[data-testid="stButton"] button:hover {
        background: rgba(0, 0, 0, 0.06) !important;
        border-radius: 50% !important;
        transform: scale(1.15) !important;
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
            <img src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa=8307940340@ptyes&pn=Jatin%20Soni&cu=INR" alt="Paytm Scanner">
            <p><b>Scan with Paytm/PhonePe/GPay</b></p>
            <p style="color:#00e5ff !important; margin-top:4px;">UPI: 8307940340@ptyes</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

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
if "show_img_box" not in st.session_state:
    st.session_state.show_img_box = False
if "show_mic_box" not in st.session_state:
    st.session_state.show_mic_box = False
if "current_image_b64" not in st.session_state:
    st.session_state.current_image_b64 = None

# Messages list
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Image / Voice Upload Trays
if st.session_state.show_img_box:
    uploaded_file = st.file_uploader("Photo choose karein", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        st.session_state.current_image_b64 = f"data:{uploaded_file.type};base64,{b64}"
        st.image(uploaded_file, caption="Photo attached. Sawal likhein.", width=160)

voice_audio = None
if st.session_state.show_mic_box:
    voice_audio = st.audio_input("Record Voice")

# Left ➕ Icon
st.markdown('<div class="dock-pill-left pill-icon-btn">', unsafe_allow_html=True)
if st.button("➕", key="btn_gemini_plus", help="Attach Photo"):
    st.session_state.show_img_box = not st.session_state.show_img_box
    st.session_state.show_mic_box = False
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Right 🎙️ Icon
st.markdown('<div class="dock-pill-right pill-icon-btn">', unsafe_allow_html=True)
if st.button("🎙️", key="btn_gemini_mic", help="Voice Input"):
    st.session_state.show_mic_box = not st.session_state.show_mic_box
    st.session_state.show_img_box = False
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# Root-level native chat input (Ab yeh kabhi gayab nahi hoga)
text_input = st.chat_input("Ask Soni AI anything...")
user_input = None

if voice_audio:
    try:
        transcription = client.audio.transcriptions.create(
            file=(voice_audio.name, voice_audio.read()),
            model="whisper-large-v3"
        )
        user_input = transcription.text
    except Exception as e:
        st.error(f"Voice error: {e}")
elif text_input:
    user_input = text_input

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
        if st.session_state.current_image_b64:
            models_to_try = [
                "qwen/qwen3.6-27b",
                "llama-3.2-11b-vision-preview",
                "llama-3.2-90b-vision-preview"
            ]
            bot_reply = None
            last_err = ""
            for m in models_to_try:
                try:
                    completion = client.chat.completions.create(
                        model=m,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": f"{SYSTEM_PROMPT}\n\nQuestion: {user_input}"},
                                    {"type": "image_url", "image_url": {"url": st.session_state.current_image_b64}}
                                ]
                            }
                        ],
                    )
                    bot_reply = completion.choices[0].message.content
                    break
                except Exception as e:
                    last_err = str(e)
                    continue

            if not bot_reply:
                bot_reply = f"Photo scan error: {last_err}"

            st.session_state.current_image_b64 = None
            st.session_state.show_img_box = False
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
