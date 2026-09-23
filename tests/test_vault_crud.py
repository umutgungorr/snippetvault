import pytest
from pathlib import Path
from snippetvault.db import Database
from snippetvault.vault import VaultService


def test_vault_service_add_and_list(tmp_path: Path):
    service = VaultService(Database(tmp_path / "test.db"))

    s1 = service.add_snippet("Docker Up", "docker compose up -d", tags=["docker", "compose"])
    s2 = service.add_snippet("Git Push", "git push origin main", tags=["git"])

    all_snippets = service.list_snippets()
    assert len(all_snippets) == 2

    docker_snippets = service.list_snippets(tag="docker")
    assert len(docker_snippets) == 1
    assert docker_snippets[0].title == "Docker Up"

    git_snippets = service.list_snippets(tag="git")
    assert len(git_snippets) == 1
    assert git_snippets[0].title == "Git Push"


def test_vault_service_validation_errors(tmp_path: Path):
    service = VaultService(Database(tmp_path / "test.db"))

    with pytest.raises(ValueError, match="title cannot be empty"):
        service.add_snippet("", "echo hi")

    with pytest.raises(ValueError, match="command cannot be empty"):
        service.add_snippet("Title", "   ")


def test_vault_service_stats(tmp_path: Path):
    service = VaultService(Database(tmp_path / "test.db"))
    s1 = service.add_snippet("Command 1", "echo 1", tags=["util", "bash"])
    s2 = service.add_snippet("Command 2", "echo 2", tags=["util", "python"])

    service.copy_snippet(s1.id)
    service.copy_snippet(s1.id)

    stats = service.get_stats()
    assert stats["total_snippets"] == 2
    assert stats["total_tags"] == 3
    assert stats["most_used"][0]["id"] == s1.id
    assert stats["most_used"][0]["uses"] == 2
