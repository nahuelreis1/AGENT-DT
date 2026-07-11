# Tasks: n8n Workflows — Dynamic & Analysis Layers

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 500-700 (2× SDK code + README) |
| 400-line budget risk | Low |
| Chained PRs recommended | No (single PR — both flows + docs) |
| Suggested split | Single PR — both flows + README |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: Yes
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Both flows + README | PR 1 | SDK code is declarative; review = n8n UI visual + declarative TS read |

## Phase 1: Flow 1 — Dynamic Layer

- [x] 1.1 Create `n8n/flow1-dynamic-layer.ts` with 9 nodes per design §Flow 1 Node Graph (Telegram Trigger, Telegram Get File, OpenAI Whisper STT, HTTP Request Contexto, DeepSeek Model subnode, Simple Memory subnode, AI Agent, ElevenLabs TTS, HTTP Request POST Audio)
- [x] 1.2 Implement Flow 1 system prompt: Rioplatense personality + instructions + `{{ $('HTTP Request Contexto').item.json.body }}` context injection
- [x] 1.3 Configure Simple Memory: `sessionKey={{ $json.message.chat.id }}`, `contextWindowLength=10` for per-chat isolation
- [x] 1.4 Use `placeholder('NGROK_AUDIO_PLAYER_URL')` and `placeholder('VOICE_ID')` for ngrok URL and ElevenLabs voice
- [x] 1.5 Call `get_sdk_reference` (section=patterns) and `get_node_types` for the 9 node types; capture discriminators
- [x] 1.6 Run `validate_workflow` on Flow 1 code; fix validation errors until 0 errors
- [x] 1.7 Call `create_workflow_from_code` for Flow 1 in project `p3bjSbaomjjaHR3z`, name "AI DT - Dynamic Layer", description 1-2 sentences

## Phase 2: Flow 2 — Analysis Layer

- [x] 2.1 Create `n8n/flow2-analysis-layer.ts` with Webhook, Switch (4 outputs, `fallbackOutput=extra`), 4× HTTP Contexto, 4× AI Agent + DeepSeek subnodes (NO memory), HTTP Predicciones, HTTP POST Prediccion (momento 3), 4× ElevenLabs TTS, 4× HTTP POST Audio
- [x] 2.2 Implement Switch rules: output 0=1,2 / 1=3 / 2=4,5 / 3=6 / extra=fallback (`combinator: 'or'` for momentos 1,2 and 4,5)
- [x] 2.3 Implement 4 branch system prompts (Diagnóstico, DT, Reacción, Auditoría) with branch-specific focus text from design §Flow 2 System Prompts
- [x] 2.4 Wire momento 6 predictions block: `{{ $('HTTP Request Predicciones').item.json }}` + "Compara... Se honesto." into Auditoría system prompt
- [x] 2.5 Wire momento 3 POST prediccion with `jsonBody: {momento: 3, content: "{{ $json.output }}"}` BEFORE TTS node
- [x] 2.6 Run `validate_workflow` on Flow 2 code; fix validation errors until 0 errors
- [x] 2.7 Call `create_workflow_from_code` for Flow 2 in project `p3bjSbaomjjaHR3z`, name "AI DT - Analysis Layer", description 1-2 sentences

## Phase 3: Documentation

- [x] 3.1 Create `n8n/README.md`: 4 credentials (Telegram/OpenAI/DeepSeek/ElevenLabs), Telegram bot creation, ngrok setup, voiceId selection, 9-step manual testing checklist from design §Manual Testing Checklist
- [x] 3.2 Document `placeholder()` values (NGROK_AUDIO_PLAYER_URL, VOICE_ID): how to replace per session after workflow creation
- [x] 3.3 Document rollback procedure: `archive_workflow` on both IDs + delete `n8n/README.md` (no backend changes)

## Phase 4: Verification

- [ ] 4.1 Run `search_workflows` in project `p3bjSbaomjjaHR3z` — confirm both flows exist, inactive
- [ ] 4.2 Run `prepare_test_pin_data` on each flow to capture schemas for future test runs
- [ ] 4.3 Document open questions from design §Open Questions in apply report (voiceId selection, outputPropertyName binary check, OR combinator Switch v3.4, switchCase onCase multi-node syntax)
- [ ] 4.4 Update `openspec/changes/n8n-workflows/state.yaml` with tasks completion markers after apply
