import React, { useState } from "react";
import AnimatedAvatar from "./AnimatedAvatar";
import ChatInterface from "./ChatInterface";
import VoiceRecorder from "./VoiceRecorder";
import ServiceStatus from "./ServiceStatus";

interface Message {
  id: string;
  text: string;
  sender: "user" | "avatar";
  timestamp: Date;
}

const AvatarPage: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | undefined>(undefined);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [avatarResponse, setAvatarResponse] = useState<{
    text: string;
    audioUrl: string;
  } | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: "Привет! Я цифровой аватар. Как дела?",
      sender: "avatar",
      timestamp: new Date(),
    },
  ]);

  const handleConnect = () => {
    setIsConnected(true);
    // TODO: Подключение к WebSocket
  };

  const handleDisconnect = () => {
    setIsConnected(false);
    // TODO: Отключение от WebSocket
  };

  // Обработка завершения записи и отправки аудио
  const handleAudioReady = (blob: Blob) => {
    if (!blob) return;
    setIsProcessing(true);
    setIsSpeaking(true);
    const url = URL.createObjectURL(blob);
    setAudioUrl(url);
  };

  // Обработка ответа от аватара
  const handleAvatarResponse = (response: {
    text: string;
    audioUrl: string;
    recognizedText?: string;
  }) => {
    setAvatarResponse(response);
    setIsSpeaking(true);

    // Логируем результат распознавания и ответа
    console.log("[Voice->AI] Распознанный текст:", response.recognizedText);
    console.log("[Voice->AI] Ответ нейронки:", response.text);

    // Добавляем сообщения в чат: сначала пользователь, потом аватар
    if (response.recognizedText) {
      setMessages((prev) => {
        const newMessages = [
          ...prev,
          {
            id: Date.now().toString() + "-user",
            text: String(response.recognizedText),
            sender: "user" as const,
            timestamp: new Date(),
          },
          {
            id: Date.now().toString() + "-avatar",
            text: response.text,
            sender: "avatar" as const,
            timestamp: new Date(),
          },
        ];
        console.log("[Voice->AI] Итоговый массив сообщений:", newMessages);
        return newMessages;
      });
    }

    // Автоматическое воспроизведение аудио ответа
    const audio = new Audio(response.audioUrl);
    audio.play().catch((err) => {
      console.error("Ошибка воспроизведения ответа аватара:", err);
    });

    // Сброс состояния речи после окончания аудио
    audio.onended = () => {
      setIsSpeaking(false);
    };
  };

  // Сброс состояния после завершения анимации
  const handleVideoReady = () => {
    setIsProcessing(false);
    setIsSpeaking(false);
    setAudioUrl(undefined);
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Левая колонка - Аватар */}
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Цифровой Аватар</h2>
            <AnimatedAvatar
              className="w-full h-96"
              imageUrl="/avatar.jpg"
              audioUrl={audioUrl}
              isSpeaking={isSpeaking}
              onVideoReady={handleVideoReady}
            />

            {/* Ответ аватара */}
            {avatarResponse && (
              <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                <h3 className="text-sm font-medium text-blue-800 mb-2">
                  Ответ аватара:
                </h3>
                <p className="text-blue-700">{avatarResponse.text}</p>
              </div>
            )}

            <div className="mt-4 flex justify-center space-x-4">
              {!isConnected ? (
                <button onClick={handleConnect} className="btn-primary">
                  Подключиться
                </button>
              ) : (
                <button onClick={handleDisconnect} className="btn-secondary">
                  Отключиться
                </button>
              )}
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Голосовое управление</h3>
            <VoiceRecorder
              isConnected={isConnected}
              isProcessing={isProcessing}
              onProcessingChange={setIsProcessing}
              onAudioReady={handleAudioReady}
              onResponseReceived={(resp) => handleAvatarResponse({ ...resp, recognizedText: resp.text ?? "" })}
            />
          </div>
        </div>

        {/* Правая колонка - Чат */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Чат с аватаром</h2>
          <ChatInterface
            isConnected={isConnected}
            isProcessing={isProcessing}
            messages={messages}
            setMessages={setMessages}
          />
        </div>
      </div>

      {/* Статус подключения и сервисов */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="text-center">
          <div
            className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${
              isConnected
                ? "bg-green-100 text-green-800"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            <div
              className={`w-2 h-2 rounded-full mr-2 ${
                isConnected ? "bg-green-500" : "bg-gray-500"
              }`}
            ></div>
            {isConnected ? "Подключено" : "Отключено"}
          </div>
        </div>

        <ServiceStatus />
      </div>
    </div>
  );
};

export default AvatarPage;
