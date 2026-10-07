import re
from typing import Dict, List

class SystemicRules:
    def __init__(self, facts: Dict[str, str]):
        self.facts = facts
        self.event = facts.get('event_name', '')
        self.location = facts.get('location', '')
        self.target = facts.get('target', '')
        self.objective = facts.get('objective', '')
        self.date = facts.get('date', '')
        self.full_text = str(facts)
        self._determine_sector()
    
    def _determine_sector(self):
        text = (self.event + ' ' + self.target + ' ' + self.objective).lower()
        if any(kw in text for kw in ['tech', 'digitale', 'conferenza', 'summit', 'ai', 'software', 'startup', 'cybersecurity']):
            self.sector = 'tech'
        elif any(kw in text for kw in ['birra', 'vino', 'cibo', 'ristorante', 'gastronomia', 'degustazione', 'food']):
            self.sector = 'food'
        elif any(kw in text for kw in ['corsa', 'maratona', 'sport', 'running', 'calcetto', 'torneo']):
            self.sector = 'sport'
        elif any(kw in text for kw in ['festa', 'party', 'divertimento', 'amici', 'compleanno', 'concerto', 'mostra', 'arte']):
            self.sector = 'leisure'
        else:
            self.sector = 'business'
    
    def _clean_hashtag(self, text: str) -> str:
        """Pulisce una stringa per trasformarla in un hashtag leggibile"""
        # Rimuovi parole inutili (articoli, preposizioni brevi)
        stop = {'il', 'lo', 'la', 'i', 'gli', 'le', 'di', 'del', 'della', 'dei', 'delle', 'a', 'in', 'at', 'per', 'con', 'su', 'da', 'tra', 'fra', 'e', 'ed'}
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        # Prendi solo le parole significative (escludendo stop word)
        meaningful = [w.capitalize() for w in words if w.lower() not in stop and len(w) > 2]
        # Se non ci sono parole significative, prendi le prime 3 parole
        if not meaningful:
            meaningful = [w.capitalize() for w in words[:3]]
        return ''.join(meaningful)
    
    def _get_location_hashtag(self) -> str:
        """Genera hashtag dalla location"""
        if self.location and self.location != 'DA DEFINIRE':
            return f'#{self.location}'
        return None
    
    
    def get_hashtags(self) -> List[str]:
        """Genera hashtag puliti, ben formati e senza duplicati"""
        # Prendi il nome base e rimuovi le preposizioni
        stop = ['di', 'della', 'del', 'dei', 'delle', 'a', 'in', 'il', 'lo', 'la', 'le', 'i', 'gli', 'per', 'con', 'su', 'da', 'tra', 'fra']
        # Rimuovi le preposizioni e prendi le parole significative
        words = [w.capitalize() for w in self.event.split() if w.lower() not in stop and len(w) > 2]
        if len(words) >= 2:
            base = ''.join(words[:2])  # Prime due parole
        else:
            base = self.event.replace(' ', '')[:20]
        
        loc = self.location.replace(' ', '')
        
        # Costruisci hashtag mirati per settore (con # davanti)
        if self.sector == 'food':
            tags = [f'#{base}', f'#{base}{loc}', f'#{loc}Food', f'#{loc}Event', '#Foodie', '#Gastronomia']
        elif self.sector == 'leisure':
            tags = [f'#{base}', f'#{loc}Event', f'#{loc}Life', '#Party', '#Divertimento', '#Amici', '#Weekend']
        elif self.sector == 'sport':
            tags = [f'#{base}', f'#{loc}Run', f'#{loc}Sport', '#Running', '#Fitness', '#Marathon']
        elif self.sector == 'tech':
            tags = [f'#{base}', f'#{loc}Tech', f'#{loc}Innovation', '#AI', '#Innovation', '#Digital']
        else:
            tags = [f'#{base}', f'#{loc}Business', f'#{loc}Networking', '#Business', '#Leadership', '#Strategy']
        
        # Aggiungi hashtag della location (se non è già incluso)
        if loc and loc != 'DA DEFINIRE' and f'#{loc}' not in tags:
            tags.append(f'#{loc}')
        
        # Rimuovi duplicati e hashtag troppo lunghi (>20 caratteri)
        seen = set()
        result = []
        for t in tags:
            if t not in seen and len(t) <= 25:
                seen.add(t)
                result.append(t)
        
        return result[:8]  # max 8 hashtag

        """Genera hashtag puliti e leggibili"""
        base = self._clean_hashtag(self.event)
        hashtags = []
        
        # 1. Hashtag principale (evento)
        if base and len(base) > 2:
            hashtags.append(f'#{base}')
        
        # 2. Hashtag evento + location (se location presente)
        loc_hashtag = self._get_location_hashtag()
        if loc_hashtag:
            hashtags.append(loc_hashtag)
            if base:
                hashtags.append(f'#{base}{self.location}')
        
        # 3. Hashtag geografici (se location presente)
        if self.location and self.location != 'DA DEFINIRE':
            hashtags.append(f'#{self.location}Event')
            hashtags.append(f'#{self.location}Life')
        
        # 4. Hashtag tematici per settore
        sector_map = {
            'tech': ['#Innovation', '#DigitalTransformation', '#AI', '#FutureOfWork'],
            'food': ['#Foodie', '#Gastronomia', '#CucinaItaliana', '#Taste'],
            'sport': ['#Running', '#Fitness', '#Marathon', '#Health'],
            'leisure': ['#Party', '#Divertimento', '#Amici', '#Weekend', '#Vibes'],
            'business': ['#Business', '#Leadership', '#Strategy', '#Growth']
        }
        hashtags.extend(sector_map.get(self.sector, sector_map['business']))
        
        # 5. Aggiungi target come hashtag (se specifico e non troppo lungo)
        if self.target and self.target != 'DA DEFINIRE':
            target_clean = self._clean_hashtag(self.target)
            if target_clean and len(target_clean) < 25:
                hashtags.append(f'#{target_clean}')
        
        # Rimuovi duplicati e hashtag troppo lunghi (> 25 caratteri)
        seen = set()
        result = []
        for tag in hashtags:
            if tag not in seen and len(tag) <= 30:
                seen.add(tag)
                result.append(tag)
        
        return result[:15]
    
    def get_posting_times(self) -> Dict[str, str]:
        base = {
            'LinkedIn': '08:30-10:00 (martedì-giovedì)',
            'Instagram': '12:00-14:00 (pranzo)',
            'Twitter': '09:00-11:00 (mattina)'
        }
        if self.sector == 'leisure':
            base['Instagram'] = '19:00-21:00 (sera)'
            base['Twitter'] = '20:00-22:00 (sera)'
        elif self.sector == 'food':
            base['Instagram'] = '18:00-20:00 (sera)'
            base['Twitter'] = '19:00-21:00 (sera)'
        elif self.sector == 'sport':
            base['Instagram'] = '07:00-09:00 (mattina)'
            base['Twitter'] = '08:00-10:00 (mattina)'
        return base
    
    def get_visual(self) -> Dict[str, str]:
        visual = {
            'tech': {
                'atmosfera': 'innovativa, professionale, futuristica',
                'soggetti': 'CEO, innovation manager, sviluppatori',
                'colori': 'blu, verde, accenti tecnologici'
            },
            'food': {
                'atmosfera': 'calda, accogliente, conviviale',
                'soggetti': 'chef, birrai, appassionati, famiglie',
                'colori': 'toni caldi (oro, ambra, rame)'
            },
            'sport': {
                'atmosfera': 'energetica, dinamica, motivante',
                'soggetti': 'atleti, runner, squadre, tifosi',
                'colori': 'toni accesi (rosso, arancione, blu)'
            },
            'leisure': {
                'atmosfera': 'divertente, calda, luminosa, accogliente',
                'soggetti': 'amici, sorrisi, momenti di convivialita',
                'colori': 'toni caldi e accoglienti, dorati e marine'
            },
            'business': {
                'atmosfera': 'istituzionale, professionale, innovativa',
                'soggetti': 'CEO, policy maker, leader di settore',
                'colori': 'palette istituzionale, blu e verde'
            }
        }
        return visual.get(self.sector, visual['business'])
    
    def get_cta(self) -> List[str]:
        cta_map = {
            'tech': [
                '📍 Registrati ora — [LINK DA DEFINIRE]',
                '💻 Partecipa alla community tech',
                '🔔 Segui per aggiornamenti sul programma',
                '📧 Richiedi info tecniche'
            ],
            'food': [
                '🍺 Prenota il tuo calice — [LINK DA DEFINIRE]',
                '🍽️ Scopri le degustazioni in programma',
                '📸 Condividi la tua esperienza con #BirraArtigianale',
                '📧 Richiedi info sugli abbinamenti'
            ],
            'sport': [
                '🏃 Iscriviti ora — [LINK DA DEFINIRE]',
                '📊 Scarica il programma di gara',
                '📸 Condividi il tuo allenamento con #RunningLife',
                '📧 Richiedi info logistiche'
            ],
            'leisure': [
                '🎉 Prenota il tuo posto — [LINK DA DEFINIRE]',
                '📸 Condividi i momenti migliori con #EventoLife',
                '🔔 Segui per aggiornamenti e sorprese',
                '📧 Richiedi info per gruppi'
            ],
            'business': [
                '📍 Registrati ora — [LINK DA DEFINIRE]',
                '💬 Partecipa — usa #Evento #Innovazione',
                '🔔 Segui per aggiornamenti',
                '📧 Richiedi info — contatta organizer'
            ]
        }
        return cta_map.get(self.sector, cta_map['business'])
    
    
    def get_reach_factor(self) -> float:
        """Tasso di conversione dinamico basato su popolazione e settore"""
        # Popolazione della città (se disponibile)
        city_pop = self._get_city_population()
        # Base per settore
        base_rates = {
            'food': 0.045,
            'leisure': 0.050,
            'sport': 0.035,
            'tech': 0.025,
            'business': 0.020
        }
        base = base_rates.get(self.sector, 0.025)
        
        # Modifica in base alla popolazione (città grandi hanno conversioni più basse)
        if city_pop > 1_000_000:
            base *= 0.7   # -30% per città grandi
        elif city_pop > 500_000:
            base *= 0.85  # -15% per città medie
        elif city_pop > 100_000:
            base *= 1.0   # invariato
        else:
            base *= 1.2   # +20% per città piccole (più facile coinvolgere)
        
        # Modifica in base al target (se specifico, conversione più alta)
        if self.target and self.target != 'DA DEFINIRE':
            if len(self.target.split()) > 1:  # target descrittivo = più specifico
                base *= 1.1
        
        # Limita tra 1% e 8%
        return max(0.01, min(0.08, base))
    
    def _get_city_population(self) -> int:
        """Restituisce la popolazione approssimativa della città"""
        city = self.location
        pop_map = {
            'Roma': 2_873_000,
            'Milano': 1_396_000,
            'Napoli': 914_000,
            'Torino': 848_000,
            'Palermo': 630_000,
            'Genova': 558_000,
            'Bologna': 392_000,
            'Firenze': 367_000,
            'Bari': 315_000,
            'Venezia': 254_000,
            'Verona': 257_000,
            'Rovigo': 50_000
        }
        return pop_map.get(city, 500_000)  # default 500k

        """Tasso di conversione basato su settore e target"""
        # Base per settore
        base_factors = {'tech': 0.03, 'food': 0.05, 'sport': 0.04, 'leisure': 0.06, 'business': 0.02}
        factor = base_factors.get(self.sector, 0.02)
        
        # Modifica in base al target (se specifico)
        target = self.target.lower() if self.target else ''
        if 'appassionati' in target or 'appassionato' in target:
            factor *= 1.3
        elif 'professionisti' in target or 'manager' in target:
            factor *= 0.8
        elif 'studenti' in target or 'giovani' in target:
            factor *= 1.2
        elif 'famiglie' in target:
            factor *= 1.1
        
        # Non superare il 10%
        return min(factor, 0.10)
    
    def get_platform_priority(self) -> List[str]:
        platforms = {
            'tech': ['LinkedIn', 'Twitter/X'],
            'food': ['Instagram', 'WhatsApp'],
            'sport': ['Instagram', 'Twitter/X'],
            'leisure': ['Instagram', 'WhatsApp', 'TikTok'],
            'business': ['LinkedIn', 'Instagram', 'Twitter/X']
        }
        return platforms.get(self.sector, ['LinkedIn', 'Instagram', 'Twitter/X'])
    
    def get_advice(self) -> str:
        target = self.target if self.target else 'professionisti'
        objective = self.objective if self.objective else 'creare valore'
        sector_advice = {
            'tech': f"Posiziona levento come il punto di riferimento per {target} che cercano {objective}. Usa un tono professionale e visionario.",
            'food': f"Posiziona levento come il luogo ideale per {target} che cercano {objective}. Usa un tono caldo e accogliente.",
            'sport': f"Posiziona levento come la sfida imperdibile per {target} che cercano {objective}. Usa un tono energico e motivante.",
            'leisure': f"Posiziona levento come la festa da non perdere per {target} che cercano {objective}. Usa un tono informale e caldo.",
            'business': f"Posiziona levento come il punto di riferimento per {target} che cercano {objective}. Usa un tono professionale e autorevole."
        }
        return sector_advice.get(self.sector, sector_advice['business'])

def apply_systemic_rules(facts: Dict[str, str], weknora_context: str = "") -> Dict[str, any]:
    """Applica regole sistemiche. Se weknora_context è presente, lo usa per override."""
    rules = SystemicRules(facts)

    result = {
        'hashtags': rules.get_hashtags(),
        'posting_times': rules.get_posting_times(),
        'visual': rules.get_visual(),
        'cta': rules.get_cta(),
        'reach_factor': rules.get_reach_factor(),
        'platform_priority': rules.get_platform_priority(),
        'sector': rules.sector,
        'advice': rules.get_advice()
    }

    # ─────────────────────────────────────────
    # Override con contesto WeKnora
    # ─────────────────────────────────────────
    if weknora_context:
        ctx_lower = weknora_context.lower()

        # 1. HASHTAG: estrai quelli brand/cooperativa
        if '#creazionimigranti' in ctx_lower:
            # Hashtag brand + locali + tematici
            weknora_hashtags = ['#creazionimigranti', '#cremona', '#sartoriasociale',
                                '#economiacircolare', '#artigianato', '#tessutowax',
                                '#secondavita', '#pezzoUnico', '#fattoamano']
            # Unisci con quelli generati (che saranno comunque scartati)
            result['hashtags'] = weknora_hashtags

        # 2. TONO: se dice "caldo, poetico" o "mai pietistico"
        if 'mai pietistico' in ctx_lower or 'caldo, poetico' in ctx_lower:
            result['advice'] = (
                "Tono di voce: caldo, poetico ma concreto, MAI pietistico. "
                "Parla di persone (non categorie), competenze (non bisogni), "
                "opportunità (non aiuto), percorsi (non integrazione). "
                "Usa parole come: intrecciare, mestiere, competenze, opportunità, "
                "percorsi, seconda vita, artigianale, creazioni, tessuto, "
                "economia circolare, punto cucito, pezzo unico. "
                "EVITA: pietismo, vittimismo, carità, 'bisognosi', 'aiuto' "
                "(come beneficenza), 'integrazione', 'inclusione sociale', "
                "'disagio', 'emergenza', 'etnico', 'tradizionale africano', 'colorato'."
            )

        # 3. PIATTAFORME: sovrascrivi la priorità
        if 'instagram' in ctx_lower and 'facebook' in ctx_lower and 'linkedin' in ctx_lower:
            result['platform_priority'] = ['Instagram', 'Facebook', 'LinkedIn']

        # 4. ORARI: estrai dalla descrizione
        if 'instagram' in ctx_lower and '12:00' in ctx_lower:
            result['posting_times'] = {
                'Instagram': '12:00-14:00 e 19:00-21:00 (Lun-Ven), 10:00-12:00 (Sab), 15:00-17:00 (Dom)',
                'Facebook': '08:00-10:00 e 20:00-22:00 (Lun-Ven), 10:00-12:00 (Sab-Dom)',
                'LinkedIn': '08:30-10:00 (Mar-Gio)',
            }

    return result
