import { workflow, node, trigger, placeholder, newCredential, languageModel, memory, expr } from '@n8n/workflow-sdk';

const telegramTrigger = trigger({
  type: 'n8n-nodes-base.telegramTrigger', version: 1.2,
  config: {
    name: 'Telegram Trigger',
    parameters: { updates: ['message'], additionalFields: { download: true } },
    credentials: { telegramApi: newCredential('Telegram Bot API') },
    position: [240, 300]
  },
  output: [{ message: { voice: { file_id: 'voice123' }, chat: { id: 12345 } } }]
});

const telegramGetFile = node({
  type: 'n8n-nodes-base.telegram', version: 1.2,
  config: {
    name: 'Telegram Get File',
    parameters: {
      resource: 'file',
      operation: 'get',
      fileId: expr('{{ $json.message.voice.file_id }}'),
      download: true
    },
    credentials: { telegramApi: newCredential('Telegram Bot API') },
    position: [460, 300]
  },
  output: [{ data: {} }]
});

const whisperStt = node({
  type: '@n8n/n8n-nodes-langchain.openAi', version: 2.3,
  config: {
    name: 'OpenAI Whisper STT',
    parameters: {
      resource: 'audio',
      operation: 'transcribe',
      binaryPropertyName: 'data',
      options: { language: 'es' }
    },
    credentials: { openAiApi: newCredential('OpenAI API') },
    position: [680, 300]
  },
  output: [{ text: 'texto transcrito' }]
});

const contextoHttp = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.4,
  config: {
    name: 'HTTP Request Contexto',
    parameters: {
      method: 'GET',
      url: 'http://localhost:8000/partido/contexto',
      authentication: 'none',
      options: { response: { response: { responseFormat: 'text', outputPropertyName: 'body' } } }
    },
    position: [900, 300]
  },
  output: [{ body: 'contexto del partido' }]
});

const deepSeekModel = languageModel({
  type: '@n8n/n8n-nodes-langchain.lmChatDeepSeek', version: 1,
  config: {
    name: 'DeepSeek Model',
    parameters: { model: 'deepseek-chat' },
    credentials: { deepSeekApi: newCredential('DeepSeek API') },
    position: [1120, 460]
  }
});

const simpleMemory = memory({
  type: '@n8n/n8n-nodes-langchain.memoryBufferWindow', version: 1.3,
  config: {
    name: 'Simple Memory',
    parameters: {
      sessionIdType: 'customKey',
      sessionKey: expr('{{ $json.message.chat.id }}'),
      contextWindowLength: 10
    },
    position: [1120, 540]
  }
});

const aiAgent = node({
  type: '@n8n/n8n-nodes-langchain.agent', version: 3.1,
  config: {
    name: 'AI Agent',
    parameters: {
      promptType: 'define',
      text: expr("{{ $('OpenAI Whisper STT').item.json.text }}"),
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
          "{{ $('HTTP Request Contexto').item.json.body }}"
        )
      }
    },
    subnodes: { model: deepSeekModel, memory: simpleMemory },
    position: [1120, 300]
  },
  output: [{ output: 'AI response' }]
});

const elevenLabsTts = node({
  type: '@elevenlabs/n8n-nodes-elevenlabs.elevenLabs', version: 1,
  config: {
    name: 'ElevenLabs TTS',
    parameters: {
      resource: 'speech',
      operation: 'textToSpeech',
      text: expr('{{ $json.output }}'),
      model: 'eleven_multilingual_v2',
      voiceId: placeholder('VOICE_ID')
    },
    credentials: { elevenLabsApi: newCredential('ElevenLabs API') },
    position: [1340, 300]
  },
  output: [{ data: {} }]
});

const postAudio = node({
  type: 'n8n-nodes-base.httpRequest', version: 4.4,
  config: {
    name: 'HTTP Request POST Audio',
    parameters: {
      method: 'POST',
      url: placeholder('NGROK_AUDIO_PLAYER_URL'),
      sendBody: true,
      contentType: 'binaryData',
      inputDataFieldName: 'data'
    },
    position: [1560, 300]
  },
  output: [{}]
});

export default workflow('ai-dt-dynamic', 'AI DT - Dynamic Layer')
  .add(telegramTrigger)
  .to(telegramGetFile)
  .to(whisperStt)
  .to(contextoHttp)
  .to(aiAgent)
  .to(elevenLabsTts)
  .to(postAudio);
