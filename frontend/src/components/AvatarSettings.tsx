import React, { useState, useCallback } from 'react';
import PhotoUpload from './PhotoUpload';

interface AvatarSettingsProps {
  onSettingsSaved: (settings: AvatarSettings) => void;
}

export interface AvatarSettings {
  photos: File[];
  voiceSamples: File[];
  personality: string;
  name: string;
  description: string;
}

const AvatarSettings: React.FC<AvatarSettingsProps> = ({ onSettingsSaved }) => {
  const [settings, setSettings] = useState<AvatarSettings>({
    photos: [],
    voiceSamples: [],
    personality: '',
    name: '',
    description: ''
  });
  
  const [activeTab, setActiveTab] = useState<'photos' | 'voice' | 'personality'>('photos');
  const [isSaving, setIsSaving] = useState(false);

  const handlePhotosUploaded = useCallback((photos: File[]) => {
    setSettings(prev => ({
      ...prev,
      photos
    }));
  }, []);

  const handleVoiceSamplesUploaded = useCallback((samples: File[]) => {
    setSettings(prev => ({
      ...prev,
      voiceSamples: samples
    }));
  }, []);

  const handleInputChange = useCallback((field: keyof AvatarSettings, value: string) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);

  const handleSave = useCallback(async () => {
    if (settings.photos.length === 0) {
      alert('Пожалуйста, загрузите хотя бы одно фото');
      return;
    }

    setIsSaving(true);
    try {
      // Здесь будет API вызов для сохранения настроек
      await new Promise(resolve => setTimeout(resolve, 1000)); // Имитация API
      onSettingsSaved(settings);
    } catch (error) {
      console.error('Ошибка сохранения настроек:', error);
      alert('Ошибка сохранения настроек');
    } finally {
      setIsSaving(false);
    }
  }, [settings, onSettingsSaved]);

  const tabs = [
    { id: 'photos', label: '📸 Фотографии', icon: '📸' },
    { id: 'voice', label: '🎤 Голос', icon: '🎤' },
    { id: 'personality', label: '🧠 Личность', icon: '🧠' }
  ] as const;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Настройка цифрового аватара
        </h1>
        <p className="text-gray-600">
          Загрузите фотографии, запишите голос и настройте личность вашего аватара
        </p>
      </div>

      {/* Вкладки */}
      <div className="border-b border-gray-200 mb-8">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Содержимое вкладок */}
      <div className="min-h-[400px]">
        {activeTab === 'photos' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Загрузка фотографий
              </h2>
              <p className="text-gray-600 mb-6">
                Загрузите качественные фотографии лица для создания аватара. 
                Рекомендуется 3-5 фото с разных ракурсов.
              </p>
            </div>
            
            <PhotoUpload
              onPhotosUploaded={handlePhotosUploaded}
              maxFiles={5}
              acceptedFormats={['image/jpeg', 'image/png', 'image/webp']}
            />
          </div>
        )}

        {activeTab === 'voice' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Запись голоса
              </h2>
              <p className="text-gray-600 mb-6">
                Запишите образцы голоса для клонирования. 
                Говорите четко и естественно, включая разные эмоции.
              </p>
            </div>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <div className="text-6xl text-gray-400 mb-4">🎤</div>
              <p className="text-lg font-medium text-gray-700 mb-2">
                Запись голоса
              </p>
              <p className="text-sm text-gray-500 mb-4">
                Нажмите кнопку для начала записи голоса
              </p>
              <button className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                🎙️ Начать запись
              </button>
            </div>
          </div>
        )}

        {activeTab === 'personality' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Настройка личности
              </h2>
              <p className="text-gray-600 mb-6">
                Опишите характер и стиль общения вашего аватара
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Имя аватара
                </label>
                <input
                  type="text"
                  value={settings.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="Введите имя аватара"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Возраст
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                  <option>Выберите возраст</option>
                  <option>5-10 лет</option>
                  <option>11-15 лет</option>
                  <option>16-20 лет</option>
                  <option>21-25 лет</option>
                  <option>26-30 лет</option>
                  <option>31+ лет</option>
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Описание личности
              </label>
              <textarea
                value={settings.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Опишите характер, интересы, стиль общения аватара..."
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Стиль общения
              </label>
              <textarea
                value={settings.personality}
                onChange={(e) => handleInputChange('personality', e.target.value)}
                placeholder="Опишите как аватар должен общаться: формально/неформально, дружелюбно/серьезно, используемые слова и фразы..."
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        )}
      </div>

      {/* Кнопки действий */}
      <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
        <div className="text-sm text-gray-500">
          {settings.photos.length > 0 && (
            <span className="mr-4">📸 Фото: {settings.photos.length}</span>
          )}
          {settings.voiceSamples.length > 0 && (
            <span>🎤 Аудио: {settings.voiceSamples.length}</span>
          )}
        </div>
        
        <div className="space-x-4">
          <button
            onClick={() => setActiveTab('photos')}
            disabled={isSaving}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors"
          >
            Назад
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving || settings.photos.length === 0}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSaving ? 'Сохранение...' : 'Сохранить настройки'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AvatarSettings; 