"""Scenario loading and management."""
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ScenarioMetadata:
    """Safe metadata about a scenario — no secrets, no character details."""
    filename: str
    company: str
    description: str
    difficulty: str
    objective: str
    extensions_hint: str
    starting_extension: str


def list_scenarios(scenarios_dir: str) -> list[ScenarioMetadata]:
    """List all scenarios in a directory, returning only safe metadata."""
    scenarios_path = Path(scenarios_dir)
    results = []

    for yaml_file in sorted(scenarios_path.glob("*.yaml")):
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        results.append(ScenarioMetadata(
            filename=yaml_file.name,
            company=data.get("company", "Unknown"),
            description=data.get("description", ""),
            difficulty=data.get("difficulty", "Unknown"),
            objective=data.get("objective", ""),
            extensions_hint=data.get("extensions_hint", ""),
            starting_extension=data.get("starting_extension", "0"),
        ))

    return results


def load_scenario(path: str) -> dict:
    """Load a full scenario from a YAML file (for engine use only)."""
    scenario_path = Path(path)
    if not scenario_path.exists():
        raise FileNotFoundError(f"Scenario file not found: {path}")

    with open(scenario_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_character(scenario: dict, extension: str) -> dict | None:
    """Find a character by extension number. Returns None if not found."""
    for character in scenario.get("characters", []):
        if character.get("extension") == extension:
            return character
    return None
