from pathlib import Path
from snippetvault.db import Database
from snippetvault.vault import VaultService


def test_search_by_exact_tag(tmp_path: Path):
    service = VaultService(Database(tmp_path / "test.db"))
    s1 = service.add_snippet("Docker Postgres", "docker run -p 5432:5432 postgres", tags=["docker", "database"])
    s2 = service.add_snippet("NPM Build", "npm run build", tags=["frontend", "build"])

    results = service.search("database")
    assert len(results) >= 1
    assert results[0].snippet.title == "Docker Postgres"
    assert results[0].matched_by == "tag"


def test_search_by_command_substring(tmp_path: Path):
    service = VaultService(Database(tmp_path / "test.db"))
    service.add_snippet("Kubectl Pods", "kubectl get pods -A -o wide", tags=["k8s"])
    service.add_snippet("Docker Logs", "docker compose logs -f", tags=["docker"])

    results = service.search("get pods")
    assert len(results) >= 1
    assert results[0].snippet.title == "Kubectl Pods"


def test_search_fuzzy_title(tmp_path: Path):
    service = VaultService(Database(tmp_path / "test.db"))
    service.add_snippet("Kubernetes Cluster Info", "kubectl cluster-info", tags=["k8s"])

    # Slightly mistyped query
    results = service.search("kubernets")
    assert len(results) >= 1
    assert results[0].snippet.title == "Kubernetes Cluster Info"
