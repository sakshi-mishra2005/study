import streamlit as st
import math
import subprocess
from PyPDF2 import PdfReader

# Page setup
st.set_page_config(page_title="Smart Study Planner AI", layout="centered")
st.title("📚 Smart Study Planner + AI Tutor")

# Sidebar input
st.sidebar.header("📌 Your Study Info")

course = st.sidebar.text_input("Course")
subjects = st.sidebar.text_input("Subjects (comma separated)")
days = st.sidebar.number_input("Days available", min_value=1)
hours = st.sidebar.number_input("Hours per day", min_value=1)

# Generate Study Plan
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

# Button to create plan
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

# Load PDF data
def load_pdf():
    try:
        path = r"C:\Users\admin\Desktop\op.pdf"
        reader = PdfReader(path)

        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        return text[:5000]  # limit size

    except Exception as e:
        return f"Error loading PDF: {str(e)}"

# Load once
PDF_TEXT = load_pdf()

# System prompt
SYSTEM_PROMPT = """
You are an expert VLSI tutor trained using Optical Reference material.

Rules:
1. Answer primarily from provided PDF notes
2. Ask prerequisite questions
3. Explain concept simply
4. Give examples
5. Give practice questions
6. Evaluate answers step-by-step

Avoid generic answers.
"""

# AI chat function
def chat_with_ai(user_input, chat_history):
    conversation = SYSTEM_PROMPT + "\n\nReference Notes:\n" + PDF_TEXT + "\n\n"

    for msg in chat_history:
        role = "Student" if msg["role"] == "user" else "Tutor"
        conversation += f"{role}: {msg['content']}\n"

    conversation += f"Student: {user_input}\nTutor:"

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=conversation,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        reply = result.stdout.strip()

        if not reply:
            return "⚠️ No response. Make sure Ollama is running."

        return reply

    except Exception as e:
        return f"Error: {str(e)}"

# Chat UI
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