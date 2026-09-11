import streamlit as st
from groq import Groq

st.set_page_config(page_title="Soni AI", page_icon="🤖")

# --- BACKGROUND & FOUNDER WATERMARK CSS ---
BG_IMAGE_URL = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe"

st.markdown(
    f"""
    <style>
    /* Pura page aur Streamlit container cover */
    .stApp {{
        background-image: url("{BG_IMAGE_URL}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    /* Neeche chat input wale container ka white background hatane ke liye */
    header, [data-testid="stHeader"], footer, [data-testid="stBottom"], [data-testid="stBottom"] > div {{
        background: transparent !important;
        background-color: transparent !important;
    }}

    /* Founder Clickable Badge (Click karte hi Gmail/Email khulega) */
    .founder-badge {{
        position: fixed;
        top: 60px;
        right: 25px;
        background: rgba(0, 0, 0, 0.7);
        color: #00e5ff !important;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        text-decoration: none !important;
        border: 1px solid rgba(0, 229, 255, 0.4);
        backdrop-filter: blur(8px);
        z-index: 9999;
        transition: 0.3s ease;
        display: inline-block;
    }}
    .founder-badge:hover {{
        background: rgba(0, 229, 255, 0.2);
        color: #ffffff !important;
        border-color: #00e5ff;
        transform: scale(1.05);
    }}

    /* Text & Chat Bubbles */
    h1, h2, h3, p {{
        color: #ffffff;
    }}
    
    [data-testid="stChatMessage"] {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }}
    [data-testid="stChatMessage"] p {{
        color: #111111 !important;
    }}
    </style>

    <!-- Clickable Badge with mailto -->
    <a href="mailto:sonijatin177@gmail.com" target="_blank" class="founder-badge">
        ⚡ Founder: Jatin Soni
    </a>
    """,
    unsafe_allow_html=True
)

st.title("🤖 Soni AI")
st.write("Aapka personal AI Assistant!")

# Groq Setup
client = Groq(api_key="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")

# Creator & Identity Details
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

# Purane messages screen par dikhayein
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Apna sawal yahan likhein...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    input_lower = user_input.lower()
    creator_triggers = [
        "kisne banaya", "who made you", "developer", "creator", 
        "owner", "kaun banaya", "maker", "who created", "who is your developer"
    ]

    # Agar creator ke baare mein sawaal ho toh direct reply
    if any(trigger in input_lower for trigger in creator_triggers):
        bot_reply = CREATOR_REPLY
    else:
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                model="openai/gpt-oss-20b",
            )
            bot_reply = chat_completion.choices[0].message.content
        except Exception as e:
            bot_reply = f"Error aaya hai: {e}"

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
