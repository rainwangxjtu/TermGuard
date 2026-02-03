from termguard.consistency import detect_inconsistencies


def test_detect_inconsistency_entropy():
    mappings = {
        "drone": [("无人机", 1.0, 3), ("无人飞行器", 0.8, 3)]
    }
    flags = detect_inconsistencies(mappings, glossary={"drone": "无人机"}, min_total_occurrences=2, entropy_threshold=0.1)
    assert len(flags) == 1
    assert flags[0]["preferred_zh"] == "无人机"
