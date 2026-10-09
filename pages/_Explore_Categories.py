import streamlit as st
from ui import inject_css, init_state, render_sidebar, hero, disclaimer, category_card_html
from knowledge import CATEGORIES

st.set_page_config(page_title="Explore Categories", page_icon="🗂️", layout="wide")
inject_css()
init_state()
render_sidebar()
hero()
disclaimer()

st.subheader("🗂️ Complaint categories")
st.caption("Pick a category to see which department handles it and what details are usually needed.")

cols = st.columns(2)
for i, cat in enumerate(CATEGORIES):
    with cols[i % 2]:
        st.markdown(category_card_html(cat), unsafe_allow_html=True)
        with st.expander("Details: department, info needed, timeline"):
            st.markdown(f"**Department:** {cat['department']}")
            st.markdown("**Information usually needed:**")
            for item in cat["info_needed"]:
                st.markdown(f"- {item}")
            st.markdown(f"**Indicative timeline:** {cat['indicative_timeline']}")
        if st.button(f"Ask about {cat['name']}", key=f"ask_{cat['id']}"):
            st.session_state["queued_question"] = f"How are {cat['name'].lower()} complaints handled?"
            st.switch_page("app.py")
