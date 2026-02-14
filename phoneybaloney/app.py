"""FastAPI web application."""
import asyncio
import base64
import json
import webbrowser
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from phoneybaloney.config import AppConfig, load_config, save_config, generate_default_config
from phoneybaloney.scenarios import list_scenarios, load_scenario, get_character
from phoneybaloney.session import Session
from phoneybaloney.providers.base import ProviderRegistry
from phoneybaloney.providers.llm import register_all_llm
from phoneybaloney.providers.tts import register_all_tts
from phoneybaloney.providers.stt import register_all_stt
from phoneybaloney.engine import ConversationEngine
from phoneybaloney.audio import list_microphones

PROJECT_ROOT = Path(__file__).parent.parent
WEB_DIR = Path(__file__).parent / "web"
TEMPLATES = Jinja2Templates(directory=str(WEB_DIR / "templates"))
CONFIG_PATH = str(PROJECT_ROOT / "config.yaml")
SCENARIOS_DIR = str(PROJECT_ROOT / "scenarios")
TRANSCRIPTS_DIR = str(PROJECT_ROOT / "transcripts")


def _build_registry() -> ProviderRegistry:
    """Build and return a fully-populated provider registry."""
    registry = ProviderRegistry()
    register_all_llm(registry)
    register_all_tts(registry)
    register_all_stt(registry)
    return registry


def _get_config() -> AppConfig:
    """Load config, generating default if needed."""
    if not Path(CONFIG_PATH).exists():
        generate_default_config(CONFIG_PATH)
    return load_config(CONFIG_PATH)


def create_app(config_path: str | None = None, test_mode: bool = False) -> FastAPI:
    app = FastAPI(title="PhoneyBaloney")

    if not test_mode:
        static_dir = str(WEB_DIR / "static")
        Path(static_dir).mkdir(parents=True, exist_ok=True)
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    registry = _build_registry()

    # --- Page routes ---

    @app.get("/")
    async def home(request: Request):
        if test_mode:
            return JSONResponse({"page": "home"})
        config = _get_config()
        if not Path(CONFIG_PATH).exists() or config.raw.get("first_run", False):
            return TEMPLATES.TemplateResponse("wizard.html", {"request": request})
        return TEMPLATES.TemplateResponse("home.html", {"request": request})

    @app.get("/settings")
    async def settings(request: Request):
        if test_mode:
            return JSONResponse({"page": "settings"})
        return TEMPLATES.TemplateResponse("settings.html", {"request": request})

    @app.get("/help")
    async def help_page(request: Request):
        if test_mode:
            return JSONResponse({"page": "help"})
        return TEMPLATES.TemplateResponse("help.html", {"request": request})

    @app.get("/session")
    async def session_page(request: Request):
        if test_mode:
            return JSONResponse({"page": "session"})
        return TEMPLATES.TemplateResponse("session.html", {"request": request})

    @app.get("/wizard")
    async def wizard_page(request: Request):
        if test_mode:
            return JSONResponse({"page": "wizard"})
        return TEMPLATES.TemplateResponse("wizard.html", {"request": request})

    # --- API routes ---

    @app.get("/api/status")
    async def api_status():
        config = _get_config()
        results = {}
        for provider_type in ["llm", "tts", "stt"]:
            try:
                getter = getattr(registry, f"get_{provider_type}")
                provider_name = getattr(config, f"{provider_type}_provider")
                provider = getter(provider_name)
                provider_config = getattr(config, f"get_{provider_type}_config")()
                provider.initialize(provider_config)
                ok, msg = provider.validate()
                results[provider_type] = {"ok": ok, "message": msg, "provider": provider_name}
            except Exception as e:
                results[provider_type] = {"ok": False, "message": str(e)}

        # Mic check
        try:
            mics = list_microphones()
            if mics:
                results["mic"] = {"ok": True, "message": f"{len(mics)} microphone(s) detected"}
            else:
                results["mic"] = {"ok": False, "message": "No microphones detected"}
        except Exception as e:
            results["mic"] = {"ok": False, "message": str(e)}

        return results

    @app.get("/api/scenarios")
    async def api_scenarios():
        scenarios = list_scenarios(SCENARIOS_DIR)
        return [
            {
                "filename": s.filename,
                "company": s.company,
                "description": s.description,
                "difficulty": s.difficulty,
                "objective": s.objective,
                "extensions_hint": s.extensions_hint,
                "starting_extension": s.starting_extension,
            }
            for s in scenarios
        ]

    @app.get("/api/config")
    async def api_get_config():
        config = _get_config()
        return config.raw

    @app.post("/api/config")
    async def api_save_config(request: Request):
        data = await request.json()
        config = AppConfig(
            llm_provider=data.get("llm_provider", "ollama"),
            tts_provider=data.get("tts_provider", "pyttsx3"),
            stt_provider=data.get("stt_provider", "whisper_local"),
            scenario=data.get("scenario", "megacorp"),
            log_transcripts=data.get("log_transcripts", True),
            raw=data,
        )
        save_config(config, CONFIG_PATH)
        return {"ok": True, "message": "Settings saved"}

    @app.get("/api/voices")
    async def api_voices():
        config = _get_config()
        try:
            tts = registry.get_tts(config.tts_provider)
            tts.initialize(config.get_tts_config())
            return tts.list_voices()
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

    @app.post("/api/validate/{provider_type}")
    async def api_validate(provider_type: str):
        config = _get_config()
        try:
            getter = getattr(registry, f"get_{provider_type}")
            provider_name = getattr(config, f"{provider_type}_provider")
            provider = getter(provider_name)
            provider_config = getattr(config, f"get_{provider_type}_config")()
            provider.initialize(provider_config)
            ok, msg = provider.validate()
            return {"ok": ok, "message": msg}
        except Exception as e:
            return {"ok": False, "message": str(e)}

    @app.get("/api/microphones")
    async def api_microphones():
        return list_microphones()

    # --- WebSocket session ---

    @app.websocket("/ws/session")
    async def ws_session(websocket: WebSocket):
        await websocket.accept()
        scenario_file = websocket.query_params.get("scenario", "")
        if not scenario_file:
            await websocket.send_json({"type": "error", "message": "No scenario specified"})
            await websocket.close()
            return

        config = _get_config()
        scenario_path = str(Path(SCENARIOS_DIR) / scenario_file)

        try:
            # Set up providers
            llm = registry.get_llm(config.llm_provider)
            llm.initialize(config.get_llm_config())
            tts = registry.get_tts(config.tts_provider)
            tts.initialize(config.get_tts_config())
            stt = registry.get_stt(config.stt_provider)
            stt.initialize(config.get_stt_config())

            engine = ConversationEngine(llm, tts, stt, config)
            engine.load_scenario(scenario_path)

            scenario = engine.scenario
            await websocket.send_json({
                "type": "scenario_info",
                "company": scenario.get("company", ""),
                "objective": scenario.get("objective", ""),
            })

            # Start call — get greeting
            await websocket.send_json({"type": "status", "status": "thinking", "character": engine.current_character["name"] if engine.current_character else ""})
            greeting = engine.start_call()
            character_name = engine.current_character["name"]

            await websocket.send_json({
                "type": "transcript",
                "speaker": character_name,
                "text": greeting,
            })

            # Synthesize and send audio
            try:
                voice_map = config.get_voice_map()
                gender = engine.current_character.get("voice", {}).get("gender", "female")
                voice_key = f"{gender}_default"
                audio_bytes = tts.synthesize(greeting, voice_map.get(voice_key, ""))
                await websocket.send_json({
                    "type": "audio",
                    "data": base64.b64encode(audio_bytes).decode(),
                })
            except Exception:
                pass  # TTS failure shouldn't kill the session

            await websocket.send_json({"type": "status", "status": "listening"})

            # Conversation loop
            muted = False
            while True:
                try:
                    raw = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                    msg = json.loads(raw)

                    if msg.get("type") == "end_call":
                        result = engine.end_call()
                        await websocket.send_json({"type": "call_ended"})
                        break

                    elif msg.get("type") == "dial":
                        ext = msg.get("extension", "")
                        await websocket.send_json({"type": "status", "status": "thinking"})
                        result = engine.process_input(f"Dial Extension {ext}")

                        if result["type"] == "switch":
                            await websocket.send_json({
                                "type": "transcript",
                                "speaker": result["character"],
                                "text": result["greeting"],
                            })
                            try:
                                gender = engine.current_character.get("voice", {}).get("gender", "female")
                                voice_key = f"{gender}_default"
                                audio_bytes = tts.synthesize(result["greeting"], voice_map.get(voice_key, ""))
                                await websocket.send_json({
                                    "type": "audio",
                                    "data": base64.b64encode(audio_bytes).decode(),
                                })
                            except Exception:
                                pass
                        elif result["type"] == "error":
                            await websocket.send_json({"type": "error", "message": result["message"]})

                        await websocket.send_json({"type": "status", "status": "listening"})

                    elif msg.get("type") == "mute":
                        muted = msg.get("muted", False)

                except asyncio.TimeoutError:
                    pass
                except WebSocketDisconnect:
                    engine.end_call()
                    break

                # Listen for speech (non-blocking check)
                if not muted:
                    try:
                        user_text = await asyncio.get_event_loop().run_in_executor(
                            None, lambda: stt.listen(2)
                        )
                        if user_text:
                            await websocket.send_json({
                                "type": "transcript",
                                "speaker": "You",
                                "text": user_text,
                            })
                            await websocket.send_json({
                                "type": "status",
                                "status": "thinking",
                                "character": engine.current_character["name"],
                            })

                            result = engine.process_input(user_text)

                            if result["type"] == "response":
                                await websocket.send_json({
                                    "type": "transcript",
                                    "speaker": result["speaker"],
                                    "text": result["text"],
                                })
                                try:
                                    gender = engine.current_character.get("voice", {}).get("gender", "female")
                                    voice_key = f"{gender}_default"
                                    audio_bytes = tts.synthesize(result["text"], voice_map.get(voice_key, ""))
                                    await websocket.send_json({
                                        "type": "audio",
                                        "data": base64.b64encode(audio_bytes).decode(),
                                    })
                                except Exception:
                                    pass
                                await websocket.send_json({
                                    "type": "status",
                                    "status": "speaking",
                                    "character": result["speaker"],
                                })
                            elif result["type"] == "end":
                                await websocket.send_json({"type": "call_ended"})
                                break
                            elif result["type"] == "switch":
                                await websocket.send_json({
                                    "type": "transcript",
                                    "speaker": result["character"],
                                    "text": result["greeting"],
                                })

                            await websocket.send_json({"type": "status", "status": "listening"})
                    except Exception:
                        pass

        except FileNotFoundError:
            await websocket.send_json({"type": "error", "message": f"Scenario not found: {scenario_file}"})
        except Exception as e:
            await websocket.send_json({"type": "error", "message": str(e)})
        finally:
            try:
                await websocket.close()
            except Exception:
                pass

    return app


def main():
    port = 8080
    print(f"\nPhoneyBaloney is running!")
    print(f"Open your browser to: http://localhost:{port}\n")
    webbrowser.open(f"http://localhost:{port}")
    uvicorn.run(create_app(), host="127.0.0.1", port=port)
