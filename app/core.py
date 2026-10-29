"""Configuration and shared database/LLM clients."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    openai_api_key: str
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str
    neo4j_database: str = "neo4j"
    max_hops: int = 4

@lru_cache
def settings() -> Settings:
    return Settings()

@lru_cache
def driver():
    s = settings()
    return GraphDatabase.driver(s.neo4j_uri, auth=(s.neo4j_username, s.neo4j_password))

@lru_cache
def llm():
    s = settings()
    return ChatOpenAI(model=s.openai_chat_model, temperature=0)

@lru_cache
def embeddings():
    return OpenAIEmbeddings(model=settings().openai_embedding_model)
