import React, { useState } from 'react'

interface VoiceRecorderProps {
  isConnected: boolean
  isProcessing: boolean
  onProcessingChange: (processing: boolean) => void
}

const VoiceRecorder: React.FC<VoiceRecorderProps> = ({ 
  isConnected, 
  isProcessing, 
  onProcessingChange 
}) => {
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)

  const handleStartRecording = async () => {
    if (!isConnected || isProcessing) return

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      const chunks: Blob[] = []

      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data)
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' })
        setAudioBlob(blob)
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (error) {
      console.error('Ошибка записи аудио:', error)
    }
  }

  const handleStopRecording = () => {
    setIsRecording(false)
    // TODO: Остановка записи и отправка аудио
  }

  const handleSendAudio = async () => {
    if (!audioBlob || isProcessing) return

    onProcessingChange(true)
    
    try {
      // TODO: Отправка аудио через WebSocket
      // TODO: Получение ответа от аватара
      
      // Имитация обработки
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      setAudioBlob(null)
    } catch (error) {
      console.error('Ошибка отправки аудио:', error)
    } finally {
      onProcessingChange(false)
    }
  }

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
          <button
            onClick={handleStopRecording}
            className="btn-secondary"
          >
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
              {isProcessing ? 'Отправка...' : 'Отправить'}
            </button>
            
            <button
              onClick={() => setAudioBlob(null)}
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
  )
}

export default VoiceRecorder 