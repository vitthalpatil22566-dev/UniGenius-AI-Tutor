import streamlit as st
from google import genai
from datetime import date

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="UniGenius - AI Student Assistant",
    page_icon="🎓UniGenius - AI Student Assistant",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #1f4037, #99f2c8);
}
.main-title {
    text-align: center;
    font-size: 38px;
    font-weight: bold;
    color: black;
}
.quote {
    text-align: center;
    font-size: 22px;
    font-weight: bold;
    color: #5b8bd1;
}
.exam-box {
    background: white;
    padding: 12px;
    border-radius: 12px;
    margin-top: 10px;
    text-align: center;
}
.chat-user {
    background: #d4edda;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 8px;
}
.chat-bot {
    background: #fff3cd;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 12px;
}
.stButton button {
    background: linear-gradient(90deg, #ff512f, #dd2476);
    color: white;
    border-radius: 10px;
    height: 3em;
    font-weight: bold;
}

/* --- TRENDING QUESTIONS SMALL --- */
h1 {
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- GEMINI CLIENT ----------------
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# ---------------- SESSION STATE ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "problem_counter" not in st.session_state:
    st.session_state.problem_counter = {}

if "weak_topics" not in st.session_state:
    st.session_state.weak_topics = {}

# ---------------- SIDEBAR ----------------
st.sidebar.image("OIP.jpg", width=100)
st.sidebar.markdown("## 👩‍🎓 Student Profile")
st.sidebar.success("Status: Active Learner 🚀")
st.sidebar.info("Consistency Beats Intensity 💪")

st.sidebar.markdown("## 🎯 Learning Controls")

subject = st.sidebar.selectbox(
    "📚 Subject",
    ["General", "DSA", "Artificial Intelligence", "DBMS", "Operating Systems"]
)

difficulty = st.sidebar.selectbox(
    "⚡ Difficulty",
    ["Easy", "Medium", "Hard"]
)

mode = st.sidebar.radio(
    "🧠 Mode",
    [
        "University Exam Mode",
        "Placement / DSA Mode",
        "Quiz Mode",
        "University Diagram Mode"
    ]
)

language = st.sidebar.selectbox(
    "🌍 Language",
    ["English", "Hindi", "Marathi"]
)

exam_date = st.sidebar.date_input("📅 Exam Date", min_value=date.today())

# ---------------- TITLE ----------------
st.markdown("<div class='main-title'>🎓 UniGenius - AI Student Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='quote'>Consistency Beats Intensity</div>", unsafe_allow_html=True)

# ---------------- DAYS REMAINING (UPPER SIDE) ----------------
if exam_date:
    today = date.today()
    days_left = (exam_date - today).days

    if days_left <= 7:
        study_tip = "🔥 High Focus Mode: Daily revision + Mock tests required."
    elif days_left <= 20:
        study_tip = "⚡ Strengthen weak areas and solve PYQs."
    else:
        study_tip = "📘 Concept Building Phase. Practice consistently."

    st.markdown(f"""
    <div class="exam-box">
    📅 <b>Days Left:</b> {days_left} <br>
    🤖 <b>AI Suggestion:</b> {study_tip}
    </div>
    """, unsafe_allow_html=True)

# ---------------- TRENDING SECTION ----------------
st.markdown("# 🔥 Trending Questions")

if st.session_state.problem_counter:
    sorted_trending = sorted(
        st.session_state.problem_counter.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    for q, count in sorted_trending:
        st.write(f"⭐ {q} ({count} times)")
else:
    st.write("No trending questions yet.")

# ---------------- ASK QUESTION (BIG LABEL + BIG BOX) ----------------
st.markdown('<p style="font-size:24px; font-weight:bold; color:black;">💬 Ask your academic question</p>', unsafe_allow_html=True)

question = st.text_area(
    "",          # no label
    height=80,   # taller input box
    max_chars=1000
)

ask_button = st.button("🚀 Generate Response")

# ---------------- RESPONSE LOGIC ----------------
if ask_button and question:

    # Update trending counter
    if question in st.session_state.problem_counter:
        st.session_state.problem_counter[question] += 1
    else:
        st.session_state.problem_counter[question] = 1

    if mode == "University Exam Mode":
        prompt = f"""
        Answer like a university exam paper.
        Structure:
        1. Definition
        2. Explanation
        3. Example
        4. Diagram description (if applicable)
        5. Conclusion
        Keep it concise and scoring.
        Subject: {subject}
        Difficulty: {difficulty}
        Question: {question}
        Answer in {language}.
        """

    elif mode == "Placement / DSA Mode":
        prompt = f"""
        Explain clearly.
        Then provide Java code.
        Then give step-by-step dry run.
        Then give time and space complexity.
        Mention edge cases.
        Difficulty: {difficulty}
        Question: {question}
        Answer in {language}.
        """

    elif mode == "University Diagram Mode":
        prompt = f"""
        Generate a neat, university-style ASCII diagram.
        Use clean boxes and arrows only.
        After diagram, explain each block.
        Topic: {question}
        Answer in {language}.
        """

    else:
        prompt = f"""
        Create 5 MCQs with answers
        on {question} in {difficulty} level.
        Answer in {language}.
        """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    # Weak topic tracker (basic logic)
    if difficulty == "Hard":
        if subject in st.session_state.weak_topics:
            st.session_state.weak_topics[subject] += 1
        else:
            st.session_state.weak_topics[subject] = 1

    st.session_state.history.append(("You", question))
    st.session_state.history.append(("Tutor", response.text))

# ---------------- DISPLAY CHAT ----------------
for role, text in st.session_state.history:
    if role == "You":
        st.markdown(f"<div class='chat-user'><b>🧑 You:</b> {text}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-bot'><b>🤖 UniGenius:</b> {text}</div>", unsafe_allow_html=True)

# ---------------- WEAK TOPIC DISPLAY ----------------
if st.session_state.weak_topics:
    st.sidebar.markdown("## 📉 Weak Topic Tracker")
    for topic, count in st.session_state.weak_topics.items():
        st.sidebar.write(f"{topic} : Needs Revision ({count})")