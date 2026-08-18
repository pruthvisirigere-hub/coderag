# CodeRAG

**CodeRAG** is an AI-powered codebase assistant that uses **Retrieval-Augmented Generation (RAG)** to help developers understand software repositories through natural-language questions.

The application can ingest a GitHub repository, analyze its Python source code, generate embeddings, store them in **PostgreSQL with pgvector**, retrieve relevant code using semantic search, and generate grounded answers using a Large Language Model.

## Core Technologies

* Python
* Django
* Django REST Framework
* PostgreSQL
* pgvector
* Sentence Transformers
* OpenRouter
* Large Language Models
* GitPython
* Retrieval-Augmented Generation (RAG)

## Features

* Ingest public GitHub repositories through a REST API
* Automatically clone and process repository source files
* Parse Python code using Python's Abstract Syntax Tree (AST)
* Create function- and class-aware code chunks
* Generate 384-dimensional code embeddings using Sentence Transformers
* Store embeddings in PostgreSQL using pgvector
* Perform semantic similarity search with cosine distance
* Use metadata-aware reranking for functions, classes, and test files
* Generate grounded codebase answers using an LLM through OpenRouter
* Return relevant file paths and line numbers with answers
* Validate API requests using Django REST Framework serializers
* Evaluate retrieval using Top-1 and Top-5 accuracy
* Automated tests for retrieval reranking behavior

## Architecture

```text
GitHub Repository
        ↓
GitPython Clone
        ↓
Repository Loader
        ↓
Source Files
        ↓
Python AST Parser
        ↓
Code-Aware Chunking
        ↓
Sentence Transformer Embeddings
        ↓
PostgreSQL + pgvector
        ↓
Semantic Retrieval
        ↓
Metadata-Aware Reranking
        ↓
RAG Context Builder
        ↓
OpenRouter LLM
        ↓
Grounded Answer + Source Files + Line Numbers
```

The application exposes two main REST API endpoints:

* `POST /api/ingest/` — clones and indexes a GitHub repository
* `POST /api/ask/` — answers natural-language questions about an indexed repository

## API Usage

### 1. Ingest a GitHub Repository

**Endpoint**

```text
POST /api/ingest/
```

**Example Request**

```json
{
  "name": "sampleproject",
  "github_url": "https://github.com/pypa/sampleproject.git"
}
```

**Example Response**

```json
{
  "repository": "sampleproject",
  "files_processed": 5,
  "chunks_created": 7,
  "embeddings_created": 7
}
```

### 2. Ask a Codebase Question

**Endpoint**

```text
POST /api/ask/
```

**Example Request**

```json
{
  "repository": "sampleproject",
  "question": "Where is the add_one function defined?"
}
```

**Example Response**

```json
{
  "repository": "sampleproject",
  "question": "Where is the add_one function defined?",
  "answer": "The add_one function is defined in src/sample/simple.py, lines 1-2."
}
```
## Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/pruthvisirigere-hub/coderag.git
cd coderag
```

### 2. Create and Activate a Virtual Environment

```bash
py -m venv .venv
```

On Windows:

```bash
.\.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

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

### 5. Apply Django Migrations

```bash
python manage.py migrate
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

> PostgreSQL and the pgvector extension must already be installed and configured before running the application.

## Docker Setup

CodeRAG can also be run inside Docker.

### Build the Docker image

```bash
docker build -t coderag .

## Retrieval Evaluation

CodeRAG includes a small retrieval evaluation pipeline to measure whether the correct source file is being retrieved for a given question.

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

## Testing

CodeRAG includes automated tests for important retrieval and reranking behavior.

Run the test suite with:

```bash
python manage.py test codebase

## Project Structure

```text
coderag/
├── codebase/
│   ├── migrations/
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
├── .env.example
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md