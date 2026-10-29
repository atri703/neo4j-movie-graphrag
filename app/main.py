from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.service import answer

app = FastAPI(title="Neo4j Movie GraphRAG", version="0.1.0")

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    hops: int = Field(default=3, ge=1, le=4)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(request: AskRequest):
    try:
        return answer(request.question, hops=request.hops)
    except Exception as exc:
        # Avoid exposing provider errors, secrets or connection strings.
        raise HTTPException(status_code=503, detail="Retrieval service unavailable") from exc
