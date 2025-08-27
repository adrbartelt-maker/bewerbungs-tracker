# main.py
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

import datetime
import smtplib
from email.message import EmailMessage
import openai

# Twilio für SMS (wenn installiert)
# from twilio.rest import Client

# --------------------------
# APP-Konfiguration
# --------------------------
APP_NAME = "MakeMyDay!"
openai.api_key = "YOUR_OPENAI_API_KEY"  # Für Chatbot-KI

# --------------------------
# Hilfsfunktionen
# --------------------------
def send_email(to_email, subject, body, attachment_path=None):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'dein.email@example.com'
    msg['To'] = to_email
    msg.set_content(body)
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            data = f.read()
            msg.add_attachment(data, maintype='application', subtype='octet-stream', filename=os.path.basename(attachment_path))
    with smtplib.SMTP_SSL('smtp.example.com', 465) as smtp:
        smtp.login('dein.email@example.com', 'dein_email_passwort')
        smtp.send_message(msg)

def send_sms(to_number, message):
    # client = Client("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN")
    # client.messages.create(body=message, from_="+1234567890", to=to_number)
    print(f"SMS an {to_number} gesendet: {message}")

def ask_ai(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# --------------------------
# Haupt-UI
# --------------------------
class MakeMyDayApp(App):
    def build(self):
        self.title = APP_NAME
        self.root = TabbedPanel()
        self.root.do_default_tab = False
        
        # Tab 1: Datei-Manager
        self.file_tab = BoxLayout(orientation='vertical')
        self.file_chooser = FileChooserListView()
        self.file_tab.add_widget(self.file_chooser)
        self.file_preview = Label(text="Dateiinhalt wird hier angezeigt")
        self.file_tab.add_widget(self.file_preview)
        self.file_chooser.bind(selection=self.preview_file)
        self.root.add_widget(self.create_tab(self.file_tab, "Dateien"))

        # Tab 2: Kalender / Termine
        self.calendar_tab = BoxLayout(orientation='vertical')
        self.event_input = TextInput(hint_text="Neues Ereignis eingeben")
        self.calendar_tab.add_widget(self.event_input)
        self.add_event_btn = Button(text="Termin hinzufügen")
        self.add_event_btn.bind(on_press=self.add_event)
        self.calendar_tab.add_widget(self.add_event_btn)
        self.calendar_list = Label(text="Keine Termine")
        self.calendar_tab.add_widget(self.calendar_list)
        self.events = []
        self.root.add_widget(self.create_tab(self.calendar_tab, "Kalender"))

        # Tab 3: Chatbot
        self.chat_tab = BoxLayout(orientation='vertical')
        self.chat_history = Label(text="Willkommen beim MakeMyDay! Chatbot", size_hint_y=None, height=300)
        self.chat_tab.add_widget(self.chat_history)
        self.chat_input = TextInput(hint_text="Frage mich etwas...")
        self.chat_tab.add_widget(self.chat_input)
        self.chat_btn = Button(text="Senden")
        self.chat_btn.bind(on_press=self.chat_with_ai)
        self.chat_tab.add_widget(self.chat_btn)
        self.root.add_widget(self.create_tab(self.chat_tab, "Chatbot"))

        return self.root

    def create_tab(self, content, title):
        tab = BoxLayout()
        tab.add_widget(content)
        tab.text = title
        return tab

    # --------------------------
    # Funktionen
    # --------------------------
    def preview_file(self, filechooser, selection):
        if selection:
            try:
                with open(selection[0], 'r', encoding='utf-8') as f:
                    data = f.read()
                    self.file_preview.text = data[:1000]  # nur die ersten 1000 Zeichen
            except Exception as e:
                self.file_preview.text = f"Datei konnte nicht gelesen werden: {e}"

    def add_event(self, instance):
        event_text = self.event_input.text
        if event_text:
            self.events.append((datetime.datetime.now(), event_text))
            self.update_calendar_display()
            self.event_input.text = ""

    def update_calendar_display(self):
        text = ""
        for dt, ev in self.events:
            text += f"{dt.strftime('%Y-%m-%d %H:%M')}: {ev}\n"
        self.calendar_list.text = text or "Keine Termine"

    def chat_with_ai(self, instance):
        question = self.chat_input.text
        if question:
            answer = ask_ai(question)
            self.chat_history.text += f"\nUser: {question}\nAI: {answer}"
            self.chat_input.text = ""

# --------------------------
# Start App
# --------------------------
if __name__ == "__main__":
    MakeMyDayApp().run()
