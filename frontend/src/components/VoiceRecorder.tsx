import React, { useState, useRef } from "react";
import avatarService from "../services/avatarService";

interface VoiceRecorderProps {
  isConnected: boolean;
  isProcessing: boolean;
  onProcessingChange: (processing: boolean) => void;
  onAudioReady?: (audio: Blob) => void;
  onResponseReceived?: (response: { text: string; audioUrl: string }) => void;
}

const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  isConnected,
  isProcessing,
  onProcessingChange,
  onAudioReady,
  onResponseReceived,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [error, setError] = useState<string>("");
  const [progress, setProgress] = useState<string>("");
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  const handleStartRecording = async () => {
    if (!isConnected || isProcessing) return;

    try {
      setError("");
      setProgress("");
      console.log("[VoiceRecorder] Старт записи...");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      const chunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: "audio/wav" });
        setAudioBlob(blob);
        stream.getTracks().forEach((track) => track.stop());
        console.log("[VoiceRecorder] Аудио записано, blob:", blob);
        if (onAudioReady) onAudioReady(blob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Ошибка записи аудио:", error);
      setError("Ошибка доступа к микрофону");
    }
  };

  const handleStopRecording = () => {
    setIsRecording(false);
    console.log("[VoiceRecorder] Стоп записи");
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
    // Автоматически отправляем аудио, если оно записано
    setTimeout(() => {
      if (audioBlob) {
        console.log("[VoiceRecorder] Отправка аудио на backend...");
        handleSendAudio();
      }
    }, 100); // небольшая задержка для корректного обновления состояния
  };

  const handleSendAudio = async () => {
    if (!audioBlob || isProcessing) return;

    onProcessingChange(true);
    setError("");
    setProgress("Обработка аудио...");
    console.log("[VoiceRecorder] handleSendAudio: отправка blob:", audioBlob);

    try {
      // Полный цикл обработки через avatarService
      const result = await avatarService.processAudioInput(audioBlob);
      console.log("[VoiceRecorder] Результат от backend:", result);

      setProgress("Готово!");

      // Передаем результат наверх
      if (onResponseReceived) {
        onResponseReceived({
          text: result.aiResponse,
          audioUrl: result.audioUrl,
        });
      }

      setAudioBlob(null);

      // Автоматическое воспроизведение аудио
      const audio = new Audio(result.audioUrl);
      audio.play().catch((err) => {
        console.error("Ошибка воспроизведения:", err);
        setError("Ошибка воспроизведения аудио");
      });
    } catch (error) {
      console.error("Ошибка обработки аудио:", error);
      setError(
        error instanceof Error ? error.message : "Ошибка обработки аудио",
      );
    } finally {
      onProcessingChange(false);
      setProgress("");
    }
  };

  return (
    <div className="space-y-4">
      {/* Кнопки управления записью */}
      <div className="flex justify-center space-x-4">
        {!isRecording ? (
          <button
            onClick={handleStartRecording}
            disabled={!isConnected || isProcessing}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            🎤 Начать запись
          </button>
        ) : (
          <button onClick={handleStopRecording} className="btn-secondary">
            ⏹️ Остановить запись
          </button>
        )}
      </div>

      {/* Индикатор записи */}
      {isRecording && (
        <div className="text-center">
          <div className="inline-flex items-center px-4 py-2 bg-red-100 text-red-800 rounded-full">
            <div className="w-3 h-3 bg-red-500 rounded-full mr-2 animate-pulse"></div>
            Запись...
          </div>
        </div>
      )}

      {/* Прогресс обработки */}
      {progress && (
        <div className="text-center">
          <div className="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-800 rounded-full">
            <div className="loading-spinner w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full mr-2"></div>
            {progress}
          </div>
        </div>
      )}

      {/* Сообщение об ошибке */}
      {error && (
        <div className="text-center">
          <div className="inline-flex items-center px-4 py-2 bg-red-100 text-red-800 rounded-full">
            <span className="mr-2">⚠️</span>
            {error}
          </div>
        </div>
      )}

      {/* Предварительное прослушивание */}
      {audioBlob && (
        <div className="space-y-2">
          <p className="text-sm text-gray-600">Записанное аудио:</p>
          <audio controls className="w-full">
            <source src={URL.createObjectURL(audioBlob)} type="audio/wav" />
            Ваш браузер не поддерживает аудио.
          </audio>

          <div className="flex justify-center space-x-2">
            <button
              onClick={handleSendAudio}
              disabled={isProcessing}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? "Обработка..." : "Отправить"}
            </button>

            <button
              onClick={() => {
                setAudioBlob(null);
                setError("");
                setProgress("");
              }}
              disabled={isProcessing}
              className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Отменить
            </button>
          </div>
        </div>
      )}

      {/* Инструкции */}
      <div className="text-xs text-gray-500 text-center">
        <p>Нажмите кнопку записи и говорите четко в микрофон</p>
        <p>Максимальная длительность: 5 минут</p>
      </div>
    </div>
  );
};

export default VoiceRecorder;
