import React, { useState, useRef, useEffect, useCallback } from "react";

interface AnimatedAvatarProps {
  className?: string;
  imageUrl?: string;
  audioUrl?: string;
  isSpeaking?: boolean;
  onVideoReady?: (videoUrl: string) => void;
}

const AnimatedAvatar: React.FC<AnimatedAvatarProps> = ({
  className = "",
  imageUrl = "/avatar.jpg",
  audioUrl,
  isSpeaking = false,
  onVideoReady,
}) => {
  const [videoUrl, setVideoUrl] = useState<string>("");
  const [isAnimating, setIsAnimating] = useState(false);
  const [animationProgress, setAnimationProgress] = useState(0);
  const [error, setError] = useState<string>("");

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Обработка аудио для анимации
  useEffect(() => {
    if (audioUrl && isSpeaking) {
      createAnimation(audioUrl);
    }
  }, [audioUrl, isSpeaking]);

  // Создание анимации через SadTalker API
  const createAnimation = useCallback(
    async (audioBlobUrl: string) => {
      try {
        setIsAnimating(true);
        setError("");
        setAnimationProgress(0);

        // Получение аудио как Blob
        const audioResponse = await fetch(audioBlobUrl);
        const audioBlob = await audioResponse.blob();

        // Создание FormData для отправки
        const formData = new FormData();
        formData.append(
          "image",
          await fetch(imageUrl).then((r) => r.blob()),
          "avatar.jpg",
        );
        formData.append("audio", audioBlob, "speech.wav");
        formData.append("pose_style", "0");
        formData.append("exp_scale", "1.0");
        formData.append("use_enhancer", "false");

        // Отправка запроса на анимацию
        const response = await fetch("http://127.0.0.1:8002/animate", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error("Ошибка создания анимации");
        }

        const result = await response.json();

        // Ожидание готовности видео
        await waitForVideo(result.video_path);

        setVideoUrl(result.video_path);
        onVideoReady?.(result.video_path);
        setAnimationProgress(100);
      } catch (err) {
        console.error("Ошибка анимации:", err);
        setError(err instanceof Error ? err.message : "Ошибка анимации");
      } finally {
        setIsAnimating(false);
      }
    },
    [imageUrl, onVideoReady],
  );

  // Ожидание готовности видео
  const waitForVideo = async (videoPath: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const checkVideo = async () => {
        try {
          const response = await fetch(
            `http://127.0.0.1:8002/video/${videoPath.split("/").pop()?.replace(".mp4", "")}`,
          );
          if (response.ok) {
            resolve();
          } else {
            setTimeout(checkVideo, 1000);
          }
        } catch {
          setTimeout(checkVideo, 1000);
        }
      };
      checkVideo();
    });
  };

  // Воспроизведение видео
  const playVideo = useCallback(() => {
    if (videoRef.current && videoUrl) {
      videoRef.current.play();
    }
  }, [videoUrl]);

  // Остановка видео
  const stopVideo = useCallback(() => {
    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.currentTime = 0;
    }
  }, []);

  // Обработка окончания видео
  const handleVideoEnded = useCallback(() => {
    stopVideo();
  }, [stopVideo]);

  // Обработка ошибки видео
  const handleVideoError = useCallback(
    (e: React.SyntheticEvent<HTMLVideoElement, Event>) => {
      console.error("Ошибка видео:", e);
      setError("Ошибка воспроизведения видео");
    },
    [],
  );

  return (
    <div className={`relative ${className}`}>
      {/* Основной контейнер */}
      <div className="relative w-full h-full bg-gray-900 rounded-lg overflow-hidden">
        {/* Статичное изображение (пока нет анимации) */}
        {!videoUrl && !isAnimating && (
          <div className="w-full h-full flex items-center justify-center">
            <img
              src={imageUrl}
              alt="Аватар"
              className="w-full h-full object-cover"
              onError={() => setError("Ошибка загрузки изображения")}
            />
          </div>
        )}

        {/* Анимированное видео */}
        {videoUrl && (
          <video
            ref={videoRef}
            src={videoUrl}
            className="w-full h-full object-cover"
            onEnded={handleVideoEnded}
            onError={handleVideoError}
            autoPlay
            muted
            loop={false}
          />
        )}

        {/* Canvas для fallback анимации */}
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full hidden"
        />

        {/* Индикатор анимации */}
        {isAnimating && (
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
            <div className="text-center text-white">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
              <p className="text-lg font-medium">Создаю анимацию...</p>
              <p className="text-sm opacity-75">{animationProgress}%</p>
            </div>
          </div>
        )}

        {/* Индикатор речи */}
        {isSpeaking && !isAnimating && (
          <div className="absolute top-4 right-4">
            <div className="flex space-x-1">
              <div className="w-2 h-6 bg-red-500 animate-pulse rounded"></div>
              <div
                className="w-2 h-6 bg-red-500 animate-pulse rounded"
                style={{ animationDelay: "0.1s" }}
              ></div>
              <div
                className="w-2 h-6 bg-red-500 animate-pulse rounded"
                style={{ animationDelay: "0.2s" }}
              ></div>
            </div>
          </div>
        )}

        {/* Сообщение об ошибке */}
        {error && (
          <div className="absolute bottom-4 left-4 right-4 bg-red-600 text-white p-3 rounded-lg">
            <p className="text-sm">{error}</p>
            <button
              onClick={() => setError("")}
              className="mt-2 text-xs underline"
            >
              Закрыть
            </button>
          </div>
        )}

        {/* Контролы */}
        <div className="absolute bottom-4 left-4 flex space-x-2">
          {videoUrl && (
            <>
              <button
                onClick={playVideo}
                className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
              >
                ▶️ Воспроизвести
              </button>
              <button
                onClick={stopVideo}
                className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
              >
                ⏹️ Остановить
              </button>
            </>
          )}
        </div>
      </div>

      {/* Информационная панель */}
      <div className="mt-2 text-xs text-gray-400">
        <p>
          Статус:{" "}
          {isAnimating ? "Анимация..." : isSpeaking ? "Говорит" : "Ожидание"}
        </p>
        {videoUrl && <p>Видео: Готово</p>}
      </div>
    </div>
  );
};

export default AnimatedAvatar;
