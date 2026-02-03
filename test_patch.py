from termguard.patch import patch_zh_text


def test_patch_replaces_alternate():
    zh = "无人飞行器项目提升了校园安全。"
    glossary = {"drone": "无人机"}
    inconsistencies = [{
        "preferred_zh": "无人机",
        "alternates": ["无人飞行器"]
    }]
    patched = patch_zh_text(zh, glossary, inconsistencies)
    assert "无人机项目" in patched
    assert "无人飞行器" not in patched
