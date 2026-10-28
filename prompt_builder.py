from pathlib import Path
import config
from hashtag_suggester import HashtagSuggester
from cognee_memory import get_client_context


PLACEHOLDER_VALUES = {
    "da definire", "n/a", "na", "non specificato", "non specificata",
    "non specificati", "none", "-", "--", "?", "tbd", "to be defined",
}


def _is_placeholder(value) -> bool:
    if value is None:
        return True
    s = str(value).strip()
    if not s:
        return True
    if s.lower() in PLACEHOLDER_VALUES:
        return True
    return False


class PromptBuilder:
    def __init__(self):
        self.prompt_file = Path(config.PROMPT_DIR) / "strategist.txt"
        self.suggester = HashtagSuggester()

    def build(self, brief: str, topic, hashtag_pool: list, platforms: list = None, entities: dict = None, mode: str = 'social', sandbox: str = 'cosper') -> str:
        file_name = "wordpress_planner.txt" if mode == "wordpress" else "strategist.txt"
        prompt_file = Path(config.PROMPT_DIR) / file_name
        
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
        else:
            system_prompt = "Sei uno strategist social media. Crea un piano in JSON."

        if entities:
            brief_data = {
                "nome_evento": entities.get("event", ""),
                "data": entities.get("date", ""),
                "luogo": entities.get("location", ""),
                "target": entities.get("target audience", ""),
                "hashtag": entities.get("hashtag", ""),
                "descrizione": entities.get("topic", ""),
            }
            brief_data = {k: v for k, v in brief_data.items() if v and not _is_placeholder(v)}
        else:
            brief_data = {}
            for line in brief.split('\n'):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()
                    if _is_placeholder(value):
                        continue
                    if "evento" in key or "nome" in key:
                        brief_data["nome_evento"] = value
                    elif "data" in key:
                        brief_data["data"] = value
                    elif "luogo" in key:
                        brief_data["luogo"] = value
                    elif "target" in key:
                        brief_data["target"] = value
                    elif "budget" in key or "costo" in key:
                        brief_data["budget"] = value
                    elif "hashtag" in key:
                        brief_data["hashtag"] = value
                    elif "descrizione" in key:
                        brief_data["descrizione"] = value

        # --- INIEZIONE EVIDENZE (SRE Logic) ---
        evidenze_nomi = brief_data.get("nome_evento", "Non specificato")
        evidenze_date = f"Data: {brief_data.get('data', 'Non specificata')} | Luogo: {brief_data.get('luogo', 'Non specificato')}"
        evidenze_numeri = brief_data.get("budget", "Non specificato")
        
        system_prompt = system_prompt.replace("{entita_nomi}", evidenze_nomi)
        system_prompt = system_prompt.replace("{entita_date_luoghi}", evidenze_date)
        system_prompt = system_prompt.replace("{entita_numeri}", evidenze_numeri)

        suggestions = self.suggester.suggest(brief_data, count=8)
        suggested_str = ", ".join(suggestions) if suggestions else ""
        
        cloud_hashtags = []
        
        # Proviamo a prendere il contesto da Cognee
        voice_content = get_client_context(sandbox)
        
        # Se Cognee fallisce o non trova nulla, facciamo il fallback al file locale
        if not voice_content:
            voice_file = Path(config.BASE_DIR) / "workspaces" / sandbox / "voice_template.txt"
            voice_content = voice_file.read_text(encoding="utf-8") if voice_file.exists() else ""
        prompt = system_prompt.replace("{tone_of_voice}", voice_content)
        prompt = prompt.replace("{voice_content}", voice_content)
        prompt = prompt.replace("{brief}", f"--- INIZIO DOCUMENTO DI RIFERIMENTO ---\n{brief}\n--- FINE DOCUMENTO DI RIFERIMENTO ---")
        # Uniamo gli hashtag semantici al prompt
        if hashtag_pool:
            suggested_str = ", ".join(hashtag_pool)
        
        prompt = prompt.replace("{hashtag_suggestions}", suggested_str)
        prompt = prompt.replace("{cloud_hashtags}", ", ".join(cloud_hashtags))
        
        return prompt

