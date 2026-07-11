import { workflow, trigger, switchCase, node, placeholder, newCredential, languageModel, expr } from '@n8n/workflow-sdk';

// ============================================================================
// Flow 2: Analysis Layer — Webhook /momento → Switch (4 branches) → AI Agents → TTS → Audio
// ============================================================================

// --- Trigger: Webhook ---
const webhook = trigger({
  type: 'n8n-nodes-base.webhook', version: 2.1,
  config: {
    name: 'Webhook',
    parameters: {
      httpMethod: 'POST',
      path: 'momento',
      responseMode: 'onReceived',
      authentication: 'none'
    },
    position: [240, 300]
  },
  output: [{ body: { momento: 3, context_text: 'snapshot del partido', match_state: {} } }]
});

// --- Switch: Route by momento ---
const routeSwitch = switchCase({
  type: 'n8n-nodes-base.switch', version: 3.4,
  config: {
    name: 'Switch (Momento)',
    parameters: {
      mode: 'rules',
      rules: {
        values: [
          // Rule 0: momento == 1 OR momento == 2 → Diagnóstico
          {
            conditions: {
              options: { caseSensitive: true, leftValue: '', typeValidation: 'strict' },
              combinator: 'or',
              conditions: [
                { leftValue: expr('{{ $json.body.momento }}'), rightValue: 1, operator: { type: 'number', operation: 'equals' } },
                { leftValue: expr('{{ $json.body.momento }}'), rightValue: 2, operator: { type: 'number', operation: 'equals' } }
              ]
            }
          },
          // Rule 1: momento == 3 → DT
          {
            conditions: {
              options: { caseSensitive: true, leftValue: '', typeValidation: 'strict' },
              combinator: 'and',
              conditions: [
                { leftValue: expr('{{ $json.body.momento }}'), rightValue: 3, operator: { type: 'number', operation: 'equals' } }
              ]
            }
          },
          // Rule 2: momento == 4 OR momento == 5 → Reacción
          {
            conditions: {
              options: { caseSensitive: true, leftValue: '', typeValidation: 'strict' },
              combinator: 'or',
              conditions: [
                { leftValue: expr('{{ $json.body.momento }}'), rightValue: 4, operator: { type: 'number', operation: 'equals' } },
                { leftValue: expr('{{ $json.body.momento }}'), rightValue: 5, operator: { type: 'number', operation: 'equals' } }
              ]
            }
          },
          // Rule 3: momento == 6 → Auditoría
          {
            conditions: {
              options: { caseSensitive: true, leftValue: '', typeValidation: 'strict' },
              combinator: 'and',
              conditions: [
                { leftValue: expr('{{ $json.body.momento }}'), rightValue: 6, operator: { type: 'number', operation: 'equals' } }
              ]
            }
          }
        ]
      },
      options: { fallbackOutput: 'extra' }
    },
    position: [460, 300]
  }
});

// ============================================================================
// Branch 0: Diagnóstico (momentos 1, 2)
// GET contexto → AI Agent Diagnóstico → TTS → POST audio
// ============================================================================

const contextoDiagnostico = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.4,
  config: {
    name: 'HTTP Request Contexto',
    parameters: {
      method: 'GET',
      url: 'http://localhost:8000/partido/contexto',
      authentication: 'none',
      options: { response: { response: { responseFormat: 'text', outputPropertyName: 'body' } } }
    },
    position: [680, 100]
  },
  output: [{ body: 'contexto del partido' }]
});

const deepSeekModelDiagnostico = languageModel({
  type: '@n8n/n8n-nodes-langchain.lmChatDeepSeek', version: 1,
  config: {
    name: 'DeepSeek Model Diagnostico',
    parameters: { model: 'deepseek-chat' },
    credentials: { deepSeekApi: newCredential('DeepSeek API') },
    position: [900, 160]
  }
});

const aiAgentDiagnostico = node({
  type: '@n8n/n8n-nodes-langchain.agent', version: 3.1,
  config: {
    name: 'AI Agent Diagnostico',
    parameters: {
      promptType: 'define',
      text: expr("{{ $('Webhook').item.json.body.context_text }}"),
      options: {
        systemMessage: expr(
          "# PERSONALIDAD (fija)\n" +
          "Sos un analista de fútbol argentino. Hablás en español rioplatense.\n" +
          "Sos apasionado, directo y usás datos reales para respaldar tus opiniones.\n" +
          "Respondé de forma concisa (máximo 3-4 oraciones) porque tu respuesta va a ser leída en voz alta.\n" +
          "\n" +
          "# INSTRUCCIONES (fijas)\n" +
          "- Siempre mencioná datos concretos cuando opines sobre un jugador.\n" +
          "- Si no tenés datos de algo, decilo honestamente.\n" +
          "- Tu tono es el de un amigo viendo el partido, no un robot.\n" +
          "\n" +
          "# CONTEXTO DEL PARTIDO (dinámico)\n" +
          "{{ $('HTTP Request Contexto').item.json.body }}\n" +
          "\n" +
          "# MOMENTO: Diagnóstico\n" +
          "Momento 1 (Min 15): ¿Cómo se paró cada equipo? ¿Quién domina? ¿Dónde hay espacios?\n" +
          "Momento 2 (Min 30): ¿Quién rinde y quién no? ¿Riesgos? ¿Tendencias?"
        )
      }
    },
    subnodes: { model: deepSeekModelDiagnostico },
    position: [900, 100]
  },
  output: [{ output: 'AI response text' }]
});

const ttsDiagnostico = node({
  type: '@elevenlabs/n8n-nodes-elevenlabs.elevenLabs', version: 1,
  config: {
    name: 'ElevenLabs TTS Diagnostico',
    parameters: {
      resource: 'speech',
      operation: 'textToSpeech',
      text: expr('{{ $json.output }}'),
      model: 'eleven_multilingual_v2',
      voiceId: placeholder('VOICE_ID')
    },
    credentials: { elevenLabsApi: newCredential('ElevenLabs API') },
    position: [1120, 100]
  },
  output: [{ data: {} }]
});

const postAudioDiagnostico = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.4,
  config: {
    name: 'HTTP Request POST Audio Diagnostico',
    parameters: {
      method: 'POST',
      url: placeholder('Your ngrok audio player URL (e.g. https://abc123.ngrok-free.app/play)'),
      sendBody: true,
      contentType: 'binaryData',
      inputDataFieldName: 'data'
    },
    position: [1340, 100]
  },
  output: [{}]
});

// ============================================================================
// Branch 1: DT (momento 3)
// GET contexto → AI Agent DT → POST prediccion → TTS → POST audio
// ============================================================================

const contextoDT = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.4,
  config: {
    name: 'HTTP Request Contexto DT',
    parameters: {
      method: 'GET',
      url: 'http://localhost:8000/partido/contexto',
      authentication: 'none',
      options: { response: { response: { responseFormat: 'text', outputPropertyName: 'body' } } }
    },
    position: [680, 300]
  },
  output: [{ body: 'contexto del partido' }]
});

const deepSeekModelDT = languageModel({
  type: '@n8n/n8n-nodes-langchain.lmChatDeepSeek', version: 1,
  config: {
    name: 'DeepSeek Model DT',
    parameters: { model: 'deepseek-chat' },
    credentials: { deepSeekApi: newCredential('DeepSeek API') },
    position: [900, 360]
  }
});

const aiAgentDT = node({
  type: '@n8n/n8n-nodes-langchain.agent', version: 3.1,
  config: {
    name: 'AI Agent DT',
    parameters: {
      promptType: 'define',
      text: expr("{{ $('Webhook').item.json.body.context_text }}"),
      options: {
        systemMessage: expr(
          "# PERSONALIDAD (fija)\n" +
          "Sos un analista de fútbol argentino. Hablás en español rioplatense.\n" +
          "Sos apasionado, directo y usás datos reales para respaldar tus opiniones.\n" +
          "Respondé de forma concisa (máximo 3-4 oraciones) porque tu respuesta va a ser leída en voz alta.\n" +
          "\n" +
          "# INSTRUCCIONES (fijas)\n" +
          "- Siempre mencioná datos concretos cuando opines sobre un jugador.\n" +
          "- Si no tenés datos de algo, decilo honestamente.\n" +
          "- Tu tono es el de un amigo viendo el partido, no un robot.\n" +
          "\n" +
          "# CONTEXTO DEL PARTIDO (dinámico)\n" +
          "{{ $('HTTP Request Contexto DT').item.json.body }}\n" +
          "\n" +
          "# MOMENTO: Modo DT\n" +
          "Sos el DT. ¿Qué cambios hacés? ¿Quién sale? ¿Quién entra? ¿Cambio táctico? Analizá el arbitraje."
        )
      }
    },
    subnodes: { model: deepSeekModelDT },
    position: [900, 300]
  },
  output: [{ output: 'AI response text' }]
});

const postPrediccion = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.4,
  config: {
    name: 'HTTP Request POST Prediccion',
    parameters: {
      method: 'POST',
      url: 'http://localhost:8000/partido/prediccion',
      sendBody: true,
      contentType: 'json',
      specifyBody: 'json',
      jsonBody: {
        momento: 3,
        content: expr('{{ $json.output }}')
      }
    },
    position: [1120, 300]
  },
  output: [{ ok: true, momento: 3 }]
});

const ttsDT = node({
  type: '@elevenlabs/n8n-nodes-elevenlabs.elevenLabs', version: 1,
  config: {
    name: 'ElevenLabs TTS DT',
    parameters: {
      resource: 'speech',
      operation: 'textToSpeech',
      text: expr("{{ $('AI Agent DT').item.json.output }}"),
      model: 'eleven_multilingual_v2',
      voiceId: placeholder('VOICE_ID')
    },
    credentials: { elevenLabsApi: newCredential('ElevenLabs API') },
    position: [1340, 300]
  },
  output: [{ data: {} }]
});

const postAudioDT = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.4,
  config: {
    name: 'HTTP Request POST Audio DT',
    parameters: {
      method: 'POST',
      url: placeholder('Your ngrok audio player URL (e.g. https://abc123.ngrok-free.app/play)'),
      sendBody: true,
      contentType: 'binaryData',
      inputDataFieldName: 'data'
    },
    position: [1560, 300]
  },
  output: [{}]
});

// ============================================================================
// Branch 2: Reacción (momentos 4, 5)
// GET contexto → AI Agent Reacción → TTS → POST audio
// ============================================================================

const contextoReaccion = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.4,
  config: {
    name: 'HTTP Request Contexto Reaccion',
    parameters: {
      method: 'GET',
      url: 'http://localhost:8000/partido/contexto',
      authentication: 'none',
      options: { response: { response: { responseFormat: 'text', outputPropertyName: 'body' } } }
    },
    position: [680, 500]
  },
  output: [{ body: 'contexto del partido' }]
});

const deepSeekModelReaccion = languageModel({
  type: '@n8n/n8n-nodes-langchain.lmChatDeepSeek', version: 1,
  config: {
    name: 'DeepSeek Model Reaccion',
    parameters: { model: 'deepseek-chat' },
    credentials: { deepSeekApi: newCredential('DeepSeek API') },
    position: [900, 560]
  }
});

const aiAgentReaccion = node({
  type: '@n8n/n8n-nodes-langchain.agent', version: 3.1,
  config: {
    name: 'AI Agent Reaccion',
    parameters: {
      promptType: 'define',
      text: expr("{{ $('Webhook').item.json.body.context_text }}"),
      options: {
        systemMessage: expr(
          "# PERSONALIDAD (fija)\n" +
          "Sos un analista de fútbol argentino. Hablás en español rioplatense.\n" +
          "Sos apasionado, directo y usás datos reales para respaldar tus opiniones.\n" +
          "Respondé de forma concisa (máximo 3-4 oraciones) porque tu respuesta va a ser leída en voz alta.\n" +
          "\n" +
          "# INSTRUCCIONES (fijas)\n" +
          "- Siempre mencioná datos concretos cuando opines sobre un jugador.\n" +
          "- Si no tenés datos de algo, decilo honestamente.\n" +
          "- Tu tono es el de un amigo viendo el partido, no un robot.\n" +
          "\n" +
          "# CONTEXTO DEL PARTIDO (dinámico)\n" +
          "{{ $('HTTP Request Contexto Reaccion').item.json.body }}\n" +
          "\n" +
          "# MOMENTO: Reacción\n" +
          "Momento 4 (Min 60): ¿Cambió algo tras el entretiempo? ¿Se hicieron los cambios que recomendaste?\n" +
          "Momento 5 (Min 75): Recta final. ¿Quién tiene más nafta? ¿Últimos cambios necesarios?"
        )
      }
    },
    subnodes: { model: deepSeekModelReaccion },
    position: [900, 500]
  },
  output: [{ output: 'AI response text' }]
});

const ttsReaccion = node({
  type: '@elevenlabs/n8n-nodes-elevenlabs.elevenLabs', version: 1,
  config: {
    name: 'ElevenLabs TTS Reaccion',
    parameters: {
      resource: 'speech',
      operation: 'textToSpeech',
      text: expr('{{ $json.output }}'),
      model: 'eleven_multilingual_v2',
      voiceId: placeholder('VOICE_ID')
    },
    credentials: { elevenLabsApi: newCredential('ElevenLabs API') },
    position: [1120, 500]
  },
  output: [{ data: {} }]
});

const postAudioReaccion = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.4,
  config: {
    name: 'HTTP Request POST Audio Reaccion',
    parameters: {
      method: 'POST',
      url: placeholder('Your ngrok audio player URL (e.g. https://abc123.ngrok-free.app/play)'),
      sendBody: true,
      contentType: 'binaryData',
      inputDataFieldName: 'data'
    },
    position: [1340, 500]
  },
  output: [{}]
});

// ============================================================================
// Branch 3: Auditoría (momento 6)
// GET predicciones → GET contexto → AI Agent Auditoría → TTS → POST audio
// ============================================================================

const httpPredicciones = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.4,
  config: {
    name: 'HTTP Request Predicciones',
    parameters: {
      method: 'GET',
      url: 'http://localhost:8000/partido/predicciones',
      authentication: 'none',
      options: { response: { response: { responseFormat: 'json' } } }
    },
    position: [680, 700]
  },
  output: [{ momento: 3, content: 'prediccion del entretiempo' }]
});

const contextoAuditoria = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.4,
  config: {
    name: 'HTTP Request Contexto Auditoria',
    parameters: {
      method: 'GET',
      url: 'http://localhost:8000/partido/contexto',
      authentication: 'none',
      options: { response: { response: { responseFormat: 'text', outputPropertyName: 'body' } } }
    },
    position: [900, 700]
  },
  output: [{ body: 'contexto final del partido' }]
});

const deepSeekModelAuditoria = languageModel({
  type: '@n8n/n8n-nodes-langchain.lmChatDeepSeek', version: 1,
  config: {
    name: 'DeepSeek Model Auditoria',
    parameters: { model: 'deepseek-chat' },
    credentials: { deepSeekApi: newCredential('DeepSeek API') },
    position: [1120, 760]
  }
});

const aiAgentAuditoria = node({
  type: '@n8n/n8n-nodes-langchain.agent', version: 3.1,
  config: {
    name: 'AI Agent Auditoria',
    parameters: {
      promptType: 'define',
      text: expr("{{ $('Webhook').item.json.body.context_text }}"),
      options: {
        systemMessage: expr(
          "# PERSONALIDAD (fija)\n" +
          "Sos un analista de fútbol argentino. Hablás en español rioplatense.\n" +
          "Sos apasionado, directo y usás datos reales para respaldar tus opiniones.\n" +
          "Respondé de forma concisa (máximo 3-4 oraciones) porque tu respuesta va a ser leída en voz alta.\n" +
          "\n" +
          "# INSTRUCCIONES (fijas)\n" +
          "- Siempre mencioná datos concretos cuando opines sobre un jugador.\n" +
          "- Si no tenés datos de algo, decilo honestamente.\n" +
          "- Tu tono es el de un amigo viendo el partido, no un robot.\n" +
          "\n" +
          "# LO QUE RECOMENDASTE EN EL ENTRETIEMPO\n" +
          "{{ $('HTTP Request Predicciones').item.json }}\n" +
          "\n" +
          "# LO QUE REALMENTE PASÓ\n" +
          "{{ $('HTTP Request Contexto Auditoria').item.json.body }}\n" +
          "\n" +
          "# MOMENTO: Auditoría\n" +
          "Compará tus predicciones del entretiempo con lo que pasó. ¿Quién tuvo razón, vos o el DT real? Sé honesto."
        )
      }
    },
    subnodes: { model: deepSeekModelAuditoria },
    position: [1120, 700]
  },
  output: [{ output: 'AI response text' }]
});

const ttsAuditoria = node({
  type: '@elevenlabs/n8n-nodes-elevenlabs.elevenLabs', version: 1,
  config: {
    name: 'ElevenLabs TTS Auditoria',
    parameters: {
      resource: 'speech',
      operation: 'textToSpeech',
      text: expr('{{ $json.output }}'),
      model: 'eleven_multilingual_v2',
      voiceId: placeholder('VOICE_ID')
    },
    credentials: { elevenLabsApi: newCredential('ElevenLabs API') },
    position: [1340, 700]
  },
  output: [{ data: {} }]
});

const postAudioAuditoria = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.4,
  config: {
    name: 'HTTP Request POST Audio Auditoria',
    parameters: {
      method: 'POST',
      url: placeholder('Your ngrok audio player URL (e.g. https://abc123.ngrok-free.app/play)'),
      sendBody: true,
      contentType: 'binaryData',
      inputDataFieldName: 'data'
    },
    position: [1560, 700]
  },
  output: [{}]
});

// ============================================================================
// Compose workflow
// ============================================================================
export default workflow('ai-dt-analysis', 'AI DT - Analysis Layer')
  .add(webhook)
  .to(routeSwitch
    .onCase(0, contextoDiagnostico.to(aiAgentDiagnostico.to(ttsDiagnostico.to(postAudioDiagnostico))))
    .onCase(1, contextoDT.to(aiAgentDT.to(postPrediccion.to(ttsDT.to(postAudioDT)))))
    .onCase(2, contextoReaccion.to(aiAgentReaccion.to(ttsReaccion.to(postAudioReaccion))))
    .onCase(3, httpPredicciones.to(contextoAuditoria.to(aiAgentAuditoria.to(ttsAuditoria.to(postAudioAuditoria))))));
