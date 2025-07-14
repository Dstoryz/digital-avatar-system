/**
 * Сервис для работы с API цифрового аватара
 */

interface SpeechRecognitionResponse {
  text: string;
  confidence: number;
}

interface AIResponse {
  text: string;
  emotion?: string;
}

interface TTSResponse {
  audio_url: string;
  duration: number;
}

class AvatarService {
  private baseUrl = "http://localhost:8000"; // Backend API
  private ttsUrl = "http://localhost:8001"; // HierSpeech_TTS API

  /**
   * Распознавание речи через Whisper
   */
  async recognizeSpeech(audioBlob: Blob): Promise<SpeechRecognitionResponse> {
    try {
      const formData = new FormData();
      formData.append("audio", audioBlob, "speech.wav");

      const response = await fetch(`${this.baseUrl}/api/v1/recognize-speech`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Ошибка распознавания речи: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Ошибка распознавания речи:", error);
      throw error;
    }
  }

  /**
   * Получение ответа от AI через Ollama
   */
  async getAIResponse(text: string, context?: string): Promise<AIResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/chat/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: text,
          context:
            context ||
            "Ты дружелюбный цифровой аватар девочки. Отвечай кратко и естественно.",
        }),
      });

      if (!response.ok) {
        throw new Error(`Ошибка получения ответа AI: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Ошибка получения ответа AI:", error);
      throw error;
    }
  }

  /**
   * Синтез речи через HierSpeech_TTS
   */
  async synthesizeSpeech(text: string): Promise<TTSResponse> {
    try {
      const response = await fetch(`${this.ttsUrl}/synthesize`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: text,
          voice_id: "default", // или ID конкретного голоса
          speed: 1.0,
          emotion: "neutral",
        }),
      });

      if (!response.ok) {
        throw new Error(`Ошибка синтеза речи: ${response.status}`);
      }

      const result = await response.json();

      // Получаем аудио файл
      const audioResponse = await fetch(
        `${this.ttsUrl}/audio/${result.audio_id}`,
      );
      if (!audioResponse.ok) {
        throw new Error("Ошибка получения аудио файла");
      }

      const audioBlob = await audioResponse.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      return {
        audio_url: audioUrl,
        duration: result.duration || 0,
      };
    } catch (error) {
      console.error("Ошибка синтеза речи:", error);
      throw error;
    }
  }

  /**
   * Полный цикл обработки: распознавание → AI → синтез
   */
  async processAudioInput(audioBlob: Blob): Promise<{
    recognizedText: string;
    aiResponse: string;
    audioUrl: string;
  }> {
    try {
      // 1. Распознавание речи
      console.log("Распознавание речи...");
      const recognition = await this.recognizeSpeech(audioBlob);

      if (!recognition.text.trim()) {
        throw new Error("Не удалось распознать речь");
      }

      // 2. Получение ответа от AI
      console.log("Получение ответа от AI...");
      const aiResponse = await this.getAIResponse(recognition.text);

      // 3. Синтез речи
      console.log("Синтез речи...");
      const ttsResponse = await this.synthesizeSpeech(aiResponse.text);

      return {
        recognizedText: recognition.text,
        aiResponse: aiResponse.text,
        audioUrl: ttsResponse.audio_url,
      };
    } catch (error) {
      console.error("Ошибка обработки аудио:", error);
      throw error;
    }
  }

  /**
   * Проверка доступности сервисов
   */
  async checkServices(): Promise<{
    backend: boolean;
    tts: boolean;
    sadtalker: boolean;
  }> {
    const results = await Promise.allSettled([
      fetch(`${this.baseUrl}/health`),
      fetch(`${this.ttsUrl}/health`),
      fetch("http://localhost:8002/health"),
    ]);

    return {
      backend: results[0].status === "fulfilled" && results[0].value.ok,
      tts: results[1].status === "fulfilled" && results[1].value.ok,
      sadtalker: results[2].status === "fulfilled" && results[2].value.ok,
    };
  }
}

export const avatarService = new AvatarService();
export default avatarService;
