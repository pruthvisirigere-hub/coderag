import logging

from git.exc import GitCommandError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from codebase.serializers import (
    AskCodebaseSerializer,
    IngestRepositorySerializer,
)
from codebase.services.github_service import ingest_github_repository
from codebase.services.rag_service import answer_codebase_question


logger = logging.getLogger(__name__)


@api_view(["POST"])
def ask_codebase(request):
    serializer = AskCodebaseSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    repository = serializer.validated_data["repository"]
    question = serializer.validated_data["question"]

    try:
        answer = answer_codebase_question(
            question=question,
            repository_name=repository,
        )

    except Exception:
        logger.exception(
            "Failed to answer question for repository: %s",
            repository,
        )

        return Response(
            {
                "error": "Unable to answer the question at this time."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "repository": repository,
            "question": question,
            "answer": answer,
        }
    )


@api_view(["POST"])
def ingest_repository(request):
    serializer = IngestRepositorySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    name = serializer.validated_data["name"]
    github_url = serializer.validated_data["github_url"]

    try:
        result = ingest_github_repository(
            name=name,
            github_url=github_url,
        )

    except GitCommandError:
        logger.exception(
            "Failed to clone GitHub repository: %s",
            github_url,
        )

        return Response(
            {
                "error": (
                    "Unable to clone the repository. "
                    "Check that the GitHub URL is valid and publicly accessible."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception:
        logger.exception(
            "Failed to ingest repository: %s",
            name,
        )

        return Response(
            {
                "error": "Unable to ingest the repository at this time."
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(result)