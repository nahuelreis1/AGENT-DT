# n8n-workflows Specification

## Purpose

Two n8n workflows producing spoken AI commentary from the backend HTTP API (mock/live identical for `/partido/*`). Flow 1 (Dynamic): Telegram voice -> Whisper (es) -> context -> AI Agent (DeepSeek + memory) -> TTS -> audio. Flow 2 (Analysis): webhook -> Switch -> stateless AI Agents per momento -> TTS -> audio; momento 3 saves predictions, momento 6 compares them.

## Requirements

### Requirement: Telegram Voice Trigger

The Dynamic Layer SHALL trigger on Telegram voice messages, downloaded as binary `data` (`updates=['message']`, `additionalFields.download=true`).

#### Scenario: Voice triggers workflow
- GIVEN a Telegram voice message
- WHEN the trigger fires
- THEN the workflow starts with the voice as binary `data`

### Requirement: Whisper STT Transcription

The OpenAI node SHALL transcribe the voice (`operation=transcribe`, `binaryPropertyName=data`, language `es`).

#### Scenario: Spanish voice transcribed
- GIVEN a Spanish voice in `data`
- WHEN Whisper runs
- THEN transcribed text becomes the AI Agent user message

### Requirement: Dynamic Context Fetch

An HTTP Request SHALL `GET /partido/contexto` (`responseFormat=text`) and inject it into the system prompt via `{{ $('HTTP Request Contexto').item.json.body }}`.

#### Scenario: Backend unreachable halts flow
- GIVEN the backend is down
- WHEN the HTTP Request runs
- THEN the node errors (no silent empty-context reply)

### Requirement: Dynamic AI Agent (DeepSeek + Memory)

The AI Agent SHALL use DeepSeek (`deepseek-chat`) with Simple Memory (`sessionKey=chat.id`, `contextWindowLength=10`). The system prompt combines FIXED personality and instructions (Rioplatense Spanish, concise, data-driven, honest) with DYNAMIC context above. The user message (`promptType=define`) is the Whisper text.

#### Scenario: Per-chat memory isolation
- GIVEN two chats send voice messages
- WHEN the AI Agent runs for each
- THEN each has independent memory (`sessionKey=chat.id`) keeping last 10 interactions

### Requirement: TTS, Audio Playback, and Player Dependency

ElevenLabs SHALL convert `{{ $json.output }}` to MP3 (`model=eleven_multilingual_v2`, binary `data`). An HTTP Request SHALL POST it to the ngrok player (`/play`, `contentType=binaryData`); the URL MUST use `placeholder()` (depends on `audio_player.py`, step 7).

#### Scenario: Ngrok URL is a placeholder
- GIVEN the workflow is created before the player runs
- WHEN the ngrok URL field is inspected
- THEN it contains a placeholder, not a hardcoded URL

### Requirement: Webhook Trigger (Momento)

The Webhook SHALL listen on `path=momento`, `httpMethod=POST`, `responseMode=onReceived` (immediate 200). Payload: `momento` (1-6), `match_state`, `context_text`.

#### Scenario: Immediate acknowledgment
- GIVEN the detector POSTs momento 3
- WHEN the webhook is received
- THEN a 200 returns before processing completes

### Requirement: Switch Routing

The Switch (`mode=rules`) SHALL route `{{ $json.body.momento }}`: 0->1,2; 1->3; 2->4,5; 3->6. Fallback (unmatched) SHALL be `extra` (NoOp).

#### Scenario: Unmatched momento to fallback
- GIVEN `momento=0`
- WHEN the Switch evaluates
- THEN the `extra` branch activates and no AI agent runs

### Requirement: Analysis Branch Common Structure

Each branch SHALL fetch `/partido/contexto` (text), run a stateless DeepSeek AI Agent (NO memory, fire-and-forget) injecting contexto into the system prompt and webhook `context_text` as user message (`promptType=define`), then TTS -> POST MP3 to the player.

#### Scenario: Common branch produces spoken output
- GIVEN any matched momento (1-6)
- WHEN the branch runs
- THEN context is fetched, the AI Agent responds, and audio is posted

### Requirement: Momento Branch Personas and Special Flows

Each output targets a distinct persona (below). Momento 3 SHALL save output via `POST /partido/prediccion` (`{momento: 3, content: "{{ $json.output }}"}`) before TTS. Momento 6 SHALL `GET /partido/predicciones` and inject `{{ $('HTTP Request Predicciones').item.json }}` with "Compara... Se honesto."

| Output | Momentos | Focus |
|---|---|---|
| 0 Diagnostico | 1 (15'), 2 (30') | Impressions; diagnosis; risks |
| 1 DT | 3 (HT) | "Sos el DT. Que cambios? Arbitraje." |
| 2 Reaccion | 4 (60'), 5 (75') | Halftime changes; stamina |
| 3 Auditoria | 6 (FT+) | Predictions vs reality; honest |

#### Scenario: Momento 3 saves prediction
- GIVEN `momento=3` and the AI Agent produced output
- WHEN the POST /prediccion node runs
- THEN the prediction persists for momento 6, then TTS -> audio

#### Scenario: Momento 6 compares predictions to reality
- GIVEN `momento=6` and a prediction was saved at momento 3
- WHEN the Auditoria branch runs
- THEN the AI Agent receives prior predictions and current context and compares them

### Requirement: Credentials and Workflow Lifecycle

Workflows SHALL use `newCredential()` placeholders for the 4 credentials (`telegramApi`, `openAiApi`, `deepSeekApi`, `elevenLabsApi`). Each SHALL pass `validate_workflow`, NOT activate on creation, and be created in project `p3bjSbaomjjaHR3z`. No real keys.

#### Scenario: Validation passes, created inactive
- GIVEN the SDK code is complete
- WHEN `validate_workflow` runs
- THEN no errors return and the workflow is created inactive
