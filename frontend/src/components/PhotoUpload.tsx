import React, { useState, useCallback, useRef } from 'react';

interface PhotoUploadProps {
  onPhotosUploaded: (photos: File[]) => void;
  maxFiles?: number;
  acceptedFormats?: string[];
}

const PhotoUpload: React.FC<PhotoUploadProps> = ({
  onPhotosUploaded,
  maxFiles = 5,
  acceptedFormats = ['image/jpeg', 'image/png', 'image/webp']
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedPhotos, setUploadedPhotos] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = useCallback((file: File): string | null => {
    // Проверка формата
    if (!acceptedFormats.includes(file.type)) {
      return `Неподдерживаемый формат: ${file.type}. Поддерживаются: ${acceptedFormats.join(', ')}`;
    }

    // Проверка размера (максимум 10MB)
    if (file.size > 10 * 1024 * 1024) {
      return `Файл слишком большой: ${(file.size / 1024 / 1024).toFixed(1)}MB. Максимум: 10MB`;
    }

    return null;
  }, [acceptedFormats]);

  const processFiles = useCallback((files: FileList) => {
    const newPhotos: File[] = [];
    const newPreviews: string[] = [];
    const errors: string[] = [];

    Array.from(files).forEach((file) => {
      const validationError = validateFile(file);
      if (validationError) {
        errors.push(`${file.name}: ${validationError}`);
        return;
      }

      if (uploadedPhotos.length + newPhotos.length >= maxFiles) {
        errors.push(`Максимальное количество файлов: ${maxFiles}`);
        return;
      }

      newPhotos.push(file);
      
      // Создание превью
      const reader = new FileReader();
      reader.onload = (e) => {
        if (e.target?.result) {
          newPreviews.push(e.target.result as string);
          setPreviews(prev => [...prev, e.target!.result as string]);
        }
      };
      reader.readAsDataURL(file);
    });

    if (errors.length > 0) {
      setError(errors.join('\n'));
      return;
    }

    if (newPhotos.length > 0) {
      const updatedPhotos = [...uploadedPhotos, ...newPhotos];
      setUploadedPhotos(updatedPhotos);
      onPhotosUploaded(updatedPhotos);
      setError(null);
    }
  }, [uploadedPhotos, maxFiles, validateFile, onPhotosUploaded]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFiles(e.dataTransfer.files);
    }
  }, [processFiles]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFiles(e.target.files);
    }
  }, [processFiles]);

  const removePhoto = useCallback((index: number) => {
    const newPhotos = uploadedPhotos.filter((_, i) => i !== index);
    const newPreviews = previews.filter((_, i) => i !== index);
    setUploadedPhotos(newPhotos);
    setPreviews(newPreviews);
    onPhotosUploaded(newPhotos);
  }, [uploadedPhotos, previews, onPhotosUploaded]);

  const openFileDialog = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Область загрузки */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={acceptedFormats.join(',')}
          onChange={handleFileInput}
          className="hidden"
        />
        
        <div className="space-y-4">
          <div className="text-6xl text-gray-400">📸</div>
          <div>
            <p className="text-lg font-medium text-gray-700">
              Перетащите фото сюда или нажмите для выбора
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Поддерживаются: JPG, PNG, WEBP (максимум {maxFiles} файлов, 10MB каждый)
            </p>
          </div>
          
          <button
            type="button"
            onClick={openFileDialog}
            disabled={uploading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {uploading ? 'Загрузка...' : 'Выбрать файлы'}
          </button>
        </div>
      </div>

      {/* Ошибки */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm whitespace-pre-line">{error}</p>
        </div>
      )}

      {/* Загруженные фото */}
      {uploadedPhotos.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-700 mb-4">
            Загруженные фото ({uploadedPhotos.length}/{maxFiles})
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {uploadedPhotos.map((photo, index) => (
              <div key={index} className="relative group">
                <img
                  src={previews[index]}
                  alt={`Фото ${index + 1}`}
                  className="w-full h-32 object-cover rounded-lg border border-gray-200"
                />
                <button
                  onClick={() => removePhoto(index)}
                  className="absolute top-2 right-2 w-6 h-6 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-sm"
                  title="Удалить фото"
                >
                  ×
                </button>
                <div className="mt-2 text-xs text-gray-500">
                  {photo.name.length > 20 
                    ? `${photo.name.substring(0, 20)}...` 
                    : photo.name
                  }
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Рекомендации */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-medium text-blue-800 mb-2">💡 Рекомендации для лучшего результата:</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Используйте фото с четким изображением лица</li>
          <li>• Выберите фото с хорошим освещением</li>
          <li>• Предпочтительно нейтральное выражение лица</li>
          <li>• Простой фон (белый или нейтральный)</li>
          <li>• Разрешение минимум 512x512 пикселей</li>
        </ul>
      </div>
    </div>
  );
};

export default PhotoUpload; 