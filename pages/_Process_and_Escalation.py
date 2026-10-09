
import streamlit as st
from ui import inject_css, init_state, render_sidebar, hero, disclaimer, timeline_html, ladder_html
from knowledge import FILING_CHECKLIST

st.set_page_config(page_title="Process & Escalation", page_icon="🪜", layout="wide")
inject_css()
init_state()
render_sidebar()
hero()
disclaimer()

left, right = st.columns(2)
with left:
    st.subheader("📋 Resolution flow (7 stages)")
    st.markdown(timeline_html(), unsafe_allow_html=True)
    if st.button("Explain the resolution flow to me"):
        st.session_state["queued_question"] = "What is the usual resolution flow?"
        st.switch_page("app.py")

with right:
    st.subheader("🪜 Escalation ladder")
    st.caption("Move up a level only if the expected timeline has passed without action.")
    st.markdown(ladder_html(), unsafe_allow_html=True)
    if st.button("Explain escalation to me"):
        st.session_state["queued_question"] = "Explain the grievance escalation process"
        st.switch_page("app.py")

st.markdown("---")
st.subheader("✅ What to prepare before filing")
for i, item in enumerate(FILING_CHECKLIST):
    st.checkbox(item, key=f"check_{i}")
