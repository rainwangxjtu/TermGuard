from termguard.preprocess import align_sentence_pairs


def test_align_sentence_pairs_truncates():
    en = "Hello world. Second sentence."
    zh = "你好世界。第二句。第三句。"
    pairs = align_sentence_pairs(en, zh)
    assert len(pairs) == 2
