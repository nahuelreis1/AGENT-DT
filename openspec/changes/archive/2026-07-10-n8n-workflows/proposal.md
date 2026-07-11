# Proposal: n8n Workflows — Dynamic & Analysis Layers

## Intent

Backend is complete (231 tests, 99.92% coverage) but nothing consumes its data or milestone webhooks. This change builds the 2 n8n workflows for end-to-end operation: a dynamic layer (Telegram voice → spoken replies) and an analysis layer (6 milestone webhooks → spoken commentary). Without these, no AI, no voice, no user.

## Scope

### In Scope
- Workflow 1 "AI DT - Dynamic Layer": Telegram Trigger → Whisper STT (`es`) → GET `/partido/contexto` → AI Agent (DeepSeek + Simple Memory, `sessionKey=chat.id`) → ElevenLabs TTS → POST audio (ngrok)
- Workflow 2 "AI DT - Analysis Layer": Webhook `/momento` → Switch (4 outputs: 1,2/3/4,5/6) → 4 AI Agent personas → ElevenLabs TTS → POST audio; momento 3 saves prediction, momento 6 injects predictions
- `n8n/README.md` setup guide (credentials, bot, ngrok, testing)

### Out of Scope
- `audio_player.py` (step 7, separate change — dependency only)
- Top-level `README.md` (step 9, separate change)
- Any backend modification (frozen)

## Capabilities

### New Capabilities
- `n8n-workflows`: Two n8n workflows consuming backend HTTP + milestone webhooks to produce spoken AI commentary. Covers node graph, system prompts, memory session key, momento routing, and the momento 3→6 prediction-compare flow.

### Modified Capabilities
None — workflows consume existing `http-api` and `milestone-detector` specs unchanged.

## Approach

Create both workflows via n8n Workflow SDK + MCP. Flow 1 = `chatbot` pattern (trigger → AI Agent + memory → response). Flow 2 = `triage` + `content_generation` hybrid (webhook → switch → 4 branches → TTS → audio). All nodes available. Use `placeholder()` for ngrok URL. Validate via `validate_workflow` (no pytest).

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| n8n instance (`p3bjSbaomjjaHR3z`) | New | 2 workflows via MCP |
| `n8n/README.md` | New | Setup guide |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `audio_player.py` not built (step 7) | High | Validate via `validate_workflow`; audio deferred |
| ngrok URL dynamic | High | `placeholder()` in SDK; fill per session |
| ElevenLabs `@scope` ID rejected by `get_node_types` | Medium | Raw JSON workaround in apply |
| Simple Memory resets on restart | Low | OK for ~2h match |
| Manual credentials in UI | Low | In README |

## Rollback Plan

Delete both workflows via `archive_workflow`. Remove `n8n/README.md`. No backend changes — empty-URL no-op means disabling breaks nothing.

## Dependencies

- Backend FastAPI reachable (`/partido/contexto`, `/partido/prediccion`, `/partido/predicciones`)
- `audio_player.py` (step 7) for playback — not needed for creation/validation
- 4 n8n credentials: `telegramApi`, `openAiApi`, `deepSeekApi`, `elevenLabsApi`
- ngrok tunnel

## Success Criteria

- [ ] Both workflows pass `validate_workflow` (no errors)
- [ ] Flow 1: Telegram → Whisper → contexto → AI Agent → TTS → audio POST
- [ ] Flow 2 Switch routes 1,2/3/4,5/6 to correct AI Agent personas
- [ ] Momento 3 output POSTed to `/partido/prediccion`
- [ ] Momento 6 prompt includes `GET /partido/predicciones` data
- [ ] `n8n/README.md` documents credentials, bot, ngrok, testing
