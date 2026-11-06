import re
import shutil

# --- 1. PATCH DI UI_SERVER.PY ---
print("🔄 Patch di ui_server.py in corso...")
with open("ui_server.py", "r", encoding="utf-8") as f:
    server_code = f.read()

shutil.copyfile("ui_server.py", "ui_server.py.bak_newsletter")

# Cerca un endpoint esistente per iniettare il nostro
if '@app.post("/genera_newsletter")' not in server_code:
    # Aggiunge l'endpoint prima di @app.post("/genera") o in fondo
    new_endpoint = '''
@app.post("/genera_newsletter")
async def api_genera_newsletter(request: Request):
    data = await request.json()
    brief = data.get("brief", "")
    cliente = data.get("cliente", "Cosper")
    try:
        # Assumiamo che l'istanza dell'app sia accessibile o che la funzione sia globale
        # Se hai un'istanza, sostituisci app_instance con il nome corretto
        risultato = genera_newsletter(brief, cliente) 
        return {"status": "ok", "newsletter": risultato}
    except Exception as e:
        return {"status": "error", "message": str(e)}
'''
    # Inietta prima dell'ultima occorrenza di @app.post o alla fine
    if '@app.post("/genera")' in server_code:
        server_code = server_code.replace('@app.post("/genera")', new_endpoint + '\n@app.post("/genera")')
    else:
        server_code += new_endpoint

    with open("ui_server.py", "w", encoding="utf-8") as f:
        f.write(server_code)
    print("✅ ui_server.py aggiornato con l'endpoint /genera_newsletter")
else:
    print("ℹ️ Endpoint /genera_newsletter già presente.")

# --- 2. PATCH DI UI.HTML ---
print("🔄 Patch di ui.html in corso...")
with open("ui.html", "r", encoding="utf-8") as f:
    html_code = f.read()

shutil.copyfile("ui.html", "ui.html.bak_newsletter")

# 2a. Aggiungi la voce nella sidebar
if 'id="nav-newsletter"' not in html_code:
    # Trova la voce Knowledge Base e aggiunge Newsletter sotto
    sidebar_regex = r'(<div[^>]*class="[^"]*nav-item[^"]*"[^>]*>\s*Knowledge Base\s*</div>)'
    match = re.search(sidebar_regex, html_code)
    if match:
        new_item = match.group(1) + '\n                <div class="nav-item" id="nav-newsletter" onclick="showNewsletter()">📰 Newsletter</div>'
        html_code = html_code.replace(match.group(1), new_item)
    else:
        # Fallback: cerca "Knowledge Base" e aggiungi dopo
        html_code = html_code.replace("Knowledge Base", "Knowledge Base\n            <div class=\"nav-item\" onclick=\"showNewsletter()\">📰 Newsletter</div>", 1)
    print("✅ Voce sidebar aggiunta.")

# 2b. Aggiungi il JS per gestire la chiamata API (in fondo al body prima di </script>)
if 'function showNewsletter()' not in html_code:
    js_code = '''
        function showNewsletter() {
            // Nasconde le altre sezioni
            document.querySelectorAll('.main-panel, .generator-panel').forEach(el => el.style.display = 'none');
            const nlPanel = document.getElementById('newsletter-panel');
            if(nlPanel) nlPanel.style.display = 'block';
        }

        async function generaNewsletter() {
            const brief = document.getElementById('newsletter-brief').value;
            const cliente = document.getElementById('cliente-select') ? document.getElementById('cliente-select').value : 'Cosper';
            
            const outputDiv = document.getElementById('newsletter-output');
            outputDiv.innerHTML = '⏳ Generazione in corso...';
            
            try {
                const response = await fetch('/genera_newsletter', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ brief: brief, cliente: cliente })
                });
                const data = await response.json();
                
                if (data.status === 'ok') {
                    try {
                        // Prova a parsare il JSON della newsletter per formattarlo bene
                        const nl = JSON.parse(data.newsletter);
                        outputDiv.innerHTML = `
                            <div style="background: rgba(0,242,254,0.1); padding: 15px; border-radius: 8px; border: 1px solid #00F2FE;">
                                <h3 style="color: #00F2FE; margin-top: 0;">Oggetto: ${nl.subject}</h3>
                                <p style="color: #aaa; font-size: 12px;">Preheader: ${nl.preheader}</p>
                                <hr style="border-color: rgba(255,255,255,0.1);">
                                <p><strong>${nl.saluto}</strong></p>
                                <p>${nl.corpo}</p>
                                <br>
                                <button style="background: #00F2FE; color: #000; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">${nl.cta}</button>
                            </div>
                        `;
                    } catch (e) {
                        // Se non è JSON valido, mostra il testo grezzo
                        outputDiv.innerText = data.newsletter;
                    }
                } else {
                    outputDiv.innerText = "Errore: " + data.message;
                }
            } catch (error) {
                outputDiv.innerText = "Errore di rete: " + error;
            }
        }
    '''
    # Inserisce il JS prima della chiusura del tag script
    html_code = html_code.replace("</script>", js_code + "\n    </script>")
    print("✅ JavaScript della Newsletter aggiunto.")

# 2c. Aggiungi il pannello HTML (nascosto di default)
if 'id="newsletter-panel"' not in html_code:
    panel_html = '''
    <div id="newsletter-panel" style="display: none; padding: 20px;">
        <h2 style="color: #00F2FE; margin-bottom: 20px;">📰 Generatore di Newsletter</h2>
        <p style="color: #ccc; margin-bottom: 15px;">Inserisci il brief del cliente per generare una newsletter completa.</p>
        
        <textarea id="newsletter-brief" rows="5" style="width: 100%; background: #1A1A1C; color: #fff; border: 1px solid rgba(0,242,254,0.3); border-radius: 8px; padding: 15px; margin-bottom: 15px; font-family: monospace;" placeholder="Es: Lancio del nuovo servizio di upcycling di Cosper a Cremona..."></textarea>
        
        <button onclick="generaNewsletter()" style="background: #00F2FE; color: #000; font-weight: bold; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin-bottom: 20px;">
            Genera Newsletter ✨
        </button>
        
        <div id="newsletter-output" style="background: #0E1117; border: 1px solid rgba(0,242,254,0.2); border-radius: 8px; padding: 20px; min-height: 200px; color: #E2E8F0;">
            <!-- L'output apparirà qui -->
        </div>
    </div>
    '''
    # Inserisce il pannello prima della chiusura del main o del body
    if '</main>' in html_code:
        html_code = html_code.replace('</main>', panel_html + '\n</main>')
    else:
        html_code = html_code.replace('</body>', panel_html + '\n</body>')
    print("✅ Pannello HTML della Newsletter aggiunto.")

with open("ui.html", "w", encoding="utf-8") as f:
    f.write(html_code)

print("✅ Patch UI completata con successo!")
print("⚠️ RICORDA: Riavvia il server (Ctrl+C e poi python3 ui_server.py) per applicare le modifiche.")
