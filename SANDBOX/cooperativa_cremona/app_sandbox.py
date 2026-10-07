"""
UI Streamlit per la sandbox CreAzioni Migranti.
Con supporto immagini e visual.
"""
import streamlit as st
import json
from pathlib import Path
from runner import run
from content_generator import generate_all, load_sandbox

st.set_page_config(
    page_title="CreAzioni Migranti",
    page_icon="🧵",
    layout="wide"
)

# CSS personalizzato per card visive
st.markdown("""
<style>
    .story-card {
        background: linear-gradient(135deg, #f5f0e8 0%, #f7cec9 100%);
        border-radius: 16px;
        padding: 30px 20px;
        text-align: center;
        min-height: 300px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 20px rgba(186, 106, 87, 0.15);
        border: 2px solid #ba6a57;
    }
    .story-card h3 {
        color: #ba6a57;
        font-size: 1.2rem;
        margin-bottom: 15px;
    }
    .story-card p {
        color: #333;
        font-size: 1rem;
        line-height: 1.5;
        white-space: pre-line;
    }
    .ig-post {
        background: #ffffff;
        border: 1px solid #dbdbdb;
        border-radius: 12px;
        padding: 20px;
        max-width: 500px;
    }
    .fb-post {
        background: #ffffff;
        border: 1px solid #dddfe2;
        border-radius: 12px;
        padding: 20px;
    }
    .brand-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #f7cec9 0%, #f5f0e8 100%);
        border-radius: 16px;
        margin-bottom: 20px;
    }
    .brand-header h1 {
        color: #ba6a57;
        margin: 0;
    }
    .brand-header p {
        color: #70a58f;
        margin: 5px 0 0 0;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Header con brand
st.markdown("""
<div class="brand-header">
    <h1>🧵 CreAzioni Migranti</h1>
    <p>Intrecciamo fili, culture e storie</p>
</div>
""", unsafe_allow_html=True)

st.caption("Genera piani social e contenuti per la sartoria sociale")

with st.sidebar:
    st.header("🧵 CreAzioni Migranti")
    st.markdown("**Sartoria sociale a Cremona**")
    st.divider()
    st.markdown("**Contatti**")
    st.markdown("📍 Via Bonomelli 11, Cremona")
    st.markdown("📩 +39 388 822 6958")
    st.markdown("✉️ creazioni.migranti@cosper.coop")
    st.markdown("📷 @creazionimigranti")
    st.divider()
    st.caption("Powered by iCrawler")

brief = st.text_area(
    "📝 Inserisci il brief dell'evento",
    height=150,
    placeholder="Es: Laboratorio di cucito per bambini, sabato 15 novembre, Cremona..."
)

if st.button("🚀 Genera", type="primary", use_container_width=True):
    if not brief.strip():
        st.warning("Inserisci un brief")
    else:
        with st.spinner("🧵 Generazione in corso..."):
            result = run(brief)
            context, _ = load_sandbox()
            contents = generate_all(
                result["facts"],
                result["piano_social"],
                context
            )

        st.success(f"✅ Piano generato! Tipo evento: **{contents['event_type']}**")

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📸 Instagram", "📘 Facebook", "📱 Storie", "🖼️ Immagini", "📊 Positioning"
        ])

        with tab1:
            st.markdown("### 📸 Post Instagram")
            st.markdown(f'<div class="ig-post">{contents["instagram_post"]}</div>', unsafe_allow_html=True)
            st.divider()
            st.download_button(
                "📥 Scarica post IG",
                contents["instagram_post"],
                file_name="post_instagram.txt",
                use_container_width=True
            )

        with tab2:
            st.markdown("### 📘 Post Facebook")
            st.markdown(f'<div class="fb-post">{contents["facebook_post"]}</div>', unsafe_allow_html=True)
            st.divider()
            st.download_button(
                "📥 Scarica post FB",
                contents["facebook_post"],
                file_name="post_facebook.txt",
                use_container_width=True
            )

        with tab3:
            st.markdown("### 📱 Storie Instagram")
            st.caption("3 slide pronte per le storie")

            # Card visive per le slide
            cols = st.columns(3)
            for i, slide in enumerate(contents["instagram_story"], 1):
                with cols[i-1]:
                    st.markdown(f"""
                    <div class="story-card">
                        <h3>SLIDE {i}</h3>
                        <p>{slide}</p>
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()

            st.markdown("**Testo completo (copia-incolla):**")
            full_stories = "\n\n---\n\n".join(
                [f"SLIDE {i}\n{slide}" for i, slide in enumerate(contents["instagram_story"], 1)]
            )
            st.code(full_stories, language="text")

            st.download_button(
                "📥 Scarica storie",
                full_stories,
                file_name="storie_instagram.txt",
                use_container_width=True
            )

        with tab4:
            st.markdown("### 🖼️ Immagini dai Web Insights")
            insights = result.get("web_insights", {})
            images = insights.get("images", [])

            if images:
                st.caption(f"Trovate {len(images)} immagini da Tavily")
                cols = st.columns(min(len(images), 3))
                for i, img_url in enumerate(images[:6]):
                    with cols[i % 3]:
                        try:
                            st.image(img_url, use_container_width=True)
                        except Exception as e:
                            st.caption(f"⚠️ Immagine non disponibile")

                st.divider()
                st.markdown("**URL immagini:**")
                for img in images[:6]:
                    st.code(img, language="text")
            else:
                st.info("ℹ️ Nessuna immagine trovata. Prova con un brief più specifico.")

        with tab5:
            st.markdown("### 📊 Positioning")
            st.text(result["positioning"])
            st.divider()
            st.download_button(
                "📥 Scarica positioning",
                result["positioning"],
                file_name="positioning.txt",
                use_container_width=True
            )
