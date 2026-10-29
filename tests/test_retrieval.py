import pytest
from app.retrieval import traversal_query

def test_hops_are_bounded():
    for invalid in (0, 5, -1):
        with pytest.raises(ValueError):
            traversal_query(invalid)

def test_query_uses_fixed_relations_and_parameters():
    q = traversal_query(3)
    assert "*1..3" in q
    assert "$title" in q
    assert "$limit" in q
    assert "ACTED_IN|DIRECTED|IN_GENRE" in q
