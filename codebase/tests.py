from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APITestCase

from codebase.models import Repository
from codebase.services.reranking_service import rerank_results

from git.exc import GitCommandError


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


class AskCodebaseAPITests(APITestCase):

    def setUp(self):
        Repository.objects.create(
            name="test_repository",
        )

    @patch("codebase.views.answer_codebase_question")
    def test_ask_codebase_returns_answer(self, mock_answer):
        mock_answer.return_value = (
            "The database is configured in config/settings.py."
        )

        response = self.client.post(
            "/api/ask/",
            {
                "repository": "test_repository",
                "question": "Where is the database configured?",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["repository"],
            "test_repository",
        )

        self.assertEqual(
            response.data["question"],
            "Where is the database configured?",
        )

        self.assertEqual(
            response.data["answer"],
            "The database is configured in config/settings.py.",
        )

    def test_ask_codebase_rejects_unknown_repository(self):
        response = self.client.post(
            "/api/ask/",
            {
                "repository": "does_not_exist",
                "question": "Where is the database configured?",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "repository",
            response.data,
        )

    def test_ask_codebase_rejects_missing_question(self):
        response = self.client.post(
            "/api/ask/",
            {
                "repository": "test_repository",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "question",
            response.data,
        )

class IngestRepositoryAPITests(APITestCase):

    @patch("codebase.views.ingest_github_repository")
    def test_ingest_repository_handles_clone_failure(self, mock_ingest):
        mock_ingest.side_effect = GitCommandError(
            "clone",
            128,
        )

        response = self.client.post(
            "/api/ingest/",
            {
                "name": "invalid_repository",
                "github_url": "https://github.com/example/invalid-repository.git",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "error",
            response.data,
        )