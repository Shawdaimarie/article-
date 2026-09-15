from pathlib import Path

from article import checks


def write(path: Path, content: str = ""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# --- transparency -----------------------------------------------------

def test_transparency_fails_without_readme(tmp_path):
    assert checks.transparency(tmp_path).status == "fail"


def test_transparency_fails_when_readme_too_short(tmp_path):
    write(tmp_path / "README.md", "hello")
    assert checks.transparency(tmp_path).status == "fail"


def test_transparency_passes_with_usage_section(tmp_path):
    write(tmp_path / "README.md", "# My Project\n\n" + ("A" * 300) + "\n\n## Usage\n\nRun it.\n")
    assert checks.transparency(tmp_path).status == "pass"


# --- licensing_hygiene --------------------------------------------------

def test_licensing_fails_without_license(tmp_path):
    assert checks.licensing_hygiene(tmp_path).status == "fail"


def test_licensing_passes_with_mit(tmp_path):
    write(tmp_path / "LICENSE", "MIT License\n\nPermission is hereby granted...")
    assert checks.licensing_hygiene(tmp_path).status == "pass"


# --- security_by_default -------------------------------------------------

def test_security_fails_on_hardcoded_secret(tmp_path):
    write(tmp_path / "SECURITY.md", "Report vulnerabilities to security@example.com")
    fake_key = "AKIA" + "1234567890ABCDEF"  # built at runtime so it never appears literally in this source file
    write(tmp_path / "config.py", f'aws_key = "{fake_key}"\n')
    assert checks.security_by_default(tmp_path).status == "fail"


def test_security_fails_without_security_md(tmp_path):
    write(tmp_path / "app.py", "print('hello world')\n")
    assert checks.security_by_default(tmp_path).status == "fail"


def test_security_passes_when_clean(tmp_path):
    write(tmp_path / "SECURITY.md", "Report vulnerabilities to security@example.com")
    write(tmp_path / "app.py", "print('hello world')\n")
    assert checks.security_by_default(tmp_path).status == "pass"


# --- privacy_and_data_respect --------------------------------------------

def test_privacy_skips_when_no_indicators(tmp_path):
    write(tmp_path / "app.py", "print('hello')\n")
    assert checks.privacy_and_data_respect(tmp_path).status == "skip"


def test_privacy_fails_when_indicator_without_policy(tmp_path):
    write(tmp_path / "app.py", "# this module collects personal data for analytics\n")
    assert checks.privacy_and_data_respect(tmp_path).status == "fail"


def test_privacy_passes_with_policy(tmp_path):
    write(tmp_path / "app.py", "# this module collects personal data for analytics\n")
    write(tmp_path / "PRIVACY.md", "We collect an email address to send receipts.")
    assert checks.privacy_and_data_respect(tmp_path).status == "pass"


# --- human_oversight_for_ai ------------------------------------------------

def test_ai_oversight_skips_without_ai_indicators(tmp_path):
    write(tmp_path / "README.md", "A simple calculator app.")
    assert checks.human_oversight_for_ai(tmp_path).status == "skip"


def test_ai_oversight_fails_without_disclosure(tmp_path):
    write(tmp_path / "README.md", "This project uses a large language model to draft replies.")
    assert checks.human_oversight_for_ai(tmp_path).status == "fail"


def test_ai_oversight_passes_with_disclosure(tmp_path):
    write(
        tmp_path / "README.md",
        "This project uses a large language model to draft replies. "
        "All drafts require human review before sending.",
    )
    assert checks.human_oversight_for_ai(tmp_path).status == "pass"


# --- accessibility -----------------------------------------------------

def test_accessibility_skips_without_html(tmp_path):
    assert checks.accessibility(tmp_path).status == "skip"


def test_accessibility_fails_without_lang(tmp_path):
    write(tmp_path / "index.html", "<html><body>hi</body></html>")
    assert checks.accessibility(tmp_path).status == "fail"


def test_accessibility_fails_on_img_without_alt(tmp_path):
    write(tmp_path / "index.html", '<html lang="en"><body><img src="a.png"></body></html>')
    assert checks.accessibility(tmp_path).status == "fail"


def test_accessibility_passes(tmp_path):
    write(tmp_path / "index.html", '<html lang="en"><body><img src="a.png" alt="a"></body></html>')
    assert checks.accessibility(tmp_path).status == "pass"


# --- testing_and_maintainability -----------------------------------------

def test_testing_fails_without_tests_or_ci(tmp_path):
    assert checks.testing_and_maintainability(tmp_path).status == "fail"


def test_testing_passes_with_tests_and_ci(tmp_path):
    write(tmp_path / "tests" / "test_something.py", "def test_ok(): assert True\n")
    write(tmp_path / ".github" / "workflows" / "ci.yml", "name: CI\n")
    assert checks.testing_and_maintainability(tmp_path).status == "pass"


# --- inclusive_community -------------------------------------------------

def test_inclusive_community_fails_when_missing(tmp_path):
    assert checks.inclusive_community(tmp_path).status == "fail"


def test_inclusive_community_passes(tmp_path):
    write(tmp_path / "CODE_OF_CONDUCT.md", "Be kind.")
    write(tmp_path / "CONTRIBUTING.md", "PRs welcome.")
    assert checks.inclusive_community(tmp_path).status == "pass"


# --- dependency_integrity -------------------------------------------------

def test_dependency_integrity_skips_without_manifest(tmp_path):
    assert checks.dependency_integrity(tmp_path).status == "skip"


def test_dependency_integrity_fails_on_unpinned_requirements(tmp_path):
    write(tmp_path / "requirements.txt", "requests>=2.0\n")
    assert checks.dependency_integrity(tmp_path).status == "fail"


def test_dependency_integrity_passes_on_pinned_requirements(tmp_path):
    write(tmp_path / "requirements.txt", "requests==2.32.3\n")
    assert checks.dependency_integrity(tmp_path).status == "pass"


def test_dependency_integrity_fails_on_package_json_without_lockfile(tmp_path):
    write(tmp_path / "package.json", "{}")
    assert checks.dependency_integrity(tmp_path).status == "fail"


def test_dependency_integrity_passes_with_lockfile(tmp_path):
    write(tmp_path / "package.json", "{}")
    write(tmp_path / "package-lock.json", "{}")
    assert checks.dependency_integrity(tmp_path).status == "pass"


# --- sustainability_longevity ----------------------------------------------

def test_sustainability_fails_without_changelog(tmp_path):
    assert checks.sustainability_longevity(tmp_path).status == "fail"


def test_sustainability_passes_with_versioned_changelog(tmp_path):
    write(tmp_path / "CHANGELOG.md", "## [1.0.0] - 2026-01-01\n\nInitial release.\n")
    assert checks.sustainability_longevity(tmp_path).status == "pass"
