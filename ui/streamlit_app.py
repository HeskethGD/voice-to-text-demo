import streamlit as st
import requests
from audio_recorder_streamlit import audio_recorder
import io
from datetime import datetime

BASE_URL = "http://localhost:8000"
CHAT_URL = f"{BASE_URL}/api/chat/"
VOICE_URL = f"{BASE_URL}/api/voice_to_text/"

def chat_response(messages):
    with requests.post(CHAT_URL, json={"messages": messages}, stream=True) as r:
        for chunk in r.iter_content(1, decode_unicode=True):
            if chunk:
                yield chunk

def transcribe_audio(audio_bytes):
    """Send audio to backend for transcription"""
    try:
        # Create a file-like object from the audio bytes
        audio_file = io.BytesIO(audio_bytes)
        
        # Create the files dictionary with a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        files = {
            'audio': (f'recording_{timestamp}.wav', audio_file, 'audio/wav')
        }
        
        # Send the request to the voice-to-text endpoint
        response = requests.post(VOICE_URL, files=files)
        
        if response.status_code == 200:
            return response.json().get('transcript')
        else:
            st.error(f"Error transcribing audio: {response.json().get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        st.error(f"Error sending audio to server: {str(e)}")
        return None

st.title('Chatbot')

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        response = st.write_stream(chat_response(messages))
    st.session_state.messages.append({"role": "assistant", "content": response})

with st.sidebar:

    audio_bytes = audio_recorder(
        text="",
        recording_color="#e87474",
        neutral_color="#808080",
        pause_threshold=30.0  # Maximum recording duration in seconds
    )

# Handle audio input
if audio_bytes:
    with st.spinner('Transcribing audio...'):
        transcript = transcribe_audio(audio_bytes)
        if transcript:
            # Add transcribed text as user message
            st.session_state.messages.append({"role": "user", "content": transcript})
            with st.chat_message("user"):
                st.markdown(transcript)
            
            # Get and display assistant response
            with st.chat_message("assistant"):
                messages = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
                response = st.write_stream(chat_response(messages))
            st.session_state.messages.append({"role": "assistant", "content": response})