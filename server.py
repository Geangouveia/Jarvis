import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

from core.system_controller import SystemController
from core.voice_engine import VoiceEngine, VOICES
from core.notes_manager import NotesManager
from core.brain import JarvisBrain

app = FastAPI(title="J.A.R.V.I.S. PC Assistant")

# Inicialização de Módulos
brain = JarvisBrain()
voice_engine = VoiceEngine()

# Diretórios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

class CommandRequest(BaseModel):
    command: str
    voice: str = None

class ConfigUpdateRequest(BaseModel):
    gemini_api_key: str = None
    voice: str = None
    user_name: str = None

class NoteCreateRequest(BaseModel):
    content: str

@app.post("/api/command")
async def handle_command(req: CommandRequest):
    """Executa um comando de voz ou texto e sintetiza o áudio da resposta do Jarvis."""
    # 1. Processa comando pelo cérebro do Jarvis
    result = await brain.process_command(req.command)
    speech_text = result.get("speech", "")

    # 2. Sintetiza áudio com voz neural Edge-TTS
    selected_voice = req.voice or brain.config.get("voice", "pt-BR-AntonioNeural")
    audio_path = await voice_engine.text_to_speech(speech_text, selected_voice)

    audio_filename = os.path.basename(audio_path) if audio_path else None

    return {
        "success": True,
        "command": req.command,
        "speech": speech_text,
        "action": result.get("action", "unknown"),
        "details": result.get("details", None),
        "audio_url": f"/api/audio/{audio_filename}" if audio_filename else None
    }

@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    filepath = os.path.join(voice_engine.cache_dir, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Áudio não encontrado")
    return FileResponse(filepath, media_type="audio/mpeg")

@app.get("/api/telemetry")
async def get_telemetry():
    return SystemController.get_system_telemetry()

@app.get("/api/notes")
async def get_notes():
    return NotesManager.list_notes()

@app.post("/api/notes")
async def add_note(req: NoteCreateRequest):
    note = NotesManager.add_note(req.content)
    return {"success": True, "note": note}

@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: int):
    NotesManager.delete_note(note_id)
    return {"success": True}

@app.get("/api/screenshots")
async def list_screenshots():
    if not os.path.exists(SCREENSHOTS_DIR):
        return []
    files = [f for f in os.listdir(SCREENSHOTS_DIR) if f.endswith(".png")]
    files.sort(reverse=True)
    return [{"filename": f, "url": f"/api/screenshots/{f}"} for f in files[:20]]

@app.get("/api/screenshots/{filename}")
async def get_screenshot(filename: str):
    filepath = os.path.join(SCREENSHOTS_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Captura de tela não encontrada")
    return FileResponse(filepath, media_type="image/png")

@app.get("/api/config")
async def get_config():
    cfg = dict(brain.config)
    # Mascara a chave da API por segurança na visualização
    key = cfg.get("gemini_api_key", "")
    cfg["has_api_key"] = bool(key)
    cfg["gemini_api_key_masked"] = (key[:6] + "..." + key[-4:]) if len(key) > 10 else ("Configurada" if key else "")
    cfg["available_voices"] = VOICES
    return cfg

@app.post("/api/config")
async def update_config(req: ConfigUpdateRequest):
    updates = {}
    if req.gemini_api_key is not None:
        updates["gemini_api_key"] = req.gemini_api_key.strip()
    if req.voice is not None:
        updates["voice"] = req.voice
        voice_engine.set_voice(req.voice)
    if req.user_name is not None:
        updates["user_name"] = req.user_name.strip()
    
    saved = brain.save_config(updates)
    return {"success": True, "config": saved}

# WebSocket para telemetria em tempo real (atualização viva do HUD)
@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = SystemController.get_system_telemetry()
            await websocket.send_json(data)
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket erro: {e}")

# Servir Frontend
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"status": "JARVIS Backend Ativo", "docs": "/docs"})

if __name__ == "__main__":
    print("\n==========================================")
    print("   J.A.R.V.I.S. - PROTOCOLO STARK INICIADO")
    print("   Acesse o HUD em: http://127.0.0.1:8000")
    print("==========================================\n")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)
