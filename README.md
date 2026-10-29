# Neo4j Movie GraphRAG

Hybrid **multi-hop movie question answering** using Python, LangChain, Neo4j and OpenAI.

## How it works

1. Seed a movie knowledge graph with Movie, Person, and Genre nodes, and ACTED_IN, DIRECTED, IN_GENRE edges.
2. Embed movie title/year/plot using OpenAI `text-embedding-3-small` and store vectors on Movie nodes.
3. Retrieve semantically relevant movies via a Neo4j vector index.
4. Expand each seed through **1–4 hops** of graph relationships using parameterized, bounded Cypher.
5. Give the retrieved paths to an OpenAI chat model to produce a grounded answer and return the evidence.

This is **actual graph traversal**, not just vector similarity. It deliberately does not let the LLM execute arbitrary Cypher.

## Quick start

Requires Python 3.11+, Docker, and an OpenAI API key.

```bash
cp .env.example .env
# Set OPENAI_API_KEY in .env; change Neo4j password in both .env and compose for real use
docker compose up -d
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.seed
uvicorn app.main:app --reload
```

Windows activation: `.venv\\Scripts\\activate`.

API documentation: http://localhost:8000/docs. Neo4j browser: http://localhost:7474.

```bash
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" \
  -d '{"question":"Which movies connect Keanu Reeves to Al Pacino?","hops":4}'
```

Other example questions:
- Which science fiction movies feature actors who also appeared in Batman movies?
- How is Anne Hathaway connected to Christopher Nolan?
- Find thriller movies involving people connected to The Matrix.

The bundled dataset is a **small, curated demo** (10 movies), not a complete movie catalog. Answers are limited to loaded data and retrieved paths. Re-run `python -m app.seed` to upsert; embeddings will be recalculated and billed.

## Layout

- `app/core.py`: configuration, Neo4j driver and OpenAI clients
- `app/seed.py`: sample movie data, constraints, vectors and indexes
- `app/retrieval.py`: vector retrieval and safe bounded graph traversal
- `app/service.py`: LangChain answer chain with evidence
- `app/main.py`: FastAPI API
- `tests/`: unit tests
- `.github/workflows/ci.yml`: automated tests

## Notes

The example uses Neo4j 5.26, which supports native vector indexes. Neo4j Aura can replace the local database via `NEO4J_URI` and credentials. Seed scripts assume the database is writable. The graph query intentionally restricts path depth and relationship types; it is not an unrestricted text-to-Cypher agent. For production, add authentication, rate limits, observability, dataset provenance, evaluation sets, and database least-privilege credentials.

## Documentation

- [Neo4j Cypher manual](https://neo4j.com/docs/cypher-manual/current/)
- [Neo4j vector indexes](https://neo4j.com/docs/cypher-manual/current/indexes/semantic-indexes/vector-indexes/)
- [LangChain Neo4j integration](https://python.langchain.com/docs/integrations/vectorstores/neo4jvector/)
