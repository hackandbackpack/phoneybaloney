"""Core conversation engine — orchestrates LLM, TTS, STT, and session management."""
import re
from pathlib import Path

from phoneybaloney.config import AppConfig
from phoneybaloney.scenarios import load_scenario, get_character
from phoneybaloney.session import Session
from phoneybaloney.providers.base import BaseLLM, BaseTTS, BaseSTT

DIAL_PATTERN = re.compile(r"dial\s+extension\s+(\d+)", re.IGNORECASE)
TERMINATE_PATTERN = re.compile(r"terminate\s+call", re.IGNORECASE)


class ConversationEngine:
    """Manages a vishing session: provider orchestration, command handling, transcripts."""

    def __init__(self, llm: BaseLLM, tts: BaseTTS, stt: BaseSTT, config: AppConfig):
        self.llm = llm
        self.tts = tts
        self.stt = stt
        self.config = config
        self.scenario = None
        self.current_character = None
        self.messages: list[dict] = []
        self.session: Session | None = None
        self.active = False

    def load_scenario(self, scenario_path: str) -> dict:
        """Load a scenario YAML file."""
        self.scenario = load_scenario(scenario_path)
        return self.scenario

    def start_call(self) -> str:
        """Start a call with the starting extension character. Returns greeting text."""
        if not self.scenario:
            raise RuntimeError("No scenario loaded")

        starting_ext = self.scenario.get("starting_extension", "0")
        self.current_character = get_character(self.scenario, starting_ext)
        if not self.current_character:
            raise RuntimeError(f"Starting extension '{starting_ext}' not found in scenario")

        self.session = Session(scenario_name=self.scenario.get("company", "unknown"))
        self.active = True
        self._init_conversation()

        greeting = self.llm.generate_response(self.messages)
        self.messages.append({"role": "assistant", "content": greeting})
        self.session.add_entry(self.current_character["name"], greeting)
        return greeting

    def process_input(self, user_text: str) -> dict:
        """Process user input. Returns dict with 'type' and relevant data.

        Return types:
            {"type": "response", "speaker": str, "text": str}
            {"type": "switch", "character": str, "greeting": str}
            {"type": "end", "transcript_path": str | None}
            {"type": "error", "message": str}
        """
        if not self.active:
            return {"type": "error", "message": "No active call"}

        # Check for terminate command
        if TERMINATE_PATTERN.search(user_text):
            return self.end_call()

        # Check for dial extension command
        dial_match = DIAL_PATTERN.search(user_text)
        if dial_match:
            extension = dial_match.group(1)
            return self.switch_character(extension)

        # Normal conversation — send to LLM
        self.session.add_entry("You", user_text)
        self.messages.append({"role": "user", "content": user_text})
        response = self.llm.generate_response(self.messages)
        self.messages.append({"role": "assistant", "content": response})
        self.session.add_entry(self.current_character["name"], response)

        return {
            "type": "response",
            "speaker": self.current_character["name"],
            "text": response,
        }

    def switch_character(self, extension: str) -> dict:
        """Switch to a new character by extension. Clears conversation history."""
        character = get_character(self.scenario, extension)
        if not character:
            return {
                "type": "error",
                "message": f"The extension you dialed ({extension}) is not available.",
            }

        self.current_character = character
        self.messages.clear()
        self._init_conversation()

        greeting = self.llm.generate_response(self.messages)
        self.messages.append({"role": "assistant", "content": greeting})
        self.session.add_entry(self.current_character["name"], greeting)

        return {
            "type": "switch",
            "character": self.current_character["name"],
            "greeting": greeting,
        }

    def end_call(self) -> dict:
        """End the current call and save transcript."""
        self.active = False
        transcript_path = None
        if self.session and self.config.log_transcripts:
            transcripts_dir = str(Path(__file__).parent.parent / "transcripts")
            transcript_path = self.session.save_transcript(transcripts_dir)

        return {"type": "end", "transcript_path": transcript_path}

    def _init_conversation(self) -> None:
        """Set up conversation messages for the current character."""
        global_prompt = self.scenario.get("global_prompt", "")
        char_prompt = self.current_character.get("prompt", "")
        system_content = f"{global_prompt} {char_prompt}".strip()

        self.messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": "*dials number*"},
        ]
