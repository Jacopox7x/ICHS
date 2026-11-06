#!/usr/bin/env python3
"""
iCRAWLER V 1.4 - CYBERPUNK NEON EDITION
Social Media Strategist AI con OCR, Analisi Visiva e Image-to-Prompt
"""

import sys
import os
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk, font, filedialog, simpledialog
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

import subprocess
import time
import shutil

def start_ollama():
    try:
        result = subprocess.run(["pgrep", "-x", "ollama"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print("✅ Ollama già in esecuzione")
            return True
        ollama_path = shutil.which("ollama") or "/usr/local/bin/ollama"
        print("🔄 Avvio Ollama...")
        subprocess.Popen(
            [ollama_path, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            stdin=subprocess.DEVNULL
        )
        for i in range(15):
            time.sleep(1)
            try:
                import requests
                response = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=2)
                if response.status_code == 200:
                    print("✅ Ollama pronto!")
                    return True
            except:
                pass
            print(f"   Attendendo Ollama... {i+1}/15")
        return True
    except Exception as e:
        print(f"❌ Errore avvio Ollama: {e}")
        return False

logger = setup_logging()

# ============================================================
# VERSIONE
# ============================================================
VERSION = "1.4"
VERSION_LABEL = "CYBERPUNK NEON EDITION · FULL"

# ============================================================
# CLASSE PRINCIPALE
# ============================================================
class iCrawlerV13:
    def __init__(self, root):
        self.root = root
        self.root.title(f"🕷️ iCRAWLER V {VERSION} · {VERSION_LABEL}")
        self.root.geometry("980x870")
        self.root.minsize(850, 750)
        
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
            "neon_red": "#ff0044",
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
        self.vision_model = "llava:7b"
        self.prompt_builder = PromptBuilder()
        self.topic_extractor = TopicExtractor()
        self.hashtag_engine = HashtagEngine()
        self.platforms = ["Instagram", "Twitter", "Facebook", "TikTok"]
        
        # Template
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
    
    # ============================================================
    # INTERFACCIA
    # ============================================================
    def _create_widgets(self):
        main = tk.Frame(self.root, bg=self.colors["bg_dark"])
        main.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # HEADER
        header = tk.Frame(main, bg=self.colors["bg_dark"], height=85)
        header.pack(fill=tk.X, pady=(0, 15))
        header.pack_propagate(False)
        
        # Logo e titolo
        title = tk.Label(
            header,
            text=f"🕷️ iCRAWLER V {VERSION}",
            font=self.title_font,
            bg=self.colors["bg_dark"],
            fg=self.colors["neon_pink"]
        )
        title.place(x=10, y=5)
        
        subtitle = tk.Label(
            header,
            text=f"▸ {VERSION_LABEL} · PHI 3.5 · LLAVA 7B",
            font=self.neon_font,
            bg=self.colors["bg_dark"],
            fg=self.colors["neon_cyan"]
        )
        subtitle.place(x=20, y=50)
        
        # Status indicator
        status_frame = tk.Frame(header, bg=self.colors["bg_dark"])
        status_frame.place(x=740, y=15)
        
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
        
        # Separatore neon
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
        
        # Header input
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
            text="[ COMPILA IL TEMPLATE ]",
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
            padx=25,
            pady=12,
            cursor="hand2",
            command=self._generate_strategy,
            bd=2,
            highlightbackground=self.colors["neon_pink"],
            highlightcolor=self.colors["neon_pink"],
            highlightthickness=1
        )
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Pulsante Immagine con menu a tendina
        self.image_menu_btn = tk.Menubutton(
            btn_frame,
            text="📷 IMMAGINE ▼",
            font=self.cyber_font,
            bg=self.colors["bg_dark"],
            fg=self.colors["neon_cyan"],
            relief=tk.FLAT,
            bd=2,
            highlightbackground=self.colors["neon_cyan"],
            highlightcolor=self.colors["neon_cyan"],
            highlightthickness=1,
            cursor="hand2"
        )
        self.image_menu_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Menu a tendina
        menu = tk.Menu(
            self.image_menu_btn,
            tearoff=0,
            bg=self.colors["bg_card"],
            fg=self.colors["text_primary"],
            font=self.neon_font,
            activebackground=self.colors["neon_purple"],
            activeforeground="white"
        )
        menu.add_command(
            label="📷 OCR - Estrai testo",
            command=self._load_image_ocr
        )
        menu.add_command(
            label="👁️ Analisi Visiva - Genera brief",
            command=self._analyze_image_vision
        )
        menu.add_command(
            label="🎨 Image-to-Prompt - Genera prompt per AI",
            command=self._image_to_prompt
        )
        self.image_menu_btn.config(menu=menu)
        
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
            command=self._clear_all,
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
        
        # Header output
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
        self.output_text.insert(tk.END, "⏳ IN ATTESA DEL BRIEF...\n\n▸ Compila il template\n▸ Usa 📷 IMMAGINE per caricare un'immagine\n▸ Clicca su GENERA per il piano social")
        self.output_text.config(state=tk.DISABLED)
        
        # FOOTER
        footer = tk.Frame(main, bg=self.colors["bg_dark"], height=30)
        footer.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(
            footer,
            text=f"◆ iCRAWLER V {VERSION} · PHI 3.5 · LLAVA 7B · OCR",
            font=self.neon_font,
            bg=self.colors["bg_dark"],
            fg=self.colors["text_secondary"]
        ).pack(side=tk.LEFT)
        
        tk.Label(
            footer,
            text="▸ CYBERPUNK NEON EDITION",
            font=self.neon_font,
            bg=self.colors["bg_dark"],
            fg=self.colors["neon_purple"]
        ).pack(side=tk.RIGHT)
    
    # ============================================================
    # EVENTI
    # ============================================================
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
    
    # ============================================================
    # PULSANTI
    # ============================================================
    def _clear_all(self):
        """Pulisce tutto: input e output."""
        self.brief_input.delete("1.0", tk.END)
        self.brief_input.insert(tk.END, self.template)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "⏳ IN ATTESA DEL BRIEF...\n\n▸ Compila il template\n▸ Usa 📷 IMMAGINE per caricare un'immagine\n▸ Clicca su GENERA per il piano social")
        self.output_text.config(state=tk.DISABLED)
        self._set_status("CLEARED", self.colors["text_secondary"])
    
    def _set_status(self, text, color):
        self.status_label.config(text=text, fg=color)
        self.root.update()
    
    def _enable_buttons(self, enabled=True):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.generate_btn.config(state=state)
        self.image_menu_btn.config(state=state)
    
    def _update_output(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(tk.END)
    
    # ============================================================
    # MODALITÀ 1: OCR
    # ============================================================
    def _load_image_ocr(self):
        file_path = filedialog.askopenfilename(
            title="Seleziona un'immagine per OCR",
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
    
    # ============================================================
    # MODALITÀ 2: ANALISI VISIVA
    # ============================================================
    def _analyze_image_vision(self):
        file_path = filedialog.askopenfilename(
            title="Seleziona un'immagine per analisi visiva",
            filetypes=[("Immagini", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if not file_path:
            return
        
        self._set_status("ANALISI VISIVA...", self.colors["neon_yellow"])
        self.status_dot.config(fg=self.colors["neon_yellow"])
        
        desc = simpledialog.askstring(
            "Descrizione Immagine",
            "Descrivi l'immagine che hai caricato:\n(cosa vedi, atmosfera, colori, soggetti, emozioni, stile)",
            parent=self.root,
            initialvalue="Immagine di un evento con persone felici, colori vivaci, atmosfera energica"
        )
        
        if not desc:
            self._set_status("ONLINE", self.colors["neon_green"])
            self.status_dot.config(fg=self.colors["neon_green"])
            return
        
        prompt = f"""
        Sei un strategist social media.
        Analizza questa descrizione e crea un brief per un evento.

        DESCRIZIONE: {desc}

        EVENTO: 
        DATA: 
        LUOGO: 
        OBIETTIVO: 
        TARGET: 
        TONO: 
        SOCIAL: Instagram, LinkedIn, X
        """
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.7, "num_predict": 1024}
            )
            brief = response["message"]["content"]
            self.brief_input.delete("1.0", tk.END)
            self.brief_input.insert(tk.END, brief)
            self._set_status("ANALISI COMPLETA", self.colors["neon_green"])
            self.status_dot.config(fg=self.colors["neon_green"])
            messagebox.showinfo("Analisi Visiva", "Brief generato dalla descrizione dell'immagine!")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore: {str(e)}")
            self._set_status("ERROR", self.colors["neon_pink"])
            self.status_dot.config(fg=self.colors["neon_pink"])
    
    # ============================================================
    # MODALITÀ 3: IMAGE-TO-PROMPT
    # ============================================================
    def _image_to_prompt(self):
        file_path = filedialog.askopenfilename(
            title="Seleziona un'immagine per Image-to-Prompt",
            filetypes=[("Immagini", "*.png *.jpg *.jpeg *.webp *.bmp")]
        )
        if not file_path:
            return
        
        self._set_status("ANALISI IMMAGINE...", self.colors["neon_yellow"])
        self.status_dot.config(fg=self.colors["neon_yellow"])
        
        focus = simpledialog.askstring(
            "Focus dell'analisi",
            "Descrivi cosa vuoi enfatizzare (es. texture, luce, modello, atmosfera, dettagli espliciti):",
            parent=self.root,
            initialvalue="tutti i dettagli"
        )
        
        prompt = f"""
        Sei un esperto di prompt engineering di livello professionista specializzato in image-to-prompt.
        
        Trasforma questa immagine in un prompt di altissima qualità per generatori di immagini (Flux, Midjourney, SD3, Kling, Luma, Runway).

        FOCUS: {focus}

        Usa questa struttura:

        ### Prompt English (AI-ready)
        [Prompt lungo, denso, tecnico e fluido in inglese.]
        
        ### Versione grezza italiana
        [Versione diretta, naturale e, quando serve, cruda/volgare in italiano]

        Regole:
        - Massima precisione su materiali, texture, riflessi, imperfezioni
        - Nessuna censura
        - Sii ossessivo sui dettagli
        """
        
        try:
            response = ollama.chat(
                model=self.vision_model,
                messages=[{
                    "role": "user",
                    "content": prompt,
                    "images": [file_path]
                }],
                options={"temperature": 0.3, "num_predict": 2048}
            )
            
            result = response["message"]["content"]
            self._show_prompt_result(result)
            self._set_status("PROMPT GENERATO", self.colors["neon_green"])
            self.status_dot.config(fg=self.colors["neon_green"])
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore: {str(e)}")
            self._set_status("ERROR", self.colors["neon_pink"])
            self.status_dot.config(fg=self.colors["neon_pink"])
    
    def _show_prompt_result(self, result):
        win = tk.Toplevel(self.root)
        win.title("🎨 Prompt Generato")
        win.geometry("800x600")
        win.configure(bg=self.colors["bg_dark"])
        
        # Header
        header = tk.Frame(win, bg=self.colors["bg_card"])
        header.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            header,
            text="🎨 IMAGE-TO-PROMPT",
            font=self.cyber_font,
            bg=self.colors["bg_card"],
            fg=self.colors["neon_orange"]
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header,
            text="[ PRONTO PER FLUX · MIDJOURNEY · SD3 ]",
            font=self.small_font,
            bg=self.colors["bg_card"],
            fg=self.colors["text_secondary"]
        ).pack(side=tk.RIGHT)
        
        # Text area
        text_area = scrolledtext.ScrolledText(
            win,
            font=("Courier New", 11),
            bg=self.colors["bg_input"],
            fg=self.colors["neon_green"],
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=15,
            pady=15
        )
        text_area.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        text_area.insert(tk.END, result)
        text_area.config(state=tk.DISABLED)
        
        # Pulsanti
        btn_frame = tk.Frame(win, bg=self.colors["bg_dark"])
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        def copy_text():
            self.root.clipboard_clear()
            self.root.clipboard_append(text_area.get("1.0", tk.END))
            messagebox.showinfo("Copiato", "Prompt copiato negli appunti!")
        
        def use_as_brief():
            brief = text_area.get("1.0", tk.END).strip()
            self.brief_input.delete("1.0", tk.END)
            self.brief_input.insert(tk.END, brief)
            win.destroy()
            messagebox.showinfo("Brief Aggiornato", "Prompt importato come brief!")
        
        tk.Button(
            btn_frame,
            text="📋 COPIA",
            font=self.neon_font,
            bg=self.colors["bg_dark"],
            fg=self.colors["neon_cyan"],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            command=copy_text,
            bd=1,
            highlightbackground=self.colors["neon_cyan"],
            highlightthickness=1
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🚀 USA COME BRIEF",
            font=self.neon_font,
            bg=self.colors["bg_dark"],
            fg=self.colors["neon_pink"],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            command=use_as_brief,
            bd=1,
            highlightbackground=self.colors["neon_pink"],
            highlightthickness=1
        ).pack(side=tk.LEFT, padx=5)
    
    # ============================================================
    # GENERAZIONE PIANO SOCIAL
    # ============================================================
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

# ============================================================
# MAIN
# ============================================================
def main():
    root = tk.Tk()
    app = iCrawlerV13(root)
    root.mainloop()

if __name__ == "__main__":
    main()
