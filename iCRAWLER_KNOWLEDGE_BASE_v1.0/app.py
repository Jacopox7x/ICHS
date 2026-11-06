import streamlit as st
import sys
import os
from datetime import datetime
from fact_extractor.regex_extractor import extract_with_regex
from fact_extractor.post_processor import post_process
from modules.positioning import get_positioning_report
from modules.systemic_rules import apply_systemic_rules
from knowledge.knowledge_retriever import KnowledgeRetriever
from modules.search_agent import get_live_insights

st.set_page_config(
    page_title="iCrawler V2.0 — Agente Social AI",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 iCrawler V2.0")
st.caption("Generazione automatica di piani social da brief evento con ricerca live")

# Sidebar con opzioni
with st.sidebar:
    st.header("⚙️ Opzioni")
    use_web_insights = st.checkbox("🌐 Web Insights live", value=True)
    st.divider()
    st.markdown("**📊 Statistiche**")
    st.metric("Versione", "V2.0")
    st.metric("Stato", "✅ Operativo")
    st.divider()
    st.caption("Powered by Tavily • DuckDuckGo fallback")

# --- INPUT BRIEF ---
brief = st.text_area(
    "📝 Inserisci il brief dell'evento",
    height=200,
    placeholder="Esempio: Convegno sull'Intelligenza Artificiale a Milano il 10 ottobre 2026. Obiettivo: attrarre professionisti del settore..."
)

# --- UPLOADER BRIEF (testo) ---
uploaded_file = st.file_uploader("📎 Carica file .txt o .md", type=["txt", "md"])
if uploaded_file is not None:
    try:
        content = uploaded_file.read().decode("utf-8")
        brief = content
        st.success(f"✅ File '{uploaded_file.name}' caricato ({len(content)} caratteri)")
    except Exception as e:
        st.error(f"❌ Errore nella lettura del file: {e}")

# --- UPLOADER PER MEDIA (immagini, gif, video) ---
st.divider()
st.subheader("🎬 Anteprima file multimediali")

media_file = st.file_uploader(
    "Carica un'immagine, GIF o video",
    type=["png", "jpg", "jpeg", "gif", "mp4", "webm", "mov"],
    key="media_uploader"
)

if media_file is not None:
    file_type = media_file.type
    st.write(f"📁 File: **{media_file.name}** ({media_file.size} bytes)")
    
    if file_type.startswith("image/"):
        st.image(media_file, use_container_width=True)
        st.caption("🖼️ Anteprima immagine")
    elif file_type == "image/gif":
        st.image(media_file, use_container_width=True)
        st.caption("🎞️ Anteprima GIF")
    elif file_type.startswith("video/"):
        st.video(media_file)
        st.caption("🎬 Anteprima video")
    else:
        st.info(f"Formato file: {file_type}")

# --- PULSANTE GENERA ---
st.divider()
generate = st.button("🚀 Genera Piano", type="primary", use_container_width=True)

# --- GENERAZIONE PIANO ---
if generate and brief:
    with st.spinner("🕷️ iCrawler sta lavorando..."):
        # Estrai fatti
        raw_facts = extract_with_regex(brief)
        facts = post_process(raw_facts, brief)
        
        # Web Insights
        if use_web_insights:
            insights = get_live_insights(facts)
        else:
            insights = {}
        
        # Applica regole sistemiche
        rules = apply_systemic_rules(facts)
        
        # Genera piano strutturato
        event = facts.get('event_name', 'Evento')
        date = facts.get('date', 'DA DEFINIRE')
        location = facts.get('location', 'DA DEFINIRE')
        target = facts.get('target', 'DA DEFINIRE')
        objective = facts.get('objective', 'DA DEFINIRE')
        hashtag = facts.get('hashtag', '#Evento #Innovazione')
        
        hashtags_suggeriti = " ".join(rules["hashtags"][:8])
        cta_list = rules["cta"]
        visual = rules["visual"]
        times = rules["posting_times"]
        
        # Creative Lab
        from fact_extractor.creative_lab_fallback import build_creative_lab
        creative_lab = build_creative_lab(facts)
        creative_lab = creative_lab.replace("IDEA", "\n\n💡 IDEA")
        
        # Positioning
        positioning = get_positioning_report(brief, facts)
    
    st.success("✅ Piano generato con successo!")
    
    # Tabs per le sezioni
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Strategia", 
        "📱 Piano Social", 
        "🎨 Creative Lab", 
        "🌐 Web Insights", 
        "📈 Positioning"
    ])
    
    with tab1:
        st.markdown(f"""
        ### 📍 Evento
        **{event}**
        
        **Data:** {date}  
        **Location:** {location}  
        **Target:** {target}  
        **Obiettivo:** {objective}
        
        **Obiettivo Strategico:** Costruire autorevolezza e engagement nel target.
        **Tono di Voce:** Professionale, autorevole, strategico
        """)
    
    with tab2:
        st.markdown("#### LinkedIn")
        st.info(f"Pubblica: {times['LinkedIn']}")
        st.markdown("- Annuncio 2 settimane prima\n- Articoli settimanali\n- Pagina evento, recap post-evento")
        
        st.markdown("#### Instagram")
        st.info(f"Pubblica: {times['Instagram']}")
        st.markdown("- Stories countdown\n- Reels backstage\n- Carousel educativi")
        
        st.markdown("#### Twitter/X")
        st.info(f"Pubblica: {times['Twitter']}")
        st.markdown("- Live coverage\n- Thread aggiornamenti\n- Hashtag ufficiale")
        
        st.markdown("#### Timeline")
        st.dataframe({
            "Settimana": ["-4", "-3", "-2", "-1", "Evento", "+1", "+2"],
            "Azione": ["Annuncio", "Programma", "Teaser", "Countdown", "Live", "Recap", "Report"],
            "Piattaforma": ["LinkedIn, IG", "LinkedIn", "IG, TW", "Tutte", "TW, IG", "LinkedIn, IG", "LinkedIn"]
        })
    
    with tab3:
        lab_lines = creative_lab.split("IDEA")
        for i, idea in enumerate(lab_lines[1:], 1):
            with st.expander(f"💡 IDEA {i}"):
                st.markdown(idea.strip())
    
    with tab4:
        if insights and use_web_insights:
            st.markdown("### 📰 Notizie e contenuti correlati")
            for news in insights.get('news', [])[:5]:
                st.markdown(f"**{news['title']}**")
                if news.get('url'):
                    st.caption(f"🔗 {news['url']}")
                st.divider()
            
            # 🖼️ GALLERIA IMMAGINI (da Tavily)
            images = insights.get('images', [])
            if images:
                st.markdown("### 🖼️ Immagini correlate")
                cols = st.columns(min(len(images), 4))
                for i, img_url in enumerate(images[:4]):
                    with cols[i % len(cols)]:
                        try:
                            st.image(img_url, use_container_width=True)
                        except:
                            st.caption("Immagine non disponibile")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("### 🏷️ Hashtag trending")
                st.code(" ".join(insights.get('trending_hashtags', [])[:10]))
            with col_b:
                st.markdown("### 🔑 Keyword emergenti")
                st.code(", ".join(insights.get('keywords', [])[:10]))
        else:
            st.info("ℹ️ Web Insights disattivati o non disponibili")
    
    with tab5:
        st.markdown(positioning)
    
    # Download del piano completo
    st.divider()
    full_output = f"""
============================================================
iCRAWLER V2.0 — PIANO COMPLETO
Generato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
============================================================

1. STRATEGIA
Evento: {event}
Data: {date}
Location: {location}
Target: {target}
Obiettivo: {objective}

2. PIANO SOCIAL
LinkedIn: {times['LinkedIn']}
Instagram: {times['Instagram']}
Twitter: {times['Twitter']}

3. CTA
{chr(10).join([f"{i+1}. {c}" for i, c in enumerate(cta_list)])}

4. HASHTAG
{hashtags_suggeriti}

5. CREATIVE LAB
{creative_lab}

6. POSITIONING
{positioning}
    """
    
    st.download_button(
        label="📥 Scarica piano completo (TXT)",
        data=full_output,
        file_name=f"piano_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

elif generate and not brief:
    st.warning("⚠️ Inserisci un brief o carica un file prima di generare.")
