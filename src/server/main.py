"""
OpenClaw Voice Server

WebSocket server that handles:
- Audio input from browser
- Speech-to-Text via Whisper
- AI backend communication
- Text-to-Speech via Chatterbox
- Audio streaming back to browser
"""

import asyncio
import base64
import json
import os
from pathlib import Path
from typing import Optional

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from loguru import logger
from pydantic_settings import BaseSettings

from .stt import WhisperSTT
from .tts import ChatterboxTTS
from .backend import AIBackend
from .vad import VoiceActivityDetector


class Settings(BaseSettings):
    """Server configuration."""
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8765
    
    # STT
    stt_model: str = "base"  # tiny, base, small, medium, large-v3-turbo
    stt_device: str = "auto"  # auto, cpu, cuda, mps
    
    # TTS
    tts_model: str = "chatterbox"
    tts_voice: Optional[str] = None  # Path to voice sample for cloning
    
    # AI Backend
    backend_type: str = "openai"  # openai, clawdbot, custom
    backend_url: str = "https://api.openai.com/v1"
    backend_model: str = "gpt-4o-mini"
    openai_api_key: Optional[str] = None
    
    # Audio
    sample_rate: int = 16000
    
    class Config:
        env_prefix = "OPENCLAW_"
        env_file = ".env"


settings = Settings()
app = FastAPI(title="OpenClaw Voice", version="0.1.0")

# Global instances (initialized on startup)
stt: Optional[WhisperSTT] = None
tts: Optional[ChatterboxTTS] = None
backend: Optional[AIBackend] = None
vad: Optional[VoiceActivityDetector] = None


@app.on_event("startup")
async def startup():
    """Initialize models on server start."""
    global stt, tts, backend, vad
    
    logger.info("Initializing OpenClaw Voice server...")
    
    # Initialize STT
    logger.info(f"Loading STT model: {settings.stt_model}")
    stt = WhisperSTT(
        model_name=settings.stt_model,
        device=settings.stt_device,
    )
    
    # Initialize TTS
    logger.info(f"Loading TTS model: {settings.tts_model}")
    tts = ChatterboxTTS(
        voice_sample=settings.tts_voice,
    )
    
    # Initialize AI backend
    logger.info(f"Connecting to backend: {settings.backend_type}")
    backend = AIBackend(
        backend_type=settings.backend_type,
        url=settings.backend_url,
        model=settings.backend_model,
        api_key=settings.openai_api_key or os.getenv("OPENAI_API_KEY"),
    )
    
    # Initialize VAD
    logger.info("Loading VAD model")
    vad = VoiceActivityDetector()
    
    logger.info("✅ OpenClaw Voice server ready!")


@app.get("/")
async def index():
    """Serve the demo page."""
    return FileResponse("src/client/index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle voice WebSocket connections."""
    await websocket.accept()
    logger.info("Client connected")
    
    audio_buffer = []
    is_listening = False
    
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            if msg["type"] == "start_listening":
                is_listening = True
                audio_buffer = []
                await websocket.send_json({"type": "listening_started"})
                logger.debug("Started listening")
                
            elif msg["type"] == "stop_listening":
                is_listening = False
                
                if audio_buffer:
                    # Combine audio chunks
                    audio_data = np.concatenate(audio_buffer)
                    
                    # Transcribe
                    logger.debug("Transcribing audio...")
                    transcript = await stt.transcribe(audio_data)
                    
                    await websocket.send_json({
                        "type": "transcript",
                        "text": transcript,
                        "final": True,
                    })
                    logger.info(f"Transcript: {transcript}")
                    
                    if transcript.strip():
                        # Get AI response
                        logger.debug("Getting AI response...")
                        response_text = await backend.chat(transcript)
                        
                        await websocket.send_json({
                            "type": "response_text",
                            "text": response_text,
                        })
                        logger.info(f"Response: {response_text}")
                        
                        # Generate speech
                        logger.debug("Generating speech...")
                        audio_response = await tts.synthesize(response_text)
                        
                        # Send audio back
                        audio_b64 = base64.b64encode(audio_response.tobytes()).decode()
                        await websocket.send_json({
                            "type": "audio_response",
                            "data": audio_b64,
                            "sample_rate": 24000,  # TTS output rate
                            "text": response_text,
                        })
                
                audio_buffer = []
                await websocket.send_json({"type": "listening_stopped"})
                logger.debug("Stopped listening")
                
            elif msg["type"] == "audio" and is_listening:
                # Decode base64 audio
                audio_bytes = base64.b64decode(msg["data"])
                audio_np = np.frombuffer(audio_bytes, dtype=np.float32)
                audio_buffer.append(audio_np)
                
            elif msg["type"] == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


# Serve static files for client
client_dir = Path(__file__).parent.parent / "client"
if client_dir.exists():
    app.mount("/static", StaticFiles(directory=str(client_dir)), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.server.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
