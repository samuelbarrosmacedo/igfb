"""Testes da fila histórica, sem dependências externas."""
import unittest

from igfb_agent.source_queue import build_source_queue


class SourceQueueTests(unittest.TestCase):
    def setUp(self):
        self.rules = {"baseline_year": 1971, "through_year": 2025}

    def test_exactly_55_brazilian_editions(self):
        queue = build_source_queue([], self.rules)
        self.assertEqual(len(queue), 55)
        self.assertEqual([s["edition"] for s in queue], list(range(1971, 2026)))

    def test_seed_duplicate_keeps_edition(self):
        url = "https://pt.wikipedia.org/wiki/Campeonato_Brasileiro_de_Futebol_de_1971"
        queue = build_source_queue([{"url": url, "trust": "exploratory", "topic": "brasileirao"}], self.rules)
        self.assertEqual(len(queue), 55)
        self.assertEqual(queue[0]["edition"], 1971)

    def test_other_official_source_is_preserved(self):
        queue = build_source_queue([{"url": "https://www.conmebol.com/libertadores/", "trust": "official"}], self.rules)
        self.assertEqual(len(queue), 56)

    def test_rejects_pre_1971(self):
        with self.assertRaises(ValueError):
            build_source_queue([], {"baseline_year": 1970, "through_year": 2025})

    def test_rejects_2026_as_closed_season(self):
        with self.assertRaises(ValueError):
            build_source_queue([], {"baseline_year": 1971, "through_year": 2026})

    def test_does_not_mutate_seed(self):
        seed = [{"url": "https://pt.wikipedia.org/wiki/Campeonato_Brasileiro_de_Futebol_de_1971"}]
        build_source_queue(seed, self.rules)
        self.assertNotIn("edition", seed[0])


if __name__ == "__main__":
    unittest.main()
