import pytest
from datetime import datetime
from unittest.mock import patch
from phoneybaloney.session import Session, TranscriptEntry


class TestSession:
    def test_create_session(self):
        session = Session(scenario_name="megacorp")
        assert session.scenario_name == "megacorp"
        assert isinstance(session.started_at, datetime)
        assert session.entries == []

    def test_add_entry(self):
        session = Session(scenario_name="megacorp")
        session.add_entry("Susan Daniels", "MegaCorp, this is Susan.")
        session.add_entry("You", "Hi, I'm calling about my account.")
        assert len(session.entries) == 2
        assert session.entries[0].speaker == "Susan Daniels"
        assert session.entries[0].text == "MegaCorp, this is Susan."
        assert session.entries[1].speaker == "You"

    def test_entry_has_timestamp(self):
        session = Session(scenario_name="megacorp")
        session.add_entry("Susan", "Hello")
        assert session.entries[0].timestamp  # non-empty string

    def test_save_transcript(self, tmp_path):
        session = Session(
            scenario_name="megacorp",
            started_at=datetime(2026, 2, 14, 10, 30, 0),
        )
        session.add_entry("Susan Daniels", "MegaCorp, this is Susan.")
        session.add_entry("You", "Hi there.")

        filepath = session.save_transcript(str(tmp_path))
        assert "megacorp" in filepath
        assert "2026-02-14" in filepath

        content = open(filepath, "r", encoding="utf-8").read()
        assert "megacorp" in content.lower() or "MegaCorp" in content
        assert "Susan Daniels" in content
        assert "Hi there." in content

    def test_save_transcript_creates_directory(self, tmp_path):
        nested = tmp_path / "deep" / "nested"
        session = Session(scenario_name="test")
        session.add_entry("Test", "Hello")
        filepath = session.save_transcript(str(nested))
        assert nested.exists()

    def test_transcript_entries_in_order(self, tmp_path):
        session = Session(
            scenario_name="test",
            started_at=datetime(2026, 1, 1, 12, 0, 0),
        )
        session.add_entry("First", "Message 1")
        session.add_entry("Second", "Message 2")
        session.add_entry("Third", "Message 3")

        filepath = session.save_transcript(str(tmp_path))
        content = open(filepath, "r", encoding="utf-8").read()
        pos1 = content.index("Message 1")
        pos2 = content.index("Message 2")
        pos3 = content.index("Message 3")
        assert pos1 < pos2 < pos3
