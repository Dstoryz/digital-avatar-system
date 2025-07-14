import React from "react";

interface AvatarVideoProps {
  isConnected: boolean;
  isProcessing: boolean;
}

const AvatarVideo: React.FC<AvatarVideoProps> = ({
  isConnected,
  isProcessing,
}) => {
  return (
    <div className="video-container">
      {isConnected ? (
        <div className="relative">
          <video
            className="w-full h-auto rounded-lg"
            autoPlay
            muted
            loop
            playsInline
          >
            <source src="/placeholder-avatar.mp4" type="video/mp4" />
            Ваш браузер не поддерживает видео.
          </video>

          {isProcessing && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-lg">
              <div className="text-white text-center">
                <div className="loading-spinner w-8 h-8 border-2 border-white border-t-transparent rounded-full mx-auto mb-2"></div>
                <p>Обработка...</p>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-gray-100 rounded-lg p-8 text-center">
          <div className="w-32 h-32 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center">
            <span className="text-4xl">👤</span>
          </div>
          <p className="text-gray-600">
            Подключитесь, чтобы увидеть анимированного аватара
          </p>
        </div>
      )}
    </div>
  );
};

export default AvatarVideo;
