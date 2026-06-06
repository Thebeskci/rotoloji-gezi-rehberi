from rota_yz.text_utils import build_place_prompt, normalize_text, slugify


def test_slugify_removes_accents_and_spaces() -> None:
    assert slugify("Topkapi Sarayi") == "topkapi-sarayi"
    assert slugify("Pantheon, Roma") == "pantheon-roma"


def test_normalize_text_collapses_whitespace() -> None:
    assert normalize_text("A  \n  B\tC") == "A B C"


def test_build_place_prompt_contains_context() -> None:
    prompt = build_place_prompt("Istanbul", "Ayasofya", "Tarih", "Turkiye")
    assert "Ayasofya" in prompt
    assert "Istanbul" in prompt
