from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_alembic_has_paper_migration():
    config = Config(str(Path("alembic.ini")))
    scripts = ScriptDirectory.from_config(config)

    assert scripts.get_current_head() == "0005"
    assert scripts.get_revision("0005").down_revision == "0004"
