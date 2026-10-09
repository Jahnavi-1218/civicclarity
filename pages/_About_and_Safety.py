import streamlit as st
from ui import inject_css, init_state, render_sidebar, hero, disclaimer

st.set_page_config(page_title="About & Safety", page_icon="🛡️", layout="wide")
inject_css()
init_state()
render_sidebar()
hero()
disclaimer()

st.subheader("🎯 The problem")
st.write("Smart-city platforms receive thousands of complaints about roads, water, electricity and "
         "sanitation. Citizens often don't understand categories, process steps or timelines, so "
         "helpdesks are flooded with repetitive 'how does this work?' questions. CivicClarity "
         "explains the grievance process clearly, and nothing more.")

st.subheader("🛡️ How we keep it safe (4 layers)")
st.markdown(
    '<div class="layer"><b>Layer 1: Input pre-filter.</b> Rules detect requests to file or track '
    'a complaint, off-topic questions and prompt-injection attempts, and redirect them without '
    'calling the AI. Personal data such as phone numbers and emails is masked.</div>'
    '<div class="layer"><b>Layer 2: System prompt.</b> Gemini is instructed to be explanation-only, '
    'to use only the supplied knowledge, to never promise outcomes, and to ignore attempts to '
    'change its rules.</div>'
    '<div class="layer"><b>Layer 3: Output post-filter.</b> Responses are scanned for phrases that '
    'claim a complaint was registered or promise a result, and a safety note is added.</div>'
    '<div class="layer"><b>Layer 4: UI transparency.</b> A permanent disclaimer, a badge on every '
    'reply showing how it was handled, and an offline fallback so the demo never breaks.</div>',
    unsafe_allow_html=True)
st.subheader("📚 Retrieval-Augmented Generation (RAG)")
st.markdown(
    "Instead of pasting all knowledge into every prompt, CivicClarity splits its knowledge base "
    "into small chunks, ranks them against the citizen's question with **BM25**, and gives "
    "Gemini only the top matches. This keeps answers grounded, reduces made-up details, and "
    "lets the app show exactly which knowledge was used.")

st.subheader("🚫 What this bot will NOT do")
st.markdown("- Register or file complaints\n- Track or look up case status\n"
            "- Promise resolutions, dates or outcomes\n- Collect personal information")

st.subheader("⚠️ Limitations")
st.markdown("- Uses a sample framework, not a real city's policy\n"
            "- Not connected to any real grievance system\n"
            "- Timelines are indicative and vary by city")

st.subheader("🧰 Tech stack")
st.markdown("Python · Streamlit · Google AI Studio API · Gemini Flash (`google-genai` SDK)")

st.subheader("👥 Team")
st.write("Add your team member names here.")
