import streamlit as st
from audiorecorder import audiorecorder
import time
import os

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize a counter for unique keys if not already present
if "audio_key_counter" not in st.session_state:
    st.session_state.audio_key_counter = 0

# Generate a unique key for the audio recorder
audio_key = f"audio_{st.session_state.audio_key_counter}"

# Accept user input or record audio
audio = audiorecorder("Record", "Stop", key=audio_key)
prompt = st.chat_input("What's up?", key="user_prompt")

final_prompt = None
if prompt:
    final_prompt = prompt
elif len(audio) > 0:
    st.write("Audio recorded!")
    # Add unique id to the audio file in case the user wants to keep it
    id_ = str(time.time())
    file_path = f"data/audio{id_}.wav"
    audio.export(file_path, format="wav")
    st.write(f"Audio saved to {file_path}")

    # Check if the file exists to confirm export
    if os.path.exists(file_path):
        st.write("Audio file exists.")
    else:
        st.write("Audio file does not exist.")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Add user or audio-transcribed prompt to chat history
if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

# Increment the audio key counter for the next interaction
st.session_state.audio_key_counter += 1
