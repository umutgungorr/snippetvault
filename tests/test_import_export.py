import json
from pathlib import Path
from snippetvault.db import Database
from snippetvault.vault import VaultService


def test_export_and_import(tmp_path: Path):
    db1 = Database(tmp_path / "db1.db")
    service1 = VaultService(db1)
    service1.add_snippet("Cmd 1", "echo 1", tags=["tag1"])
    service1.add_snippet("Cmd 2", "echo 2", tags=["tag2"])

    data = service1.export_snippets()
    assert len(data) == 2

    db2 = Database(tmp_path / "db2.db")
    service2 = VaultService(db2)
    count = service2.import_snippets(data)
    assert count == 2
    assert len(service2.list_snippets()) == 2
