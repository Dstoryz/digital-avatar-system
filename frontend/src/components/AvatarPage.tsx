import React, { useState } from 'react'
import AvatarVideo from './AvatarVideo'
import ChatInterface from './ChatInterface'
import VoiceRecorder from './VoiceRecorder'

const AvatarPage: React.FC = () => {
  const [isConnected, setIsConnected] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleConnect = () => {
    setIsConnected(true)
    // TODO: Подключение к WebSocket
  }

  const handleDisconnect = () => {
    setIsConnected(false)
    // TODO: Отключение от WebSocket
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Левая колонка - Аватар */}
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Цифровой Аватар</h2>
            <AvatarVideo isConnected={isConnected} isProcessing={isProcessing} />
            
            <div className="mt-4 flex justify-center space-x-4">
              {!isConnected ? (
                <button 
                  onClick={handleConnect}
                  className="btn-primary"
                >
                  Подключиться
                </button>
              ) : (
                <button 
                  onClick={handleDisconnect}
                  className="btn-secondary"
                >
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
            />
          </div>
        </div>

        {/* Правая колонка - Чат */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Чат с аватаром</h2>
          <ChatInterface 
            isConnected={isConnected}
            isProcessing={isProcessing}
          />
        </div>
      </div>

      {/* Статус подключения */}
      <div className="mt-8 text-center">
        <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${
          isConnected 
            ? 'bg-green-100 text-green-800' 
            : 'bg-gray-100 text-gray-800'
        }`}>
          <div className={`w-2 h-2 rounded-full mr-2 ${
            isConnected ? 'bg-green-500' : 'bg-gray-500'
          }`}></div>
          {isConnected ? 'Подключено' : 'Отключено'}
        </div>
      </div>
    </div>
  )
}

export default AvatarPage 