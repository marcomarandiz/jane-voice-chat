"""
Text-to-Speech module using Chatterbox or fallbacks.
"""

import asyncio
from typing import Optional
from pathlib import Path

import numpy as np
from loguru import logger


class ChatterboxTTS:
    """Text-to-Speech using Chatterbox or fallbacks."""
    
    def __init__(
        self,
        voice_sample: Optional[str] = None,
        device: str = "auto",
    ):
        self.voice_sample = voice_sample
        self.device = device
        self.model = None
        self._backend = "mock"
        self._load_model()
    
    def _load_model(self):
        """Load the TTS model."""
        # Try Chatterbox
        try:
            from chatterbox.tts import ChatterboxTTS as CBModel
            logger.info("Loading Chatterbox TTS...")
            self.model = CBModel.from_pretrained(device=self._get_device())
            self._backend = "chatterbox"
            logger.info("✅ Chatterbox loaded")
            return
        except ImportError:
            logger.warning("Chatterbox not installed")
        except Exception as e:
            logger.warning(f"Chatterbox failed: {e}")
        
        # Try XTTS
        try:
            from TTS.api import TTS
            logger.info("Loading Coqui XTTS...")
            self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            self._backend = "xtts"
            logger.info("✅ XTTS loaded")
            return
        except ImportError:
            logger.warning("Coqui TTS not installed")
        except Exception as e:
            logger.warning(f"XTTS failed: {e}")
        
        # Mock mode
        logger.warning("⚠️ No TTS backend - using mock mode (silence)")
        self._backend = "mock"
    
    def _get_device(self) -> str:
        if self.device != "auto":
            return self.device
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        return "cpu"
    
    async def synthesize(self, text: str) -> np.ndarray:
        """Synthesize speech from text."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._synthesize_sync, text)
    
    def _synthesize_sync(self, text: str) -> np.ndarray:
        """Synchronous synthesis."""
        if self._backend == "chatterbox":
            if self.voice_sample:
                audio = self.model.generate(text, audio_prompt=self.voice_sample)
            else:
                audio = self.model.generate(text)
            return audio.cpu().numpy().astype(np.float32)
        
        elif self._backend == "xtts":
            if self.voice_sample:
                wav = self.model.tts(text=text, speaker_wav=self.voice_sample, language="en")
            else:
                wav = self.model.tts(text=text, language="en")
            return np.array(wav, dtype=np.float32)
        
        else:
            # Mock mode - return short silence
            logger.debug(f"Mock TTS: '{text[:50]}...'")
            # 0.5 seconds of silence at 24kHz
            return np.zeros(12000, dtype=np.float32)
