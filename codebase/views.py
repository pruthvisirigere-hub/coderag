from rest_framework.decorators import api_view
from rest_framework.response import Response

from codebase.serializers import (
    AskCodebaseSerializer,
    IngestRepositorySerializer,
)
from codebase.services.github_service import ingest_github_repository
from codebase.services.rag_service import answer_codebase_question


@api_view(["POST"])
def ask_codebase(request):
    serializer = AskCodebaseSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    repository = serializer.validated_data["repository"]
    question = serializer.validated_data["question"]

    answer = answer_codebase_question(
        question=question,
        repository_name=repository,
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

    result = ingest_github_repository(
        name=name,
        github_url=github_url,
    )

    return Response(result)