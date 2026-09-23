import json
from pathlib import Path
from snippetvault.cli import main


def test_cli_add_and_list(tmp_path: Path, capsys):
    db_file = str(tmp_path / "cli.db")
    ret = main(["--db", db_file, "add", "ls -la", "-t", "List Files", "--tags", "files,unix"])
    assert ret == 0

    out = capsys.readouterr().out
    assert "saved successfully" in out

    ret2 = main(["--db", db_file, "list", "--json"])
    assert ret2 == 0
    items = json.loads(capsys.readouterr().out)
    assert len(items) == 1
    assert items[0]["title"] == "List Files"


def test_cli_find(tmp_path: Path, capsys):
    db_file = str(tmp_path / "cli.db")
    main(["--db", db_file, "add", "docker compose up", "-t", "Docker Compose", "--tags", "docker"])
    capsys.readouterr()

    ret = main(["--db", db_file, "find", "compose", "--json"])
    assert ret == 0
    matches = json.loads(capsys.readouterr().out)
    assert len(matches) == 1
    assert matches[0]["snippet"]["title"] == "Docker Compose"


def test_cli_get_and_delete(tmp_path: Path, capsys):
    db_file = str(tmp_path / "cli.db")
    main(["--db", db_file, "add", "pwd", "-t", "Print Workdir"])
    capsys.readouterr()

    ret_get = main(["--db", db_file, "get", "1"])
    assert ret_get == 0
    assert "Print Workdir" in capsys.readouterr().out

    ret_del = main(["--db", db_file, "delete", "1"])
    assert ret_del == 0
    assert "deleted" in capsys.readouterr().out
