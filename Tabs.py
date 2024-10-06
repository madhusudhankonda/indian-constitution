import streamlit as st

tab1, tab2 = st.tabs(["Chat", "Use Case Config"])

with tab1:
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    for msg in st.session_state.messages:
        if isinstance(msg["content"], str):
            st.chat_message(msg["role"]).write(msg["content"])
        else:
            st.chat_message(msg["role"]).write_stream(msg["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        bot_response = generate_response(st.session_state.conversation_id, prompt, st.session_state.use_case)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        st.chat_message("assistant").write(bot_response)
        