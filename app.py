"""
Kisan Vaani (किसान वाणी) - Streamlit Voice & Chat Application
Multimodal AI Assistant for Mandi Prices and Government Schemes
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load local environment
load_dotenv()

import agent
import voice

# Configure page
st.set_page_config(
    page_title="Kisan Vaani | किसान वाणी (Voice AI)",
    page_icon="🌾",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom Styling for agricultural & voice theme
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e4620;
        margin-bottom: 0.2rem;
        text-align: center;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4a6b4c;
        text-align: center;
        margin-bottom: 1.2rem;
    }
    .intro-box {
        background-color: #f4fbf4;
        border: 1px solid #cce8cc;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 20px;
        font-size: 0.95rem;
    }
    .voice-tag {
        display: inline-block;
        background: #e7f5e7;
        color: #1a5e1e;
        border: 1px solid #b7dfb8;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.markdown("### 🌾 Kisan Vaani (किसान वाणी)")
    st.caption("Multimodal Voice & Chat Sahayak • First Commit Hackathon")

    api_key_set = bool(agent.get_api_key())
    if api_key_set:
        st.success("● Gemini AI Connected", icon="✅")
    else:
        st.error("● GEMINI_API_KEY is missing in .env!", icon="⚠️")

    st.markdown("---")
    st.markdown("#### ⚙️ Voice Settings")
    enable_voice = st.checkbox("🔊 Enable Voice Output (आवाज़ में उत्तर)", value=True)

    st.markdown("---")
    st.markdown("**Quick Sample Queries / नमूना प्रश्न:**")

    sample_prompt = None
    if st.button("🧅 Onion price in Nashik", use_container_width=True):
        sample_prompt = "What is the onion price in Nashik?"
    if st.button("📜 3 acres eligibility for PM-KISAN", use_container_width=True):
        sample_prompt = "I have 3 acres of land, am I eligible for PM-KISAN? I am a farmer."
    if st.button("🌾 इंदौर में गेहूं का भाव", use_container_width=True):
        sample_prompt = "इंदौर में गेहूं का भाव क्या चल रहा है?"
    if st.button("🚜 Subsidy on machinery (Tenant)", use_container_width=True):
        sample_prompt = "I am a tenant farmer with 5 acres. Can I get subsidy on farm machinery?"

    st.markdown("---")
    if st.button("🔄 New Conversation / नई बातचीत", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.last_recorded_audio = None
        try:
            st.session_state.chat_session = agent.start_chat_session()
        except Exception:
            st.session_state.chat_session = None
        st.rerun()

    st.markdown("---")
    st.caption(
        "Voice Stack: Gemini Audio Multimodal (STT) + gTTS (TTS). "
        "Tracks 5 crops across Nashik, Pune, Indore, and Karnal."
    )

# Title Header
st.markdown('<div class="main-title">🌾 Kisan Vaani (किसान वाणी)</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Bilingual AI Voice Sahayak for Mandi Prices & Government Schemes</div>',
    unsafe_allow_html=True,
)

# Check API key before continuing
if not api_key_set:
    st.error(
        "⚠️ **GEMINI_API_KEY is missing.**\n\n"
        "Please check that `.env` contains `GEMINI_API_KEY=your_key`.",
        icon="🚨",
    )
    st.stop()

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state or st.session_state.chat_session is None:
    try:
        st.session_state.chat_session = agent.start_chat_session()
    except Exception as e:
        st.error(f"Failed to initialize Gemini Agent: {e}")
        st.stop()

if "mic_key_idx" not in st.session_state:
    st.session_state.mic_key_idx = 0

if "last_audio_bytes" not in st.session_state:
    st.session_state.last_audio_bytes = None

# Welcome Banner if no chat history
if len(st.session_state.messages) == 0:
    st.markdown(
        """
        <div class="intro-box">
            <span class="voice-tag">🎙️ Continuous Voice & Text Chat</span><br>
            <b>Namaste! Welcome to Kisan Vaani (किसान वाणी में आपका स्वागत है).</b><br><br>
            You can <b>speak into the microphone</b> or <b>type</b> to ask multiple questions in a continuous conversation:<br>
            1. <b>Check Mandi Rates:</b> Onion, Wheat, Rice, Cotton, and Tomato in Nashik, Pune, Indore, and Karnal.<br>
            2. <b>Check Government Schemes:</b> PM-KISAN, PMFBY (Crop Insurance), and SMAM (Machinery Subsidy).<br><br>
            <i>बोलकर या लिखकर लगातार सवाल पूछें (हिंदी / English)!</i>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("audio"):
            st.audio(msg["audio"], format="audio/mp3")

# Microphone Input Widget for Voice Queries (Auto-resets after each turn)
st.markdown("##### 🎙️ Speak to Kisan Vaani (बोलकर पूछें):")
audio_input = st.audio_input(
    "Click red circle to record, speak your question, then click stop:",
    key=f"mic_recorder_{st.session_state.mic_key_idx}"
)

voice_query_text = None
if audio_input is not None:
    audio_bytes = audio_input.getvalue()
    if audio_bytes != st.session_state.last_audio_bytes:
        st.session_state.last_audio_bytes = audio_bytes
        with st.spinner("🎙️ Transcribing your voice / आवाज़ को समझा जा रहा है..."):
            try:
                voice_query_text = voice.transcribe_audio(audio_bytes, mime_type="audio/wav")
                if not voice_query_text:
                    st.info("🎙️ Could not hear clearly. Please speak closer to your microphone or type your question below! / आवाज़ स्पष्ट नहीं आई, कृपया माइक के पास बोलें या नीचे लिखकर पूछें।")
            except Exception as e:
                st.info("🎙️ Audio input was unclear or interrupted. Please try again or type below.")

# Text Input
text_query = st.chat_input("Or type your question / या यहाँ लिखकर पूछें...")

# Determine which input was triggered
prompt_to_send = sample_prompt or voice_query_text or text_query
is_voice_prompt = bool(voice_query_text)

if prompt_to_send:
    # Append user message
    user_display = f"🎙️ *\"{prompt_to_send}\"*" if is_voice_prompt else prompt_to_send
    st.session_state.messages.append({"role": "user", "content": user_display})
    with st.chat_message("user"):
        st.markdown(user_display)

    # Generate Agent response
    with st.chat_message("assistant"):
        with st.spinner("🌾 Kisan Vaani is checking records / जानकारी खोजी जा रही है..."):
            try:
                answer = agent.send_message(st.session_state.chat_session, prompt_to_send)
                st.markdown(answer)

                audio_data = None
                if enable_voice:
                    with st.spinner("🔊 Generating spoken voice / आवाज़ तैयार की जा रही है..."):
                        audio_data = voice.generate_speech(answer)
                        if audio_data:
                            st.audio(audio_data, format="audio/mp3", autoplay=True)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "audio": audio_data,
                })

                # If triggered by voice, auto-advance the mic counter so mic is immediately ready for next turn
                if is_voice_prompt:
                    st.session_state.mic_key_idx += 1
                    st.session_state.last_audio_bytes = None
                    st.rerun()

            except Exception as e:
                error_msg = f"Sorry, an error occurred while processing your query: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

