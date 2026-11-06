import streamlit as st
import subprocess
import tempfile
import os
from datetime import datetime

# Configurazione pagina
st.set_page_config(
    page_title="iCrawler V2.0",
    page_icon="🕷️",
    layout="wide"
)

# CSS personalizzato (stile cyberpunk leggero)
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; }
    .stTextArea textarea { background-color: #111; color: #00ff88; border: 1px solid #00ff88; }
    .stButton button { background-color: #00ff88; color: #0a0a0a; font-weight: bold; }
    .stCodeBlock { background-color: #111; border: 1px solid #00ff88; }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🕷️ iCRAWLER V2.0")
st.caption("Agente Sociale Autonomo · Heraclitus Edition")

# Layout a colonne
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📝 Inserisci il brief")
    brief = st.text_area(
        "Descrizione dell'evento",
        height=200,
        placeholder="Es. Fiera del mattone il 10 Settembre a Rovigo. Obiettivo attirare lavoratori del ferro..."
    )
    
    # Opzioni avanzate
    with st.expander("⚙️ Opzioni"):
        show_positioning_only = st.checkbox("Mostra solo posizionamento", value=False)
    
    generate = st.button("🚀 GENERA PIANO SOCIAL", use_container_width=True)

with col2:
    st.markdown("### 📋 Piano generato")
    output_placeholder = st.empty()

# Logica di generazione
if generate:
    if not brief.strip():
        st.warning("⚠️ Inserisci un brief valido")
    else:
        with st.spinner("🕷️ iCrawler sta lavorando..."):
            # Crea file temporaneo per il brief
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(brief)
                tmp_path = f.name
            
            try:
                # Comando
                if show_positioning_only:
                    cmd = f"python3 icrawler.py {tmp_path} --positioning"
                else:
                    cmd = f"python3 icrawler.py {tmp_path}"
                
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300,
                    cwd=os.getcwd()
                )
                
                # Pulisci il file temporaneo
                os.unlink(tmp_path)
                
                if result.returncode == 0:
                    output = result.stdout
                    
                    # Mostra output nella colonna destra
                    with col2:
                        st.success("✅ Piano generato!")
                        if show_positioning_only:
                            st.markdown("**📊 POSIZIONAMENTO STRATEGICO**")
                        st.code(output, language="markdown")
                        
                        # Download
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"icrawler_plan_{timestamp}.txt"
                        st.download_button(
                            label="📥 Scarica TXT",
                            data=output,
                            file_name=filename,
                            mime="text/plain",
                            use_container_width=True
                        )
                else:
                    with col2:
                        st.error(f"❌ Errore: {result.stderr}")
            except subprocess.TimeoutExpired:
                with col2:
                    st.error("⏰ Timeout: il sistema ha impiegato troppo tempo")
            except Exception as e:
                with col2:
                    st.error(f"❌ Errore imprevisto: {e}")

# Footer
st.markdown("---")
st.caption("🕷️ iCrawler V2.0 · 1 Settembre 2026 · Costruito con passione e un computer vecchio")
