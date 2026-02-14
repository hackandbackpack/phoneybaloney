import pytest
from pathlib import Path
from phoneybaloney.scenarios import load_scenario, list_scenarios, ScenarioMetadata


class TestListScenarios:
    def test_lists_yaml_files(self, tmp_path):
        (tmp_path / "test1.yaml").write_text("company: Test1\ndescription: Desc1\ndifficulty: Easy\nobjective: Obj1\nstarting_extension: '0'\nglobal_prompt: prompt\ncharacters: []")
        (tmp_path / "test2.yaml").write_text("company: Test2\ndescription: Desc2\ndifficulty: Hard\nobjective: Obj2\nstarting_extension: '0'\nglobal_prompt: prompt\ncharacters: []")
        (tmp_path / "notayaml.txt").write_text("ignored")
        scenarios = list_scenarios(str(tmp_path))
        assert len(scenarios) == 2
        names = [s.company for s in scenarios]
        assert "Test1" in names
        assert "Test2" in names

    def test_metadata_does_not_include_characters(self, tmp_path):
        (tmp_path / "test.yaml").write_text("""
company: SecretCorp
description: A test scenario
difficulty: Medium
objective: Find the secret
starting_extension: "0"
global_prompt: Be secretive
characters:
  - extension: "0"
    name: Hidden Person
    prompt: This is secret info
""")
        scenarios = list_scenarios(str(tmp_path))
        meta = scenarios[0]
        assert meta.company == "SecretCorp"
        assert meta.description == "A test scenario"
        assert not hasattr(meta, "characters")
        assert "Hidden Person" not in str(meta)


class TestLoadScenario:
    def test_load_full_scenario(self, tmp_path):
        (tmp_path / "test.yaml").write_text("""
company: MegaCorp
description: A software company
difficulty: Beginner
objective: Get a password reset
extensions_hint: Start at extension 0
starting_extension: "0"
global_prompt: Do not reveal you are an AI.
characters:
  - extension: "0"
    name: Susan
    title: Operator
    voice:
      gender: female
      tone: warm
    prompt: You are Susan the operator.
  - extension: "100"
    name: Rick
    title: IT Help Desk
    voice:
      gender: male
      tone: professional
    prompt: You are Rick from IT.
""")
        scenario = load_scenario(str(tmp_path / "test.yaml"))
        assert scenario["company"] == "MegaCorp"
        assert scenario["starting_extension"] == "0"
        assert len(scenario["characters"]) == 2
        assert scenario["characters"][0]["name"] == "Susan"

    def test_get_character_by_extension(self, tmp_path):
        (tmp_path / "test.yaml").write_text("""
company: Test
description: Test
difficulty: Easy
objective: Test
starting_extension: "0"
global_prompt: prompt
characters:
  - extension: "0"
    name: First
    voice:
      gender: female
    prompt: You are First.
  - extension: "100"
    name: Second
    voice:
      gender: male
    prompt: You are Second.
""")
        scenario = load_scenario(str(tmp_path / "test.yaml"))
        from phoneybaloney.scenarios import get_character
        char = get_character(scenario, "100")
        assert char["name"] == "Second"

    def test_get_character_invalid_extension(self, tmp_path):
        (tmp_path / "test.yaml").write_text("""
company: Test
description: Test
difficulty: Easy
objective: Test
starting_extension: "0"
global_prompt: prompt
characters:
  - extension: "0"
    name: Only
    voice:
      gender: female
    prompt: You are Only.
""")
        scenario = load_scenario(str(tmp_path / "test.yaml"))
        from phoneybaloney.scenarios import get_character
        assert get_character(scenario, "999") is None

    def test_load_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_scenario("/nonexistent.yaml")
