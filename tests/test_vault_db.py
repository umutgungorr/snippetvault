from pathlib import Path
from snippetvault.db import Database
from snippetvault.models import Snippet


def test_database_initialization(tmp_path: Path):
    db_file = tmp_path / "test.db"
    db = Database(db_file)
    assert db_file.exists()
    assert db.get_all() == []


def test_database_insert_and_get(tmp_path: Path):
    db = Database(tmp_path / "test.db")
    snippet = Snippet(
        id=None,
        title="Test Command",
        command="echo 'hello'",
        tags=["test", "demo"],
        description="A simple echo",
    )
    saved = db.insert(snippet)
    assert saved.id is not None
    assert saved.id > 0

    retrieved = db.get_by_id(saved.id)
    assert retrieved is not None
    assert retrieved.title == "Test Command"
    assert retrieved.command == "echo 'hello'"
    assert retrieved.tags == ["test", "demo"]
    assert retrieved.times_used == 0


def test_database_update_and_delete(tmp_path: Path):
    db = Database(tmp_path / "test.db")
    s = db.insert(Snippet(id=None, title="Old", command="ls", tags=["files"]))
    
    s.title = "New Title"
    s.tags = ["files", "updated"]
    assert db.update(s) is True

    updated = db.get_by_id(s.id)
    assert updated.title == "New Title"
    assert updated.tags == ["files", "updated"]

    assert db.delete(s.id) is True
    assert db.get_by_id(s.id) is None


def test_database_usage_increment(tmp_path: Path):
    db = Database(tmp_path / "test.db")
    s = db.insert(Snippet(id=None, title="Count test", command="date", tags=[]))
    assert s.times_used == 0

    db.increment_usage(s.id)
    db.increment_usage(s.id)

    updated = db.get_by_id(s.id)
    assert updated.times_used == 2
    assert updated.last_used_at is not None
