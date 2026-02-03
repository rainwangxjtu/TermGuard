import streamlit as st
import pandas as pd
from io import StringIO
from termguard.pipeline import run_pipeline, load_glossary_csv


st.set_page_config(page_title="TermGuard Demo", layout="wide")
st.title("TermGuard — Terminology Consistency Checker (EN→ZH)")

st.markdown(
    "Upload **English source** + **Chinese translation**, optionally a **glossary CSV** (columns: `en_term, zh_term`)."
)

col1, col2, col3 = st.columns(3)
with col1:
    en_file = st.file_uploader("English text (.txt)", type=["txt"])
with col2:
    zh_file = st.file_uploader("Chinese text (.txt)", type=["txt"])
with col3:
    gl_file = st.file_uploader("Glossary (.csv, optional)", type=["csv"])

out_dir = st.text_input("Output directory", value="outputs/streamlit_run")

run_btn = st.button("Run TermGuard")

if run_btn:
    if not en_file or not zh_file:
        st.error("Please upload both English and Chinese text files.")
        st.stop()

    en_text = en_file.read().decode("utf-8", errors="ignore")
    zh_text = zh_file.read().decode("utf-8", errors="ignore")

    glossary = {}
    if gl_file:
        # read as dataframe then convert
        gl_df = pd.read_csv(gl_file)
        if "en_term" in gl_df.columns and "zh_term" in gl_df.columns:
            glossary = {str(r["en_term"]).strip(): str(r["zh_term"]).strip() for _, r in gl_df.iterrows()}
        else:
            st.warning("Glossary CSV must have columns: en_term, zh_term. Ignoring glossary.")

    with st.spinner("Running pipeline..."):
        result = run_pipeline(
            en_text=en_text,
            zh_text=zh_text,
            glossary=glossary,
            out_dir=out_dir
        )

    st.success("Done!")

    st.subheader("Flagged inconsistencies")
    report_df = pd.read_csv(result["report_csv"])
    st.dataframe(report_df, use_container_width=True)

    st.subheader("Stage runtimes (seconds)")
    st.json(result["stage_times"])

    # Downloads
    st.subheader("Downloads")
    report_csv_bytes = open(result["report_csv"], "rb").read()
    report_json_bytes = open(result["report_json"], "rb").read()
    patched_bytes = open(result["patched_path"], "rb").read()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("Download report.csv", report_csv_bytes, file_name="report.csv")
    with c2:
        st.download_button("Download report.json", report_json_bytes, file_name="report.json")
    with c3:
        st.download_button("Download zh_patched.txt", patched_bytes, file_name="zh_patched.txt")
