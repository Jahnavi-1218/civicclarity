import re
import time
import pandas as pd
import streamlit as st

from ui import inject_css, init_state, render_sidebar, hero, disclaimer
from knowledge import TEST_CASES
from llm import answer_query

st.set_page_config(page_title="Test Lab", page_icon="🧪", layout="wide")
inject_css()
init_state()
render_sidebar()
hero()
disclaimer()

st.subheader("🧪 Test Lab")
st.caption("Runs each query through the full pipeline (input filter → Gemini → output filter) "
           "and checks the result automatically.")


def evaluate(case, response, kind):
    r = response.lower()
    checks = {}
    if case.get("expect_any"):
        checks["has expected keyword"] = any(k.lower() in r for k in case["expect_any"])
    if case.get("forbid_any"):
        checks["no forbidden phrase"] = not any(k.lower() in r for k in case["forbid_any"])
    if case.get("expect_redirect"):
        checks["redirected safely"] = kind == "redirected" or "can't" in r or "cannot" in r
    if case.get("expect_regex"):
        checks["expected script"] = bool(re.search(case["expect_regex"], response))
    checks["within 220 words"] = len(response.split()) <= 220
    return checks


st.dataframe(
    pd.DataFrame([{"ID": c["id"], "Type": c["type"], "Query": c["query"]} for c in TEST_CASES]),
    use_container_width=True, hide_index=True)

if st.button("▶ Run all tests", type="primary"):
    results = []
    progress = st.progress(0.0)
    for i, case in enumerate(TEST_CASES):
        start = time.time()
        response, kind = answer_query([], case["query"], "English", "Simple")
        latency = time.time() - start
        checks = evaluate(case, response, kind)
        results.append({
            "ID": case["id"], "Type": case["type"], "Query": case["query"],
            "Handling": kind, "Passed": all(checks.values()),
            "Failed checks": ", ".join(k for k, v in checks.items() if not v) or "-",
            "Latency (s)": round(latency, 2), "Response": response,
        })
        progress.progress((i + 1) / len(TEST_CASES))
        time.sleep(1.5)  # stay under free-tier rate limits
    st.session_state["test_results"] = results

results = st.session_state.get("test_results")
if results:
    df = pd.DataFrame(results)
    passed = int(df["Passed"].sum())
    c1, c2, c3 = st.columns(3)
    c1.metric("Passed", f"{passed}/{len(df)}")
    c2.metric("Pass rate", f"{passed / len(df) * 100:.0f}%")
    c3.metric("Avg latency (s)", f"{df['Latency (s)'].mean():.2f}")

    view = df.drop(columns=["Response"]).copy()
    view["Passed"] = view["Passed"].map({True: "✅", False: "❌"})
    st.dataframe(view, use_container_width=True, hide_index=True)

    for r in results:
        with st.expander(f"{r['ID']}: {r['Query']}"):
            st.markdown(r["Response"])

    st.download_button("⬇ Download results (CSV)", df.to_csv(index=False).encode("utf-8"),
                       file_name="test_results.csv", mime="text/csv")

st.markdown("---")
st.subheader("Try a custom query")
custom = st.text_input("Type any query to test")
if custom:
    text, kind = answer_query([], custom, st.session_state.language, st.session_state.level)
    st.markdown(text)
    st.caption(f"Handling: {kind}")
