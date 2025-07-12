import React, { useState } from 'react'

interface ChatInterfaceProps {
  isConnected: boolean
  isProcessing: boolean
}

interface Message {
  id: string
  text: string
  sender: 'user' | 'avatar'
  timestamp: Date
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ isConnected, isProcessing }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Привет! Я цифровой аватар. Как дела?',
      sender: 'avatar',
      timestamp: new Date()
    }
  ])
  const [inputText, setInputText] = useState('')

  const handleSendMessage = () => {
    if (!inputText.trim() || !isConnected || isProcessing) return

    const newMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, newMessage])
    setInputText('')

    // TODO: Отправка сообщения через WebSocket
    // TODO: Получение ответа от аватара
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* История сообщений */}
      <div className="chat-container flex-1 mb-4 p-4 bg-gray-50 rounded-lg">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`mb-4 flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-white text-gray-800 border border-gray-200'
              }`}
            >
              <p className="text-sm">{message.text}</p>
              <p className={`text-xs mt-1 ${
                message.sender === 'user' ? 'text-primary-100' : 'text-gray-500'
              }`}>
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        
        {isProcessing && (
          <div className="flex justify-start">
            <div className="bg-white text-gray-800 border border-gray-200 px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="loading-spinner w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full"></div>
                <span className="text-sm">Аватар печатает...</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Поле ввода */}
      <div className="flex space-x-2">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={isConnected ? "Введите сообщение..." : "Подключитесь для общения"}
          disabled={!isConnected || isProcessing}
          className="flex-1 input-field resize-none"
          rows={3}
        />
        <button
          onClick={handleSendMessage}
          disabled={!isConnected || isProcessing || !inputText.trim()}
          className="btn-primary self-end disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Отправить
        </button>
      </div>
    </div>
  )
}

export default ChatInterface 