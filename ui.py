import streamlit as st
from knowledge import PROCESS_STAGES, ESCALATION_LEVELS

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: none; }
}

.hero {
  background: linear-gradient(135deg, #0B3C5D, #14B8A6);
  color: white; padding: 28px 32px; border-radius: 20px;
  margin-bottom: 14px; animation: fadeUp .6s ease both;
}
.hero h1 { color: white; margin: 0; font-size: 2.2rem; padding: 0; }
.hero p  { margin: 6px 0 0; opacity: .95; font-size: 1.05rem; }

.disclaimer {
  background: #FEF3C7; border-left: 5px solid #F59E0B; color: #78350F;
  padding: 10px 16px; border-radius: 10px; margin-bottom: 16px; font-size: .92rem;
}

.cat-card {
  background: white; border-radius: 16px; padding: 18px 20px; margin-bottom: 8px;
  box-shadow: 0 4px 16px rgba(11,60,93,0.08); transition: all .2s ease;
  animation: fadeUp .5s ease both;
}
.cat-card:hover { transform: translateY(-4px); box-shadow: 0 10px 24px rgba(11,60,93,0.15); }
.cat-card h3 { margin: 4px 0 0 0; color: #0B3C5D; }
.cat-emoji { font-size: 2rem; }
.cat-dept { color: #5B6B7C; font-size: .85rem; margin: 2px 0 8px 0; }

.badge {
  display: inline-block; padding: 3px 12px; border-radius: 999px;
  font-size: .75rem; font-weight: 600; margin-top: 6px;
}
.badge-explained  { background: #DCFCE7; color: #166534; }
.badge-redirected { background: #FEF3C7; color: #92400E; }
.badge-filtered   { background: #DBEAFE; color: #1E40AF; }

.timeline { margin-left: 4px; }
.tl-item { display: flex; gap: 14px; margin-bottom: 14px; animation: fadeUp .5s ease both; }
.tl-num {
  min-width: 38px; height: 38px; border-radius: 50%; background: #0F766E; color: white;
  display: flex; align-items: center; justify-content: center; font-weight: 700;
}
.tl-body {
  background: white; padding: 10px 16px; border-radius: 12px; flex: 1;
  box-shadow: 0 2px 10px rgba(11,60,93,0.08);
}
.tl-body span { color: #5B6B7C; font-size: .92rem; }

.lad-step {
  padding: 12px 16px; border-radius: 12px; margin-bottom: 10px; color: white;
  animation: fadeUp .5s ease both;
}
.lad-step small { opacity: .92; }

.layer {
  background: white; border-radius: 14px; padding: 14px 18px; margin-bottom: 10px;
  border-left: 6px solid #0F766E; box-shadow: 0 2px 10px rgba(11,60,93,0.08);
}

div.stButton > button { border-radius: 999px; border: 1px solid #0F766E; transition: all .15s ease; }
div.stButton > button:hover { transform: translateY(-2px); background: #0F766E; color: white; }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "metrics" not in st.session_state:
        st.session_state.metrics = {"answered": 0, "redirected": 0, "latencies": []}
    if "offline_mode" not in st.session_state:
        st.session_state.offline_mode = False


def render_sidebar():
    with st.sidebar:
        st.markdown("## 🏙️ CivicClarity")
        st.selectbox("Language", ["English", "Hindi", "Telugu"], key="language")
        st.radio("Reading level", ["Simple", "Standard"], key="level", horizontal=True)
        st.markdown("---")

        m = st.session_state.metrics
        avg = sum(m["latencies"]) / len(m["latencies"]) if m["latencies"] else 0
        c1, c2 = st.columns(2)
        c1.metric("Answered", m["answered"])
        c2.metric("Redirected", m["redirected"])
        st.metric("Avg response (s)", f"{avg:.1f}")
        st.caption(f"Estimated helpdesk calls deflected: {m['answered']}")

        if st.session_state.offline_mode:
            st.warning("Offline demo mode (AI service unavailable)")

        if st.session_state.messages:
            transcript = "\n\n".join(
                f"{'You' if x['role'] == 'user' else 'CivicClarity'}: {x['content']}"
                for x in st.session_state.messages)
            st.download_button("Download conversation", transcript, file_name="conversation.txt")
            if st.button("Clear chat"):
                st.session_state.messages = []
                st.rerun()


def hero():
    st.markdown(
        '<div class="hero"><h1>🏙️ CivicClarity</h1>'
        '<p>Understand your city\'s grievance process, clearly. 🛣️ 💧 ⚡ ♻️</p></div>',
        unsafe_allow_html=True)


def disclaimer():
    st.markdown(
        '<div class="disclaimer">ℹ️ <b>Explanation only.</b> This assistant cannot register or track '
        'complaints or promise outcomes. Timelines shown are indicative.</div>',
        unsafe_allow_html=True)


def badge(kind):
    labels = {"explained": "Explained", "redirected": "Redirected (cannot file/track)",
              "filtered": "Safety-filtered"}
    return f'<span class="badge badge-{kind}">{labels.get(kind, kind)}</span>'


def category_card_html(c):
    subs = "".join(f"<li>{x}</li>" for x in c["sub_issues"][:4])
    return (f'<div class="cat-card" style="border-top:6px solid {c["color"]}">'
            f'<div class="cat-emoji">{c["emoji"]}</div><h3>{c["name"]}</h3>'
            f'<div class="cat-dept">{c["department"]}</div><ul>{subs}</ul></div>')


def timeline_html():
    items = ""
    for i, s in enumerate(PROCESS_STAGES):
        items += (f'<div class="tl-item" style="animation-delay:{i * 0.12}s">'
                  f'<div class="tl-num">{s["step"]}</div>'
                  f'<div class="tl-body"><b>{s["title"]}</b><br><span>{s["description"]}</span></div></div>')
    return f'<div class="timeline">{items}</div>'


def ladder_html():
    colors = ["#14B8A6", "#0F9F95", "#0F766E", "#0B5A73", "#0B3C5D"]
    steps = ""
    for i, e in enumerate(ESCALATION_LEVELS):
        steps += (f'<div class="lad-step" style="margin-left:{i * 24}px;background:{colors[i]};'
                  f'animation-delay:{i * 0.12}s"><b>L{e["level"]}: {e["title"]}</b><br>'
                  f'<small>{e["when_to_use"]}</small></div>')
    return f"<div>{steps}</div>"