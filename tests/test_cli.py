from typer.testing import CliRunner
from codesmells.cli import app

runner = CliRunner()

def test_scan_help():
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0
    assert "Scan directory for anti-patterns" in result.stdout

def test_scan_basic():
    result = runner.invoke(app, ["scan"])
    assert result.exit_code == 0
    assert "Scanning" in result.stdout
