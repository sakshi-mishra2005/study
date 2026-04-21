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
    import requests
    text = user_input.lower()

    # -------- Try API first --------
    try:
        query = "Explain in simple terms with examples: " + user_input
        url = "https://api.duckduckgo.com/?q=" + query + "&format=json"

        response = requests.get(url)
        data = response.json()

        if data.get("AbstractText"):
            return data["AbstractText"]

        elif data.get("RelatedTopics"):
            for topic in data["RelatedTopics"]:
                if isinstance(topic, dict) and topic.get("Text"):
                    return topic["Text"]

    except:
        pass

    # -------- SMART TEACHING FALLBACK --------

    if "cmos" in text:
        return """📘 CMOS (Complementary Metal-Oxide Semiconductor)

👉 CMOS is used to build digital circuits like NOT gate (inverter).

👉 It uses:
- PMOS transistor
- NMOS transistor

👉 Working:
- Input = 0 → PMOS ON, NMOS OFF → Output = 1
- Input = 1 → PMOS OFF, NMOS ON → Output = 0

👉 Why CMOS is important:
- Very low power consumption
- High efficiency
- Used in processors, ICs, memory chips

👉 Example:
CMOS inverter gives output opposite of input."""

    elif "pn junction" in text:
        return """📘 PN Junction

👉 Formed by joining P-type and N-type semiconductor.

👉 Depletion region forms at junction (no free charges).

👉 Forward bias → current flows  
👉 Reverse bias → blocks current  

👉 Used in diodes and rectifiers."""

    elif "fermi level" in text:
        return """📘 Fermi Level

👉 Energy level where probability of electron is 50%.

👉 In N-type → shifts upward  
👉 In P-type → shifts downward  

👉 Important for understanding conductivity."""

    elif "resistivity" in text:
        return """📘 Resistivity in Semiconductor

👉 Opposite of conductivity.

👉 With increase in temperature:
- Charge carriers increase
- Resistivity decreases

👉 This is opposite of metals."""

    elif "depletion" in text:
        return """📘 Depletion Region

👉 Region near PN junction with no free charge carriers.

👉 Contains only immobile ions.

👉 Acts like a barrier for current."""

    else:
        return "Try asking like: 'Explain CMOS working', 'PN junction in detail', 'Fermi level in p-type'."
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
