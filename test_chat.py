import streamlit as st

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Append sample messages to chat history if not already present
if not st.session_state.messages:
    st.session_state.messages.append({"role": "user", "content": "sample prompt"})
    st.session_state.messages.append(
        {"role": "assistant", "content": "sample response"}
    )

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # For now, we will set the response to mirror the prompt
    response = f"{prompt}"
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
