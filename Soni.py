try:
    # Conversation history
    sanitized_history = []

    for m in st.session_state.messages[-12:]:
        clean_content = re.sub(
            r'<think>.*?</think>',
            '',
            m["content"],
            flags=re.DOTALL
        ).strip()

        if clean_content:
            sanitized_history.append({
                "role": m["role"],
                "content": clean_content
            })

    payload = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ] + sanitized_history

    chat_completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=payload,
        max_tokens=1000,
        temperature=0.5,
    )

    raw_reply = chat_completion.choices[0].message.content or ""

    bot_reply = re.sub(
        r'<think>.*?</think>',
        '',
        raw_reply,
        flags=re.DOTALL
    ).strip()

    if not bot_reply:
        bot_reply = "Sorry, mujhe iska proper answer generate nahi ho paya."

except Exception as e:
    bot_reply = "Sorry, abhi response generate karne mein problem aa rahi hai."
    print("Groq Error:", e)
