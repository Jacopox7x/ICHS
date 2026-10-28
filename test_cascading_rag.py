"""Test di regressione per cascading_rag, senza servizi esterni."""

import unittest
from unittest.mock import patch

import cascading_rag


class FakeMemory:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def find_similar(self, query, cliente=None):
        self.calls.append((query, cliente))
        return self.results


class TestCascadingRAG(unittest.TestCase):
    def setUp(self):
        self.web_results = [
            {
                "testo": "Risultato web simulato",
                "url": "https://example.invalid/test",
            }
        ]

    def test_query_vuota_non_interroga_i_servizi(self):
        memory = FakeMemory([])

        with patch.object(
            cascading_rag, "_search_web"
        ) as web, patch.object(
            cascading_rag, "_enrich_query_with_gliner"
        ) as gliner:
            result = cascading_rag.retrieve_context(
                "   ", memory_module=memory
            )

        self.assertEqual(result["fonte"], "nessuna")
        self.assertEqual(result["risultati"], [])
        self.assertEqual(result["percorso"], "query_vuota")
        memory_calls = memory.calls
        self.assertEqual(memory_calls, [])
        web.assert_not_called()
        gliner.assert_not_called()

    def test_risultato_sopra_soglia_evoca_memoria_locale(self):
        memory = FakeMemory([
            ("Laboratorio di sartoria", "Piano pertinente", 0.81),
        ])

        with patch.object(
            cascading_rag, "_search_web"
        ) as web, patch.object(
            cascading_rag, "_enrich_query_with_gliner"
        ) as gliner:
            result = cascading_rag.retrieve_context(
                "laboratorio sartoria",
                cliente="cosper",
                memory_module=memory,
            )

        self.assertEqual(result["fonte"], "locale")
        self.assertEqual(result["percorso"], "soglia_locale_superata")
        self.assertEqual(len(result["risultati"]), 1)
        self.assertEqual(result["risultati"][0]["testo"], "Piano pertinente")
        web.assert_not_called()
        gliner.assert_not_called()

    def test_risultati_sotto_soglia_attivano_fallback_web(self):
        memory = FakeMemory([
            ("Evento generico", "Piano poco pertinente", 0.55),
        ])

        with patch.object(
            cascading_rag, "_search_web", return_value=self.web_results
        ) as web, patch.object(
            cascading_rag, "_enrich_query_with_gliner",
            return_value="query arricchita",
        ):
            result = cascading_rag.retrieve_context(
                "evento sartoria",
                cliente="cosper",
                memory_module=memory,
            )

        self.assertEqual(result["fonte"], "web")
        self.assertEqual(result["percorso"], "fallback_web")
        self.assertEqual(result["risultati"], self.web_results)
        web.assert_called_once()
        
    def test_risultati_sotto_soglia_senza_web_conservano_memoria(self):
        memory = FakeMemory([
            ("Evento generico", "Piano indicativo", 0.55),
        ])

        with patch.object(
            cascading_rag, "_search_web", return_value=[]
        ), patch.object(
            cascading_rag, "_enrich_query_with_gliner",
            return_value="query arricchita",
        ):
            result = cascading_rag.retrieve_context(
                "evento sartoria",
                memory_module=memory,
            )

        self.assertEqual(result["fonte"], "locale")
        self.assertEqual(
            result["percorso"], "soglia_locale_non_superata"
        )
        self.assertEqual(result["risultati"][0]["testo"], "Piano indicativo")

    def test_nessun_risultato_locale_o_web(self):
        memory = FakeMemory([])

        with patch.object(
            cascading_rag, "_search_web", return_value=[]
        ), patch.object(
            cascading_rag, "_enrich_query_with_gliner",
            return_value="query arricchita",
        ):
            result = cascading_rag.retrieve_context(
                "brief senza risultati",
                memory_module=memory,
            )

        self.assertEqual(result["fonte"], "nessuna")
        self.assertEqual(result["risultati"], [])
        self.assertEqual(result["percorso"], "nessun_risultato")

    def test_risultato_sopra_soglia_non_dovrebbe_includere_quello_sotto(self):
        memory = FakeMemory([
            ("Brief A", "Piano pertinente", 0.83),
            ("Brief B", "Piano non pertinente", 0.41),
        ])

        with patch.object(
            cascading_rag, "_search_web"
        ) as web:
            result = cascading_rag.retrieve_context(
                "brief A",
                memory_module=memory,
            )

        testi = [item["testo"] for item in result["risultati"]]

        # Questo è il comportamento desiderato.
        # Con l'implementazione attuale il test dovrebbe fallire.
        self.assertEqual(testi, ["Piano pertinente"])
        web.assert_not_called()

    def test_risultati_locali_duplicati_non_dovrebbero_ripetersi(self):
        memory = FakeMemory([
            ("Brief A", "Stesso piano", 0.84),
            ("Brief A copia", "Stesso piano", 0.79),
        ])

        with patch.object(
            cascading_rag, "_search_web"
        ):
            result = cascading_rag.retrieve_context(
                "brief A",
                memory_module=memory,
            )

        testi = [item["testo"] for item in result["risultati"]]

        # Questo è il comportamento desiderato.
        # Con l'implementazione attuale il test dovrebbe fallire.
        self.assertEqual(testi, ["Stesso piano"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
