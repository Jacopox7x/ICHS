"""
iCRAWLER — Export PDF
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import re

def export_pdf(output_text, filename="output.pdf"):
    """Esporta un piano in PDF"""
    
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Stili personalizzati
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.darkblue,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.darkgreen,
        spaceAfter=10
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )
    
    story = []
    
    # Dividi il testo in sezioni
    lines = output_text.split('\n')
    for line in lines:
        if not line.strip():
            story.append(Spacer(1, 6))
            continue
        
        # Titolo principale
        if line.startswith('#'):
            clean = line.replace('#', '').strip()
            story.append(Paragraph(clean, title_style))
            story.append(Spacer(1, 10))
        
        # Sezione
        elif re.match(r'^\d+\.\s+[A-Z]', line):
            clean = line.replace('📍', '').replace('📅', '').replace('🎯', '').strip()
            story.append(Paragraph(clean, heading_style))
            story.append(Spacer(1, 6))
        
        # Hashtag
        elif line.startswith('#'):
            story.append(Paragraph(line, body_style))
        
        # Tabella / pipeline (semplificata)
        elif '|' in line:
            clean = line.replace('|', ' ').strip()
            story.append(Paragraph(clean, body_style))
        
        # Tutto il resto
        else:
            story.append(Paragraph(line, body_style))
    
    # Build PDF
    doc.build(story)
    print(f"✅ PDF salvato in: {filename}")

if __name__ == "__main__":
    # Test
    test_text = """# iCRAWLER - PIANO SOCIAL

1. STRATEGIA
📍 Evento: Tech4Good Summit 2026
📅 Data: 22 agosto 2026

2. PIANO SOCIAL
- LinkedIn: Annuncio
- Instagram: Stories

## HASHTAG
#Tech4Good2026 #Innovazione
"""
    export_pdf(test_text, "test_output.pdf")
    print("✅ Test PDF completato")
