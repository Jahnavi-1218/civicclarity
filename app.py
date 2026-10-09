import time
import streamlit as st

from ui import inject_css, init_state, render_sidebar, hero, disclaimer, badge
from guardrails import classify_intent, mask_pii, redirect_message, postfilter
from llm import stream_answer, STATUS
from knowledge import SUGGESTED_QUESTIONS, followups_for

st.set_page_config(page_title="CivicClarity", page_icon="🏙️", layout="wide")
inject_css()
init_state()
render_sidebar()
hero()
disclaimer()


def queue_question(q):
    st.session_state["queued_question"] = q


# 1. Get the question (typed, or queued from a chip / another page)
typed = st.chat_input("Ask how a complaint is handled…")
question = typed or st.session_state.pop("queued_question", None)

msgs = st.session_state.messages

# 2. Suggestion chips on an empty chat
if not msgs and not question:
    st.markdown("#### Try asking")
    cols = st.columns(2)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        cols[i % 2].button(q, key=f"chip_{i}", on_click=queue_question,
                           args=(q,), use_container_width=True)

# 3. Replay the conversation
for idx, m in enumerate(msgs):
    role = "user" if m["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(m["content"])
        if role == "assistant":
            st.markdown(badge(m["badge"]), unsafe_allow_html=True)
            if idx == len(msgs) - 1 and not question:
                prev_q = msgs[idx - 1]["content"] if idx > 0 else ""
                for j, fq in enumerate(followups_for(prev_q)):
                    st.button(fq, key=f"fu_{idx}_{j}", on_click=queue_question, args=(fq,))

# 4. Handle a new question
if question:
    history = list(msgs)
    clean, found_pii = mask_pii(question)

    with st.chat_message("user"):
        st.markdown(clean)
    if found_pii:
        st.warning("Please don't share personal details here. I've masked them.")
    st.session_state.messages.append({"role": "user", "content": clean})

    intent = classify_intent(clean)
    start = time.time()

    with st.chat_message("assistant"):
        if intent != "OK":
            answer = redirect_message(intent)
            st.markdown(answer)
            kind = "redirected"
            st.session_state.metrics["redirected"] += 1
        else:
            raw = st.write_stream(
                stream_answer(history, clean,
                              st.session_state.language, st.session_state.level))
            answer, flagged = postfilter(raw)
            kind = "filtered" if flagged else "explained"
            st.session_state.metrics["answered"] += 1
            st.session_state.offline_mode = STATUS["offline"]

    st.session_state.metrics["latencies"].append(time.time() - start)
    st.session_state.messages.append({"role": "assistant", "content": answer, "badge": kind})
    st.rerun()