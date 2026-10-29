"""Load the public Neo4j movie example and embed movie summaries."""
import argparse
from app.core import driver, settings, embeddings

# Small self-contained graph; extend data/movies.json for larger catalogs.
MOVIES = [
    {"title":"The Matrix","year":1999,"plot":"A hacker discovers reality is a simulation and joins a rebellion.","genres":["Science Fiction","Action"],"directors":["Lana Wachowski","Lilly Wachowski"],"actors":["Keanu Reeves","Carrie-Anne Moss","Laurence Fishburne"]},
    {"title":"John Wick","year":2014,"plot":"A retired assassin returns to the criminal underworld seeking revenge.","genres":["Action","Thriller"],"directors":["Chad Stahelski"],"actors":["Keanu Reeves","Ian McShane"]},
    {"title":"Speed","year":1994,"plot":"A police officer must prevent a bomb from exploding on a moving bus.","genres":["Action","Thriller"],"directors":["Jan de Bont"],"actors":["Keanu Reeves","Sandra Bullock"]},
    {"title":"The Devil's Advocate","year":1997,"plot":"A lawyer discovers his charismatic boss has supernatural secrets.","genres":["Drama","Thriller"],"directors":["Taylor Hackford"],"actors":["Keanu Reeves","Al Pacino"]},
    {"title":"The Godfather","year":1972,"plot":"The aging patriarch of a crime dynasty transfers control to his son.","genres":["Crime","Drama"],"directors":["Francis Ford Coppola"],"actors":["Al Pacino","Marlon Brando"]},
    {"title":"The Dark Knight","year":2008,"plot":"Batman confronts the Joker in Gotham City.","genres":["Action","Crime"],"directors":["Christopher Nolan"],"actors":["Christian Bale","Heath Ledger","Michael Caine"]},
    {"title":"Inception","year":2010,"plot":"A thief enters dreams to steal secrets and plant an idea.","genres":["Science Fiction","Thriller"],"directors":["Christopher Nolan"],"actors":["Leonardo DiCaprio","Michael Caine"]},
    {"title":"Interstellar","year":2014,"plot":"Explorers travel through a wormhole to find a new home for humanity.","genres":["Science Fiction","Drama"],"directors":["Christopher Nolan"],"actors":["Matthew McConaughey","Michael Caine","Anne Hathaway"]},
    {"title":"The Intern","year":2015,"plot":"A senior intern befriends a young founder at a fashion startup.","genres":["Comedy","Drama"],"directors":["Nancy Meyers"],"actors":["Anne Hathaway","Robert De Niro"]},
    {"title":"The Dark Knight Rises","year":2012,"plot":"Batman returns to protect Gotham from a masked revolutionary.","genres":["Action","Crime"],"directors":["Christopher Nolan"],"actors":["Christian Bale","Anne Hathaway","Michael Caine"]},
]

SCHEMA = [
    "CREATE CONSTRAINT movie_title IF NOT EXISTS FOR (m:Movie) REQUIRE m.title IS UNIQUE",
    "CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Person) REQUIRE p.name IS UNIQUE",
    "CREATE CONSTRAINT genre_name IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE",
]
UPSERT = """
MERGE (m:Movie {title:$title})
SET m.year=$year, m.plot=$plot, m.embedding=$embedding
WITH m
UNWIND $actors AS actor
MERGE (p:Person {name:actor})
MERGE (p)-[:ACTED_IN]->(m)
WITH DISTINCT m
UNWIND $directors AS director
MERGE (p:Person {name:director})
MERGE (p)-[:DIRECTED]->(m)
WITH DISTINCT m
UNWIND $genres AS genre
MERGE (g:Genre {name:genre})
MERGE (m)-[:IN_GENRE]->(g)
"""

def seed():
    d, s = driver(), settings()
    with d.session(database=s.neo4j_database) as session:
        for stmt in SCHEMA:
            session.run(stmt).consume()
    vectors = embeddings().embed_documents([f"{m['title']} ({m['year']}): {m['plot']}" for m in MOVIES])
    with d.session(database=s.neo4j_database) as session:
        for movie, vector in zip(MOVIES, vectors):
            session.run(UPSERT, **movie, embedding=vector).consume()
        session.run(
            "CREATE VECTOR INDEX movie_embedding IF NOT EXISTS FOR (m:Movie) ON (m.embedding) "
            "OPTIONS {indexConfig: {`vector.dimensions`: $dim, `vector.similarity_function`: 'cosine'}}",
            dim=len(vectors[0]),
        ).consume()
    print(f"Seeded {len(MOVIES)} movies and their relationships.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.parse_args()
    seed()
