import pytest
from pathlib import Path
from typer.testing import CliRunner
from codesmells.cli import app

runner = CliRunner()

def test_install_skill_no_args():
    result = runner.invoke(app, ["install-skill"])
    assert result.exit_code == 0
    assert "CodeSmells AI Agent Skill" in result.stdout
    assert "Suggested Installation Paths" in result.stdout

def test_install_skill_with_path(tmp_path):
    dest = tmp_path / "skills"
    result = runner.invoke(app, ["install-skill", str(dest)])
    assert result.exit_code == 0
    assert "Success: Installed CodeSmells skill to" in result.stdout
    assert str(dest) in result.stdout.replace("\n", "")
    
    skill_file = dest / "codesmells" / "SKILL.md"
    assert skill_file.exists()
    assert "# CodeSmells: Expert Agentic Refactoring" in skill_file.read_text()

def test_install_skill_force(tmp_path):
    dest = tmp_path / "skills"
    dest_dir = dest / "codesmells"
    dest_dir.mkdir(parents=True)
    skill_file = dest_dir / "SKILL.md"
    skill_file.write_text("Old Content")
    
    # Try without force
    result = runner.invoke(app, ["install-skill", str(dest)])
    assert result.exit_code == 1
    assert "Error: Skill already exists" in result.stdout
    assert skill_file.read_text() == "Old Content"
    
    # Try with force
    result = runner.invoke(app, ["install-skill", str(dest), "--force"])
    assert result.exit_code == 0
    assert "Success: Installed CodeSmells skill" in result.stdout
    assert "# CodeSmells: Expert Agentic Refactoring" in skill_file.read_text()
