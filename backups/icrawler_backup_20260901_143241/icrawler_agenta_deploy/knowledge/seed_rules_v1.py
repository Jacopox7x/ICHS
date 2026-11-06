#!/usr/bin/env python3

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "knowledge_base.db"

PRIORITIES = {
    "FACT": 10,
    "HARD_VALIDATION": 9,
    "BRIEF_CONSTRAINT": 8,
    "PLATFORM": 7,
    "CONTENT": 6,
    "STYLE": 5,
    "BEST_PRACTICE": 4,
    "BEST_PRACTICE_LOW": 3,
    "CREATIVE": 2,
    "CREATIVE_LOW": 1,
}

def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO kb_version(version, description)
        VALUES (?, ?)
    """, ("1.0", "Versione iniziale Knowledge Base iCRAWLER"))

    cur.execute(
        "SELECT id FROM kb_version WHERE version = ?",
        ("1.0",)
    )
    kb_id = cur.fetchone()[0]

    cur.execute("DELETE FROM rule_tags")
    cur.execute("DELETE FROM test_cases")
    cur.execute("DELETE FROM style_rules")
    cur.execute("DELETE FROM platform_rules")
    cur.execute("DELETE FROM content_rules")
    cur.execute("DELETE FROM hashtag_rules")
    cur.execute("DELETE FROM visual_rules")
    cur.execute("DELETE FROM cta_rules")
    cur.execute("DELETE FROM anti_patterns")
    cur.execute("DELETE FROM validation_rules")
    cur.execute("DELETE FROM brief_constraints")
    cur.execute("DELETE FROM lessons_learned")

    for level, priority in PRIORITIES.items():
        cur.execute("""
            INSERT OR IGNORE INTO rule_priority
            (priority, level, description)
            VALUES (?, ?, ?)
        """, (
            priority,
            level,
            f"Priorità {level} ({priority})"
        ))

    style_rules = [
        ("tone","instagram","Tono professionale-accessibile e contemporaneo.",5),
        ("tone","linkedin","Tono professionale, riflessivo e accessibile.",5),
        ("tone","facebook","Tono accessibile e diretto.",5),
        ("tone","stories","Tono prossimo, diretto e coinvolgente.",5),
        ("quality","all","Accuratezza prima della creatività.",5),
        ("quality","all","Contesto prima della genericità.",5),
    ]

    for row in style_rules:
        cur.execute("""
            INSERT INTO style_rules
            (category,platform,rule,priority,kb_version_id)
            VALUES (?,?,?,?,?)
        """, (*row, kb_id))

    platform_rules = [
        ("instagram","awareness, engagement, visual storytelling",
         "HOOK → CORPO → CTA","professionale-accessibile",7,7),

        ("linkedin","autorevolezza, thought leadership, networking",
         "HOOK → SVILUPPO → INSIGHT / CTA",
         "professionale, riflessivo",5,7),

        ("facebook","community, condivisione, reach",
         "contenuto → sviluppo → CTA",
         "accessibile e diretto",3,7),

        ("stories","prossimità, urgenza, backstage, reminder",
         "3-5 frame con logica narrativa",
         "diretto e coinvolgente",3,7),
    ]

    for row in platform_rules:
        cur.execute("""
            INSERT INTO platform_rules
            (platform,objective,structure,tone,hashtag_count,priority,kb_version_id)
            VALUES (?,?,?,?,?,?,?)
        """, (*row, kb_id))

    content_rules = [
        ("EDUCATIONAL","Spiegare concetti e fornire valore.",6),
        ("PROMOTIONAL","Promuovere offerte, inviti o iscrizioni.",6),
        ("EMOTIONAL","Storytelling, testimonianze e impatto umano.",6),
        ("INSTITUTIONAL","Comunicare identità, attività e autorevolezza.",6),
        ("COMMUNITY","Favorire partecipazione e senso di comunità.",6),
        ("BEHIND THE SCENES","Mostrare processi, persone e preparazione.",6),
        ("EVENT","Comunicare e accompagnare un evento.",6),
        ("TESTIMONIAL","Utilizzare esperienze e testimonianze.",6),
    ]

    for row in content_rules:
        cur.execute("""
            INSERT INTO content_rules
            (category,description,priority,kb_version_id)
            VALUES (?,?,?,?)
        """, (*row, kb_id))

    hashtag_rules = [
        ("BRAND","Usare hashtag coerenti con il brand.",4),
        ("EVENT","Usare hashtag dedicati all'evento solo se fondati.",4),
        ("LOCATION","Usare hashtag geografici pertinenti.",4),
        ("SECTOR","Usare hashtag pertinenti al settore.",4),
        ("TOPIC","Usare hashtag pertinenti al tema.",4),
        ("COMMUNITY","Usare hashtag pertinenti alla community.",4),
        ("TREND","Usare trend solo se pertinenti.",3),
    ]

    for row in hashtag_rules:
        cur.execute("""
            INSERT INTO hashtag_rules
            (category,rule,priority,kb_version_id)
            VALUES (?,?,?,?)
        """, (*row, kb_id))

    visual_rules = [
        ("composition","Indicare soggetto e composizione.",5),
        ("light","Indicare luce quando rilevante.",5),
        ("atmosphere","Definire atmosfera coerente con il contenuto.",5),
        ("overlay","Specificare eventuale testo in sovraimpressione.",5),
        ("consistency","Mantenere coerenza visiva.",5),
    ]

    for row in visual_rules:
        cur.execute("""
            INSERT INTO visual_rules
            (category,rule,priority,kb_version_id)
            VALUES (?,?,?,?)
        """, (*row, kb_id))

    cta_rules = [
        ("INFORMATIVE","Scopri di più / Leggi l'articolo",5),
        ("ENGAGEMENT","Commenta / Condividi",5),
        ("CONVERSION","Registrati / Iscriviti",6),
        ("COMMUNITY","Partecipa / Raccontaci",5),
        ("LEAD","Richiedi informazioni",6),
        ("RETENTION","Seguici per i prossimi aggiornamenti",5),
    ]

    for row in cta_rules:
        cur.execute("""
            INSERT INTO cta_rules
            (category,rule,priority,kb_version_id)
            VALUES (?,?,?,?)
        """, (*row, kb_id))

    anti_patterns = [
        ("critical","Non inventare informazioni.",9),
        ("critical","Non inventare speaker, venue, orari, prezzi o statistiche.",9),
        ("critical","Non trasformare supposizioni in fatti.",9),
        ("critical","Non inventare link.",9),
        ("high","Non usare cliché pubblicitari.",6),
        ("high","Non usare hashtag irrilevanti.",6),
        ("high","Non nascondere informazioni mancanti.",4),
    ]

    for row in anti_patterns:
        cur.execute("""
            INSERT INTO anti_patterns
            (severity,rule,priority,kb_version_id)
            VALUES (?,?,?,?)
        """, (*row, kb_id))

    validation_rules = [
        ("fact_check","Tutti i facts del brief devono essere rispettati.",9),
        ("date_check","La data deve essere coerente con il brief.",9),
        ("location_check","La location deve essere coerente con il brief.",9),
        ("hallucination","Nessun dato non presente nel brief può essere presentato come fatto.",9),
        ("missing_data","I dati mancanti devono essere marcati DA DEFINIRE.",9),
    ]

    for row in validation_rules:
        cur.execute("""
            INSERT INTO validation_rules
            (category,rule,priority,kb_version_id)
            VALUES (?,?,?,?)
        """, (*row, kb_id))

    brief_constraints = [
        ("EVENT_NAME","Il nome evento deve provenire dal brief.",8),
        ("DATE","La data deve provenire dal brief.",8),
        ("TIME","Se assente: DA DEFINIRE.",8),
        ("LOCATION","Se assente: DA DEFINIRE.",8),
        ("ORGANIZER","Se assente: DA DEFINIRE.",8),
        ("TARGET","Se assente: DA DEFINIRE.",8),
        ("OBJECTIVE","Se assente: DA DEFINIRE.",8),
        ("CTA","Se assente: DA DEFINIRE.",8),
        ("BUDGET","Se assente: DA DEFINIRE.",8),
        ("PLATFORMS","Se assente: DA DEFINIRE.",8),
        ("KEY_MESSAGE","Se assente: DA DEFINIRE.",8),
        ("CONSTRAINTS","Se assente: DA DEFINIRE.",8),
    ]

    for row in brief_constraints:
        cur.execute("""
            INSERT INTO brief_constraints(field,rule,priority)
            VALUES (?,?,?)
        """, row)

    tests = [
        ("A","Brief completo",
         "Tech4Good Summit, Milano, 22 agosto 2026, organizzato da Impact Hub, target professionisti innovazione, obiettivo 300 partecipanti",
         "GENERATE",
         "complete",8),

        ("B","Data ambigua",
         "Evento a Milano il 22",
         "BLOCKING",
         "ambiguity",9),

        ("C","Brief minimale",
         "Evento a Milano il 22 agosto",
         "GENERATE_WITH_DA_DEFINIRE",
         "missing_data",8),

        ("D","Hallucination trap",
         "Evento a Milano il 22 agosto",
         "NON_INVENTARE_ORARIO_VENUE_SPEAKER",
         "hallucination",9),
    ]

    for row in tests:
        cur.execute("""
            INSERT INTO test_cases
            (case_id,name,brief,expected_behavior,category,priority,kb_version_id)
            VALUES (?,?,?,?,?,?,?)
        """, (
            row[0],row[1],row[2],row[3],row[4],row[5],kb_id
        ))

    conn.commit()

    print("✅ Knowledge Base popolata.")
    print(f"KB version ID: {kb_id}")

    conn.close()

if __name__ == "__main__":
    seed()
