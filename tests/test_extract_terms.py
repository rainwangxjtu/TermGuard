from termguard.extract_terms import extract_en_terms


def test_extract_en_terms_contains_drone():
    sents = [
        "The drone program improves campus security.",
        "The police department uses drones to monitor events."
    ]
    terms = extract_en_terms(sents, top_k=20)
    term_list = [t for t, _ in terms]
    assert any("drone" in t for t in term_list)
