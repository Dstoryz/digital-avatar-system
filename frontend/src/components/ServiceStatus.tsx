import React, { useState, useEffect } from "react";
import avatarService from "../services/avatarService";

interface ServiceStatusProps {
  className?: string;
}

interface ServiceState {
  backend: boolean;
  tts: boolean;
  sadtalker: boolean;
}

const ServiceStatus: React.FC<ServiceStatusProps> = ({ className = "" }) => {
  const [services, setServices] = useState<ServiceState>({
    backend: false,
    tts: false,
    sadtalker: false,
  });
  const [isChecking, setIsChecking] = useState(false);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  const checkServices = async () => {
    setIsChecking(true);
    try {
      const status = await avatarService.checkServices();
      setServices(status);
      setLastCheck(new Date());
    } catch (error) {
      console.error("Ошибка проверки сервисов:", error);
    } finally {
      setIsChecking(false);
    }
  };

  useEffect(() => {
    checkServices();
    // Проверяем каждые 30 секунд
    const interval = setInterval(checkServices, 30000);
    return () => clearInterval(interval);
  }, []);

  const getServiceIcon = (isOnline: boolean) => {
    return isOnline ? "🟢" : "🔴";
  };

  const getServiceName = (key: keyof ServiceState) => {
    switch (key) {
      case "backend":
        return "Backend API";
      case "tts":
        return "HierSpeech TTS";
      case "sadtalker":
        return "SadTalker";
      default:
        return key;
    }
  };

  const allServicesOnline = Object.values(services).every(Boolean);

  return (
    <div
      className={`bg-white rounded-lg shadow-sm border border-gray-200 p-4 ${className}`}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-900">Статус сервисов</h3>
        <button
          onClick={checkServices}
          disabled={isChecking}
          className="text-xs text-blue-600 hover:text-blue-800 disabled:opacity-50"
        >
          {isChecking ? "Проверка..." : "Обновить"}
        </button>
      </div>

      <div className="space-y-2">
        {Object.entries(services).map(([key, isOnline]) => (
          <div key={key} className="flex items-center justify-between">
            <span className="text-sm text-gray-600">
              {getServiceName(key as keyof ServiceState)}
            </span>
            <div className="flex items-center space-x-2">
              <span className="text-lg">{getServiceIcon(isOnline)}</span>
              <span
                className={`text-xs ${isOnline ? "text-green-600" : "text-red-600"}`}
              >
                {isOnline ? "Онлайн" : "Офлайн"}
              </span>
            </div>
          </div>
        ))}
      </div>

      {lastCheck && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="text-xs text-gray-500">
            Последняя проверка: {lastCheck.toLocaleTimeString()}
          </p>
        </div>
      )}

      {/* Общий статус */}
      <div className="mt-3 pt-3 border-t border-gray-100">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-900">
            Общий статус:
          </span>
          <div className="flex items-center space-x-2">
            <span className="text-lg">{allServicesOnline ? "🟢" : "🟡"}</span>
            <span
              className={`text-sm font-medium ${
                allServicesOnline ? "text-green-600" : "text-yellow-600"
              }`}
            >
              {allServicesOnline ? "Все сервисы работают" : "Есть проблемы"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ServiceStatus;
