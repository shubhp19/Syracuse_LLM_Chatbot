"""
Syracuse University AI Chatbot — Full Featured Streamlit UI
Students: courses, professors, financial aid, deadlines
Professors: policies, catalog, departments, announcements
"""
import streamlit as st
from chatbot import SUChatbot
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="SU AI Assistant",
    page_icon="🍊",
    layout="wide"
)

# ── Styles ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.su-logo {
    text-align: center;
    padding: 1.2rem 0 0.3rem;
}
.su-logo h1 {
    font-family: 'Source Serif 4', serif;
    font-size: 1.9rem;
    color: #1a1a1a;
    margin: 0;
}
.su-logo .tagline { color: #888; font-size: 0.82rem; }

.role-pill-student  { background:#003087; color:white; padding:3px 12px; border-radius:20px; font-size:0.78rem; }
.role-pill-professor{ background:#D44500; color:white; padding:3px 12px; border-radius:20px; font-size:0.78rem; }

.ann-card {
    background: #fffbf7;
    border-left: 4px solid #D44500;
    padding: 0.75rem 1rem;
    border-radius: 0 8px 8px 0;
    margin-bottom: 0.6rem;
}
.ann-card .ann-course { font-size:0.72rem; color:#D44500; font-weight:600; text-transform:uppercase; }
.ann-card .ann-title  { font-size:0.95rem; font-weight:600; color:#1a1a1a; margin:2px 0; }
.ann-card .ann-body   { font-size:0.85rem; color:#444; }
.ann-card .ann-meta   { font-size:0.72rem; color:#999; margin-top:4px; }

.source-chip {
    display:inline-block; background:#f0f4ff; color:#003087;
    padding:3px 10px; border-radius:20px; font-size:0.72rem;
    margin:2px; text-decoration:none; border:1px solid #d0daf5;
}

.feature-card {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.5rem;
    border: 1px solid #e9ecef;
}
</style>
""", unsafe_allow_html=True)


# ── Login ──────────────────────────────────────────────────────────────────────
def show_login():
    api_key = os.environ.get("GROQ_API_KEY")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="su-logo">
            <h1>🍊 SU AI Assistant</h1>
            <p class="tagline">Syracuse University · Powered by Groq LLaMA 70B</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("##### 👤 Who are you?")
        col_s, col_p = st.columns(2)
        with col_s:
            student_btn = st.button("🎓 Student", use_container_width=True, type="primary")
        with col_p:
            prof_btn = st.button("👨‍🏫 Professor", use_container_width=True)

        if student_btn and api_key:
            st.session_state.api_key = api_key
            st.session_state.role = "student"
            st.rerun()
        elif prof_btn and api_key:
            st.session_state.api_key = api_key
            st.session_state.role = "professor"
            st.session_state.needs_name = True
            st.rerun()


def show_professor_name():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 👨‍🏫 Welcome, Professor!")
        name = st.text_input("What's your name?", placeholder="Dr. Smith")
        dept = st.text_input("Your department?", placeholder="Computer Science")
        if st.button("Continue →", type="primary"):
            if name:
                st.session_state.prof_name = name
                st.session_state.prof_dept = dept
                st.session_state.pop("needs_name", None)
                st.rerun()
            else:
                st.error("Please enter your name.")


# ── Student Chat ───────────────────────────────────────────────────────────────
def show_student_chat():
    # Init bot
    if "bot" not in st.session_state:
        with st.spinner("Loading SU knowledge base..."):
            st.session_state.bot = SUChatbot(
                api_key=st.session_state.api_key,
                role="student"
            )

    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Hi! 👋 I'm your SU assistant. Ask me about **courses, programs, financial aid, deadlines, professors, or campus life** at Syracuse University!"
        }]

    # Layout
    chat_col, info_col = st.columns([2, 1])

    with chat_col:
        st.markdown("""
        <div class="su-logo" style="text-align:left; padding:0.5rem 0">
            <h1 style="font-size:1.4rem">🍊 SU Student Assistant
            <span class="role-pill-student">Student</span></h1>
        </div>
        """, unsafe_allow_html=True)

        # Chat messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    chips = " ".join(
                        f'<a class="source-chip" href="{s["url"]}" target="_blank">📄 {s["title"][:30]}</a>'
                        for s in msg["sources"] if s.get("url")
                    )
                    st.markdown(f"<div style='margin-top:6px'>{chips}</div>", unsafe_allow_html=True)

        # Input
        user_input = st.session_state.pop("pending", None) or \
                     st.chat_input("Ask about courses, aid, deadlines, professors...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Searching SU knowledge base..."):
                    result = st.session_state.bot.chat(user_input)
                st.markdown(result["answer"])
                sources = result.get("sources", [])
                if sources:
                    chips = " ".join(
                        f'<a class="source-chip" href="{s["url"]}" target="_blank">📄 {s["title"][:30]}</a>'
                        for s in sources if s.get("url")
                    )
                    st.markdown(f"<div style='margin-top:6px'>{chips}</div>", unsafe_allow_html=True)
            st.session_state.messages.append({
                "role": "assistant", "content": result["answer"], "sources": sources
            })

    with info_col:
        # Announcements panel
        active_anns = st.session_state.bot.announcements.get_all()
        if active_anns:
            st.markdown("#### 📢 Professor Announcements")
            for ann in reversed(active_anns[-5:]):
                st.markdown(f"""
                <div class="ann-card">
                    <div class="ann-course">{ann['course']}</div>
                    <div class="ann-title">{ann['title']}</div>
                    <div class="ann-body">{ann['body']}</div>
                    <div class="ann-meta">— {ann['professor']} · {ann['posted_at']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.markdown("#### 💡 Quick Questions")
        questions = [
            "What majors does Syracuse offer?",
            "How do I apply for financial aid?",
            "What is the tuition cost?",
            "How do I register for classes?",
            "What are the scholarship options?",
            "How do I find my advisor?",
            "What are withdrawal deadlines?",
            "How do I contact a professor?",
        ]
        for q in questions:
            if st.button(q, use_container_width=True, key=f"sq_{q[:15]}"):
                st.session_state.pending = q
                st.rerun()

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.messages = [{"role": "assistant", "content": "Chat cleared! How can I help?"}]
                st.session_state.bot.reset()
                st.rerun()
        with col2:
            if st.button("🔄 Switch", use_container_width=True):
                for k in ["role", "bot", "messages", "pending", "prof_name", "prof_dept"]:
                    st.session_state.pop(k, None)
                st.rerun()


# ── Professor Dashboard ────────────────────────────────────────────────────────
def show_professor_chat():
    prof_name = st.session_state.get("prof_name", "Professor")
    prof_dept = st.session_state.get("prof_dept", "")

    if "bot" not in st.session_state:
        with st.spinner("Loading SU knowledge base..."):
            st.session_state.bot = SUChatbot(
                api_key=st.session_state.api_key,
                role="professor"
            )

    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"Hello, {prof_name}! 👋 I can help with **university policies, course catalog, department info, and administrative procedures**. You can also post announcements for your students using the panel on the right."
        }]

    chat_col, tools_col = st.columns([2, 1])

    with chat_col:
        st.markdown(f"""
        <div class="su-logo" style="text-align:left; padding:0.5rem 0">
            <h1 style="font-size:1.4rem">🍊 SU Faculty Assistant
            <span class="role-pill-professor">Professor</span></h1>
            <p class="tagline">{prof_name} · {prof_dept}</p>
        </div>
        """, unsafe_allow_html=True)

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    chips = " ".join(
                        f'<a class="source-chip" href="{s["url"]}" target="_blank">📄 {s["title"][:30]}</a>'
                        for s in msg["sources"] if s.get("url")
                    )
                    st.markdown(f"<div style='margin-top:6px'>{chips}</div>", unsafe_allow_html=True)

        user_input = st.session_state.pop("pending", None) or \
                     st.chat_input("Ask about policies, catalog, departments, procedures...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Searching SU knowledge base..."):
                    result = st.session_state.bot.chat(user_input)
                st.markdown(result["answer"])
                sources = result.get("sources", [])
                if sources:
                    chips = " ".join(
                        f'<a class="source-chip" href="{s["url"]}" target="_blank">📄 {s["title"][:30]}</a>'
                        for s in sources if s.get("url")
                    )
                    st.markdown(f"<div style='margin-top:6px'>{chips}</div>", unsafe_allow_html=True)
            st.session_state.messages.append({
                "role": "assistant", "content": result["answer"], "sources": sources
            })

    with tools_col:
        tab1, tab2, tab3 = st.tabs(["📢 Post", "📋 Manage", "💡 Quick"])

        # ── Tab 1: Post Announcement ──
        with tab1:
            st.markdown("#### Post Announcement")
            course = st.text_input("Course", placeholder="CIS 351 or All Students")
            title  = st.text_input("Title", placeholder="Midterm Date Change")
            body   = st.text_area("Message", placeholder="The midterm has been moved to...", height=100)
            if st.button("📢 Post Announcement", type="primary", use_container_width=True):
                if course and title and body:
                    ann = st.session_state.bot.announcements.post(
                        professor=prof_name, course=course,
                        title=title, body=body
                    )
                    st.success(f"✅ Posted! (ID #{ann['id']})")
                    st.rerun()
                else:
                    st.error("Fill in all fields.")

        # ── Tab 2: Manage Announcements ──
        with tab2:
            st.markdown("#### My Announcements")
            all_anns = st.session_state.bot.announcements.get_all()
            my_anns  = [a for a in all_anns if a.get("professor") == prof_name]

            if not my_anns:
                st.caption("No announcements yet.")
            else:
                for ann in reversed(my_anns):
                    with st.expander(f"[{ann['course']}] {ann['title']}"):
                        st.write(ann["body"])
                        st.caption(f"Posted: {ann['posted_at']}")

                        new_title = st.text_input("Edit title", value=ann["title"], key=f"et_{ann['id']}")
                        new_body  = st.text_area("Edit body",  value=ann["body"],  key=f"eb_{ann['id']}", height=80)

                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("💾 Save", key=f"save_{ann['id']}", use_container_width=True):
                                st.session_state.bot.announcements.edit(
                                    ann["id"], title=new_title, body=new_body)
                                st.success("Updated!")
                                st.rerun()
                        with c2:
                            if st.button("🗑️ Delete", key=f"del_{ann['id']}", use_container_width=True):
                                st.session_state.bot.announcements.delete(ann["id"])
                                st.success("Deleted.")
                                st.rerun()

        # ── Tab 3: Quick Questions ──
        with tab3:
            st.markdown("#### Quick Questions")
            questions = [
                "What is the academic integrity policy?",
                "How do I submit final grades?",
                "What are withdrawal deadlines?",
                "How does incomplete grade policy work?",
                "What courses are in the CS catalog?",
                "How do I request curriculum changes?",
                "Where can I refer struggling students?",
                "What are research funding resources?",
            ]
            for q in questions:
                if st.button(q, use_container_width=True, key=f"pq_{q[:15]}"):
                    st.session_state.pending = q
                    st.rerun()

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = [{"role": "assistant", "content": "Chat cleared!"}]
                st.session_state.bot.reset()
                st.rerun()
        with col2:
            if st.button("🔄 Switch Role", use_container_width=True):
                for k in ["role", "bot", "messages", "pending", "prof_name", "prof_dept"]:
                    st.session_state.pop(k, None)
                st.rerun()


# ── Router ─────────────────────────────────────────────────────────────────────
if "role" not in st.session_state or "api_key" not in st.session_state:
    show_login()
elif st.session_state.get("needs_name"):
    show_professor_name()
elif st.session_state.role == "student":
    show_student_chat()
else:
    show_professor_chat()
