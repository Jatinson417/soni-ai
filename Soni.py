import streamlit as st
from groq import Groq
import base64

st.set_page_config(page_title="Soni AI", page_icon="🤖", layout="centered")

# --- BACKGROUND & GEMINI UI CSS ---
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

    [data-testid="stSidebar"] {{
        display: none;
    }}

    header, [data-testid="stHeader"], footer, [data-testid="stBottom"], [data-testid="stBottom"] > div {{
        background: transparent !important;
        background-color: transparent !important;
    }}

    .founder-badge {{
        position: fixed;
        top: 55px;
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
    }}

    h1, h2, h3, p {{
        color: #ffffff;
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

    div.stButton > button {{
        background-color: rgba(255, 255, 255, 0.85) !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 25px !important;
        font-size: 15px !important;
        padding: 4px 14px !important;
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

# Purane messages dikhana
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Action Buttons
col1, col2, _ = st.columns([1.3, 1.3, 6])
with col1:
    if st.button("➕ Photo"):
        st.session_state.show_img_box = not st.session_state.show_img_box
        st.session_state.show_mic_box = False
        st.rerun()

with col2:
    if st.button("🎙️ Mic"):
        st.session_state.show_mic_box = not st.session_state.show_mic_box
        st.session_state.show_img_box = False
        st.rerun()

# Photo Uploader
if st.session_state.show_img_box:
    uploaded_file = st.file_uploader("Photo select karein", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        b64 = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
        st.session_state.current_image_b64 = f"data:{uploaded_file.type};base64,{b64}"
        st.image(uploaded_file, caption="Photo attached ready to ask", width=180)

voice_audio = None
if st.session_state.show_mic_box:
    voice_audio = st.audio_input("Record Voice")

text_input = st.chat_input("Apna sawal yahan likhein (photo ke baare mein bhi)...")
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
        # Vision Request Handling
        if st.session_state.current_image_b64:
            vision_models = ["meta-llama/llama-4-scout-17b-preview", "llama-3.2-90b-vision-preview"]
            bot_reply = None
            for model_name in vision_models:
                try:
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": f"{SYSTEM_PROMPT}\n\nQuestion: {user_input}"},
                                    {"type": "image_url", "image_url": {"url": st.session_state.current_image_b64}}
                                ]
                            }
                        ],
                        model=model_name,
                    )
                    bot_reply = chat_completion.choices[0].message.content
                    break
                except Exception:
                    continue
            
            if not bot_reply:
                bot_reply = "Photo scan karne mein issue aaya. Kripya doosri photo try karein."

            st.session_state.current_image_b64 = None
            st.session_state.show_img_box = False
        else:
            # Regular Text / Contextual Memory Request
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
