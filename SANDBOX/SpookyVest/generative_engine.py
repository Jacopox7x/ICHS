import ollama
import base64
import urllib.parse
import urllib.request

class GenerativeEngine:
    def generate(self, image_bytes: bytes, style: str = "horror"):
        try:
            img_b64 = base64.b64encode(image_bytes).decode('utf-8')

            res_vl = ollama.chat(
                model='qwen2.5vl:3b',
                messages=[{
                    'role': 'user',
                    'content': "Describe this image briefly in English. Focus on the person's appearance, clothing, and background.",
                    'images': [img_b64]
                }],
                options={'temperature': 0.3}
            )
            descrizione = res_vl['message']['content'].strip()

            res_llm = ollama.chat(
                model='qwen2.5:3b',
                messages=[{
                    'role': 'user',
                    'content': f"Take this description: '{descrizione}'. Transform it into a prompt for an AI image generator. The goal is a spooky Halloween image. Replace the person's face with a pumpkin or skull mask. Keep the clothes and background original. Style: highly detailed, cinematic lighting. Reply ONLY with the English prompt."
                }],
                options={'temperature': 0.7}
            )
            prompt_finale = res_llm['message']['content'].strip()

            prompt_encoded = urllib.parse.quote(prompt_finale + ", halloween style, spooky, highly detailed")
            url = f"https://image.pollinations.ai/prompt/{prompt_encoded}?width=1024&height=1024&nologo=true"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                result_bytes = response.read()

            return result_bytes, prompt_finale

        except Exception as e:
            return None, str(e)
