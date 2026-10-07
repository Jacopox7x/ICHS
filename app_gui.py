import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(page_title="🕷️ iCrawler", page_icon="🕷️")
st.title("🕷️ iCrawler")
st.markdown("Genera piani social per eventi con IA")

brief = st.text_area("Inserisci il brief:", height=200)

if st.button("Genera"):
    from icrawler_simple import ICrawler
    import os
    os.environ["ICRAWLER_MODEL"] = "qwen3.5:4b"
    crawler = ICrawler()
    result = crawler.generate_strategy(brief, {})
    st.markdown("---")
    st.markdown(result)
