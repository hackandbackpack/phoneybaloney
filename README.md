# PhoneyBaloney

A self-hosted vishing (voice phishing) simulator for penetration testers and security training. Have real-time voice conversations with AI-powered characters in configurable scenarios, practicing social engineering techniques in a safe environment.

Originally inspired by [MakeAVish](https://github.com/brandonscholet/MakeAVish) by Brandon Scholet.

Shout out to Brandon for the original thought! Find us on Twitter [@hackandbackpack](https://twitter.com/hackandbackpack) or on Discord at [RedSiege.com/Discord](https://redsiege.com/Discord).

## What is Vishing?

Vishing (voice phishing) is a social engineering technique where an attacker uses phone calls to manipulate people into revealing sensitive information. PhoneyBaloney lets you practice these techniques against AI characters — no real people involved, no risk, full learning.

## Features

- **Multi-provider support** — Choose your AI brain (LLM), voice output (TTS), and voice input (STT) from multiple providers
- **Free by default** — Runs entirely on your machine with Ollama + pyttsx3 + Whisper. Zero API keys, zero cost
- **Web-based UI** — Clean browser interface with real-time conversation transcript, provider status dashboard, and guided setup wizard
- **YAML scenarios** — Create and share custom scenarios. Character secrets stay hidden from the UI — users discover information through conversation, not by reading a menu
- **Transcript logging** — Every session is saved as a markdown file for review and training debriefs
- **Cross-platform** — Windows (priority), Mac, and Linux
- **Extensible** — Add your own LLM, TTS, or STT providers with a simple plugin interface

## Provider Options

PhoneyBaloney supports multiple providers at every layer. Pick what works for your budget and hardware.

### LLM Providers (the AI brain behind conversations)

| Provider | Cost | Quality | Requirements | Best For |
|----------|------|---------|-------------|----------|
| **Ollama** | Free | Good | [Ollama](https://ollama.ai) installed locally, ~4GB RAM | Privacy-conscious users, offline use, no budget |
| **OpenAI** | Paid | Excellent | API key from [platform.openai.com](https://platform.openai.com) | Best conversation quality, fast responses |
| **Claude** | Paid | Excellent | API key from [console.anthropic.com](https://console.anthropic.com) | Nuanced character roleplay |

### TTS Providers (voice output — what you hear)

| Provider | Cost | Quality | Requirements | Best For |
|----------|------|---------|-------------|----------|
| **pyttsx3** | Free | Basic | None — uses your OS built-in voices | Getting started fast, no downloads |
| **Coqui TTS** | Free | Good | ~1GB model download, decent CPU | Better voice quality without paying |
| **Google Cloud** | Paid | Great | API key from [console.cloud.google.com](https://console.cloud.google.com) | Natural-sounding voices at low cost |
| **ElevenLabs** | Paid | Premium | API key from [elevenlabs.io](https://elevenlabs.io) | Most realistic voices, custom voice cloning |

### STT Providers (voice input — how it hears you)

| Provider | Cost | Quality | Requirements | Best For |
|----------|------|---------|-------------|----------|
| **Whisper Local** | Free | Great | ~150MB model download, decent CPU | Best free option, good accuracy |
| **Vosk** | Free | Good | Model download from [alphacephei.com/vosk](https://alphacephei.com/vosk/models) | Older hardware, lightweight |
| **Google Web Speech** | Free | Good | Internet connection | No downloads needed, works everywhere |
| **OpenAI Whisper API** | Paid | Excellent | API key (same as OpenAI LLM) | Best accuracy, low latency |

## Quick Start

### Prerequisites

- **Python 3.10 or higher** — [Download Python](https://www.python.org/downloads/)
- **A microphone** — Built-in or USB, PhoneyBaloney needs to hear you
- **Speakers or headphones** — To hear the AI characters

### Windows

```
git clone https://github.com/hackandbackpack/phoneybaloney.git
cd phoneybaloney
python setup.py
start.bat
```

### Mac

```bash
git clone https://github.com/hackandbackpack/phoneybaloney.git
cd phoneybaloney
python3 setup.py
./start.sh
```

### Linux

```bash
git clone https://github.com/hackandbackpack/phoneybaloney.git
cd phoneybaloney
python3 setup.py
./start.sh
```

### What the Setup Script Does

The setup script (`setup.py`) handles everything automatically:

1. **Checks your Python version** — tells you if you need to upgrade
2. **Detects your operating system** — installs the right dependencies for your platform
3. **Creates a virtual environment** — keeps PhoneyBaloney's packages isolated from your system
4. **Installs base dependencies** — the core packages everyone needs
5. **Installs audio dependencies** — pygame (for audio playback) and SpeechRecognition (for microphone input, which requires PyAudio as a backend)
6. **Asks about optional components** — choose whether to download Whisper, Coqui, Vosk, or cloud TTS packages
7. **Generates your config file** — creates `config.yaml` with sensible defaults
8. **Validates the installation** — confirms everything is working
9. **Prints launch instructions** — tells you exactly how to start the app on your OS

After setup, double-click `start.bat` (Windows) or run `./start.sh` (Mac/Linux) and your browser opens to the PhoneyBaloney dashboard.

## How It Works

1. **Launch PhoneyBaloney** — your browser opens to the dashboard
2. **Check provider status** — the dashboard shows green/red indicators for each provider. All must be green before starting a call
3. **Choose a scenario** — pick from available scenarios (e.g., MegaCorp). You'll see a description and objective, but character details are hidden
4. **Start the call** — you're automatically connected to the starting character (e.g., the company operator)
5. **Speak naturally** — talk into your microphone. The AI character responds through your speakers. The conversation transcript appears in real-time on screen
6. **Navigate the company** — discover extensions and transfer between characters to achieve your objective
7. **End the call** — your full transcript is saved for review

### Voice Commands

During a call, you can say:
- **"Dial Extension [number]"** — Transfer to a different character (e.g., "Dial Extension 3100")
- **"Terminate Call"** — End the session and save the transcript

You can also use the on-screen controls to dial extensions or end the call.

### Important Notes

- **Each call is fresh.** When you dial a new extension, the character has no memory of any previous conversation. This is by design — it keeps responses fast and costs low.
- **Take your own notes.** The UI shows the conversation transcript, but it won't highlight key information or track what you've discovered. Part of the challenge is keeping track of names, extensions, and details yourself — just like a real vishing engagement.

## Configuration

PhoneyBaloney uses a single `config.yaml` file for all settings. You can edit it by hand or use the web UI settings page.

### How Provider Selection Works

The config file has three key lines that control which providers are active:

```yaml
llm_provider: ollama        # Options: ollama, openai, claude
tts_provider: pyttsx3       # Options: pyttsx3, coqui, google_tts, elevenlabs
stt_provider: whisper_local # Options: whisper_local, vosk, google_stt, whisper_api
```

**Only the selected provider's section is read.** Everything else in the file is ignored. You don't need to comment out, delete, or modify sections you aren't using. Just change the provider name on the selector line.

For example, if `llm_provider` is set to `ollama`, then the `openai:` and `claude:` sections are completely ignored — even if they have empty API keys.

### Setting Up Providers

**For free/local providers (Ollama, pyttsx3, Whisper Local):**
No API keys needed. Just make sure the software is installed and running.

**For paid/cloud providers (OpenAI, Claude, Google TTS, ElevenLabs):**
1. Get an API key from the provider's website (links in `config.example.yaml`)
2. Paste it into the appropriate section of `config.yaml`
3. The web UI settings page will validate your key immediately

### Voice Configuration

Scenarios define characters with a `gender` and `tone` (e.g., "female, warm"). The actual voice used depends on your TTS provider. Each provider section in `config.yaml` has a `voice_map`:

```yaml
google_tts:
  api_key: "your-key"
  voice_map:
    female_default: en-US-Journey-F
    male_default: en-US-Wavenet-J
```

The web UI settings page includes a voice browser — select your TTS provider, click "Load Voices," and pick from a dropdown of all available voices. You can preview them before assigning.

See `config.example.yaml` for the full documented configuration with all options explained.

## Creating Scenarios

Scenarios are YAML files in the `scenarios/` directory. Drop a new `.yaml` file in and it appears in the web UI automatically.

### Scenario Structure

```yaml
# Metadata — shown to the user in the UI
company: YourCompany
description: Brief scenario description shown on the dashboard
difficulty: Beginner       # Beginner, Intermediate, or Advanced
objective: What the user is trying to accomplish
extensions_hint: "Start by calling the operator at extension 0"
starting_extension: "0"    # Which character answers first

# Global prompt — shared instructions for ALL characters (never shown in UI)
global_prompt: >
  Do not reveal that you are an AI. Identify as a company employee.

# Characters — the people in the scenario (never shown in UI)
characters:
  - extension: "0"
    name: Character Name
    title: Job Title
    voice:
      gender: female       # Used to select the right voice from voice_map
      tone: warm           # Human-readable description for reference
    prompt: >
      Detailed character instructions: personality, knowledge,
      what they can and can't share, verification requirements,
      secrets, escalation paths, etc.
```

### Key Design Principles for Scenarios

- **The UI only shows metadata** — company name, description, difficulty, objective, and the starting hint. Character names, prompts, extensions, and secrets are never displayed.
- **Users discover everything through conversation.** Extensions, employee names, departments, override codes — all of it must be extracted by talking to characters.
- **Characters should have interlocking dependencies.** The best scenarios require talking to multiple characters, where information from one unlocks progress with another.
- **`starting_extension`** determines who answers when the user clicks "Start Call." Usually this is a receptionist or operator.
- **`global_prompt`** is prepended to every character's prompt. Use it for rules that apply to everyone (e.g., "don't reveal you're an AI").

### Sharing Scenarios

Scenario files are self-contained. You can share them with others by sending the `.yaml` file. The recipient drops it in their `scenarios/` folder and it works. Since character details are hidden in the UI, they can go in blind.

See `scenarios/example_template.yaml` for a full template with comments.

## The Web UI

### Dashboard

The home page shows:
- **Provider status** — green/red indicators for LLM, TTS, STT, and microphone. All must be green to start a call.
- **Scenario cards** — available scenarios with company name, description, difficulty, and objective. Click "Start Call" to begin.

### Settings

Configure all providers through the browser:
- Select providers from dropdowns
- Enter API keys
- Test connections with instant validation
- Browse and preview available voices
- Select your microphone

Changes save directly to `config.yaml`.

### Session

The active call screen:
- Real-time conversation transcript
- Status indicators: "Listening...", "[Name] is thinking...", "[Name] is speaking..."
- Controls: mute/unmute, dial extension, end call, volume slider
- First-time users see a "How This Works" overlay explaining the basics

### Help

In-app documentation covering:
- What is vishing
- How to use PhoneyBaloney
- Tips for beginners
- Creating scenarios
- Adding providers
- Troubleshooting

## Project Structure

```
phoneybaloney/
├── phoneybaloney/          # Main package
│   ├── app.py              # FastAPI web application
│   ├── engine.py           # Conversation engine
│   ├── config.py           # Configuration management
│   ├── session.py          # Session and transcript logging
│   ├── audio.py            # Audio playback utilities
│   ├── scenarios.py        # Scenario loading
│   ├── providers/          # Plugin-based provider system
│   │   ├── base.py         # Abstract base classes
│   │   ├── llm/            # Ollama, OpenAI, Claude
│   │   ├── tts/            # pyttsx3, Coqui, Google, ElevenLabs
│   │   └── stt/            # Whisper, Vosk, Google, OpenAI API
│   └── web/                # HTML templates, CSS, JavaScript
├── scenarios/              # YAML scenario files
├── transcripts/            # Saved session logs
├── requirements/           # Tiered dependency files
├── docs/                   # Developer documentation
├── config.example.yaml     # Fully documented config template
├── setup.py                # Cross-platform installer
├── start.bat               # Windows launcher (double-click)
└── start.sh                # Mac/Linux launcher
```

## Troubleshooting

### Setup Issues

**Python version too old?**
PhoneyBaloney requires Python 3.10+. Download the latest from [python.org](https://www.python.org/downloads/).

**PyAudio installation fails?**
SpeechRecognition uses PyAudio under the hood for microphone access. PyAudio needs a system audio library to compile:
- **Windows:** `pip install pyaudio` usually works out of the box (pre-built wheel)
- **Mac:** Run `brew install portaudio` first, then `pip install pyaudio`
- **Linux:** Run `sudo apt install portaudio19-dev` first, then `pip install pyaudio`

The setup script handles this automatically, but if it fails, the above manual steps should fix it.

### Runtime Issues

**Ollama not running?**
Open a terminal and run `ollama serve`. If Ollama isn't installed, download it from [ollama.ai](https://ollama.ai), install it, then run `ollama pull llama3` to download a model.

**No microphone detected?**
- Check that your microphone is plugged in and not muted
- **Windows:** Settings > Privacy & Security > Microphone — make sure apps can access your mic
- **Mac:** System Settings > Privacy & Security > Microphone
- **Linux:** Check `pavucontrol` or `alsamixer`

**Provider shows red on the dashboard?**
Click the provider in Settings and use "Test Connection" for a specific error message. Common causes:
- API key is empty or invalid
- Ollama isn't running or the model isn't downloaded
- Internet connection required for cloud providers

**Slow responses?**
- Use a smaller LLM model (e.g., `llama3` instead of `llama3:70b`)
- Use pyttsx3 for instant TTS (no network delay)
- Use a smaller Whisper model (`tiny` or `base` instead of `large`)

**Browser doesn't open automatically?**
Navigate manually to `http://localhost:8080` in any browser.

## Adding Custom Providers

PhoneyBaloney's plugin architecture makes it straightforward to add new providers. Each provider type (LLM, TTS, STT) has a simple abstract base class with 3-4 methods to implement.

See `docs/adding-providers.md` for a complete step-by-step guide with example code.

## Contributing

Issues and pull requests welcome! Find us on Twitter [@hackandbackpack](https://twitter.com/hackandbackpack) or on Discord at [RedSiege.com/Discord](https://redsiege.com/Discord).
