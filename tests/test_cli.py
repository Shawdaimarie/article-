import json

from click.testing import CliRunner

from article.cli import main


def write_minimal_passing_project(tmp_path):
    (tmp_path / "README.md").write_text(
        "# Demo\n\n" + ("x" * 300) + "\n\n## Usage\n\nRun it.\n", encoding="utf-8"
    )
    (tmp_path / "LICENSE").write_text("MIT License", encoding="utf-8")
    (tmp_path / "SECURITY.md").write_text("Report issues to security@example.com", encoding="utf-8")
    (tmp_path / "CODE_OF_CONDUCT.md").write_text("Be kind.", encoding="utf-8")
    (tmp_path / "CONTRIBUTING.md").write_text("PRs welcome.", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("## [1.0.0] - 2026-01-01\n\nInitial release.\n", encoding="utf-8")
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_demo.py").write_text("def test_ok(): assert True\n", encoding="utf-8")
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text("name: CI\n", encoding="utf-8")


def test_check_exits_zero_on_high_score(tmp_path):
    write_minimal_passing_project(tmp_path)
    result = CliRunner().invoke(main, ["check", str(tmp_path), "--min-score", "90"])
    assert result.exit_code == 0, result.output


def test_check_exits_nonzero_below_threshold(tmp_path):
    result = CliRunner().invoke(main, ["check", str(tmp_path), "--min-score", "50"])
    assert result.exit_code == 1


def test_check_json_output_is_valid(tmp_path):
    write_minimal_passing_project(tmp_path)
    result = CliRunner().invoke(main, ["check", str(tmp_path), "--json"])
    payload = json.loads(result.output)
    assert payload["score"] == 100.0
    assert len(payload["results"]) == 10


def test_principles_command_lists_all_ten():
    result = CliRunner().invoke(main, ["principles"])
    assert result.exit_code == 0
    for principle_id in (
        "transparency", "licensing_hygiene", "security_by_default", "privacy_and_data_respect",
        "human_oversight_for_ai", "accessibility", "testing_and_maintainability",
        "inclusive_community", "dependency_integrity", "sustainability_longevity",
    ):
        assert principle_id in result.output
