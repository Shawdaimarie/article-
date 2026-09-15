from pathlib import Path

from article.engine import load_charter, run

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_charter_loads_and_has_ten_principles():
    charter = load_charter()
    assert charter["name"]
    assert len(charter["principles"]) == 10
    for p in charter["principles"]:
        assert {"id", "title", "statement", "check"} <= p.keys()


def test_repo_and_packaged_charter_copies_stay_in_sync():
    top_level = (REPO_ROOT / "principles" / "article.yaml").read_text(encoding="utf-8")
    packaged = (REPO_ROOT / "src" / "article" / "data" / "article.yaml").read_text(encoding="utf-8")
    assert top_level == packaged, "principles/article.yaml and src/article/data/article.yaml have drifted apart"


def test_run_on_this_repo_scores_perfectly():
    result = run(REPO_ROOT)
    failures = [(r.id, r.message) for r in result.results if r.status == "fail"]
    assert failures == [], f"Article fails its own charter: {failures}"
    assert result.score == 100.0


def test_run_on_empty_directory_scores_zero(tmp_path):
    result = run(tmp_path)
    assert result.score == 0.0
    assert result.failed > 0
