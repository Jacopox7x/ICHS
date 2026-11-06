with open("icrawler_simple.py", "r", encoding="utf-8") as f:
    code = f.read()

# Il blocco rotto (con l'indentazione sbagliata e duplicata)
old_block = '''            record_model_call(ctx)
output = response["message"]["content"]
            # Pulisce i backtick di markdown se presenti
            if output.strip().startswith("```"):
                output = output.replace("```json", "").replace("```", "").strip()
            print(f"🔍 DEBUG: Output ricevuto ({len(output)} caratteri)")
            
            output_check = check_output_size(ctx, output)
            if not output_check['allowed']:
                return f"❌ Errore: {output_check['reason']}"

            output_check = check_output_size(ctx, output)
            if not output_check['allowed']:
                return f"❌ Errore: {output_check['reason']}"'''

# Il blocco corretto (tutto indentato, senza duplicati, con l'except finale)
new_block = '''            record_model_call(ctx)
            output = response["message"]["content"]
            
            # Pulisce i backtick di markdown se presenti
            if output.strip().startswith("```"):
                output = output.replace("```json", "").replace("```", "").strip()
                
            print(f"🔍 DEBUG: Output ricevuto ({len(output)} caratteri)")
            
            output_check = check_output_size(ctx, output)
            if not output_check['allowed']:
                return f"❌ Errore: {output_check['reason']}"
                
            return output

        except Exception as e:
            print(f"❌ Errore critico durante la generazione: {e}")
            return f"❌ Errore: {e}"'''

if old_block in code:
    code = code.replace(old_block, new_block)
    with open("icrawler_simple.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("✅ Codice riparato con successo! L'indentazione è a posto e l'except è stato ripristinato.")
else:
    print("⚠️ Blocco non trovato esattamente. Potrebbe esserci uno spazio di troppo. Fammi sapere.")
