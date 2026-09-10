import streamlit as st
from groq import Groq

st.set_page_config(page_title="Soni AI", page_icon="🤖")

st.title("🤖 Soni AI")
st.write("Aapka personal AI Assistant!")

# Groq Client Setup
client = Groq(api_key="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")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Previous messages display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Apna sawal yahan likhein...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Aap Soni AI hain, ek helpful aur smart AI assistant. Hinglish aur Hindi/English mein natural jawab dein."},
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
