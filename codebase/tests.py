from django.test import SimpleTestCase

from codebase.services.reranking_service import rerank_results


class RerankingServiceTests(SimpleTestCase):

    def test_exact_function_match_is_ranked_first(self):
        results = [
            {
                "file_path": "config/wsgi.py",
                "symbol_name": None,
                "symbol_type": "text",
                "distance": 0.70,
            },
            {
                "file_path": "manage.py",
                "symbol_name": "main",
                "symbol_type": "FunctionDef",
                "distance": 0.85,
            },
        ]

        reranked = rerank_results(
            "Where is the main function defined?",
            results,
        )

        self.assertEqual(
            reranked[0]["symbol_name"],
            "main",
        )

    def test_test_file_is_ranked_first_for_test_question(self):
        results = [
            {
                "file_path": "src/sample/simple.py",
                "symbol_name": "add_one",
                "symbol_type": "FunctionDef",
                "distance": 0.60,
            },
            {
                "file_path": "tests/test_simple.py",
                "symbol_name": "test_add_one",
                "symbol_type": "FunctionDef",
                "distance": 0.75,
            },
        ]

        reranked = rerank_results(
            "Where are the tests for add_one?",
            results,
        )

        self.assertEqual(
            reranked[0]["file_path"],
            "tests/test_simple.py",
        )