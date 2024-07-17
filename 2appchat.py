# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 14:17:36 2024

@author: mikym
"""

import streamlit as st
import hashlib
import sqlite3
from datetime import datetime

# Datenbankfunktionen
def init_db():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY, sender TEXT, message TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Überprüfen, ob der Benutzername bereits existiert
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return False  # Benutzername existiert bereits
    
    c.execute("INSERT INTO users VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()
    return True

def verify_user(username, password):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
    result = c.fetchone()
    conn.close()
    return result is not None

def save_message(sender, message):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)",
              (sender, message, timestamp))
    conn.commit()
    conn.close()

def get_messages():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute("SELECT sender, message, timestamp FROM messages ORDER BY timestamp DESC LIMIT 50")
    messages = c.fetchall()
    conn.close()
    return messages[::-1]  # Umkehren der Reihenfolge, um neueste Nachrichten unten anzuzeigen

def show_registration_form():
    st.title("Registrierung")

    username = st.text_input("Benutzername", key="register_username")
    password = st.text_input("Passwort", type="password", key="register_password")
    invite_code = st.text_input("Einladungscode", key="register_invite_code")
    
    if st.button("Registrieren", key="register_button_2"):
        if invite_code == "ABCD1234":
            if add_user(username, password):
                st.success("Registrierung erfolgreich! Bitte melden Sie sich an.")
                st.session_state.show_registration = False
            else:
                st.error("Benutzername bereits vergeben. Bitte wählen Sie einen anderen Benutzernamen.")
        else:
            st.error("Ungültiger Einladungscode")

# Initialisierung der Datenbank
init_db()

# Streamlit App
st.title("M Messenger")

# Initialisieren der Session State Variablen
if 'username' not in st.session_state:
    st.session_state.username = None
if 'show_registration' not in st.session_state:
    st.session_state.show_registration = False

# Registrierung anzeigen
if st.session_state.show_registration:
    show_registration_form()
else:
    if st.session_state.username is None:
        username = st.text_input("Benutzername", key="login_username")
        password = st.text_input("Passwort", type="password", key="login_password")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Anmelden", key="login_button"):
                if verify_user(username, password):
                    st.session_state.username = username
                    st.experimental_rerun()
                else:
                    st.error("Ungültige Anmeldedaten")
        with col2:
            if st.button("Registrieren", key="register_button"):
                st.session_state.show_registration = True
                st.experimental_rerun()
    else:
        st.write(f"Angemeldet als: {st.session_state.username}")
        if st.button("Abmelden", key="logout_button"):
            st.session_state.username = None
            st.experimental_rerun()

        # Chat-Bereich
        st.subheader("Chat")
        
        messages = get_messages()
        for sender, message, timestamp in messages:
            with st.chat_message(sender):
                st.write(f"{sender}: {message}")
                st.caption(f"Gesendet am {timestamp}")

        # Nachrichteneingabe
        prompt = st.chat_input("Nachricht eingeben", key="chat_input")
        if prompt:
            save_message(st.session_state.username, prompt)
            st.experimental_rerun()

# Datenschutzhinweis
st.sidebar.title("Datenschutz")
st.sidebar.info(
    "Diese App speichert Benutzerdaten und Chatnachrichten. "
    "Bitte beachten Sie, dass dies nur ein Beispiel ist und in einer "
    "Produktionsumgebung weitere Sicherheitsmaßnahmen implementiert werden sollten."
)

#%%