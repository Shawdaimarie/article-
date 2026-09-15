import os
import tempfile

# Point the API at a throwaway SQLite file for the whole test session, before
# `article.api.db` (and therefore its module-level engine) gets imported.
_tmp_dir = tempfile.mkdtemp(prefix="article-test-db-")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp_dir}/test.db")
