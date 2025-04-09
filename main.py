import sys
import threading
import uuid
import speech_recognition as sr
import requests
import pygame
from io import BytesIO
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# --------- Initialize pygame mixer for audio playback ---------
pygame.mixer.init()

# --------- Generate Random UID for Each Session ---------
USER_ID = str(uuid.uuid4())

# --------- API Configuration ---------
API_URL = "https://personal-ai-assistant-by-nzr.onrender.com/pai"

# --------- Voice Input ---------
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."

# --------- Audio Playback ---------
def play_audio(audio_url):
    try:
        response = requests.get(audio_url)
        audio_data = BytesIO(response.content)
        pygame.mixer.music.load(audio_data, "mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print("Audio playback error:", e)

# --------- GUI Application ---------
class VoiceChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎤 Voice-to-Voice Chat AI")
        self.setGeometry(100, 100, 400, 600)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)

        # UID Label
        self.uid_label = QLabel(f"🆔 Session ID: {USER_ID}")
        self.uid_label.setStyleSheet("color: #666; font-size: 10px;")
        self.layout.addWidget(self.uid_label)

        # Chat Area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet(
            "background-color: #fdfdfd; font-size: 14px; border: 1px solid #ccc; padding: 8px;"
        )
        self.layout.addWidget(self.chat_area)

        # Typing Indicator
        self.typing_label = QLabel("🤖 AI is typing...")
        self.typing_label.setStyleSheet("color: gray; font-style: italic;")
        self.typing_label.setVisible(False)
        self.layout.addWidget(self.typing_label)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(line)

        # Talk Button
        self.ask_button = QPushButton("🎤 Talk to AI")
        self.ask_button.setStyleSheet("padding: 10px; font-size: 16px;")
        self.ask_button.clicked.connect(self.start_conversation)
        self.layout.addWidget(self.ask_button)

    def start_conversation(self):
        threading.Thread(target=self.run_conversation, daemon=True).start()

    def append_chat(self, sender, text, emoji):
        self.chat_area.append(f"{emoji} <b>{sender}</b>: {text}")
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def run_conversation(self):
        query = get_voice_input()
        self.append_chat("You", query, "🧑")
        self.typing_label.setVisible(True)

        response_data = send_request(query)

        self.typing_label.setVisible(False)
        if response_data:
            self.append_chat("AI", response_data.get('text', "No response."), "🤖")

            # Play audio if available
            if response_data.get("audio"):
                play_audio(response_data["audio"])

# --------- Send HTTP Request to AI API ---------
def send_request(query):
    try:
        params = {
            "ask": query,
            "voice": "true",
            "uid": USER_ID
        }
        response = requests.get(API_URL, params=params)
        return response.json()
    except Exception as e:
        print("API request error:", e)
        return {"text": "Sorry, there was a problem connecting to the AI.", "audio": None}

# --------- Run App ---------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceChatApp()
    window.show()
    sys.exit(app.exec_())
