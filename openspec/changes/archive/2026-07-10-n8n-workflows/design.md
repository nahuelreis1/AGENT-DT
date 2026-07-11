# Design: n8n Workflows — Dynamic & Analysis Layers

## Technical Approach

Two n8n workflows built via Workflow SDK (`@n8n/workflow-sdk`) + MCP. Flow 1 = `ai_agent_workflow` pattern (Telegram voice → STT → context → AI Agent with memory → TTS → audio POST). Flow 2 = `webhook_processing` + `multi_way_routing` hybrid (webhook → Switch 4 outputs → stateless AI Agents → TTS → audio). Both use DeepSeek (`@n8n/n8n-nodes-langchain.lmChatDeepSeek`), ElevenLabs TTS, and `placeholder()` for the ngrok audio-player URL. Created inactive in project `p3bjSbaomjjaHR3z`.

## Architecture Decisions

| # | Decision | Choice | Alternatives | Rationale |
|---|----------|--------|--------------|-----------|
| 1 | Flow 1 memory | Simple Memory (`memoryBufferWindow`, `contextWindowLength=10`) | Postgres Chat Memory | In-memory is zero-config; resets on restart but match is ~2h. Spec requires `sessionKey=chat.id`. |
| 2 | Flow 2 memory | None (stateless) | Simple Memory per branch | Fire-and-forget commentary; each momento is independent. Spec: "NO memory". |
| 3 | Webhook response | `responseMode=onReceived` (immediate 200) | `responseNode` (deferred) | Detector POSTs with `timeout=5.0`; must acknowledge before processing. Spec requires immediate 200. |
| 4 | Switch fallback | `options.fallbackOutput=extra` (NoOp) | Drop unmatched | Spec: "unmatched momento to fallback". Extra output = no AI agent runs. Prevents silent drop (NODE_FAMILY_GOTCHAS). |
| 5 | DeepSeek model node | `@n8n/n8n-nodes-langchain.lmChatDeepSeek` (v1) | OpenAI Chat Model with custom baseURL | Native DeepSeek node has `deepSeekApi` credential type and `model` param. Cleaner than OpenAI-compatible hack. |
| 6 | ElevenLabs config | Raw JSON from search results | `get_node_types` | `get_node_types` rejects `@elevenlabs/*` scope IDs ("invalid characters"). Document config from `search_nodes` output. |
| 7 | Context text access | `responseFormat=text`, `outputPropertyName=body` → `{{ $('HTTP Request Contexto').item.json.body }}` | `autodetect` | `/partido/contexto` returns `text/plain`. Setting `outputPropertyName=body` aligns property name with spec's expression. |
| 8 | Ngrok URL | `placeholder('NGROK_AUDIO_PLAYER_URL')` | Hardcode | URL is dynamic per ngrok session. Spec requires placeholder. |
| 9 | Momento 3 save | POST `/partido/prediccion` **before** TTS | After TTS | Spec: "save output via POST, then TTS → audio". Prediction must persist even if TTS/audio fails. |
| 10 | Momento 6 predictions | GET `/partido/predicciones` **before** AI Agent, inject into system prompt | Pass as user message | Spec: "inject `{{ $('HTTP Request Predicciones').item.json }}`". Agent needs predictions + context together in system prompt for comparison. |

## Flow 1: Dynamic Layer — Node Graph & Configuration

```
Telegram Trigger → Telegram Get File → OpenAI Whisper STT → HTTP Request Contexto
→ AI Agent (DeepSeek + Simple Memory) → ElevenLabs TTS → HTTP Request POST Audio
```

| # | Node Name | Type | Version | Key Parameters | Credentials | Data In | Data Out |
|---|-----------|------|---------|----------------|-------------|---------|----------|
| 1 | Telegram Trigger | `n8n-nodes-base.telegramTrigger` | 1.2 | `updates: ['message']`, `additionalFields.download: true` | `telegramApi` | — | `$json.message` (voice file_id in `$json.message.voice.file_id`, chat ID in `$json.message.chat.id`) |
| 2 | Telegram Get File | `n8n-nodes-base.telegram` | 1.2 | `resource: 'file'`, `operation: 'get'`, `fileId: {{ $json.message.voice.file_id }}`, `download: true` | `telegramApi` | Node 1 output | Binary `data` (voice .ogg) |
| 3 | OpenAI Whisper STT | `@n8n/n8n-nodes-langchain.openAi` | 2.3 | `resource: 'audio'`, `operation: 'transcribe'`, `binaryPropertyName: 'data'`, `options.language: 'es'` | `openAiApi` | Node 2 binary `data` | `$json.text` (transcribed Spanish text) |
| 4 | HTTP Request Contexto | `n8n-nodes-base.httpRequest` | 4.4 | `method: 'GET'`, `url: 'http://localhost:8000/partido/contexto'`, `responseFormat: 'text'`, `outputPropertyName: 'body'`, `authentication: 'none'` | — | Node 3 output (passed through) | `$json.body` (context text string) |
| 5a | DeepSeek Model | `@n8n/n8n-nodes-langchain.lmChatDeepSeek` | 1 | `model: 'deepseek-chat'` | `deepSeekApi` | — (sub-node, `ai_languageModel`) | — |
| 5b | Simple Memory | `@n8n/n8n-nodes-langchain.memoryBufferWindow` | 1.3 | `sessionIdType: 'customKey'`, `sessionKey: {{ $json.message.chat.id }}`, `contextWindowLength: 10` | — | — (sub-node, `ai_memory`) | — |
| 5 | AI Agent | `@n8n/n8n-nodes-langchain.agent` | 3.1 | `promptType: 'define'`, `text: {{ $('OpenAI Whisper STT').item.json.text }}`, `options.systemMessage: <system prompt>`, `subnodes: { model: 5a, memory: 5b }` | — | Node 4 (main input) | `$json.output` (AI response text) |
| 6 | ElevenLabs TTS | `@elevenlabs/n8n-nodes-elevenlabs.elevenLabs` | 1 | `resource: 'speech'`, `operation: 'textToSpeech'`, `text: {{ $json.output }}`, `model: 'eleven_multilingual_v2'`, `voiceId: <placeholder>` | `elevenLabsApi` | Node 5 output | Binary `data` (.mp3) |
| 7 | HTTP Request POST Audio | `n8n-nodes-base.httpRequest` | 4.4 | `method: 'POST'`, `url: placeholder('NGROK_AUDIO_PLAYER_URL')`, `sendBody: true`, `contentType: 'binaryData'`, `inputDataFieldName: 'data'` | — | Node 6 binary `data` | HTTP response |

### Flow 1 System Prompt

```
# PERSONALIDAD (fija)
Sos un analista de fútbol argentino. Hablás en español rioplatense.
Sos apasionado, directo y usás datos reales para respaldar tus opiniones.
Respondé de forma concisa (máximo 3-4 oraciones) porque tu respuesta va a ser leída en voz alta.

# INSTRUCCIONES (fijas)
- Siempre mencioná datos concretos cuando opines sobre un jugador.
- Si no tenés datos de algo, decilo honestamente.
- Tu tono es el de un amigo viendo el partido, no un robot.

# CONTEXTO DEL PARTIDO (dinámico)
{{ $('HTTP Request Contexto').item.json.body }}
```

## Flow 2: Analysis Layer — Node Graph & Configuration

```
Webhook /momento (POST) → Switch (4 outputs by momento)
  ├─ Output 0 (1,2): GET contexto → AI Agent Diagnóstico → TTS → POST audio
  ├─ Output 1 (3):    GET contexto → AI Agent DT → POST prediccion → TTS → POST audio
  ├─ Output 2 (4,5):  GET contexto → AI Agent Reacción → TTS → POST audio
  └─ Output 3 (6):    GET predicciones → GET contexto → AI Agent Auditoría → TTS → POST audio
```

| # | Node Name | Type | Version | Key Parameters | Credentials | Data In | Data Out |
|---|-----------|------|---------|----------------|-------------|---------|----------|
| 1 | Webhook | `n8n-nodes-base.webhook` | 2.1 | `httpMethod: 'POST'`, `path: 'momento'`, `responseMode: 'onReceived'`, `authentication: 'none'` | — | HTTP POST from detector | `$json.body` = `{momento, context_text, match_state}` |
| 2 | Switch | `n8n-nodes-base.switch` | 3.4 | `mode: 'rules'`, `rules.values[0..3]`, `options.fallbackOutput: 'extra'` | — | Node 1 `$json.body.momento` | Routes to output 0/1/2/3 or extra |
| 3 | HTTP Request Contexto | `n8n-nodes-base.httpRequest` | 4.4 | `method: 'GET'`, `url: 'http://localhost:8000/partido/contexto'`, `responseFormat: 'text'`, `outputPropertyName: 'body'` | — | Switch output | `$json.body` (context text) |
| 4 | AI Agent (×4) | `@n8n/n8n-nodes-langchain.agent` | 3.1 | `promptType: 'define'`, `text: {{ $json.body.context_text }}`, `options.systemMessage: <branch prompt>`, `subnodes: { model: deepSeekModel }` (NO memory) | — | Node 3 (main); Node 1 (for `context_text` via `$('Webhook').item.json.body.context_text`) | `$json.output` |
| 5 | HTTP Request Predicciones | `n8n-nodes-base.httpRequest` | 4.4 | `method: 'GET'`, `url: 'http://localhost:8000/partido/predicciones'`, `responseFormat: 'json'` | — | Switch output 3 | `$json` (predictions JSON array) |
| 6 | HTTP Request POST Prediccion | `n8n-nodes-base.httpRequest` | 4.4 | `method: 'POST'`, `url: 'http://localhost:8000/partido/prediccion'`, `sendBody: true`, `contentType: 'json'`, `specifyBody: 'json'`, `jsonBody: {"momento": 3, "content": "{{ $json.output }}"}` | — | AI Agent DT output | `{ok: true, momento: 3}` |
| 7 | ElevenLabs TTS | `@elevenlabs/n8n-nodes-elevenlabs.elevenLabs` | 1 | `resource: 'speech'`, `operation: 'textToSpeech'`, `text: {{ $json.output }}`, `model: 'eleven_multilingual_v2'`, `voiceId: <placeholder>` | `elevenLabsApi` | AI Agent output | Binary `data` (.mp3) |
| 8 | HTTP Request POST Audio | `n8n-nodes-base.httpRequest` | 4.4 | `method: 'POST'`, `url: placeholder('NGROK_AUDIO_PLAYER_URL')`, `sendBody: true`, `contentType: 'binaryData'`, `inputDataFieldName: 'data'` | — | TTS binary `data` | HTTP response |

**DeepSeek Model** (shared sub-node, `ai_languageModel`): `@n8n/n8n-nodes-langchain.lmChatDeepSeek` v1, `model: 'deepseek-chat'`, credential `deepSeekApi`. One instance per AI Agent node (4 total in Flow 2).

### Switch Routing Rules (exact configuration)

The Switch `mode: 'rules'` evaluates `{{ $json.body.momento }}` (number). Each rule's `conditions` uses `combinator: 'and'` with multiple `equals` operators OR'd via separate conditions in the same rule.

| Output Index | Rule Label | Conditions | Momentos | Target Chain |
|-------------|-----------|------------|----------|--------------|
| 0 | Diagnóstico | `momento` equals `1` **OR** `momento` equals `2` | 1 (15'), 2 (30') | GET contexto → AI Agent Diagnóstico → TTS → POST audio |
| 1 | DT | `momento` equals `3` | 3 (HT) | GET contexto → AI Agent DT → POST prediccion → TTS → POST audio |
| 2 | Reacción | `momento` equals `4` **OR** `momento` equals `5` | 4 (60'), 5 (75') | GET contexto → AI Agent Reacción → TTS → POST audio |
| 3 | Auditoría | `momento` equals `6` | 6 (FT+) | GET predicciones → GET contexto → AI Agent Auditoría → TTS → POST audio |
| extra (fallback) | — | No rule matches | 0 or invalid | NoOp (no AI agent) |

**Multiple conditions per rule**: Each rule's `conditions.conditions` array contains one entry per value. For Output 0: `[{leftValue: "{{ $json.body.momento }}", rightValue: 1, operator: {type: "number", operation: "equals"}}, {leftValue: "{{ $json.body.momento }}", rightValue: 2, operator: {type: "number", operation: "equals"}}]` with `combinator: 'or'`.

### Flow 2 System Prompts

**Common header** (all 4 agents, same as Flow 1 personality + instructions block):

```
# PERSONALIDAD (fija)
Sos un analista de fútbol argentino. Hablás en español rioplatense.
Sos apasionado, directo y usás datos reales para respaldar tus opiniones.
Respondé de forma concisa (máximo 3-4 oraciones) porque tu respuesta va a ser leída en voz alta.

# INSTRUCCIONES (fijas)
- Siempre mencioná datos concretos cuando opines sobre un jugador.
- Si no tenés datos de algo, decilo honestamente.
- Tu tono es el de un amigo viendo el partido, no un robot.
```

**Branch-specific focus** (appended after common header, before context):

| Output | Agent Name | Focus Text |
|--------|-----------|------------|
| 0 | AI Agent Diagnóstico | `# FOCO\nPrimeras impresiones. ¿Cómo se paró cada equipo? ¿Quién domina? ¿Dónde hay espacios? Diagnóstico táctico: ¿Quién rinde y quién no? ¿Riesgos? ¿Tendencias?` |
| 1 | AI Agent DT | `# FOCO\nSos el DT. ¿Qué cambios hacés? ¿Quién sale? ¿Quién entra? ¿Cambio táctico? Analizá el arbitraje.` |
| 2 | AI Agent Reacción | `# FOCO\n¿Cambió algo tras el entretiempo? ¿Se hicieron los cambios que recomendaste? Recta final: ¿Quién tiene más nafta? ¿Últimos cambios necesarios?` |
| 3 | AI Agent Auditoría | `# FOCO\nAuditoría completa. Compará tus predicciones del entretiempo con lo que pasó. ¿Quién tuvo razón, vos o el DT real?` |

**Context injection** (all branches, appended after focus):

```
# CONTEXTO DEL PARTIDO (dinámico)
{{ $('HTTP Request Contexto').item.json.body }}
```

**Momento 6 only** — predictions block (appended after context, before end):

```
# PREDICCIONES DEL ENTRETIEMPO
{{ $('HTTP Request Predicciones').item.json }}

Compará tus predicciones del entretiempo con lo que pasó. ¿Quién tuvo razón: vos o el DT real? Sé honesto.
```

**User message** (all Flow 2 branches): `{{ $('Webhook').item.json.body.context_text }}` — the webhook payload's `context_text` field (natural-language match snapshot from the detector).

## Expression Syntax

| Expression | Used In | Reads From | Purpose |
|------------|---------|------------|---------|
| `{{ $json.body.momento }}` | Switch `rules.values[].conditions` | Webhook node output | Route by momento number (1-6) |
| `{{ $('HTTP Request Contexto').item.json.body }}` | AI Agent `systemMessage` | HTTP Request Contexto output | Inject 7-section context text into system prompt |
| `{{ $json.output }}` | ElevenLabs `text`, POST Prediccion `content` | AI Agent node output | AI-generated response text |
| `{{ $json.message.chat.id }}` | Simple Memory `sessionKey` | Telegram Trigger output | Per-chat memory isolation key |
| `{{ $('OpenAI Whisper STT').item.json.text }}` | AI Agent `text` (Flow 1) | OpenAI Whisper node output | Whisper transcription as user message |
| `{{ $('Webhook').item.json.body.context_text }}` | AI Agent `text` (Flow 2) | Webhook node output | Detector's context snapshot as user message |
| `{{ $('HTTP Request Predicciones').item.json }}` | AI Agent Auditoría `systemMessage` | HTTP Request Predicciones output | Prior predictions JSON for comparison |

**SDK convention**: all `{{ }}` expressions are wrapped in `expr('...')` per SDK guidelines. Example: `expr('{{ $json.body.momento }}')`.

## SDK Code Structure

### Flow 1: Dynamic Layer

```typescript
import { workflow, node, trigger, placeholder, newCredential, languageModel, memory, expr } from '@n8n/workflow-sdk';

// 1. Declare all nodes first
const telegramTrigger = trigger({ type: 'n8n-nodes-base.telegramTrigger', version: 1.2,
  config: { name: 'Telegram Trigger', parameters: { updates: ['message'], additionalFields: { download: true } },
    credentials: { telegramApi: newCredential('Telegram') }, position: [240, 300] },
  output: [{ message: { voice: { file_id: 'voice123' }, chat: { id: 12345 } } }] });

const telegramGetFile = node({ type: 'n8n-nodes-base.telegram', version: 1.2,
  config: { name: 'Telegram Get File', parameters: { resource: 'file', operation: 'get',
    fileId: expr('{{ $json.message.voice.file_id }}'), download: true },
    credentials: { telegramApi: newCredential('Telegram') }, position: [460, 300] },
  output: [{ data: {} }] });

const whisperStt = node({ type: '@n8n/n8n-nodes-langchain.openAi', version: 2.3,
  config: { name: 'OpenAI Whisper STT', parameters: { resource: 'audio', operation: 'transcribe',
    binaryPropertyName: 'data', options: { language: 'es' } },
    credentials: { openAiApi: newCredential('OpenAI') }, position: [680, 300] },
  output: [{ text: 'texto transcrito' }] });

const contextoHttp = node({ type: 'n8n-nodes-base.httpRequest', version: 4.4,
  config: { name: 'HTTP Request Contexto', parameters: { method: 'GET',
    url: 'http://localhost:8000/partido/contexto', authentication: 'none',
    options: { response: { responseFormat: 'text', outputPropertyName: 'body' } } },
    position: [900, 300] },
  output: [{ body: 'contexto del partido' }] });

const deepSeekModel = languageModel({ type: '@n8n/n8n-nodes-langchain.lmChatDeepSeek', version: 1,
  config: { name: 'DeepSeek Model', parameters: { model: 'deepseek-chat' },
    credentials: { deepSeekApi: newCredential('DeepSeek') }, position: [1120, 460] } });

const simpleMemory = memory({ type: '@n8n/n8n-nodes-langchain.memoryBufferWindow', version: 1.3,
  config: { name: 'Simple Memory', parameters: { sessionIdType: 'customKey',
    sessionKey: expr('{{ $json.message.chat.id }}'), contextWindowLength: 10 }, position: [1120, 540] } });

const aiAgent = node({ type: '@n8n/n8n-nodes-langchain.agent', version: 3.1,
  config: { name: 'AI Agent', parameters: { promptType: 'define',
    text: expr('{{ $("OpenAI Whisper STT").item.json.text }}'),
    options: { systemMessage: '<system prompt with {{ $("HTTP Request Contexto").item.json.body }}>' } },
    subnodes: { model: deepSeekModel, memory: simpleMemory }, position: [1120, 300] },
  output: [{ output: 'AI response' }] });

const elevenLabsTts = node({ type: '@elevenlabs/n8n-nodes-elevenlabs.elevenLabs', version: 1,
  config: { name: 'ElevenLabs TTS', parameters: { resource: 'speech', operation: 'textToSpeech',
    text: expr('{{ $json.output }}'), model: 'eleven_multilingual_v2', voiceId: placeholder('VOICE_ID') },
    credentials: { elevenLabsApi: newCredential('ElevenLabs') }, position: [1340, 300] },
  output: [{ data: {} }] });

const postAudio = node({ type: 'n8n-nodes-base.httpRequest', version: 4.4,
  config: { name: 'HTTP Request POST Audio', parameters: { method: 'POST',
    url: placeholder('NGROK_AUDIO_PLAYER_URL'), sendBody: true, contentType: 'binaryData',
    inputDataFieldName: 'data' }, position: [1560, 300] },
  output: [{}] });

// 2. Compose workflow
export default workflow('ai-dt-dynamic', 'AI DT - Dynamic Layer')
  .add(telegramTrigger)
  .to(telegramGetFile)
  .to(whisperStt)
  .to(contextoHttp)
  .to(aiAgent)
  .to(elevenLabsTts)
  .to(postAudio);
```

### Flow 2: Analysis Layer

```typescript
import { workflow, node, trigger, switchCase, placeholder, newCredential, languageModel, expr } from '@n8n/workflow-sdk';

// 1. Declare nodes (abbreviated — full configs mirror Flow 1 patterns)
const webhook = trigger({ type: 'n8n-nodes-base.webhook', version: 2.1,
  config: { name: 'Webhook', parameters: { httpMethod: 'POST', path: 'momento',
    responseMode: 'onReceived', authentication: 'none' }, position: [240, 300] },
  output: [{ body: { momento: 3, context_text: '...', match_state: {} } }] });

const routeSwitch = switchCase({ type: 'n8n-nodes-base.switch', version: 3.4,
  config: { name: 'Switch', parameters: { mode: 'rules',
    rules: { values: [
      { conditions: { combinator: 'or', conditions: [
        { leftValue: expr('{{ $json.body.momento }}'), rightValue: 1, operator: { type: 'number', operation: 'equals' } },
        { leftValue: expr('{{ $json.body.momento }}'), rightValue: 2, operator: { type: 'number', operation: 'equals' } }
      ]}},
      { conditions: { combinator: 'and', conditions: [
        { leftValue: expr('{{ $json.body.momento }}'), rightValue: 3, operator: { type: 'number', operation: 'equals' } }
      ]}},
      { conditions: { combinator: 'or', conditions: [
        { leftValue: expr('{{ $json.body.momento }}'), rightValue: 4, operator: { type: 'number', operation: 'equals' } },
        { leftValue: expr('{{ $json.body.momento }}'), rightValue: 5, operator: { type: 'number', operation: 'equals' } }
      ]}},
      { conditions: { combinator: 'and', conditions: [
        { leftValue: expr('{{ $json.body.momento }}'), rightValue: 6, operator: { type: 'number', operation: 'equals' } }
      ]}}
    ]},
    options: { fallbackOutput: 'extra' } }, position: [460, 300] } });

// ... contextoHttp, deepSeekModel (×4), aiAgentDiagnostico, aiAgentDT, aiAgentReaccion,
//     aiAgentAuditoria, httpPredicciones, postPrediccion, elevenLabsTts (×4), postAudio (×4)

// 2. Compose with switch branching
export default workflow('ai-dt-analysis', 'AI DT - Analysis Layer')
  .add(webhook)
  .to(routeSwitch
    .onCase(0, contextoHttp.to(aiAgentDiagnostico.to(elevenLabsTts.to(postAudio))))
    .onCase(1, contextoHttp.to(aiAgentDT.to(postPrediccion.to(elevenLabsTts.to(postAudio)))))
    .onCase(2, contextoHttp.to(aiAgentReaccion.to(elevenLabsTts.to(postAudio))))
    .onCase(3, httpPredicciones.to(contextoHttp.to(aiAgentAuditoria.to(elevenLabsTts.to(postAudio))))));
```

### Credentials (both flows, `newCredential` placeholders)

| Credential Key | Node(s) Using It | Display Name |
|----------------|-----------------|--------------|
| `telegramApi` | Telegram Trigger, Telegram Get File | `newCredential('Telegram')` |
| `openAiApi` | OpenAI Whisper STT | `newCredential('OpenAI')` |
| `deepSeekApi` | DeepSeek Chat Model (×5 total: 1 Flow1 + 4 Flow2) | `newCredential('DeepSeek')` |
| `elevenLabsApi` | ElevenLabs TTS (×5 total: 1 Flow1 + 4 Flow2) | `newCredential('ElevenLabs')` |

## Data Flow — Sequence Diagrams

### Flow 1: Dynamic Layer

```
User sends voice message
  │
  ▼
Telegram Trigger (updates=['message'], download=true)
  │  $json.message.voice.file_id, $json.message.chat.id
  ▼
Telegram Get File (file/get, fileId=voice.file_id, download=true)
  │  binary data = voice .ogg
  ▼
OpenAI Whisper STT (audio/transcribe, binaryPropertyName='data', language='es')
  │  $json.text = "¿Cómo está jugando Messi?"
  ▼
HTTP Request Contexto (GET localhost:8000/partido/contexto, responseFormat=text)
  │  $json.body = "7-section context text..."
  ▼
AI Agent (DeepSeek + Simple Memory, sessionKey=chat.id, contextWindowLength=10)
  │  systemMessage: personality + instructions + {{ $('HTTP Request Contexto').item.json.body }}
  │  text (user msg): {{ $('OpenAI Whisper STT').item.json.text }}
  │  $json.output = "Messi está participando mucho..."
  ▼
ElevenLabs TTS (speech/textToSpeech, text={{ $json.output }}, model=eleven_multilingual_v2)
  │  binary data = response .mp3
  ▼
HTTP Request POST Audio (POST ngrok/play, contentType=binaryData, inputDataFieldName='data')
  │
  ▼
Audio plays on PC speakers
```

### Flow 2: Analysis Layer — Momento 3 (DT)

```
Backend MilestoneDetector fires momento 3 (status == HT)
  │
  │  POST http://localhost:5678/webhook/momento
  │  Body: {"momento": 3, "context_text": "...", "match_state": {...}}
  │  Timeout: 5.0s
  ▼
Webhook (POST /momento, responseMode=onReceived)
  │  ← 200 OK returned immediately
  │  $json.body.momento = 3
  ▼
Switch (mode=rules, evaluates $json.body.momento)
  │  Rule 1 matches (momento equals 3) → Output 1
  ▼
HTTP Request Contexto (GET /partido/contexto, responseFormat=text)
  │  $json.body = "context text..."
  ▼
AI Agent DT (DeepSeek, NO memory)
  │  systemMessage: personality + "Sos el DT..." + {{ $('HTTP Request Contexto').item.json.body }}
  │  text (user msg): {{ $('Webhook').item.json.body.context_text }}
  │  $json.output = "Cambiaría a López por Martínez..."
  ▼
HTTP Request POST Prediccion (POST /partido/prediccion)
  │  jsonBody: {"momento": 3, "content": "{{ $json.output }}"}
  │  ← {ok: true, momento: 3}
  ▼
ElevenLabs TTS → HTTP Request POST Audio → audio plays
```

### Flow 2: Analysis Layer — Momento 6 (Auditoría)

```
Backend MilestoneDetector fires momento 6 (status == FT)
  │
  │  POST http://localhost:5678/webhook/momento
  │  Body: {"momento": 6, "context_text": "...", "match_state": {...}}
  ▼
Webhook (POST /momento, responseMode=onReceived)
  │  ← 200 OK immediately
  │  $json.body.momento = 6
  ▼
Switch (mode=rules)
  │  Rule 3 matches (momento equals 6) → Output 3
  ▼
HTTP Request Predicciones (GET /partido/predicciones, responseFormat=json)
  │  $json = [{"momento": 3, "content": "Cambiaría a López..."}]
  ▼
HTTP Request Contexto (GET /partido/contexto, responseFormat=text)
  │  $json.body = "final context text..."
  ▼
AI Agent Auditoría (DeepSeek, NO memory)
  │  systemMessage: personality + "Auditoría completa..." + 
  │    {{ $('HTTP Request Contexto').item.json.body }} +
  │    "PREDICCIONES: {{ $('HTTP Request Predicciones').item.json }}"
  │  text (user msg): {{ $('Webhook').item.json.body.context_text }}
  │  $json.output = "Recomendé cambiar a López, el DT no lo hizo..."
  ▼
ElevenLabs TTS → HTTP Request POST Audio → audio plays
```

### Webhook Payload (from MilestoneDetector — exact shape)

```
POST {n8n_url}/webhook/momento
Content-Type: application/json
Timeout: 5.0s

Body:
{
  "momento": N,              // 1-6
  "context_text": str,       // match_state.get_context_text() — 7-section natural-language snapshot
  "match_state": dict        // match_state.get_state().model_dump(mode="json")
                             //   keys: home, away, events, status, fixture_id
}
```

| Momento | Trigger | Status Guard | Focus |
|---------|---------|-------------|-------|
| 1 | `elapsed >= 15` | `short == "1H"` | First impressions |
| 2 | `elapsed >= 30` | `short in ("1H","HT","2H")` | Tactical diagnosis |
| 3 | `short == "HT"` | — | DT mode (saves prediction) |
| 4 | `elapsed >= 60` | `short in ("HT","2H","ET","BT","P","AET","PEN","FT")` | Post-HT reaction |
| 5 | `elapsed >= 75` | `short in ("2H","ET","BT","P","AET","PEN","FT")` | Final stretch |
| 6 | `short in ("FT","AET","PEN")` | — | Audit (compares predictions) |

## File Changes

| File | Action | Description |
|------|--------|-------------|
| n8n instance (project `p3bjSbaomjjaHR3z`) | Create | Flow 1 "AI DT - Dynamic Layer" via `create_workflow_from_code` |
| n8n instance (project `p3bjSbaomjjaHR3z`) | Create | Flow 2 "AI DT - Analysis Layer" via `create_workflow_from_code` |
| `n8n/README.md` | Create | Setup guide: credentials, Telegram bot setup, ngrok, testing checklist |

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Validation | Both workflows pass `validate_workflow` with 0 errors | Call `validate_workflow` on full SDK code; fix errors; re-validate until clean |
| Pin data | Generate pin data for triggers + credential nodes | `prepare_test_pin_data` for each flow — pin Telegram Trigger (voice binary), Webhook (momento payload), and all credential nodes (DeepSeek, OpenAI, ElevenLabs) |
| Test run | Data flows correctly through each node chain | `test_workflow` with pin data — verify Switch routes correctly, AI Agent produces output, TTS produces binary, POST fires |
| Manual E2E | End-to-end voice interaction | Configure real credentials in n8n UI; start `audio_player.py` + ngrok; send Telegram voice; verify audio plays |
| Manual E2E | Momento webhook → commentary | `POST /mock/avanzar {momento: 3}` on backend; verify n8n receives, AI Agent responds, prediction saved, audio plays |

### Manual Testing Checklist (for `n8n/README.md`)

1. [ ] Create 4 credentials in n8n UI: Telegram, OpenAI, DeepSeek, ElevenLabs
2. [ ] Set ngrok URL in both workflows' POST Audio node (replace placeholder)
3. [ ] Set ElevenLabs `voiceId` in both workflows' TTS node
4. [ ] Start backend: `cd backend && uvicorn main:app --port 8000` (MOCK_MODE=true)
5. [ ] Start audio player: `python audio_player/player.py` (port 5555)
6. [ ] Start ngrok: `ngrok http 5555`
7. [ ] Activate Flow 1, send Telegram voice, verify audio plays
8. [ ] Activate Flow 2, `POST /mock/avanzar {momento: 3}`, verify prediction saved + audio
9. [ ] `POST /mock/avanzar {momento: 6}`, verify prediction comparison in audio

## Migration / Rollout

No migration required. Both workflows are created inactive — no data flows until manually activated and credentials configured. Rollback = `archive_workflow` on both + delete `n8n/README.md`. No backend changes.

## Open Questions

- [ ] ElevenLabs `voiceId` — user must select a voice in n8n UI; placeholder used in SDK code. Which voice ID?
- [ ] `outputPropertyName: 'body'` for HTTP Request Contexto — verify n8n v4.4 stores text response in `$json[outputPropertyName]` (not binary). If binary, expression must change to `$binary.data.data` or use `responseFormat: 'autodetect'`.
- [ ] Switch conditions `combinator: 'or'` — verify n8n Switch v3.4 supports OR combinator within a single rule (for momentos 1,2 and 4,5). If only `and` is supported, use 2 separate rules mapping to same output (not possible in Switch) or use expression mode instead.
- [ ] SDK `switchCase()` `onCase` chaining with multi-node branches — verify `.onCase(0, nodeA.to(nodeB.to(nodeC)))` syntax works for chains longer than 1 node.
