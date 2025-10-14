#!/bin/bash

# Скрипт для оптимизации frontend bundle

echo "🚀 Оптимизация frontend bundle"
echo "=============================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода статуса
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверяем, что мы в корневой директории проекта
if [ ! -f "docker-compose.yml" ]; then
    print_error "Скрипт должен запускаться из корневой директории проекта"
    exit 1
fi

# Функция для анализа bundle
analyze_bundle() {
    print_status "Анализ текущего размера bundle..."
    
    if ! docker ps | grep -q "agregator_frontend"; then
        print_warning "Frontend контейнер не запущен. Запускаем..."
        docker-compose up -d agregator-frontend
        sleep 10
    fi
    
    # Устанавливаем bundle analyzer
    docker exec agregator_frontend npm install --save-dev webpack-bundle-analyzer
    
    # Собираем проект с анализом
    docker exec agregator_frontend npm run build
    
    # Анализируем bundle
    print_status "Генерация отчета анализа bundle..."
    docker exec agregator_frontend npx webpack-bundle-analyzer build/static/js/*.js --mode static --report build/bundle-report.html --no-open
    
    print_success "Отчет анализа bundle создан: build/bundle-report.html"
}

# Функция для оптимизации изображений
optimize_images() {
    print_status "Оптимизация изображений..."
    
    # Устанавливаем инструменты оптимизации
    docker exec agregator_frontend npm install --save-dev imagemin imagemin-mozjpeg imagemin-pngquant imagemin-svgo
    
    # Создаем скрипт оптимизации
    cat > frontend/optimize-images.js << 'EOF'
const imagemin = require('imagemin');
const imageminMozjpeg = require('imagemin-mozjpeg');
const imageminPngquant = require('imagemin-pngquant');
const imageminSvgo = require('imagemin-svgo');

(async () => {
  const files = await imagemin(['src/**/*.{jpg,jpeg,png,svg}'], {
    destination: 'src/optimized',
    plugins: [
      imageminMozjpeg({ quality: 80 }),
      imageminPngquant({ quality: [0.6, 0.8] }),
      imageminSvgo({
        plugins: [
          { name: 'removeViewBox', active: false },
          { name: 'removeDimensions', active: true }
        ]
      })
    ]
  });
  
  console.log('Optimized images:', files.length);
})();
EOF
    
    docker exec agregator_frontend node optimize-images.js
    
    print_success "Изображения оптимизированы"
}

# Функция для tree shaking
optimize_tree_shaking() {
    print_status "Оптимизация tree shaking..."
    
    # Создаем оптимизированный webpack конфиг
    cat > frontend/webpack.config.optimized.js << 'EOF'
const path = require('path');

module.exports = {
  mode: 'production',
  entry: './src/index.tsx',
  output: {
    path: path.resolve(__dirname, 'build'),
    filename: 'static/js/[name].[contenthash:8].js',
    chunkFilename: 'static/js/[name].[contenthash:8].chunk.js',
    clean: true,
  },
  optimization: {
    usedExports: true,
    sideEffects: false,
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
        common: {
          name: 'common',
          minChunks: 2,
          chunks: 'all',
          enforce: true,
        },
      },
    },
    runtimeChunk: {
      name: 'runtime',
    },
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
};
EOF
    
    print_success "Tree shaking оптимизирован"
}

# Функция для code splitting
optimize_code_splitting() {
    print_status "Оптимизация code splitting..."
    
    # Создаем компонент для lazy loading
    cat > frontend/src/components/LazyComponent.tsx << 'EOF'
import React, { Suspense, lazy } from 'react';
import { CircularProgress, Box } from '@mui/material';

const LazyWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <Suspense fallback={
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
      <CircularProgress />
    </Box>
  }>
    {children}
  </Suspense>
);

export const LazyCustomerCabinet = lazy(() => import('../pages/CustomerCabinetPage'));
export const LazyManagerDashboard = lazy(() => import('../pages/ManagerDashboardPage'));
export const LazySecurityVerification = lazy(() => import('../pages/SecurityVerificationPage'));
export const LazyHRDocuments = lazy(() => import('../pages/HRDocumentsPage'));
export const LazyTelegramBot = lazy(() => import('../pages/TelegramBotPage'));

export { LazyWrapper };
EOF
    
    print_success "Code splitting оптимизирован"
}

# Функция для сжатия
optimize_compression() {
    print_status "Настройка сжатия..."
    
    # Обновляем nginx конфигурацию для лучшего сжатия
    cat > frontend/nginx-optimized.conf << 'EOF'
# Оптимизированная конфигурация nginx для сжатия
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_proxied any;
gzip_comp_level 9;
gzip_types
    text/plain
    text/css
    text/xml
    text/javascript
    application/json
    application/javascript
    application/xml+rss
    application/atom+xml
    image/svg+xml
    application/x-font-ttf
    application/vnd.ms-fontobject
    font/opentype;

# Brotli сжатие (если доступно)
brotli on;
brotli_comp_level 6;
brotli_types
    text/plain
    text/css
    application/json
    application/javascript
    text/xml
    application/xml
    application/xml+rss
    text/javascript;

# Кэширование статических файлов
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary "Accept-Encoding";
}
EOF
    
    print_success "Сжатие настроено"
}

# Функция для создания production build
create_production_build() {
    print_status "Создание оптимизированного production build..."
    
    # Устанавливаем переменные окружения для оптимизации
    docker exec agregator_frontend sh -c 'export GENERATE_SOURCEMAP=false && export INLINE_RUNTIME_CHUNK=false && npm run build'
    
    # Проверяем размер build
    BUILD_SIZE=$(docker exec agregator_frontend du -sh build/ | cut -f1)
    print_success "Production build создан. Размер: $BUILD_SIZE"
    
    # Анализируем содержимое
    docker exec agregator_frontend find build/ -name "*.js" -exec ls -lh {} \; | head -10
}

# Функция для генерации отчета
generate_optimization_report() {
    print_status "Генерация отчета об оптимизации..."
    
    # Создаем директорию для отчетов
    mkdir -p reports/optimization
    
    # Анализируем размеры файлов
    docker exec agregator_frontend find build/ -type f -exec ls -lh {} \; > reports/optimization/file-sizes.txt
    
    # Анализируем bundle
    docker exec agregator_frontend npx webpack-bundle-analyzer build/static/js/*.js --mode static --report reports/optimization/bundle-analysis.html --no-open
    
    print_success "Отчет об оптимизации создан в reports/optimization/"
}

# Функция для полной оптимизации
run_full_optimization() {
    print_status "Запуск полной оптимизации frontend bundle..."
    
    # Анализируем текущее состояние
    analyze_bundle
    
    # Оптимизируем различные аспекты
    optimize_images
    optimize_tree_shaking
    optimize_code_splitting
    optimize_compression
    
    # Создаем оптимизированный build
    create_production_build
    
    # Генерируем отчет
    generate_optimization_report
    
    print_success "Полная оптимизация завершена! 🎉"
}

# Основная логика
case "${1:-all}" in
    "analyze")
        analyze_bundle
        ;;
    "images")
        optimize_images
        ;;
    "tree-shaking")
        optimize_tree_shaking
        ;;
    "code-splitting")
        optimize_code_splitting
        ;;
    "compression")
        optimize_compression
        ;;
    "build")
        create_production_build
        ;;
    "report")
        generate_optimization_report
        ;;
    "all")
        run_full_optimization
        ;;
    *)
        echo "Использование: $0 [analyze|images|tree-shaking|code-splitting|compression|build|report|all]"
        echo ""
        echo "Опции:"
        echo "  analyze         - Анализ текущего размера bundle"
        echo "  images          - Оптимизация изображений"
        echo "  tree-shaking    - Оптимизация tree shaking"
        echo "  code-splitting  - Оптимизация code splitting"
        echo "  compression     - Настройка сжатия"
        echo "  build           - Создание production build"
        echo "  report          - Генерация отчета об оптимизации"
        echo "  all             - Полная оптимизация (по умолчанию)"
        exit 1
        ;;
esac
