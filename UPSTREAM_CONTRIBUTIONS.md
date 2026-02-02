# Improvements for Upstream

This document tracks improvements made to the OpenClaw Voice fork that could benefit the upstream project.

## 🎵 Critical Fix: Choppy Audio Playback

**Commit:** [5c8f240](https://github.com/marcomarandiz/jane-voice-chat/commit/5c8f240)

**Problem:** Audio was very choppy and unusable during streaming TTS playback.

**Root Cause:** The client was creating a NEW AudioContext for every single audio chunk, which is extremely inefficient and causes stuttering/gaps.

**Solution:**
- Reuse a single `playbackAudioContext` across all chunks
- Add `latencyHint: 'playback'` for browser optimization
- Properly schedule audio buffers to play sequentially using `nextStartTime` tracking
- Each chunk starts exactly when the previous one ends (no gaps)

**Files Changed:** `src/client/index.html`

**Key Code Changes:**
```javascript
// BEFORE: New AudioContext per chunk (bad!)
const audioCtx = new AudioContext({ sampleRate });
source.onended = () => {
    audioCtx.close();
    playNextInQueue();
};

// AFTER: Reuse one context, schedule buffers properly
if (!playbackAudioContext || playbackAudioContext.state === 'closed') {
    playbackAudioContext = new AudioContext({
        sampleRate: sampleRate,
        latencyHint: 'playback'  // Optimize for smooth playback
    });
}
const startTime = Math.max(nextStartTime, playbackAudioContext.currentTime);
source.start(startTime);
nextStartTime = startTime + buffer.duration;
playNextInQueue();  // Immediately queue next chunk
```

**Impact:** Transforms audio from unusable stuttering to smooth, natural playback.

---

## 🎛️ Setup Page for Easy Configuration

**Commit:** [1027a14](https://github.com/marcomarandiz/jane-voice-chat/commit/1027a14)

**Problem:** Users need to configure gateway URL and API key, but there was no easy way to do this without editing code.

**Solution:** Created `/setup.html` with:
- Pre-configured options for common scenarios (local network, Tailscale remote)
- Custom configuration form
- Saves settings to localStorage
- Clear instructions and troubleshooting tips

**Files Added:** `src/client/setup.html`

**User Experience:** One-click setup for common configurations, custom form for advanced users.

---

## 🔧 WebSocket Connection Error Handling

**Commit:** [524571f](https://github.com/marcomarandiz/jane-voice-chat/commit/524571f)

**Problem:** If WebSocket connection failed, the entire script would crash and the page would break.

**Solution:** Wrapped WebSocket connection in try-catch block in the client.

**Files Changed:** `src/client/index.html`

**Code:**
```javascript
// Wrap connection attempt to prevent page crash
try {
    connect();
} catch (e) {
    console.error('Initial connection failed:', e);
    errorEl.textContent = 'Connection failed. Please check settings.';
}
```

---

## ⚙️ Visual Status Indicator

**Commit:** [d4b45f2](https://github.com/marcomarandiz/jane-voice-chat/commit/d4b45f2)

**Problem:** Users couldn't tell if they were connected to the server or not.

**Solution:** Added a small status dot (red=disconnected, blue=connected) next to the settings button.

**Files Changed:** `src/client/index.html`

**Visual Design:** Subtle but clear - red dot when offline, blue when connected.

---

## 📝 Comprehensive Documentation

**Commit:** [28866f2](https://github.com/marcomarandiz/jane-voice-chat/commit/28866f2)

**Changes:** Updated README.md with:
- Clear installation steps
- Environment variable documentation
- Deployment options (local, Docker, cloud)
- Troubleshooting section
- Architecture overview

---

## 🤔 Recommendations for Upstream

### High Priority (Critical Usability)
1. **Audio Fix (5c8f240)** - Essential for production use
2. **Setup Page (1027a14)** - Makes first-run experience much better
3. **Connection Error Handling (524571f)** - Prevents crashes

### Medium Priority (Nice to Have)
4. **Status Indicator (d4b45f2)** - Helpful UX improvement
5. **Documentation (28866f2)** - Helps new users get started

### Suggested PR Structure
- **PR #1:** Audio playback fix (critical bug fix)
- **PR #2:** Setup page + connection error handling (onboarding improvements)
- **PR #3:** Status indicator + docs (polish)

---

## Testing Notes

All changes were tested on:
- **MacBook Pro** (Apple Silicon) via Tailscale HTTPS
- **Local network** (HTTP, same WiFi)
- **Browsers:** Brave (Chromium-based), Safari
- **Audio Quality:** Smooth playback with ElevenLabs streaming TTS

---

## Original Repo

- **Upstream:** https://github.com/Purple-Horizons/openclaw-voice
- **Our Fork:** https://github.com/marcomarandiz/jane-voice-chat
- **Author:** Purple Horizons (@Purple-Horizons)

---

## Contact

If Purple Horizons wants to discuss these improvements or needs help with integration, reach out via GitHub issues or PR discussion.

**Forked by:** Marco Marandiz (@marcomarandiz)  
**Date:** February 2, 2026
