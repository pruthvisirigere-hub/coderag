from django.urls import path

from codebase.views import ask_codebase, ingest_repository


urlpatterns = [
    path("ask/", ask_codebase, name="ask_codebase"),
    path("ingest/", ingest_repository, name="ingest_repository"),
]