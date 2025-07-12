import React from 'react'

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">А</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900">
              Цифровой Аватар
            </h1>
          </div>
          
          <nav className="hidden md:flex items-center space-x-6">
            <a href="#" className="text-gray-600 hover:text-primary-600 transition-colors">
              Главная
            </a>
            <a href="#" className="text-gray-600 hover:text-primary-600 transition-colors">
              Документация
            </a>
            <a href="#" className="text-gray-600 hover:text-primary-600 transition-colors">
              О проекте
            </a>
          </nav>
          
          <div className="flex items-center space-x-3">
            <button className="btn-secondary text-sm">
              Настройки
            </button>
            <button className="btn-primary text-sm">
              Начать общение
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header 