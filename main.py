import os
import time
import pygame
from gtts import gTTS
import streamlit as st
import speech_recognition as sr
from googletrans import LANGUAGES, Translator

is_translation_active = False

translator_engine = Translator()  # Initialize the translator module.
pygame.mixer.init()  # Initialize the mixer module.

# Create a mapping between language names and language codes
language_map = {name: code for code, name in LANGUAGES.items()}


def get_language_code(language_name):
    return language_map.get(language_name, language_name)


def translate_text(spoken_text, source_language, target_language):
    return translator_engine.translate(spoken_text, src=source_language, dest=target_language)


def text_to_speech(text, language_code):
    tts = gTTS(text=text, lang=language_code, slow=False)
    tts.save("temp_audio.mp3")
    audio_clip = pygame.mixer.Sound("temp_audio.mp3")  # Load the sound.
    audio_clip.play()
    # Ensure the sound completes before deleting.
    time.sleep(audio_clip.get_length())
    os.remove("temp_audio.mp3")  # Clean up temp file.


def translation_loop(output_placeholder, source_language_code, target_language_code):
    global is_translation_active

    progress_bar = st.progress(0)
    step = 0

    while is_translation_active:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            output_placeholder.markdown("🎙️ **Listening...**")
            recognizer.pause_threshold = 1
            audio_data = recognizer.listen(source, phrase_time_limit=10)

        try:
            step += 1
            progress_bar.progress(step % 100)  # Update progress
            output_placeholder.markdown("⏳ **Processing speech...**")
            spoken_text = recognizer.recognize_google(
                audio_data, language=source_language_code)

            output_placeholder.markdown("🔄 **Translating...**")
            translated_text = translate_text(
                spoken_text, source_language_code, target_language_code)

            output_placeholder.markdown(
                f"✅ **Translation Completed:** {translated_text.text}")
            text_to_speech(translated_text.text, target_language_code)
            progress_bar.progress(0)  # Reset progress bar after completion

        except Exception as e:
            st.error(f"⚠️ An error occurred: {e}")
            is_translation_active = False


# UI layout

st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 Real-Time Language Translator")

# Header
st.header("Translate Spoken Language in Real Time")
st.info("This app listens to your speech, translates it into the target language, and speaks it back.")

# Language selection
st.subheader("🌍 Select Source and Target Languages")
source_language_name = st.selectbox(
    "Select Source Language:", list(LANGUAGES.values()), index=list(LANGUAGES.values()).index("english"))
target_language_name = st.selectbox(
    "Select Target Language:", list(LANGUAGES.values()), index=list(LANGUAGES.values()).index("spanish"))

# Convert language names to language codes
source_language_code = get_language_code(source_language_name)
target_language_code = get_language_code(target_language_name)

# Buttons to control translation
st.subheader("🎤 Translation Controls")
col1, col2 = st.columns(2)
with col1:
    start_translation = st.button(
        "🚀 Start Translation", key="start_button", help="Click to start the real-time translation.")
with col2:
    stop_translation = st.button(
        "⛔ Stop Translation", key="stop_button", help="Click to stop the translation process.")

# Output area
output_area = st.empty()

# Logic for starting/stopping translation
if start_translation:
    if not is_translation_active:
        is_translation_active = True
        output_area.markdown("⌛ **Starting translation...**")
        translation_loop(output_area, source_language_code,
                         target_language_code)

if stop_translation:
    is_translation_active = False
    output_area.markdown("🚫 **Translation stopped.**")
    st.success("You can restart the translation anytime!")
