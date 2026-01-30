# OpenClaw Voice

**Open-source browser-based voice interface for AI assistants.**

Talk to your AI like you talk to Alexa — but self-hosted, private, and free from subscription fees.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)

## Why?

Voice AI platforms like ElevenLabs Agents ($0.08-0.12/min) and Retell.ai ($0.13-0.31/min) are expensive. OpenClaw Voice runs entirely on your own hardware for ~$0.003/min at scale.

## Features

- 🎙️ **Browser voice widget** — Push-to-talk or hands-free continuous mode
- 🚗 **Continuous mode** — Like Grok voice. Auto-listens after each response. Perfect for Tesla browser!
- 🔊 **Self-hosted STT** — Whisper Large V3 Turbo (runs on Mac/Linux/GPU)
- 🗣️ **Self-hosted TTS** — Chatterbox (MIT license, ElevenLabs quality)
- 🔌 **Pluggable backend** — Connect to any AI (OpenAI, Claude, Clawdbot, etc.)
- 🌐 **WebRTC audio** — Low latency (<500ms end-to-end achievable)
- 🏠 **Fully self-hosted** — Your data stays on your servers

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for client dev)
- CUDA GPU recommended (CPU works but slower)

### Installation

```bash
# Clone the repo
git clone https://github.com/Purple-Horizons/openclaw-voice.git
cd openclaw-voice

# Install Python dependencies
pip install -r requirements.txt

# Download models (first run only)
python scripts/download_models.py

# Start the voice server
python -m src.server.main

# Open http://localhost:8765 in your browser
```

### Docker (Recommended)

```bash
docker compose up
```

## Architecture

```
┌─────────────────┐     WebRTC      ┌─────────────────┐
│    Browser      │ ◄─────────────► │  Voice Gateway  │
│  (Voice Widget) │   Audio/Text    │    (Python)     │
└─────────────────┘                 └────────┬────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
              ┌─────▼─────┐          ┌───────▼───────┐        ┌──────▼──────┐
              │  Whisper  │          │   Your AI     │        │ Chatterbox  │
              │   (STT)   │          │   Backend     │        │    (TTS)    │
              └───────────┘          └───────────────┘        └─────────────┘
```

## Configuration

```yaml
# config.yaml
stt:
  model: "whisper-large-v3-turbo"
  device: "cuda"  # or "cpu", "mps" (Mac)

tts:
  model: "chatterbox"
  voice: "default"  # or path to voice sample for cloning

backend:
  type: "openai"  # or "clawdbot", "custom"
  url: "https://api.openai.com/v1"
  model: "gpt-4o"

server:
  host: "0.0.0.0"
  port: 8765
  ssl: false  # Set true + provide certs for production
```

## Supported Models

### Speech-to-Text (STT)
| Model | Speed | Quality | VRAM |
|-------|-------|---------|------|
| Whisper Large V3 Turbo | 216x realtime | Best | ~6GB |
| Distil-Whisper | 6x faster | Good | ~3GB |
| Whisper.cpp (CPU) | Slower | Best | N/A |

### Text-to-Speech (TTS)
| Model | Speed | Quality | Voice Cloning |
|-------|-------|---------|---------------|
| Chatterbox | ~1s | Excellent | 5-second samples |
| Kokoro-82M | <0.3s | Very Good | No |
| XTTS-v2 | ~1s | Excellent | 6-second samples |

## Browser Widget

Embed the voice widget in any webpage:

```html
<script src="https://unpkg.com/@openclaw/voice-widget"></script>
<openclaw-voice server="wss://your-server:8765"></openclaw-voice>
```

Or use React:

```jsx
import { VoiceWidget } from '@openclaw/voice-widget-react';

<VoiceWidget serverUrl="wss://your-server:8765" />
```

## API

### WebSocket Protocol

Connect to `ws://localhost:8765/ws` and send/receive JSON messages:

```javascript
// Start listening
{ "type": "start_listening" }

// Audio data (base64 PCM)
{ "type": "audio", "data": "base64..." }

// Stop listening
{ "type": "stop_listening" }

// Receive transcription
{ "type": "transcript", "text": "Hello world", "final": true }

// Receive AI response audio
{ "type": "audio_response", "data": "base64...", "text": "Hi there!" }
```

## Roadmap

- [x] Basic WebSocket voice gateway
- [x] Whisper STT integration
- [x] Chatterbox TTS integration
- [ ] WebRTC for lower latency
- [ ] Voice Activity Detection (VAD)
- [ ] Streaming responses
- [ ] Voice cloning UI
- [ ] Browser widget npm package
- [ ] React/Vue components
- [ ] Docker GPU support
- [ ] Kubernetes Helm chart

## Cost Comparison

| Platform | Cost/Minute |
|----------|-------------|
| ElevenLabs Conversational AI | $0.08-0.12 |
| Retell.ai | $0.13-0.31 |
| Vapi.ai | $0.05-0.15 |
| **OpenClaw Voice (self-hosted)** | **~$0.003** |

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License — see [LICENSE](LICENSE).

## Credits

- [Whisper](https://github.com/openai/whisper) — OpenAI
- [Chatterbox](https://github.com/resemble-ai/chatterbox) — Resemble AI
- [Silero VAD](https://github.com/snakers4/silero-vad) — Silero
- Built for [Clawdbot](https://github.com/clawdbot/clawdbot)

---

**Made with 🦀 by [Purple Horizons](https://purplehorizons.io)**
