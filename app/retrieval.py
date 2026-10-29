"""Hybrid semantic search + bounded, parameterized graph expansion."""
from app.core import driver, settings, embeddings

VECTOR = """
CALL db.index.vector.queryNodes('movie_embedding', $k, $embedding)
YIELD node, score
RETURN node.title AS title, score ORDER BY score DESC
"""
# Only known relationship types; depth is validated and interpolated as an integer,
# never taken directly from a generated Cypher string.
def traversal_query(hops: int) -> str:
    if not 1 <= hops <= 4:
        raise ValueError("hops must be between 1 and 4")
    return f"""
    MATCH (start:Movie {{title:$title}})
    MATCH p=(start)-[:ACTED_IN|DIRECTED|IN_GENRE*1..{hops}]-(other)
    WHERE all(n IN nodes(p) WHERE single(x IN nodes(p) WHERE x=n))
    RETURN [n IN nodes(p) | coalesce(n.title,n.name)] AS nodes,
           [r IN relationships(p) | type(r)] AS relations,
           length(p) AS hops
    ORDER BY hops ASC LIMIT $limit
    """

def retrieve(question: str, hops: int = 3, top_k: int = 4, max_paths: int = 30):
    if not 1 <= top_k <= 10:
        raise ValueError("top_k must be between 1 and 10")
    query = traversal_query(hops)
    vector = embeddings().embed_query(question)
    with driver().session(database=settings().neo4j_database) as session:
        seeds = [dict(r) for r in session.run(VECTOR, k=top_k, embedding=vector)]
        paths = []
        for seed in seeds:
            for record in session.run(query, title=seed["title"], limit=max_paths):
                paths.append({"seed": seed["title"], **dict(record)})
    return {"seeds": seeds, "paths": paths}
