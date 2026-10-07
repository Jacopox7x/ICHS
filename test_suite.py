#!/usr/bin/env python3
import subprocess
from pathlib import Path

def main():
    print("🧪 iCRAWLER TEST SUITE")
    print("=" * 40)
    tests = list(Path("tests").glob("brief*.txt"))
    for test in tests:
        print(f"\n📝 {test.name}...")
        result = subprocess.run(
            ["python3", "test_interactive_v18_hybrid.py", str(test)],
            capture_output=True,
            text=True,
            timeout=60
        )
        if "PIANO COMPLETO" in result.stdout:
            print("  ✅ PASSATO")
        else:
            print("  ❌ FALLITO")
    print("\n🏁 TEST COMPLETATO")

if __name__ == "__main__":
    main()
