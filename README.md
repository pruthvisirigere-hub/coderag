# CodeRAG

**CodeRAG** is an AI-powered codebase assistant that uses **Retrieval-Augmented Generation (RAG)** to help developers understand software repositories through natural-language questions.

The application can ingest a public GitHub repository, analyze Python source code and Markdown documentation, generate embeddings, store them in **PostgreSQL with pgvector**, retrieve relevant repository context using semantic search and metadata-aware reranking, and generate grounded answers using a Large Language Model.

---

## Core Technologies

- Python
- Django
- Django REST Framework
- PostgreSQL
- pgvector
- Sentence Transformers
- OpenRouter
- Large Language Models
- GitPython
- Retrieval-Augmented Generation (RAG)
- Docker

---

## Features

- Ingest public GitHub repositories through a REST API
- Automatically clone repositories using GitPython
- Process Python `.py` files
- Process Markdown `.md` documentation
- Parse Python code using Python's Abstract Syntax Tree (AST)
- Create function- and class-aware Python code chunks
- Use heading-aware chunking for Markdown documentation
- Generate 384-dimensional embeddings using Sentence Transformers
- Store embeddings in PostgreSQL using pgvector
- Perform semantic similarity search using cosine distance
- Use metadata-aware reranking for functions, classes, and test files
- Generate grounded repository answers using an LLM through OpenRouter
- Return relevant source file paths and line numbers when available
- Validate API requests using Django REST Framework serializers
- Handle GitHub ingestion and RAG failures with controlled API responses
- Evaluate retrieval using Top-1 and Top-5 accuracy
- Automated tests for reranking and API behavior
- Docker support for containerized execution

---

## Architecture

```text
GitHub Repository
        ↓
GitPython Clone
        ↓
Repository Loader
        ↓
Python (.py) + Markdown (.md) Files
        ↓
        ├── Python → AST-Aware Chunking
        │
        └── Markdown → Heading-Aware Chunking
        ↓
Sentence Transformer Embeddings
        ↓
PostgreSQL + pgvector
        ↓
Semantic Vector Retrieval
        ↓
Metadata-Aware Reranking
        ↓
RAG Context Builder
        ↓
OpenRouter LLM
        ↓
Grounded Answer + Source References
```

CodeRAG exposes two main REST API endpoints:

- `POST /api/ingest/` — clones and indexes a GitHub repository
- `POST /api/ask/` — answers natural-language questions about an indexed repository

---

# API Usage

## 1. Ingest a GitHub Repository

### Endpoint

```text
POST /api/ingest/
```

### Example Request

```json
{
  "name": "sampleproject",
  "github_url": "https://github.com/pypa/sampleproject.git"
}
```

### Example Response

```json
{
  "repository": "sampleproject",
  "files_processed": 5,
  "chunks_created": 7,
  "embeddings_created": 7
}
```

The ingestion pipeline performs:

```text
GitHub URL
    ↓
Clone Repository
    ↓
Load Supported Files
    ↓
Chunk Repository Content
    ↓
Generate Embeddings
    ↓
Store in PostgreSQL + pgvector
```

---

## 2. Ask a Codebase Question

### Endpoint

```text
POST /api/ask/
```

### Example Request

```json
{
  "repository": "sampleproject",
  "question": "Where is the add_one function defined?"
}
```

### Example Response

```json
{
  "repository": "sampleproject",
  "question": "Where is the add_one function defined?",
  "answer": "The add_one function is defined in src/sample/simple.py, lines 1-2."
}
```

CodeRAG retrieves relevant repository chunks and passes the retrieved context to the LLM to generate a grounded answer.

---

# Local Setup

## 1. Clone the Repository

```bash
git clone https://github.com/pruthvisirigere-hub/coderag.git
cd coderag
```

---

## 2. Create and Activate a Virtual Environment

Create the virtual environment:

```bash
py -m venv .venv
```

On Windows:

```bash
.\.venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file using `.env.example` as a reference.

Required variables include:

```env
DJANGO_SECRET_KEY=your_django_secret_key

DB_NAME=coderag_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432

OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openrouter/free
```

Do not commit your real `.env` file or API credentials to GitHub.

---

## 5. PostgreSQL and pgvector

CodeRAG requires PostgreSQL with the `pgvector` extension available.

The Django migration enables the PostgreSQL vector extension before creating the pgvector-backed embedding field.

The embedding column stores:

```text
vector(384)
```

because CodeRAG currently uses a Sentence Transformer model that produces 384-dimensional embeddings.

---

## 6. Apply Django Migrations

```bash
python manage.py migrate
```

---

## 7. Start the Development Server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

Available endpoints:

```text
POST http://127.0.0.1:8000/api/ingest/
POST http://127.0.0.1:8000/api/ask/
```

---

# Docker Setup

CodeRAG can also be run inside Docker.

## Build the Docker Image

From the project directory:

```bash
docker build -t coderag .
```

This creates a Docker image named:

```text
coderag
```

---

## Run the Docker Container

CodeRAG currently uses PostgreSQL running on the host machine.

When running Django inside Docker on Windows, use `host.docker.internal` so the container can communicate with PostgreSQL running on the Windows host.

```bash
docker run --rm -p 8000:8000 --env-file .env -e DB_HOST=host.docker.internal coderag
```

The API will then be available at:

```text
http://127.0.0.1:8000/
```

Available endpoints:

```text
POST /api/ingest/
POST /api/ask/
```

The Dockerized application runs the complete CodeRAG pipeline:

```text
GitHub Repository
        ↓
Repository Ingestion
        ↓
Python / Markdown Processing
        ↓
Code-Aware or Text Chunking
        ↓
Sentence Transformer Embeddings
        ↓
PostgreSQL + pgvector
        ↓
Vector Retrieval
        ↓
Metadata-Aware Reranking
        ↓
OpenRouter LLM
        ↓
Grounded Answer with Source References
```

---

# Repository File Support

CodeRAG currently indexes:

| File Type | Extension | Processing |
|---|---|---|
| Python | `.py` | AST-aware code chunking |
| Markdown | `.md` | Heading-aware documentation chunking |

Python files are parsed using Python's `ast` module so functions and classes can be represented as meaningful chunks.

Markdown files such as `README.md` are indexed as documentation and can also be retrieved by the RAG pipeline.

For example:

```text
Question:
According to the README, how do I run CodeRAG using Docker?

Retrieved source:
README.md
```

---

# Retrieval and Reranking

CodeRAG first converts the user's question into an embedding using Sentence Transformers.

The query embedding is compared against stored repository embeddings using pgvector cosine distance.

```text
User Question
      ↓
Query Embedding
      ↓
pgvector Cosine Similarity Search
      ↓
Candidate Chunks
      ↓
Metadata-Aware Reranking
      ↓
Top Relevant Chunks
```

The reranking layer can give additional importance to repository metadata.

Examples include:

- Exact function-name matches
- Function-related questions
- Class-related questions
- Test-related questions
- Files located in test paths

This allows CodeRAG to combine:

```text
Semantic Similarity
        +
Repository Metadata
        =
Improved Retrieval
```

---

# Code-Aware Chunking

Python source code is parsed using Python's Abstract Syntax Tree.

Instead of only splitting files by arbitrary line counts, CodeRAG can identify structures such as:

```text
FunctionDef
AsyncFunctionDef
ClassDef
```

Each Python chunk can store metadata including:

```text
symbol_name
symbol_type
start_line
end_line
```

For example:

```text
File:
src/sample/simple.py

Symbol:
add_one

Type:
FunctionDef

Lines:
1-2
```

If AST parsing cannot be used, CodeRAG falls back to normal text chunking.

Markdown documentation uses heading-aware chunking so related documentation sections remain together during retrieval.

---

# Embeddings

CodeRAG uses:

```text
sentence-transformers/all-MiniLM-L6-v2
```

to generate embeddings.

Each embedding contains:

```text
384 dimensions
```

The embeddings are stored directly in PostgreSQL using:

```text
pgvector
```

This allows semantic similarity searches to be performed directly through the database.

---

# RAG Answer Generation

After retrieval and reranking, CodeRAG builds a context containing information such as:

```text
File
Symbol
Symbol Type
Line Numbers
Chunk
Repository Content
```

The context is sent to an LLM through OpenRouter.

The LLM is instructed to:

- Answer using only retrieved repository context
- Mention exact file paths
- Mention line numbers when available
- Avoid inventing files, symbols, or functionality
- State when there is insufficient information
- Include source references

This helps reduce hallucination and keeps answers grounded in the indexed repository.

---

# Error Handling

CodeRAG returns controlled API errors instead of exposing raw application errors to API users.

Examples include:

### Repository Clone Failure

If a GitHub repository cannot be cloned:

```json
{
  "error": "Unable to clone the repository. Check that the GitHub URL is valid and publicly accessible."
}
```

### RAG Processing Failure

If an unexpected error occurs while answering a question:

```json
{
  "error": "Unable to answer the question at this time."
}
```

Detailed exceptions are still logged on the server for debugging.

---

# Retrieval Evaluation

CodeRAG includes a small retrieval evaluation pipeline that measures whether the correct source file is retrieved for a given question.

Current metrics include:

- Top-1 Accuracy
- Top-5 Accuracy
- Retrieval Rank

Example evaluation case:

```text
Question:
Where is the add_one function defined?

Expected file:
src/sample/simple.py

Retrieved rank:
1
```

On the current small evaluation dataset, CodeRAG achieved:

```text
Top-1 Accuracy: 100%
Top-5 Accuracy: 100%
```

These results apply only to the current small evaluation dataset and should not be interpreted as a general benchmark of retrieval performance.

---

# Testing

CodeRAG includes automated tests for reranking, request validation, API responses, and error handling.

Run the test suite with:

```bash
python manage.py test codebase
```

Current automated test coverage includes:

1. Exact function-name reranking
2. Test-file reranking for test-related questions
3. Successful `/api/ask/` response behavior
4. Unknown repository validation
5. Missing question validation
6. Internal RAG failure handling
7. GitHub repository clone failure handling

Current test result:

```text
Ran 7 tests
OK
```

During testing, Django automatically creates a temporary PostgreSQL test database.

The pgvector Django migration enables the `vector` extension before the `CodeChunk` model containing the vector field is created.

The temporary database is destroyed automatically after the tests finish.

---

# Project Structure

```text
coderag/
│
├── codebase/
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_sourcefile.py
│   │   ├── 0003_codechunk.py
│   │   └── 0004_codechunk_end_line_codechunk_start_line_and_more.py
│   │
│   ├── services/
│   │   ├── chunking_service.py
│   │   ├── code_chunker.py
│   │   ├── embedding_service.py
│   │   ├── evaluation_service.py
│   │   ├── github_service.py
│   │   ├── ingestion_service.py
│   │   ├── llm_service.py
│   │   ├── python_parser.py
│   │   ├── rag_service.py
│   │   ├── repository_loader.py
│   │   ├── reranking_service.py
│   │   └── retrieval_service.py
│   │
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── evaluation/
│   └── evaluation_cases.py
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── manage.py
├── requirements.txt
└── README.md
```

---

# Current CodeRAG Workflow

```text
User provides GitHub repository
            ↓
POST /api/ingest/
            ↓
GitPython clones repository
            ↓
.py and .md files discovered
            ↓
Python AST / Markdown text chunking
            ↓
Sentence Transformer embeddings
            ↓
PostgreSQL + pgvector storage
            ↓
User asks repository question
            ↓
POST /api/ask/
            ↓
Question embedding
            ↓
Semantic vector retrieval
            ↓
Metadata-aware reranking
            ↓
RAG context construction
            ↓
OpenRouter LLM
            ↓
Grounded answer + sources
```

---

# Purpose

CodeRAG was built as a practical RAG engineering project demonstrating how modern AI applications can combine:

- Backend API development
- GitHub repository ingestion
- Source-code parsing
- Document ingestion
- Embeddings
- Vector databases
- Semantic retrieval
- Reranking
- Retrieval-Augmented Generation
- LLM integration
- Evaluation
- Automated testing
- Error handling
- Docker containerization

The project demonstrates an end-to-end implementation of a repository-aware AI assistant rather than only a standalone LLM prompt.