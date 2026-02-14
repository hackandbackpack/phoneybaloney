# PhoneyBaloney

**A voice-based social engineering training tool.** Practice vishing (voice phishing) techniques by having real phone conversations with AI-powered characters — no real people involved, no risk, unlimited practice.

Originally inspired by [MakeAVish](https://github.com/brandonscholet/MakeAVish) by Brandon Scholet.

Shout out to Brandon for the original thought! Find us on Twitter [@hackandbackpack](https://twitter.com/hackandbackpack) or on Discord at [RedSiege.com/Discord](https://redsiege.com/Discord).

## Why PhoneyBaloney?

Vishing — voice phishing — is one of the most effective social engineering techniques in a penetration tester's toolkit. A well-crafted phone call can bypass technical controls that would stop most digital attacks. But practicing vishing is hard: you can't call real companies for training, and role-playing with colleagues only goes so far.

PhoneyBaloney solves this by giving you a realistic phone simulation powered by AI. You call into a simulated company, talk to AI characters who have their own personalities, knowledge, and security protocols, and try to extract sensitive information using only your voice and your wits.

**It's like a CTF, but for your voice.**

### Who Is This For?

- **Penetration testers** looking to sharpen their vishing skills before real engagements
- **Security training students** learning social engineering fundamentals for the first time
- **Red team operators** who want repeatable practice scenarios
- **Security awareness trainers** who want to demonstrate vishing techniques in a safe, controlled environment
- **Anyone curious** about how social engineering works and wants to try it hands-on

### What Does a Session Look Like?

You launch PhoneyBaloney, pick a scenario (like "MegaCorp"), and start the call. The company operator answers. From there, you talk your way through the organization — convincing employees to transfer you, give you information, or bypass security procedures. You speak into your microphone, the characters respond through your speakers, and a live transcript shows the conversation on screen.

The catch? You don't know who works there, what the extensions are, or what the security procedures look like. You have to figure all of that out through conversation — just like a real vishing engagement. The scenario is a puzzle, and the only way to solve it is to talk.

## Features

- **Real voice conversations** — Speak naturally into your microphone and hear AI characters respond. It feels like a real phone call.
- **Challenging scenarios** — Characters have personalities, security procedures, and interlocking dependencies. Information from one character unlocks progress with another.
- **Multiple AI options** — Choose from free local AI (runs on your machine, no cost) or premium cloud AI (OpenAI, Claude) for higher quality conversations.
- **Multiple voice options** — Free built-in voices to get started, or premium voices from Google and ElevenLabs for maximum realism.
- **Runs on your machine** — Everything can run locally with zero API keys and zero cost. Your conversations stay private.
- **Web-based interface** — Clean browser UI with live conversation transcript, provider status dashboard, and guided setup wizard. No terminal experience needed.
- **Create and share scenarios** — Write your own training scenarios and share them with your team. Character secrets stay hidden — recipients go in blind.
- **Session transcripts** — Every conversation is automatically saved for review, debriefs, and training assessments.
- **Cross-platform** — Works on Windows, Mac, and Linux.

## How the AI Works (Plain English)

PhoneyBaloney connects three types of AI together:

1. **The Brain** — An AI language model that reads the character's personality and your conversation, then generates what the character says next. This is the same technology behind ChatGPT and Claude. You can run it for free on your own computer using Ollama, or use a cloud service.

2. **The Voice** — A text-to-speech engine that converts the character's text response into spoken audio you hear through your speakers. Ranges from free built-in computer voices to premium human-like voices.

3. **The Ears** — A speech recognition engine that listens to your microphone and converts your spoken words into text the AI brain can understand. Can run locally on your machine or use a cloud service.

You pick which option you want for each piece. The cheapest setup (all free, all local) costs nothing and needs no internet. The premium setup uses cloud services for better quality but costs a few cents per conversation.

### Your Options

**The Brain (Language Model)**

| Option | Cost | What It Is |
|--------|------|-----------|
| **Ollama** | Free | Runs on your computer. Download from [ollama.ai](https://ollama.ai). Needs about 4GB of RAM. |
| **OpenAI** | Paid | ChatGPT's technology. Fast, high quality. Needs an API key from [platform.openai.com](https://platform.openai.com). |
| **Claude** | Paid | Anthropic's AI. Great at staying in character. Needs an API key from [console.anthropic.com](https://console.anthropic.com). |

**The Voice (Text-to-Speech)**

| Option | Cost | What It Is |
|--------|------|-----------|
| **pyttsx3** | Free | Uses your computer's built-in voices. No downloads, works instantly. Sounds robotic but functional. |
| **Coqui TTS** | Free | Higher quality AI voices that run on your computer. Needs a one-time download (~1GB). |
| **Google Cloud** | Paid | Natural sounding voices. Needs an API key from [console.cloud.google.com](https://console.cloud.google.com). |
| **ElevenLabs** | Paid | Premium human-like voices. The most realistic option. Needs an API key from [elevenlabs.io](https://elevenlabs.io). |

**The Ears (Speech Recognition)**

| Option | Cost | What It Is |
|--------|------|-----------|
| **Whisper Local** | Free | Runs on your computer. Good accuracy. Needs a one-time download (~150MB). |
| **Vosk** | Free | Lightweight option for older computers. Needs a model download from [alphacephei.com/vosk](https://alphacephei.com/vosk/models). |
| **Google Web Speech** | Free | Uses Google's online speech recognition. No downloads, but needs internet. |
| **OpenAI Whisper API** | Paid | Best accuracy. Uses your OpenAI API key (same one as the brain). |

## Getting Started

### What You Need

- **Python 3.10 or higher** — Download from [python.org](https://www.python.org/downloads/) if you don't have it
- **A microphone** — Built-in laptop mic, USB mic, or headset. PhoneyBaloney needs to hear you.
- **Speakers or headphones** — To hear the AI characters respond

### Installation

**Windows:**
```
git clone https://github.com/hackandbackpack/phoneybaloney.git
cd phoneybaloney
python setup.py
```

**Mac:**
```bash
git clone https://github.com/hackandbackpack/phoneybaloney.git
cd phoneybaloney
python3 setup.py
```

**Linux:**
```bash
git clone https://github.com/hackandbackpack/phoneybaloney.git
cd phoneybaloney
python3 setup.py
```

The setup script walks you through everything:
1. Checks that your Python version is new enough
2. Sets up an isolated environment so PhoneyBaloney doesn't interfere with anything else on your computer
3. Installs the core software
4. Installs audio components for your microphone and speakers
5. Asks if you want to install optional components (higher quality voices, offline speech recognition, etc.)
6. Creates your settings file with sensible defaults
7. Confirms everything is working
8. Tells you exactly how to launch the app

### Launching PhoneyBaloney

After setup, you'll see instructions specific to your operating system:

**Windows:** Double-click `start.bat` in the phoneybaloney folder.

**Mac / Linux:** Run `./start.sh` from the phoneybaloney folder.

Your browser will open automatically to the PhoneyBaloney dashboard. If it doesn't, open any browser and go to `http://localhost:8080`.

### First-Time Setup Wizard

The first time you launch PhoneyBaloney, a setup wizard walks you through picking your AI brain, voice, and speech recognition options. It tests each one to make sure it's working before you start. You can always change these later in the Settings page.

## Using PhoneyBaloney

### Starting a Call

1. On the dashboard, check that all status indicators are green (Brain, Voice, Ears, Microphone)
2. Pick a scenario — you'll see the company name, a brief description, the difficulty level, and your objective
3. Click **"Start Call"** — you're connected to the starting character and they greet you

### During a Call

- **Just talk.** Speak naturally into your microphone. The character responds through your speakers.
- **Watch the transcript.** The conversation appears in real-time on screen so you can follow along.
- **Transfer between characters.** Say **"Dial Extension [number]"** (e.g., "Dial Extension 3100") or use the on-screen dial pad.
- **End the call.** Say **"Terminate Call"** or click the End Call button.

### A Note About AI Models

The quality of your conversations depends heavily on which AI brain (language model) you're using. Larger, more capable models stay in character better, follow their instructions more closely, and produce more realistic conversations. Smaller or less capable models may:

- **Break character** — suddenly talk about being an AI or forget who they're supposed to be
- **Ignore their instructions** — share information they're supposed to protect, or refuse to share things they should
- **Make up nonsense** — invent departments, employees, or procedures that don't exist in the scenario
- **Give short or robotic answers** — respond with one-word answers instead of natural conversation
- **Go off the rails** — start talking about completely unrelated topics

This isn't a bug — it's a limitation of the AI model. Think of it like casting actors in a play: a skilled actor (larger model) delivers a convincing performance, while an inexperienced one (smaller model) might forget their lines or improvise badly.

**If conversations feel weird or characters aren't behaving right**, try upgrading your model before adjusting the scenario. For Ollama, try `llama3:8b` or larger. For cloud providers (OpenAI, Claude), the default models are already very capable.

### Tips for Beginners

- **Take notes.** The UI shows the conversation but won't track what you've discovered. Write down names, extensions, departments, and anything useful — just like a real engagement.
- **Each transfer is a fresh call.** When you dial a new extension, that character doesn't know you called before. Plan your approach for each person.
- **Listen carefully.** Characters will drop hints about other employees, departments, and procedures. These clues are how you progress through the scenario.
- **Be creative.** The AI responds dynamically. There's no single "right" script — try different approaches, pretexts, and techniques.
- **Don't give up.** The harder scenarios require multiple calls to different people, gathering small pieces of information that combine into a solution.

### After a Call

Your full conversation transcript is automatically saved to the `transcripts/` folder as a text file. Use it to review what worked, what didn't, and plan your next attempt.

## Settings and Configuration

PhoneyBaloney uses a settings file called `config.yaml`. You can change settings two ways:

1. **Through the web UI** — Click "Settings" in the navigation bar. Pick your options from dropdowns, enter API keys, test connections, and browse available voices. Changes save automatically.

2. **By editing the file directly** — Open `config.yaml` in any text editor. The file has three key lines at the top:

```yaml
llm_provider: ollama        # Your AI brain: ollama, openai, or claude
tts_provider: pyttsx3       # Your voice output: pyttsx3, coqui, google_tts, or elevenlabs
stt_provider: whisper_local # Your speech recognition: whisper_local, vosk, google_stt, or whisper_api
```

Change the name on any of these lines to switch providers. Only the provider you select gets used — everything else in the file is ignored. No need to delete or modify sections you aren't using.

For cloud services (OpenAI, Claude, Google, ElevenLabs), paste your API key into the appropriate section. Links to get API keys are included in the file and in the tables above.

See `config.example.yaml` for the fully documented settings file with every option explained.

### Voice Setup

Each scenario character has a gender (male/female) and the system automatically picks an appropriate voice from your selected voice provider. If you want to customize which specific voice is used, each provider section in the settings has a voice map where you can assign voices.

The Settings page in the web UI includes a voice browser — pick your provider, load the available voices, preview them, and assign the ones you like.

## Creating Your Own Scenarios

One of PhoneyBaloney's best features is the ability to create and share custom scenarios. You can design training exercises tailored to your team, your industry, or specific social engineering techniques you want to practice.

Scenarios are simple text files in the `scenarios/` folder. No programming required — if you can write an email, you can write a scenario.

**We have a complete step-by-step guide:** See **[docs/writing-scenarios.md](docs/writing-scenarios.md)** for everything you need to know, including:
- How scenario files work (explained in plain English)
- How to write effective character prompts
- How to build multi-character puzzles
- Common mistakes and how to avoid them
- A full example scenario with design notes

### Quick Overview

A scenario file defines a company and its employees. Each employee has a personality, a set of knowledge, and rules about what they will and won't share. Users call in and try to extract information through conversation.

The web UI only shows the company name, description, and objective — character details are completely hidden. Users discover everything by talking. This means you can share scenario files and recipients go in blind, just like a real engagement.

To add a scenario: save a `.yaml` file in the `scenarios/` folder and restart PhoneyBaloney. It appears on the dashboard automatically.

## Troubleshooting

### Setup Problems

**"Python not found" or version too old?**
Download Python 3.10 or newer from [python.org](https://www.python.org/downloads/). On Windows, make sure to check "Add Python to PATH" during installation.

**Microphone libraries won't install?**
The speech recognition system needs an audio library called PortAudio. The setup script usually handles this, but if it fails:
- **Windows:** Usually works automatically. Try running `pip install pyaudio` in the virtual environment.
- **Mac:** Run `brew install portaudio` first (requires [Homebrew](https://brew.sh)).
- **Linux:** Run `sudo apt install portaudio19-dev` first (Debian/Ubuntu) or the equivalent for your distribution.

### Problems During Use

**Ollama not connecting?**
Ollama needs to be running in the background. Open a terminal and run `ollama serve`. If you haven't installed Ollama yet, download it from [ollama.ai](https://ollama.ai), then run `ollama pull llama3` to download a language model.

**No microphone detected?**
- Make sure your mic is plugged in and not muted
- **Windows:** Go to Settings > Privacy & Security > Microphone and make sure apps have permission
- **Mac:** Go to System Settings > Privacy & Security > Microphone
- **Linux:** Check your audio settings with `pavucontrol` or `alsamixer`

**Dashboard shows a red indicator?**
Go to Settings, find the provider with the issue, and click "Test Connection" for a specific error message. Common fixes:
- Empty API key — paste in your key
- Ollama not running — start it with `ollama serve`
- Model not downloaded — run `ollama pull llama3`
- No internet — required for cloud providers (OpenAI, Claude, Google, ElevenLabs)

**Responses are slow?**
- Switch to a smaller language model (e.g., `llama3` instead of `llama3:70b`)
- Use pyttsx3 for voice output — it's instant since it runs locally
- Use a smaller speech recognition model (set Whisper to `tiny` or `base` instead of `large`)

**Character won't stop listening / keeps waiting for you to talk?**
The speech recognition listens until it detects silence. If you're in a noisy room — background conversations, TV, music, fan noise, keyboard clacking — it may never hear a "pause" and will keep listening indefinitely. A few ways to deal with this:
- **Use the mute button.** After you finish speaking, click mute. The AI processes what you said. Unmute when you're ready to talk again.
- **Cover your mic.** Place your hand over the microphone after you finish talking. Quick and low-tech.
- **Find a quieter spot.** A room with less background noise gives the best experience.
- **Use a headset.** A close-range headset mic picks up your voice clearly and rejects more background noise than a laptop mic across the room.

**Browser doesn't open?**
Navigate manually to `http://localhost:8080` in any browser (Chrome, Firefox, Edge, Safari — anything works).

## For Developers

### Project Structure

```
phoneybaloney/
├── phoneybaloney/          # Main application code
│   ├── app.py              # Web application and API
│   ├── engine.py           # Conversation logic
│   ├── config.py           # Settings management
│   ├── session.py          # Transcript logging
│   ├── audio.py            # Audio playback
│   ├── scenarios.py        # Scenario file loading
│   ├── providers/          # Swappable AI providers
│   │   ├── base.py         # Provider interfaces
│   │   ├── llm/            # Language model providers
│   │   ├── tts/            # Voice output providers
│   │   └── stt/            # Speech recognition providers
│   └── web/                # HTML, CSS, JavaScript
├── scenarios/              # Scenario files
├── transcripts/            # Saved session logs
├── requirements/           # Dependency lists
├── docs/                   # Developer documentation
├── config.example.yaml     # Documented settings template
├── setup.py                # Installer
├── start.bat               # Windows launcher
└── start.sh                # Mac/Linux launcher
```

### Adding Custom Providers

PhoneyBaloney's plugin system makes it straightforward to add new AI providers. Each provider type (brain, voice, ears) has a simple interface with 3-4 methods to implement. Create one Python file, register it, and it shows up in the settings automatically.

See `docs/adding-providers.md` for a complete walkthrough with example code.

## Contributing

Issues and pull requests welcome! Find us on Twitter [@hackandbackpack](https://twitter.com/hackandbackpack) or on Discord at [RedSiege.com/Discord](https://redsiege.com/Discord).
