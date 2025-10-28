/**
 * Utilidades compartidas para todos los minijuegos
 * Componentes UI reutilizables y helpers
 */

const GameUtils = {
    
    /**
     * Crea el header común para todos los juegos
     */
    createGameHeader(config) {
        const { 
            title, 
            iconGradient = 'from-purple-500 to-pink-500',
            iconSvg,
            currentQuestion = 1,
            totalQuestions = 5,
            score = 0
        } = config;
        
        return `
            <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 mb-6 transition-colors duration-200">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <div class="w-12 h-12 bg-gradient-to-r ${iconGradient} rounded-xl flex items-center justify-center">
                            ${iconSvg}
                        </div>
                        <div>
                            <h2 class="text-xl font-bold text-gray-900 dark:text-white">${title}</h2>
                            <p class="text-sm text-gray-500 dark:text-gray-400">
                                Nivel 1 • Pregunta <span id="current-question">${currentQuestion}</span> de <span id="total-questions">${totalQuestions}</span>
                            </p>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-3xl font-bold text-gray-900 dark:text-white" id="game-score">${score}</div>
                        <div class="text-xs font-medium text-gray-500 dark:text-gray-400">Puntos</div>
                    </div>
                </div>
            </div>
        `;
    },
    
    /**
     * Crea el panel de timer e intentos
     */
    createTimerAndAttempts(timeLimit = 30, attempts = 0) {
        return `
            <div class="flex justify-center gap-4 mb-6">
                <div class="inline-flex items-center gap-2 bg-orange-50 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 px-4 py-2 rounded-lg border border-orange-200 dark:border-orange-800">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span id="question-timer" class="font-semibold">${timeLimit}</span>
                    <span class="text-sm">seg</span>
                </div>
                <div class="inline-flex items-center gap-2 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 px-4 py-2 rounded-lg border border-blue-200 dark:border-blue-800">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span class="text-sm">Intentos: <span id="attempts-counter" class="font-semibold">${attempts}/3</span></span>
                </div>
            </div>
        `;
    },
    
    /**
     * Crea el contenedor de imagen
     */
    createImageContainer() {
        return `
            <div class="flex justify-center mb-6">
                <div class="relative">
                    <img id="question-image" 
                        src="" 
                        alt="Pista visual" 
                        class="w-80 h-64 object-contain rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 shadow-sm">
                </div>
            </div>
        `;
    },
    
    /**
     * Crea el panel de pista
     */
    createHintPanel() {
        return `
            <div class="text-center mb-4">
                <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">Pista</p>
                <p id="hint-text" class="text-lg font-medium text-gray-900 dark:text-white"></p>
            </div>
        `;
    },
    
    /**
     * Crea el botón de pista adicional
     */
    createHintButton(buttonText = 'Ver pista (-5 puntos)') {
        return `
            <div class="text-center">
                <button id="show-hint-btn" class="px-4 py-2 bg-yellow-50 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400 rounded-lg border border-yellow-200 dark:border-yellow-800 hover:bg-yellow-100 dark:hover:bg-yellow-900/50 transition-colors text-sm font-medium">
                    <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    ${buttonText}
                </button>
            </div>
        `;
    },
    
    /**
     * Iconos SVG predefinidos
     */
    icons: {
        edit: `
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
        `,
        warning: `
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
        `,
        search: `
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
        `,
        puzzle: `
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
            </svg>
        `,
        check: `
            <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        `,
        cross: `
            <svg class="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        `
    },
    
    /**
     * Gradientes predefinidos por tipo de juego
     */
    gradients: {
        purple: 'from-purple-500 to-pink-500',
        red: 'from-red-500 to-orange-500',
        blue: 'from-blue-500 to-cyan-500',
        green: 'from-green-500 to-emerald-500',
        yellow: 'from-yellow-500 to-amber-500'
    },
    
    /**
     * Crea una tarjeta de estadística
     */
    createStatCard(value, label, colorClass = 'purple') {
        const colorClasses = {
            purple: 'bg-purple-50 dark:bg-purple-900/30 border-purple-200 dark:border-purple-800 text-purple-600 dark:text-purple-400',
            green: 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800 text-green-600 dark:text-green-400',
            red: 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800 text-red-600 dark:text-red-400',
            yellow: 'bg-yellow-50 dark:bg-yellow-900/30 border-yellow-200 dark:border-yellow-800 text-yellow-600 dark:text-yellow-400',
            blue: 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800 text-blue-600 dark:text-blue-400'
        };
        
        return `
            <div class="${colorClasses[colorClass]} border rounded-xl p-4 text-center">
                <div class="text-3xl font-bold mb-1">${value}</div>
                <div class="text-xs font-medium text-gray-600 dark:text-gray-400">${label}</div>
            </div>
        `;
    },
    
    /**
     * Formatea el tiempo en formato legible
     */
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
    },
    
    /**
     * Calcula el porcentaje de precisión
     */
    calculateAccuracy(correct, total) {
        if (total === 0) return 0;
        return Math.round((correct / total) * 100);
    },
    
    /**
     * Muestra una notificación toast
     */
    showToast(message, type = 'info') {
        const toastColors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };
        
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 ${toastColors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('animate-fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },
    
    /**
     * Crea un loader/spinner
     */
    createLoader() {
        return `
            <div class="flex items-center justify-center p-8">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
            </div>
        `;
    },
    
    /**
     * Valida si hay conexión a internet
     */
    async checkConnection() {
        try {
            const response = await fetch('/ping', { method: 'HEAD' });
            return response.ok;
        } catch {
            return false;
        }
    },
    
    /**
     * Debounce function para optimizar eventos
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Detecta si el usuario está en modo oscuro
     */
    isDarkMode() {
        return document.documentElement.classList.contains('dark') ||
               window.matchMedia('(prefers-color-scheme: dark)').matches;
    },
    
    /**
     * Genera un ID único
     */
    generateId() {
        return `game_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    },
    
    /**
     * Guarda datos en localStorage con prefijo
     */
    saveLocal(key, data) {
        try {
            localStorage.setItem(`dyslexia_game_${key}`, JSON.stringify(data));
            return true;
        } catch (e) {
            console.error('Error guardando en localStorage:', e);
            return false;
        }
    },
    
    /**
     * Recupera datos de localStorage
     */
    loadLocal(key) {
        try {
            const data = localStorage.getItem(`dyslexia_game_${key}`);
            return data ? JSON.parse(data) : null;
        } catch (e) {
            console.error('Error cargando de localStorage:', e);
            return null;
        }
    },
    
    /**
     * Limpia datos antiguos de localStorage
     */
    cleanOldData(daysOld = 7) {
        const cutoffTime = Date.now() - (daysOld * 24 * 60 * 60 * 1000);
        
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('dyslexia_game_')) {
                try {
                    const data = JSON.parse(localStorage.getItem(key));
                    if (data.timestamp && data.timestamp < cutoffTime) {
                        localStorage.removeItem(key);
                    }
                } catch (e) {
                    // Si hay error parseando, eliminar la clave
                    localStorage.removeItem(key);
                }
            }
        }
    }
};

// Estilos adicionales para animaciones
const utilStyles = document.createElement('style');
utilStyles.textContent = `
    @keyframes fade-in {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fade-out {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-10px);
        }
    }
    
    .animate-fade-in {
        animation: fade-in 0.3s ease-out;
    }
    
    .animate-fade-out {
        animation: fade-out 0.3s ease-in;
    }
`;
document.head.appendChild(utilStyles);

// Exportar para uso global
window.GameUtils = GameUtils;