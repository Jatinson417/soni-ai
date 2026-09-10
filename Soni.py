import streamlit as st
from google import genai
from google.genai import types

# Page settings
st.set_page_config(page_title="Soni AI Bot", page_icon="🤖")
st.title("🤖 Soni AI Assistant")

# Aapki API Key
API_KEY = "AQ.Ab8RN6LGDLUanT_w1dMluRKpOQowKKsIae9b3dQATmaAst6_Kw"

# Gemini client initialize
client = genai.Client(api_key=API_KEY)

# Custom Creator Instructions
system_instruction = (
    "Aapka naam Soni AI hai. "
    "Jab bhi koi aapse pooche ki aapko kisne banaya hai, aapka creator ya developer kaun hai, "
    "toh hamesha batana ki aapko Jatin Soni ne banaya hai, jinki age 16 years hai, aur wo "
    "Sirsa district ke Rori village me rehte hain. "
    "Zaroori Niyam: User jis bhasha me sawal pooche (Hindi, English, Hinglish, Punjabi, etc.), "
    "aapko ye creator details usi bhasha me translate karke natural tareeqe se batani hai. "
    "Baaki sabhi sawalon ke jawab hamesha helpful aur friendly tone me dena."
)

# Chat history memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Screen par purani chat show karna
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User ka input box
if prompt := st.chat_input("Poochiye apna sawal..."):
    # User message screen par show karein
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI se jawab mangna
    with st.chat_message("assistant"):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            reply = response.text
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Error aaya hai: {e}")