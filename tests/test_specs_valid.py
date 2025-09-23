from pathlib import Path
from shinigami.models import list_specs

SPECS_DIR = Path(__file__).parent.parent / "shinigami" / "specs"


def test_all_specs_load():
    specs = list_specs(SPECS_DIR)
    assert len(specs) == 32  # 33 minus Shinigami itself


def test_all_specs_have_required_fields():
    specs = list_specs(SPECS_DIR)
    for spec in specs:
        assert spec.name, "Missing name"
        assert spec.display_name, f"Missing display_name for {spec.name}"
        assert spec.category in ("real-world", "trading", "agentic"), f"Bad category for {spec.name}"
        assert spec.stack.language, f"Missing language for {spec.name}"
        assert spec.stack.framework, f"Missing framework for {spec.name}"
        assert spec.stack.database, f"Missing database for {spec.name}"
        assert len(spec.models) >= 1, f"No models for {spec.name}"
        assert len(spec.api_routes) >= 1, f"No routes for {spec.name}"


def test_categories_have_correct_counts():
    specs = list_specs(SPECS_DIR)
    cats: dict[str, int] = {}
    for s in specs:
        cats[s.category] = cats.get(s.category, 0) + 1
    assert cats["real-world"] == 11
    assert cats["trading"] == 12
    assert cats["agentic"] == 9  # 10 minus Shinigami
