import streamlit as st
import math
import requests
from PyPDF2 import PdfReader

# ------------------ PAGE SETUP ------------------
st.set_page_config(page_title="Smart Study Planner AI", layout="centered")
st.title("📚 Smart Study Planner + AI Tutor")

# ------------------ SIDEBAR ------------------
st.sidebar.header("📌 Your Study Info")

course = st.sidebar.text_input("Course")
subjects = st.sidebar.text_input("Subjects (comma separated)")
days = st.sidebar.number_input("Days available", min_value=1)
hours = st.sidebar.number_input("Hours per day", min_value=1)

# ------------------ STUDY PLAN FUNCTION ------------------
def generate_plan(subjects, days, hours):
    plan = {}
    subject_list = [s.strip() for s in subjects.split(",") if s.strip()]

    if len(subject_list) == 0:
        return {}

    total_hours = days * hours
    hours_per_subject = total_hours // len(subject_list)

    day = 1

    for subject in subject_list:
        study_days = math.ceil(hours_per_subject / hours)

        for i in range(study_days):
            if day > days:
                break

            if day not in plan:
                plan[day] = []

            plan[day].append(f"{subject} - Topic {i+1}")
            day += 1

    # Revision days
    for d in range(day, days + 1):
        plan[d] = ["Revision + Practice"]

    return plan

# ------------------ CREATE PLAN ------------------
if st.sidebar.button("🚀 Create Smart Plan"):
    plan = generate_plan(subjects, days, hours)

    if plan:
        st.subheader("📅 Your Smart Study Plan")

        for day, tasks in plan.items():
            st.write(f"### Day {day}")
            for task in tasks:
                st.write(f"• {task}")
    else:
        st.warning("⚠️ Please enter valid subjects")

# ------------------ OPTIONAL PDF LOAD ------------------
def load_pdf():
    try:
        uploaded_file = st.file_uploader("📄 Upload PDF (optional)", type="pdf")

        if uploaded_file:
            reader = PdfReader(uploaded_file)
            text = ""

            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

            return text[:2000]

        return ""

    except:
        return ""

PDF_TEXT = load_pdf()

# ------------------ AI TUTOR ------------------
def chat_with_ai(user_input, chat_history):
    try:
        query = "Explain like a teacher with simple examples: " + user_input
        url = "https://api.duckduckgo.com/?q=" + query + "&format=json"

        response = requests.get(url)
        data = response.json()

        if data.get("AbstractText"):
            return data["AbstractText"]

        elif data.get("RelatedTopics"):
            return data["RelatedTopics"][0].get("Text", "No clear answer found.")

        elif PDF_TEXT:
            return "From your uploaded notes:\n\n" + PDF_TEXT[:500]

        else:
            return "Try asking a more specific question."

    except:
        return "Error fetching AI response"

# ------------------ CHAT UI ------------------
st.subheader("💬 AI Study Tutor")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        st.markdown(f"**🧑 You:** {msg['content']}")
    else:
        st.markdown(f"**🤖 Tutor:** {msg['content']}")

# Input
user_input = st.text_input("Ask your doubt or topic")

if st.button("Send"):
    if user_input:
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        reply = chat_with_ai(user_input, st.session_state.chat_history)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply}
        )

        st.rerun()
