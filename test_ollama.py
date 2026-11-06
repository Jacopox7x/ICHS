import ollama

print('Inizio test Ollama...')
try:
    response = ollama.chat(
        model='qwen3:4b',
        messages=[{'role': 'user', 'content': 'Scrivi una frase di 10 parole sul marketing.'}],
        options={'temperature': 0.7}
    )
    print('--- STRUTTURA RISPOSTA ---')
    print(response)
    print('--- CONTENUTO ESTRATTO ---')
    print(response['message']['content'])
except Exception as e:
    print('ERRORE:', e)
