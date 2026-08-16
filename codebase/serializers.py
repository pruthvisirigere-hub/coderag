from rest_framework import serializers

from codebase.models import Repository


class AskCodebaseSerializer(serializers.Serializer):
    repository = serializers.CharField(max_length=255)
    question = serializers.CharField()

    def validate_repository(self, value):
        if not Repository.objects.filter(name=value).exists():
            raise serializers.ValidationError(
                "Repository has not been indexed."
            )

        return value


class IngestRepositorySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    github_url = serializers.URLField()