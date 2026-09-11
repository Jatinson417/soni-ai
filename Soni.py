import streamlit as st
from groq import Groq
import base64

st.set_page_config(page_title="Soni AI", page_icon="🤖", initial_sidebar_state="collapsed")

# --- BACKGROUND & BADGE CSS ---
BG_IMAGE_URL = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{BG_IMAGE_URL}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Sidebar hide karna */
    [data-testid="stSidebar"] {{
        display: none;
    }}

    header, [data-testid="stHeader"], footer, [data-testid="stBottom"], [data-testid="stBottom"] > div {{
        background: transparent !important;
        background-color: transparent !important;
    }}

    /* Founder Badge */
    .founder-badge {{
        position: fixed;
        top: 60px;
        right: 25px;
        background: rgba(0, 0, 0, 0.75);
        color: #00e5ff !important;
        padding: 8px 18px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        text-decoration: none !important;
        border: 1px solid rgba(0, 229, 255, 0.4);
        backdrop-filter: blur(8px);
        z-index: 9999;
        transition: all 0.3s ease;
        display: inline-block;
    }}
    .founder-badge:hover {{
        background: rgba(0, 229, 255, 0.25);
        color: #ffffff !important;
        border-color: #00e5ff;
        transform: scale(1.05);
    }}

    h1, h2, h3, p {{
        color: #ffffff;
    }}

    /* Chat bubble design */
    [data-testid="stChatMessage"] {{
        background-color: rgba(255, 255, 255, 0.92) !important;
        border-radius: 14px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }}
    [data-testid="stChatMessage"] p {{
        color: #111111 !important;
    }}
    </style>

    <a href="https://mail.google.com/mail/?view=cm&fs=1&to=sonijatin177@gmail.com" 
       target="_blank" 
       class="founder-badge">
        ⚡ Founder: Jatin Soni
    </a>
    """,
    unsafe_allow_html=True
)

st.title("🤖 Soni AI")
st.write("Aapka personal AI Assistant!")

# Groq Setup
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
Hamesha pichli conversation ka context yaad rakhein aur friendly Hinglish/Hindi/English mein jawab dein.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_uploader" not in st.session_state:
    st.session_state.show_uploader = False
if "show_mic" not in st.session_state:
    st.session_state.show_mic = False

# Chat History Display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- GEMINI STYLE COMPACT ACTION BUTTONS (Above input bar) ---
btn_col1, btn_col2, _ = st.columns([1, 1, 6])
with btn_col1:
    if st.button("➕ Photo"):
        st.session_state.show_uploader = not st.session_state.show_uploader
with btn_col2:
    if st.button("🎙️ Mic"):
        st.session_state.show_mic = not st.session_state.show_mic

uploaded_image = None
if st.session_state.show_uploader:
    uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    if uploaded_image:
        st.image(uploaded_image, width=220)

voice_audio = None
if st.session_state.show_mic:
    voice_audio = st.audio_input("Bol kar puchein", label_visibility="collapsed")

text_input = st.chat_input("Apna sawal yahan likhein...")
user_input = None

if voice_audio:
    try:
        transcription = client.audio.transcriptions.create(
            file=(voice_audio.name, voice_audio.read()),
            model="whisper-large-v3"
        )
        user_input = transcription.text
    except Exception as e:
        st.error(f"Voice detect error: {e}")
elif text_input:
    user_input = text_input

if uploaded_image and not user_input:
    user_input = "Describe this image in detail and tell me what is in it."

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
            if uploaded_image:
                base64_image = base64.b64encode(uploaded_image.getvalue()).decode('utf-8')
                image_url = f"data:{uploaded_image.type};base64,{base64_image}"

                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": user_input},
                                {"type": "image_url", "image_url": {"url": image_url}}
                            ]
                        }
                    ],
                    model="llama-3.2-11b-vision-preview",
                )
                bot_reply = chat_completion.choices[0].message.content
            else:
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
            bot_reply = f"Error aaya hai: {e}"

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
