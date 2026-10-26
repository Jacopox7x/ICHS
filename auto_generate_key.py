import requests
import json
import os

BASE_URL = "https://weknora.weixin.qq.com/api/v1"

def main():
    print("🔑 Generazione automatica API Key per WeKnora\n")
    email = input("Inserisci la tua EMAIL di WeKnora: ").strip()
    password = input("Inserisci la tua PASSWORD di WeKnora: ").strip()

    # 1. Login per ottenere il token
    print("\n⏳ Login in corso...")
    login_url = f"{BASE_URL}/auth/login"
    try:
        res = requests.post(login_url, json={"email": email, "password": password}, timeout=10)
        if res.status_code != 200:
            print(f"❌ Login fallito (HTTP {res.status_code}): {res.text}")
            return
    except Exception as e:
        print(f"❌ Errore di rete durante il login: {e}")
        return

    data = res.json()
    token = data.get("token")
    
    # Estraiamo l'ID del tenant attivo
    active_tenant = data.get("active_tenant", {})
    tenant_id = active_tenant.get("id")
    
    if not token or not tenant_id:
        print("❌ Impossibile trovare il token o l'ID del tenant nella risposta.")
        return
        
    print(f"✅ Login riuscito! Tenant attivo ID: {tenant_id}")

    # 2. Creazione della API Key
    print("\n⏳ Creazione della API Key con permessi di ricerca...")
    key_url = f"{BASE_URL}/tenants/{tenant_id}/api-keys"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "iCrawler Agent Reach",
        "capabilities": ["retrieve", "chat"]
    }
    
    try:
        res_key = requests.post(key_url, headers=headers, json=payload, timeout=10)
        if res_key.status_code not in [200, 201]:
            print(f"❌ Errore creazione chiave (HTTP {res_key.status_code}): {res_key.text}")
            return
            
        key_data = res_key.json()
        # La chiave in chiaro di solito è in 'api_key' o 'key'
        new_api_key = key_data.get("api_key") or key_data.get("key")
        
        if not new_api_key:
            print(f"⚠️ Chiave creata ma non trovata nella risposta: {json.dumps(key_data, indent=2)}")
            return
            
        print(f"\n✅ API Key generata con successo: {new_api_key[:10]}...")

        # 3. Salvataggio nel file .env
        with open(".env", "w") as f:
            f.write(f'WEKNORA_API_KEY="{new_api_key}"\n')
        print("✅ Chiave salvata automaticamente nel file .env!")

    except Exception as e:
        print(f"❌ Errore durante la creazione della chiave: {e}")

if __name__ == "__main__":
    main()
