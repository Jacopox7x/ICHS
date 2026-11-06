#!/usr/bin/env python3
"""
iCrawler - Cyberpunk Neon Edition
Social Media Strategist AI con OCR e Template
"""

import sys
import os
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, font, filedialog
import ollama
from datetime import datetime
from PIL import Image
import pytesseract

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from prompt_builder import PromptBuilder
from topics import TopicExtractor
from hashtags import HashtagEngine
from utils import setup_logging, save_output

logger = setup_logging()

class CyberpunkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🕷️ iCRAWLER · CYBERPUNK EDITION")
        self.root.geometry("950x850")
        self.root.minsize(800, 700)
        
        # Colori Cyberpunk Neon
        self.colors = {
            "bg_dark": "#0a0a0f",
            "bg_card": "#12121e",
            "bg_input": "#0d0d1a",
            "neon_pink": "#ff2d95",
            "neon_cyan": "#00f0ff",
            "neon_purple": "#b400ff",
            "neon_green": "#00ff9d",
            "neon_yellow": "#ffea00",
            "neon_orange": "#ff6a00",
            "text_primary": "#e0e0ff",
            "text_secondary": "#8888bb",
            "glow_pink": "#ff2d9544",
            "glow_cyan": "#00f0ff33",
            "glow_purple": "#b400ff44",
            "glow_green": "#00ff9d33"
        }
        
        self.root.configure(bg=self.colors["bg_dark"])
        
        # Font cyberpunk
        self.cyber_font = font.Font(family="Courier New", size=11, weight="bold")
        self.title_font = font.Font(family="Courier New", size=22, weight="bold")
        self.neon_font = font.Font(family="Courier New", size=10)
        self.small_font = font.Font(family="Courier New", size=9)
        
        # Variabili
        self.is_generating = False
        
        # Engine
        self.model = config.get("OLLAMA_MODEL", "phi3.5:3.8b-mini-instruct-q4_K_M")
        self.prompt_builder = PromptBuilder()
        self.topic_extractor = TopicExtractor()
        self.hashtag_engine = HashtagEngine()
        self.platforms = ["Instagram", "Twitter", "Facebook", "TikTok"]
        
        # Template di esempio
        self.template = """EVENTO: 
DATA: 
LUOGO: 
OBIETTIVO: 
TARGET: 
TONO: 
SOCIAL: Instagram, LinkedIn, X"""
        
        # Crea interfaccia
        self._create_widgets()
        self._check_ollama()
    
    def _create_widgets(self):
        # Container principale
        main = tk.Frame(self.root, bg=self.colors["bg_dark"])
        main.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # HEADER
        header = tk.Frame(main, bg=self.colors["bg_dark"], height=80)
        header.pack(fill=tk.X, pady=(0, 15))
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="🕷️ iCRAWLER",
            font=self.title_font,
            bg=self.colors["bg_dark"],
            fg=self.colors["neon_pink"]
        )
        title.place(x=10, y=5)
        
        subtitle = tk.Label(
            header,
            text="▸ SOCIAL MEDIA STRATEGIST · v3.0 · CYBERPUNK",
            font=self.neon_font,
            bg=self.colors["bg_dark"],
            fg=self.colors["neon_cyan"]
        )
        subtitle.place(x=20, y=50)
        
        # Status
        status_frame = tk.Frame(header, bg=self.colors["bg_dark"])
        status_frame.place(x=720, y=15)
        
        self.status_dot = tk.Label(
            status_frame,
            text="●",
            font=("Courier New", 18),
            bg=self.colors["bg_dark"],
            fg=self.colors["neon_yellow"]
        )
        self.status_dot.pack(side=tk.LEFT)
        
        self.status_label = tk.Label(
            status_frame,
            text="INITIALIZING",
            font=self.neon_font,
            bg=self.colors["bg_dark"],
            fg=self.colors["text_secondary"]
        )
        self.status_label.pack(side=tk.LEFT, padx=(8, 0))
        
        # Separatore
        sep = tk.Frame(main, bg=self.colors["neon_cyan"], height=2)
        sep.pack(fill=tk.X, pady=(0, 15))
        
        # CARD INPUT
        input_card = tk.Frame(
            main,
            bg=self.colors["bg_card"],
            relief=tk.FLAT,
            bd=2,
            highlightbackground=self.colors["neon_purple"],
            highlightcolor=self.colors["neon_purple"],
            highlightthickness=1
        )
        input_card.pack(fill=tk.X, pady=(0, 15))
        
        input_header = tk.Frame(input_card, bg=self.colors["bg_card"])
        input_header.pack(fill=tk.X, padx=15, pady=(10, 0))
        
        tk.Label(
            input_header,
            text="⍟ BRIEF INPUT",
            font=self.cyber_font,
            bg=self.colors["bg_card"],
            fg=self.colors["neon_cyan"]
        ).pack(side=tk.LEFT)
        
        tk.Label(
            input_header,
            text="[ INSERISCI L'EVENTO ]",
            font=self.small_font,
            bg=self.colors["bg_card"],
            fg=self.colors["text_secondary"]
        ).pack(side=tk.RIGHT)
        
        # Text area input
        self.brief_input = scrolledtext.ScrolledText(
            input_card,
            height=8,
            font=("Courier New", 11),
            bg=self.colors["bg_input"],
            fg=self.colors["text_primary"],
            insertbackground=self.colors["neon_cyan"],
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=15,
            pady=15,
            bd=0
        )
        self.brief_input.pack(fill=tk.X, padx=15, pady=(5, 15))
        self.brief_input.insert(tk.END, self.template)
        self.brief_input.bind('<FocusIn>', self._on_focus_in)
        self.brief_input.bind('<FocusOut>', self._on_focus_out)
        
        # Pulsanti
        btn_frame = tk.Frame(main, bg=self.colors["bg_dark"])
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Pulsante Genera
        self.generate_btn = tk.Button(
            btn_frame,
            text="⚡ GENERA PIANO SOCIAL",
            font=self.cyber_font,
            bg=self.colors["bg_dark"],
            fg=self.colors["neon_pink"],
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor="hand2",
            command=self._generate_strategy,
            bd=2,
            highlightbackground=self.colors["neon_pink"],
            highlightcolor=self.colors["neon_pink"],
            highlightthickness=1
        )
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Pulsante Carica Immagine
        self.image_btn = tk.Button(
            btn_frame,
            text="📷 CARICA IMMAGINE",
            font=self.cyber_font,
            bg=self.colors["bg_dark"],
            fg=self.colors["neon_cyan"],
            relief=tk.FLAT,
            padx=20,
            pady=12,
            cursor="hand2",
            command=self._load_image,
            bd=2,
            highlightbackground=self.colors["neon_cyan"],
            highlightcolor=self.colors["neon_cyan"],
            highlightthickness=1
        )
        self.image_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # Pulsante Clear
        clear_btn = tk.Button(
            btn_frame,
            text="⏎ CLEAR",
            font=self.neon_font,
            bg=self.colors["bg_dark"],
            fg=self.colors["text_secondary"],
            relief=tk.FLAT,
            padx=20,
            pady=12,
            cursor="hand2",
            command=self._clear_output,
            bd=1,
            highlightbackground=self.colors["text_secondary"],
            highlightthickness=1
        )
        clear_btn.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main,
            mode='indeterminate',
            length=200
        )
        self.progress.pack(fill=tk.X, pady=(0, 10))
        self.progress.pack_forget()
        
        # CARD OUTPUT
        output_card = tk.Frame(
            main,
            bg=self.colors["bg_card"],
            relief=tk.FLAT,
            bd=2,
            highlightbackground=self.colors["neon_green"],
            highlightcolor=self.colors["neon_green"],
            highlightthickness=1
        )
        output_card.pack(fill=tk.BOTH, expand=True)
        
        output_header = tk.Frame(output_card, bg=self.colors["bg_card"])
        output_header.pack(fill=tk.X, padx=15, pady=(10, 0))
        
        tk.Label(
            output_header,
            text="⍟ OUTPUT STRATEGY",
            font=self.cyber_font,
            bg=self.colors["bg_card"],
            fg=self.colors["neon_green"]
        ).pack(side=tk.LEFT)
        
        tk.Label(
            output_header,
            text="[ PIANO GENERATO ]",
            font=self.small_font,
            bg=self.colors["bg_card"],
            fg=self.colors["text_secondary"]
        ).pack(side=tk.RIGHT)
        
        self.output_text = scrolledtext.ScrolledText(
            output_card,
            height=18,
            font=("Courier New", 10),
            bg=self.colors["bg_input"],
            fg=self.colors["neon_green"],
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=15,
            pady=15,
            bd=0
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))
        self.output_text.insert(tk.END, "⏳ IN ATTESA DEL BRIEF...\n\n▸ Compila il template o carica un'immagine\n▸ Clicca su GENERA PIANO SOCIAL\n▸ Il piano verrà generato in pochi secondi")
        self.output_text.config(state=tk.DISABLED)
        
        # FOOTER
        footer = tk.Frame(main, bg=self.colors["bg_dark"], height=30)
        footer.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(
            footer,
            text="◆ iCRAWLER · POWERED BY OLLAMA · v3.0",
            font=self.neon_font,
            bg=self.colors["bg_dark"],
            fg=self.colors["text_secondary"]
        ).pack(side=tk.LEFT)
        
        tk.Label(
            footer,
            text="▸ CYBERPUNK NEON EDITION · OCR SUPPORT",
            font=self.neon_font,
            bg=self.colors["bg_dark"],
            fg=self.colors["neon_purple"]
        ).pack(side=tk.RIGHT)
    
    def _on_focus_in(self, event):
        if self.brief_input.get("1.0", tk.END).strip() == self.template.strip():
            self.brief_input.delete("1.0", tk.END)
    
    def _on_focus_out(self, event):
        if not self.brief_input.get("1.0", tk.END).strip():
            self.brief_input.insert(tk.END, self.template)
    
    def _check_ollama(self):
        try:
            import requests
            response = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=3)
            if response.status_code == 200:
                self.status_dot.config(fg=self.colors["neon_green"])
                self.status_label.config(text="ONLINE", fg=self.colors["neon_green"])
            else:
                self.status_dot.config(fg=self.colors["neon_yellow"])
                self.status_label.config(text="WARNING", fg=self.colors["neon_yellow"])
        except:
            self.status_dot.config(fg=self.colors["neon_pink"])
            self.status_label.config(text="OFFLINE", fg=self.colors["neon_pink"])
    
    def _load_image(self):
        """Carica un'immagine ed estrae il testo con OCR."""
        file_path = filedialog.askopenfilename(
            title="Seleziona un'immagine",
            filetypes=[("Immagini", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff")]
        )
        if not file_path:
            return
        
        self._set_status("OCR IN PROGRESS", self.colors["neon_yellow"])
        self.status_dot.config(fg=self.colors["neon_yellow"])
        
        try:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img, lang='ita+eng')
            if text.strip():
                self.brief_input.delete("1.0", tk.END)
                self.brief_input.insert(tk.END, text)
                self._set_status("OCR COMPLETE", self.colors["neon_green"])
                self.status_dot.config(fg=self.colors["neon_green"])
                messagebox.showinfo("OCR Completato", "Testo estratto dall'immagine con successo!")
            else:
                messagebox.showwarning("OCR Fallito", "Nessun testo rilevato nell'immagine.")
                self._set_status("ONLINE", self.colors["neon_green"])
                self.status_dot.config(fg=self.colors["neon_green"])
        except Exception as e:
            messagebox.showerror("Errore OCR", f"Errore durante l'OCR:\n{str(e)}")
            self._set_status("ERROR", self.colors["neon_pink"])
            self.status_dot.config(fg=self.colors["neon_pink"])
    
    def _set_status(self, text, color):
        self.status_label.config(text=text, fg=color)
        self.root.update()
    
    def _enable_buttons(self, enabled=True):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.generate_btn.config(state=state)
        self.image_btn.config(state=state)
    
    def _clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "⏳ IN ATTESA DEL BRIEF...\n\n▸ Compila il template o carica un'immagine\n▸ Clicca su GENERA PIANO SOCIAL\n▸ Il piano verrà generato in pochi secondi")
        self.output_text.config(state=tk.DISABLED)
    
    def _update_output(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(tk.END)
    
    def _generate_strategy(self):
        if self.is_generating:
            return
        
        brief = self.brief_input.get("1.0", tk.END).strip()
        if not brief or brief == self.template.strip():
            messagebox.showwarning("BRIEF VUOTO", "Inserisci un brief valido o carica un'immagine.")
            return
        
        self.is_generating = True
        self._enable_buttons(False)
        self.progress.pack(fill=tk.X, pady=(0, 10))
        self.progress.start(10)
        self._set_status("GENERATING", self.colors["neon_yellow"])
        self.status_dot.config(fg=self.colors["neon_yellow"])
        
        thread = threading.Thread(target=self._generate_thread, args=(brief,))
        thread.daemon = True
        thread.start()
    
    def _generate_thread(self, brief):
        try:
            topic = self.topic_extractor.extract(brief)
            hashtag_pool = self.hashtag_engine.generate_pool_for_prompt(topic.main_topic, topic.category)
            prompt = self.prompt_builder.build(brief, topic, hashtag_pool, self.platforms)
            
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "temperature": config.get("TEMPERATURE", 0.7),
                    "num_predict": config.get("MAX_TOKENS", 4096)
                }
            )
            
            output = response["message"]["content"]
            save_output(brief, output, topic.category)
            
            self.root.after(0, lambda: self._on_complete(output))
            
        except Exception as e:
            logger.error(f"Errore: {e}")
            self.root.after(0, lambda: self._on_error(str(e)))
    
    def _on_complete(self, output):
        self._update_output(output)
        self._set_status("COMPLETE", self.colors["neon_green"])
        self.status_dot.config(fg=self.colors["neon_green"])
        self.progress.stop()
        self.progress.pack_forget()
        self.is_generating = False
        self._enable_buttons(True)
    
    def _on_error(self, error):
        self._update_output(f"✖ ERRORE\n\n{error}\n\n▸ Verifica che Ollama sia in esecuzione\n▸ Esegui: ollama serve")
        self._set_status("ERROR", self.colors["neon_pink"])
        self.status_dot.config(fg=self.colors["neon_pink"])
        self.progress.stop()
        self.progress.pack_forget()
        self.is_generating = False
        self._enable_buttons(True)

def main():
    root = tk.Tk()
    app = CyberpunkGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
