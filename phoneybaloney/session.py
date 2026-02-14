"""Session management and transcript logging."""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class TranscriptEntry:
    timestamp: str
    speaker: str
    text: str


@dataclass
class Session:
    scenario_name: str
    started_at: datetime = field(default_factory=datetime.now)
    entries: list[TranscriptEntry] = field(default_factory=list)

    def add_entry(self, speaker: str, text: str) -> None:
        entry = TranscriptEntry(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            speaker=speaker,
            text=text,
        )
        self.entries.append(entry)

    def save_transcript(self, transcripts_dir: str) -> str:
        path = Path(transcripts_dir)
        path.mkdir(parents=True, exist_ok=True)
        filename = f"{self.scenario_name}_{self.started_at.strftime('%Y-%m-%d_%H%M%S')}.md"
        filepath = path / filename

        lines = [f"# {self.scenario_name} — Session Transcript", ""]
        lines.append(f"**Date:** {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        for entry in self.entries:
            lines.append(f"**[{entry.timestamp}] {entry.speaker}:** {entry.text}")
            lines.append("")

        filepath.write_text("\n".join(lines), encoding="utf-8")
        return str(filepath)
