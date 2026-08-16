from django.db import models
from pgvector.django import VectorField


class Repository(models.Model):
    name = models.CharField(max_length=255)
    github_url = models.URLField(blank=True, null=True)
    local_path = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SourceFile(models.Model):
    repository = models.ForeignKey(
        Repository,
        on_delete=models.CASCADE,
        related_name="source_files",
    )
    file_path = models.CharField(max_length=1000)
    language = models.CharField(max_length=50, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_path

class CodeChunk(models.Model):
    source_file = models.ForeignKey(
        SourceFile,
        on_delete=models.CASCADE,
        related_name="chunks",
    )
    content = models.TextField()
    chunk_index = models.PositiveIntegerField()
    embedding = VectorField(dimensions=384, null=True, blank=True)

    def __str__(self):
        return f"{self.source_file.file_path} - chunk {self.chunk_index}"