import os
import requests
from dotenv import load_dotenv

load_dotenv()
# Puliamo la chiave da eventuali virgolette o spazi accidentali nel .env
API_KEY = os.getenv("WEKNORA_API_KEY", "").strip().strip('"').strip("'")
DEFAULT_BASE_URL = "https://weknora.weixin.qq.com/api/v1"

def test_connection():
    if not API_KEY or API_KEY == "LA_TUA_CHIAVE_QUI":
        print("❌ ERRORE: La chiave non è stata inserita o è ancora il placeholder.")
        return

    # Mostriamo solo i primi 5 e gli ultimi 5 caratteri per sicurezza
    print(f"🔑 Chiave letta: {API_KEY[:5]}...{API_KEY[-5:]}")
    
    url = f"{DEFAULT_BASE_URL}/knowledge-bases"
    
    # Test 1: X-API-Key
    headers_x = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    print(f"\n🔗 Test 1: X-API-Key su {url}...")
    try:
        r1 = requests.get(url, headers=headers_x, timeout=10)
        print(f"Risposta: {r1.status_code}")
        if r1.status_code == 200:
            print("✅ Successo con X-API-Key!")
            print(r1.json())
            return
    except Exception as e:
        print(f"Errore: {e}")

    # Test 2: Authorization Bearer
    headers_b = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    print(f"\n🔗 Test 2: Authorization Bearer su {url}...")
    try:
        r2 = requests.get(url, headers=headers_b, timeout=10)
        print(f"Risposta: {r2.status_code}")
        if r2.status_code == 200:
            print("✅ Successo con Authorization Bearer!")
            print(r2.json())
            return
    except Exception as e:
        print(f"Errore: {e}")

    print("\n❌ Entrambi i metodi hanno fallito. La chiave potrebbe essere scaduta o non valida per questo endpoint.")

if __name__ == "__main__":
    test_connection()
