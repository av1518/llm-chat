import streamlit as st
from audiorecorder import audiorecorder
import time
import httpx
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    PrerecordedOptions,
    FileSource,
    SpeakOptions,
)
from utils import stream_content
import warnings

# Suppress specific deprecation warnings (deepgram v("1"))
warnings.filterwarnings("ignore", category=DeprecationWarning)

DEEPGRAM_API_KEY = "2c4355877a0cc0c302be01872780f27cf28cee94"

# Initialise chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Placeholderf dictionary for requesting data to ollama API
request_data = {"model": "llama3", "messages": []}

# Accept user input or record audio
col1, col2 = st.columns([5, 1])
with col1:
    prompt = st.chat_input("What's up?", key="user_prompt")
with col2:
    audio = audiorecorder("Record", "Stop")

final_prompt = None
if prompt:
    final_prompt = prompt
elif audio:
    print("audio recorded")
    # using deepgram to transcribe audio
    # add unique id to the audio file in case the user wants to keep it
    id_ = str(time.time())
    audio.export(f"data/audio{id_}.wav", format="wav")

    with open(f"data/audio{id_}.wav", "rb") as file:
        buffer_data = file.read()

    # deepgram config and API keys
    config: DeepgramClientOptions = DeepgramClientOptions()
    deepgram: DeepgramClient = DeepgramClient(DEEPGRAM_API_KEY, config)

    payload: FileSource = {
        "buffer": buffer_data,
    }

    options: PrerecordedOptions = PrerecordedOptions(model="nova-2", smart_format=True)

    transcription = deepgram.listen.rest.v("1").transcribe_file(
        payload, options, timeout=httpx.Timeout(300.0, connect=10.0)
    )

    # retrieve the fully punctuated response from the raw data
    final_prompt = str(
        transcription["results"]["channels"][0]["alternatives"][0]["transcript"]
    )
    print("audio transcribed to final_prompt = ", final_prompt)

# Add user or audio-transcribed prompt to chat history
if final_prompt:
    # Add the 'final_prompt' to the chat history
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    # Display the 'final_prompt' in the chat
    with st.chat_message("user"):
        st.markdown(final_prompt)

    # Make streaming request to ollama
    with st.chat_message("assistant"):
        # Add all the messages to the request data
        request_data["messages"] = st.session_state.messages
        response = st.write_stream(
            stream_content("http://localhost:11434/api/chat", request_data)
        )

        # Configure the TTS
        deepgram: DeepgramClient = DeepgramClient(DEEPGRAM_API_KEY)
        options = SpeakOptions(
            model="aura-luna-en", encoding="linear16", container="wav"
        )
        # Unique identifier for the audio response file
        id_ = str(time.time())
        # Call the save method on the speak property
        _ = deepgram.speak.v("1").save(
            f"data/audio_response{id_}.wav", {"text": response}, options
        )
        # Display audio using streamlit
        with open(f"data/audio_response{id_}.wav", "rb") as file:
            audio_bytes = file.read()

        st.audio(audio_bytes, format="audio/wav")
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
