import React, { useState, useRef, useEffect, useCallback } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import AnimatedAvatar from "./AnimatedAvatar";
import AvatarPage from "./AvatarPage";
import ServiceStatus from "./ServiceStatus";
import avatarService from "../services/avatarService";

interface Message {
  id: string;
  type: "user" | "assistant";
  text: string;
  audio?: string;
  timestamp: Date;
}

interface AvatarSystemProps {
  className?: string;
}

const AvatarSystem: React.FC<AvatarSystemProps> = ({ className = "" }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [inputText, setInputText] = useState("");
  const [selectedVoice, setSelectedVoice] = useState("default");
  const [currentAudioUrl, setCurrentAudioUrl] = useState<string>("");
  const [avatarImageUrl, setAvatarImageUrl] = useState("/avatar.jpg");
  const [error, setError] = useState<string>("");
  const [isConnected, setIsConnected] = useState(false);
  const [servicesStatus, setServicesStatus] = useState({
    backend: false,
    tts: false,
    sadtalker: false,
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);

  // --- обработчики событий WebSocket ---
  const handleWSOpen = useCallback(() => {
    console.log("WebSocket открыт");
    setError("");
    // Тестовое сообщение
    sendMessage && sendMessage("ping");
  }, []); // sendMessage будет обновлён ниже

  const handleWSClose = useCallback(() => {
    console.log("WebSocket закрыт");
  }, []);

  const handleWSError = useCallback((e: Event) => {
    console.error("WebSocket ошибка:", e);
    setError("Ошибка WebSocket: " + (e ? e.toString() : "unknown"));
  }, []);

  const handleWSMessage = useCallback((msg: string) => {
    console.log("WebSocket сообщение:", msg);
  }, []);

  const { sendMessage, lastMessage, connectionStatus, connect, disconnect } =
    useWebSocket("ws://localhost:8000/ws", {
      onOpen: handleWSOpen,
      onClose: handleWSClose,
      onError: handleWSError,
      onMessage: handleWSMessage,
    });

  // Инициализация аудио контекста
  useEffect(() => {
    audioContextRef.current = new (window.AudioContext ||
      (window as any).webkitAudioContext)();
    return () => {
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  // Проверка статуса сервисов при загрузке
  useEffect(() => {
    checkServicesStatus();
    const interval = setInterval(checkServicesStatus, 30000); // Проверяем каждые 30 секунд
    return () => clearInterval(interval);
  }, []);

  // Обработка статуса подключения WebSocket
  useEffect(() => {
    setIsConnected(connectionStatus === "Connected");

    if (connectionStatus === "Disconnected" || connectionStatus === "Error") {
      // Автоматическое переподключение через 5 секунд
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      reconnectTimeoutRef.current = window.setTimeout(() => {
        console.log("Попытка переподключения к WebSocket...");
        connect();
      }, 5000);
    }
  }, [connectionStatus, connect]);

  // Обработка входящих сообщений WebSocket
  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage);
        handleWebSocketMessage(data);
      } catch (error) {
        console.error("Ошибка обработки WebSocket сообщения:", error);
        setError("Ошибка обработки сообщения от сервера");
      }
    }
  }, [lastMessage]);

  // Проверка статуса сервисов
  const checkServicesStatus = async () => {
    try {
      const status = await avatarService.checkServices();
      setServicesStatus(status);

      // Автоматическое подключение к WebSocket если все сервисы доступны
      if (
        Object.values(status).every(Boolean) &&
        connectionStatus !== "Connected"
      ) {
        connect();
      }
    } catch (error) {
      console.error("Ошибка проверки сервисов:", error);
    }
  };

  // Обработка WebSocket сообщений
  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case "assistant_response":
        handleAssistantResponse(data);
        break;
      case "processing_status":
        handleProcessingStatus(data);
        break;
      case "error":
        handleErrorMessage(data);
        break;
      case "service_status":
        setServicesStatus(data.services);
        break;
      default:
        console.log("Неизвестный тип сообщения:", data.type);
    }
  };

  // Обработка ответа ассистента
  const handleAssistantResponse = (data: any) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      type: "assistant",
      text: data.text,
      audio: data.audio,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);

    // Воспроизведение аудио ответа
    if (data.audio) {
      playAudioResponse(data.audio);
    }

    setIsSpeaking(true);
    setIsProcessing(false);
  };

  // Обработка статуса обработки
  const handleProcessingStatus = (data: any) => {
    setIsProcessing(data.processing);
    if (data.progress) {
      console.log(`Прогресс: ${data.progress}%`);
    }
  };

  // Обработка ошибок
  const handleErrorMessage = (data: any) => {
    setError(data.message || "Произошла ошибка");
    setIsProcessing(false);
    setIsSpeaking(false);
  };

  // Начало записи аудио
  const startRecording = useCallback(async () => {
    if (!isConnected) {
      setError("Нет подключения к серверу");
      return;
    }

    try {
      setError("");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/wav",
        });
        await processAudioInput(audioBlob);
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Ошибка записи аудио:", error);
      setError("Не удалось получить доступ к микрофону");
    }
  }, [isConnected]);

  // Остановка записи аудио
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream
        .getTracks()
        .forEach((track) => track.stop());
      setIsRecording(false);
    }
  }, [isRecording]);

  // Обработка аудио ввода с использованием avatarService
  const processAudioInput = async (audioBlob: Blob) => {
    setIsProcessing(true);
    setError("");

    try {
      // Используем avatarService для полного цикла обработки
      const result = await avatarService.processAudioInput(audioBlob);

      // Добавляем сообщение пользователя
      const userMessage: Message = {
        id: Date.now().toString(),
        type: "user",
        text: result.recognizedText,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Добавляем сообщение ассистента
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        text: result.aiResponse,
        audio: result.audioUrl,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Воспроизводим аудио
      playAudioResponse(result.audioUrl);
    } catch (error) {
      console.error("Ошибка обработки аудио:", error);
      setError(
        error instanceof Error ? error.message : "Ошибка обработки аудио",
      );
    } finally {
      setIsProcessing(false);
    }
  };

  // Воспроизведение аудио ответа
  const playAudioResponse = async (audioUrl: string) => {
    try {
      setIsSpeaking(true);
      setCurrentAudioUrl(audioUrl);

      const audio = new Audio(audioUrl);
      audio.onended = () => {
        setIsSpeaking(false);
        setCurrentAudioUrl("");
      };

      await audio.play();
    } catch (error) {
      console.error("Ошибка воспроизведения аудио:", error);
      setError("Ошибка воспроизведения аудио");
      setIsSpeaking(false);
    }
  };

  // Отправка текстового сообщения
  const handleSendText = async () => {
    if (!inputText.trim() || !isConnected) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      text: inputText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    setIsProcessing(true);

    try {
      // Отправляем через WebSocket
      sendMessage(
        JSON.stringify({
          type: "user_message",
          text: inputText,
        }),
      );
    } catch (error) {
      console.error("Ошибка отправки сообщения:", error);
      setError("Ошибка отправки сообщения");
      setIsProcessing(false);
    }
  };

  // Обработка нажатия Enter
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendText();
    }
  };

  // Обработка готовности видео
  const handleVideoReady = (videoUrl: string) => {
    console.log("Видео готово:", videoUrl);
  };

  // Подключение/отключение
  const handleConnect = () => {
    if (isConnected) {
      disconnect();
    } else {
      connect();
    }
  };

  // Очистка при размонтировании
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div className={`min-h-screen bg-gray-50 ${className}`}>
      {/* Заголовок с статусом */}
      <div className="bg-white shadow-sm border-b border-gray-200 p-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">А</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900">Цифровой Аватар</h1>
          </div>

          <div className="flex items-center space-x-4">
            <ServiceStatus className="w-64" />
            <button
              onClick={handleConnect}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                isConnected
                  ? "bg-red-100 text-red-700 hover:bg-red-200"
                  : "bg-green-100 text-green-700 hover:bg-green-200"
              }`}
            >
              {isConnected ? "Отключиться" : "Подключиться"}
            </button>
          </div>
        </div>
      </div>

      {/* Основной контент */}
      <div className="max-w-6xl mx-auto p-6">
        <AvatarPage />
      </div>

      {/* Сообщение об ошибке */}
      {error && (
        <div className="fixed bottom-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg shadow-lg">
          <div className="flex items-center justify-between">
            <span>{error}</span>
            <button
              onClick={() => setError("")}
              className="ml-4 text-red-500 hover:text-red-700"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AvatarSystem;
