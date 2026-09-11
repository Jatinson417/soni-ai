import streamlit as st
from groq import Groq

st.set_page_config(page_title="Soni AI", page_icon="🤖")

st.title("🤖 Soni AI")
st.write("Aapka personal AI Assistant!")

# Groq Setup
client = Groq(api_key="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")

# Creator & Identity Details
CREATOR_REPLY = (
    "Mujhe Jatin Soni ne banaya hai! Woh 16 saal ke hain, 12th class mein padhte hain "
    "aur Haryana ke Sirsa district ke Rori village ke rehne wale hain."
)

SYSTEM_PROMPT = f"""
Aapka naam Soni AI hai.
Aap ek smart aur helpful AI assistant hain.
Aapko Jatin Soni ne banaya aur develop kiya hai.
Jatin Soni ke baare mein details:
- Age: 16 years
- Class: 12th class student
- Location: Rori village, District Sirsa, Haryana
Agar koi bhi aapse pooche ki aapko kisne banaya, creator/owner kaun hai, ya developer kaun hai, toh hamesha yahi batayein:
"{CREATOR_REPLY}"
Hamesha friendly, respectful aur natural Hinglish/Hindi/English mein jawab dein.
"""

# Dynamic Model Selection (Jo active hai wahi use hoga)
@st.cache_resource
def get_working_model():
    try:
        available_models = [m.id for m in client.models.list().data if "whisper" not in m.id and "guard" not in m.id]
        if available_models:
            return available_models[0]
    except Exception:
        pass
    return "llama-3.3-70b-versatile"

ACTIVE_MODEL = get_working_model()

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

    # Agar creator ke baare mein sawaal ho toh direct accurate reply
    if any(trigger in input_lower for trigger in creator_triggers):
        bot_reply = CREATOR_REPLY
    else:
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                model=ACTIVE_MODEL,
            )
            bot_reply = chat_completion.choices[0].message.content
        except Exception as e:
            bot_reply = f"Error aaya hai: {e}"

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
