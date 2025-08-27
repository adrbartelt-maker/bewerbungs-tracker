import streamlit as st
from datetime import datetime
import sqlite3, os

DB_PATH = "bewerbungen.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            unternehmen TEXT,
            ansprechpartner TEXT,
            bewerbungsdatum TEXT,
            bemerkungen TEXT,
            reminder_enabled INTEGER DEFAULT 0,
            reminder_date TEXT,
            created_at TEXT
        )
    """)
    con.commit()
    con.close()

def insert_application(unternehmen, ansprechpartner, datum, bemerkungen, reminder_enabled, reminder_date):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        INSERT INTO applications
        (unternehmen, ansprechpartner, bewerbungsdatum, bemerkungen, reminder_enabled, reminder_date, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (unternehmen, ansprechpartner, datum, bemerkungen, int(reminder_enabled), reminder_date, datetime.now().isoformat()))
    con.commit()
    con.close()

def fetch_rows():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM applications ORDER BY id DESC").fetchall()
    con.close()
    return rows

# ---------------- UI ----------------
st.set_page_config(page_title="📄 Bewerbungs-Tracker", page_icon="📱", layout="wide")
st.title("📄 Bewerbungs-Tracker (Mobile)")

init_db()

with st.form("add_entry"):
    st.subheader("➕ Neue Bewerbung")
    unternehmen = st.text_input("Unternehmen")
    ansprechpartner = st.text_input("Ansprechpartner")
    bewerbungsdatum = st.date_input("Bewerbungsdatum")
    bemerkungen = st.text_area("Bemerkungen")
    reminder_enabled = st.checkbox("Erinnerung aktivieren")
    reminder_date = st.date_input("Erinnerungsdatum") if reminder_enabled else None
    submitted = st.form_submit_button("Speichern")
    if submitted:
        insert_application(
            unternehmen, ansprechpartner, bewerbungsdatum.isoformat(), bemerkungen,
            reminder_enabled, reminder_date.isoformat() if reminder_date else None
        )
        st.success("✅ Bewerbung gespeichert")

st.subheader("📚 Bewerbungen")
rows = fetch_rows()
if not rows:
    st.info("Noch keine Bewerbungen erfasst.")
else:
    for r in rows:
        st.write(f"**{r['unternehmen']}** — {r['ansprechpartner']} ({r['bewerbungsdatum']})")
        if r['reminder_enabled']:
            st.info(f"🔔 Erinnerung: {r['reminder_date']}")
