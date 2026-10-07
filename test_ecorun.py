"""
Test Validator con output reale di EcoRun 2026
"""

from validator import Validator

brief = {
    "data": "10 ottobre 2026",
    "luogo": "Parco del Valentino, Torino",
    "target": "Runner e famiglie attente all'ambiente",
    "hashtag_autorizzati": ["#EcoRun2026", "#CorriGreen", "#TorinoSostenibile"],
    "budget": None,
    "link": None,
    "kpi": None
}

output_reale = """
## ANALISI
- **Target:** Runner e famiglie attente all'ambiente
- **Mood:** Green, motivazionale, inclusivo
- **Concept:** Promuovere la corsa ecologica e la sostenibilità attraverso l'evento EcoRun 2026

### INSTAGRAM
**Hook:** Unisciti alla marcia per il pianeta con #EcoRun2026!
**Corpo:** Il Parco del Valentino è pronto a ospitare l'evento di running più ecologico della Torino. Mettiti nei panni dei runner attenti all'ambiente ed entra nella corsa per una sostenibilità verde con #TorinoSostenibile!
**CTA:** Iscriviti ora, preparati a correre insieme alla comunità green di Torino in EcoRun 2026.
**Visual:** Un'istantanea del Parco del Valentino nel boschetto mentre runner attenti all'ambiente corrono tra gli alberi luminosi; sfondo verde con i hashtag #EcoRun2026 e #TorinoSostenibile prominenti in alto.
**Hashtag:** #EcoRun2026, #CorriGreen, #TorinoSostenibile

### LINKEDIN
**Hook:** Unisciti alla corsa per il pianeta e diventa parte della comunità green di Torino con EcoRun 2026.
**Corpo:** L'evento del Parco del Valentino, #EcoRun2026, presenta una gara sostenibile che promuove la salute dello sportivo ed è un impegno per l'ambiente. Scopri come puoi partecipare e incoraggiare il movimento green nella tua comunità con i nostri hashtag: #CorriGreen e #TorinoSostenibile.
**CTA:** Iscriviti all'evento, condividi la notizia su LinkedIn ed unisciti alla marcia verso una vita più verde!
**Visual:** Un infografico mostrando l'interazione tra runner in abbigliamento ecologico al Parco del Valentino; i hashtag #EcoRun2026, #CorriGreen e #TorinoSostenibile sono visibili sullo sfondo.
**Hashtag:** #EcoRun2

### X (TWITTER)
**Tweet 1:** Pronto a correre verso un futuro sostenibile? Unisciti all'escalation di EcoRun 2026 al Parco del Valentino! Testa la tua resistenza e il tuo impegno ambientale con i nostri hashtag🌿🏃 #EcoRun2026 #CorriGreen
**Tweet 2:** Eccone l'evento di running che ti fa correre per la Terra! Conosciuto come il più ecologico della Torino, preparati a una marcia verde incontaminata con @EcoRun_Italia al Parco del Valentino.🌎✨ #TorinoSostenibile
**Tweet 3:** È ora di correre per un motivo che conta! Eccone l'evento estivo della Torino sostenibile - EcoRun 2026 al Parco del Valentino. Unisciti alla nostra squadra ecologica in corsa🥇 #EcoRun2026
**Tweet 4:** Vuoi far parte di una marcia per la Terra? Non aspetta! Eccone l'evento estivo della Torino sostenibile - @EcoRun_Italia presenta il grande evento del Parco del Valentino, #EcoRun2026. Corri con noi🏃‍♂️🌍
**Tweet 5:** Ecco per te l'evento di running estivo della Torino sostenibile - preparati a correre nel grande evento dell'anno in programma al Parco del Valentino, #EcoRun2026. Corri verde e diventa parte integrante della comunità green🌿#TorinoSostenibile

### FACEBOOK
**Hook:** Unisciti alla corsa più sostenibile di Torino con EcoRun 2026!
**Corpo:** Il Parco del Valentino offre una bellissima opportunità per runner attenti all'ambiente. Affrontiamo la distanza ecoristica insieme in questo evento unico - #EcoRun2026, dove il nostro impegno ambientale si trasforma con ogni passo!
**CTA:** Iscriviti ora al tuo avventura green alla base del Parco del Valentino. Condividi la tua esperienza e ispiri gli altri a correre insieme per una sostenibilità verde!
**Visual:** Una foto in bianco nero di runner attenti all'ambiente al tramonto nel Parco del Valentino; i hashtag #EcoRun2026, #CorriGreen e @EcoRun_Italia sono visibili sullo sfondo.
**Hashtag:** #EcoRun2026, #TorinoSostenibile

### TIKTOK
**Script 1:** "Preparati per una corsa verde! Eccone l'evento estivo della Torino sostenibile - @EcoRun_Italia presenta il grande evento del Parco del Valentino, #EcoRun2026. Corri verso un futuro più pulito con ogni passo!"
**Script 2:** "Scopri chi è l'ambientalista runner della tua vita! Lanciamo EcoRun 2026 nel Parco del Valentino, Torino - dove il running si fonde con la sostenibilità. #EcoRun2026"
**Script 3:** "Non aspetta altro per unirti alla marcia verso una vita più verdi! Eccone l'evento estivo della Torino, @EcoRun_Italia presenta il grande evento del Parco del Valentino - #EcoRun2026. Corri con noi!"
**Script 4:** "Quando la corsa si fonde col verde... Eccone l'evento estivo della Torino sostenibile, @EcoRun_Italia presenta il grande evento del Parco del Valentino - #EcoRun2026. Corri verso un futuro più pulito!"
**Script 5:** "Lanciamo EcoRun 2026 nel cuore della Torino! Affrontiamo la distanza insieme al Parco del Valentino, dove il running si fonde con l'ambiente - #EcoRun2026. Corri verdi e diventa parte integrante dell'evento!"

### STORIES (5 frame)
1. Foto di runner attenti all'ambiente mentre aspettano al Parco del Valentino, con i hashtag #EcoRun2026 visibili in primo piano e sfondo verde naturale.
2. Un montaggio video della partenza dell'evento mostrando la folla di runner attenti all'ambiente mentre corrono insieme al Parco del Valentino, con i hashtag #TorinoSostenibile visibili in primo piano e sfondo verde naturale.
3. Una foto a tema tempo reale dei runners che superano una pista di fitness riciclata nel Parco del Valentino, con il testo "Corri Green" scritto sulla parete dello stagno visibile al centro dell'immagine e i hashtag #EcoRun2026 in primo piano.
4. Un montaggio video dei runner che si uniscono per una piccola riunione di gruppo dopo la corsa nel Parco del Valentino, con il testo "Impegnati alla Sostenibilità" scritto sullo sfondo verde naturale e i hashtag #CorriGreen visibili in primo piano.
5. Un'istantanea grafica dell'evento estivo della Torino sostenibile mostrando runner attenti all'ambiente che festeggiano la loro vittoria nel Parco del Valentino, con il testo "Vincitori Ecoresi" scritto su sfondo verde naturale e i hashtag #TorinoSostenibile visibili in primo piano.

### CALENDARIO RICEVE: 10 ottobre 2026
- **KPI:** Numero di iscritti, coinvolgimento sui social media (like e condivisioni), engagement durante i tweet X del parco dei Valentino
"""

validator = Validator()
result = validator.validate(output_reale, brief)

print("=" * 60)
print("🧪 VALIDAZIONE ECORUN 2026")
print("=" * 60)
print(f"Valid: {result['valid']}")
print(f"Errors: {result['errors']}")
print("=" * 60)
