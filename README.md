# PhoneyBaloney

A self-hosted vishing (voice phishing) simulator for penetration testers and security training. Have voice conversations with AI-powered characters in configurable scenarios, practicing social engineering techniques in a safe environment.

Originally inspired by [MakeAVish](https://github.com/brandonscholet/MakeAVish) by Brandon Scholet.

## Features

- **Multi-provider support** — Choose your LLM, TTS, and STT providers
- **Free by default** — Runs with Ollama + pyttsx3 + Whisper (zero API keys needed)
- **Web-based UI** — Browser interface with real-time session management
- **YAML scenarios** — Create custom scenarios with hidden character secrets
- **Transcript logging** — Review every session with saved markdown transcripts
- **Cross-platform** — Windows (priority), Mac, Linux
- **Guided setup** — First-run wizard walks you through configuration

## Provider Options

| Category | Provider | Cost | Quality | Requirements |
|----------|----------|------|---------|-------------|
| **LLM** | Ollama | Free | Good | [Ollama](https://ollama.ai) installed locally |
| | OpenAI | Paid | Excellent | API key |
| | Claude | Paid | Excellent | API key |
| **TTS** | pyttsx3 | Free | Basic | None (uses OS voices) |
| | Coqui TTS | Free | Good | ~1GB model download |
| | Google Cloud | Paid | Great | API key |
| | ElevenLabs | Paid | Premium | API key |
| **STT** | Whisper Local | Free | Great | ~150MB model download |
| | Vosk | Free | Good | Model download |
| | Google Web Speech | Free | Good | Internet connection |
| | OpenAI Whisper API | Paid | Excellent | API key |

## Quick Start

### Windows

```
git clone https://github.com/hackandbackpack/phoneybaloney.git
cd phoneybaloney
python setup.py
start.bat
```

### Mac / Linux

```bash
git clone https://github.com/hackandbackpack/phoneybaloney.git
cd phoneybaloney
python3 setup.py
./start.sh
```

The setup script will:
1. Create a virtual environment
2. Install base dependencies
3. Walk you through optional component installation
4. Generate your configuration file
5. Print launch instructions

Your browser will open automatically to the PhoneyBaloney dashboard.

## How It Works

1. **Choose a scenario** from the dashboard (e.g., MegaCorp)
2. **Start the call** — you're connected to the starting character
3. **Speak naturally** into your microphone
4. **Navigate the company** by asking to be transferred or saying "Dial Extension [number]"
5. **Achieve the objective** using social engineering techniques
6. **End the call** and review your transcript

### Voice Commands

- **"Dial Extension [number]"** — Transfer to a different character
- **"Terminate Call"** — End the session

## Creating Scenarios

Drop a YAML file into the `scenarios/` directory and it appears in the web UI automatically.

```yaml
company: YourCompany
description: Brief scenario description
difficulty: Beginner  # Beginner, Intermediate, Advanced
objective: What the user is trying to accomplish
starting_extension: "0"

global_prompt: Instructions for all characters

characters:
  - extension: "0"
    name: Character Name
    title: Job Title
    voice:
      gender: female
      tone: warm
    prompt: Detailed character instructions and knowledge
```

See `scenarios/example_template.yaml` for a full template with comments.

## Configuration

Copy `config.example.yaml` to `config.yaml` and adjust settings. The web UI settings page can also manage configuration through the browser.

Key settings:
- `llm_provider` — Which LLM to use (ollama, openai, claude)
- `tts_provider` — Which TTS to use (pyttsx3, coqui, google_tts, elevenlabs)
- `stt_provider` — Which STT to use (whisper_local, vosk, google_stt, whisper_api)

Only the selected provider's configuration section is read — no need to comment/uncomment blocks.

## Project Structure

```
phoneybaloney/
├── phoneybaloney/          # Main package
│   ├── app.py              # FastAPI web application
│   ├── engine.py           # Conversation engine
│   ├── config.py           # Configuration management
│   ├── session.py          # Session & transcript logging
│   ├── audio.py            # Audio playback utilities
│   ├── scenarios.py        # Scenario loading
│   ├── providers/          # Plugin-based provider system
│   │   ├── base.py         # Abstract base classes
│   │   ├── llm/            # LLM providers
│   │   ├── tts/            # TTS providers
│   │   └── stt/            # STT providers
│   └── web/                # Templates, CSS, JS
├── scenarios/              # YAML scenario files
├── transcripts/            # Session logs
├── requirements/           # Tiered dependency files
├── config.example.yaml     # Documented configuration template
├── setup.py                # Cross-platform installer
├── start.bat               # Windows launcher
└── start.sh                # Mac/Linux launcher
```

## Troubleshooting

**Ollama not running?**
Open a terminal and run `ollama serve`. If not installed, download from [ollama.ai](https://ollama.ai) and run `ollama pull llama3`.

**No microphone detected?**
Check OS privacy settings and ensure your microphone isn't muted. On Windows, check Settings > Privacy > Microphone.

**PyAudio installation fails?**
- Windows: `pip install pyaudio` (pre-built wheel available)
- Mac: `brew install portaudio` then `pip install pyaudio`
- Linux: `sudo apt install portaudio19-dev` then `pip install pyaudio`

**Slow responses?**
Use a smaller model (e.g., `llama3` instead of `llama3:70b`). For faster TTS, use pyttsx3.

## Adding Custom Providers

See `docs/adding-providers.md` for a step-by-step guide on creating new LLM, TTS, or STT providers.

## Contributing

Issues and pull requests welcome. Find me on Twitter [@hackandbackpack](https://twitter.com/hackandbackpack) or on Discord at [RedSiege.com/Discord](https://redsiege.com/Discord).
