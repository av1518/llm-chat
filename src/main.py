import requests
import json
import streamlit as st
from audiorecorder import audiorecorder
import time

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    PrerecordedOptions,
    FileSource,
    SpeakOptions,
)
import httpx

DEEPGRAM_API_KEY = "2c4355877a0cc0c302be01872780f27cf28cee94"


def stream_content(url, data):
    """
    Make a streaming POST request and yield the 'content' part of each JSON response as they arrive.

    :param url: The URL to which the POST request is made.
    :param data: A dictionary or JSON string to be sent in the body of the POST request.
    """
    headers = {"Content-Type": "application/json"}

    # If data is a dictionary, convert it to a JSON string
    if isinstance(data, dict):
        data = json.dumps(data)

    # Make a streaming POST request
    with requests.post(url, data=data, headers=headers, stream=True) as response:
        # Raise an error for bad responses
        response.raise_for_status()

        # Process the stream
        for chunk in response.iter_lines():
            if chunk:
                # Decode chunk from bytes to string
                decoded_chunk = chunk.decode("utf-8")

                # Convert string to JSON
                json_chunk = json.loads(decoded_chunk)

                # if the model is done generating, return
                if json_chunk["done"] == True:
                    return
                # Yield the 'content' part
                yield json_chunk["message"]["content"]


style = """
<style>
iframe{
    position: fixed;
    bottom: -25px;
    height: 70px;
    z-index: 9;
}
</style>
"""

st.markdown(style, unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

request_data = {"model": "llama3", "messages": []}

# Accept user input or record audio
audio = audiorecorder("Record", "Stop")
prompt = st.chat_input("What is up?", key="user_prompt")

final_prompt = None
if prompt:
    final_prompt = prompt
elif audio:
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

    response = deepgram.listen.prerecorded.v("1").transcribe_file(
        payload, options, timeout=httpx.Timeout(300.0, connect=10.0)
    )

    # retrieve the fully punctuated response from the raw data
    final_prompt = str(
        response["results"]["channels"][0]["alternatives"][0]["transcript"]
    )

# Add user or audio-transcribed prompt to chat history
if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    # Make streaming request to ollama
    with st.chat_message("assistant"):
        request_data["messages"] = st.session_state.messages
        response = st.write_stream(
            stream_content("http://localhost:11434/api/chat", request_data)
        )
        deepgram: DeepgramClient = DeepgramClient(DEEPGRAM_API_KEY)
        # Configure the TTS
        options = SpeakOptions(
            model="aura-luna-en", encoding="linear16", container="wav"
        )
        # Unique identifier for the audio response file
        id_ = str(time.time())
        # Call the save method on the speak property
        _ = deepgram.speak.v("1").save(
            f"audio_response{id_}.wav", {"text": response}, options
        )
        # Display audio using streamlit
        with open(f"audio_response{id_}.wav", "rb") as file:
            audio_bytes = file.read()

        st.audio(audio_bytes, format="audio/wav")
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

    # ###
    # # Configure the TTS

    # # Make streaming request to ollama
    # with st.chat_message("assistant"):
    #     request_data["messages"] = st.session_state.messages
    #     # Generate a text response first
    #     response = st.write_stream(
    #         stream_content("http://localhost:11434/api/chat", request_data)
    #     )
    #     deepgram: DeepgramClient = DeepgramClient(DEEPGRAM_API_KEY)
    #     # Configure the TTS
    #     options = SpeakOptions(
    #         model="aura-luna-en", encoding="linear16", container="wav"
    #     )
    #     # Unique identifier for the audio response file
    #     id_ = str(time.time())
    #     # Call the save method on the speak property
    #     _ = deepgram.speak.v("1").save(
    #         f"audio_response{id_}.wav", {"text": response}, options
    #     )
    #     # Display audio using streamlit
    #     with open(f"audio_response{id_}.wav", "rb") as file:
    #         audio_bytes = file.read()

    #     st.audio(audio_bytes, format="audio/wav")
    # # Add assistant response to chat history
    # st.session_state.messages.append({"role": "assistant", "content": response})
