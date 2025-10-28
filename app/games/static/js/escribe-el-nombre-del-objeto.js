/**
 * Juego: Escribe el Nombre del Objeto (Refactorizado)
 * Extiende BaseGame para reutilizar funcionalidad común
 */

class EscribeElNombreGame extends BaseGame {
    constructor(sessionData, gameConfig) {
        super(sessionData, gameConfig, 'Escribe el Nombre');
    }
    
    createGameInterface() {
        const gameArea = document.getElementById('game-area');
        if (!gameArea) {
            console.error('❌ No se encontró el elemento #game-area');
            return;
        }
        
        gameArea.innerHTML = `
            <div class="write-word-game max-w-7xl mx-auto p-4">
                <!-- Encabezado del juego -->
                ${GameUtils.createGameHeader({
                    title: 'Escribe el Nombre',
                    iconGradient: 'from-green-500 to-teal-500',
                    iconSvg: GameUtils.icons.edit
                })}

                <!-- Contenedor de dos columnas -->
                <div class="grid grid-cols-2 gap-6">
                    <!-- COLUMNA IZQUIERDA - Imagen y timer/intentos -->
                    <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 transition-colors duration-200">
                        ${GameUtils.createTimerAndAttempts(60)}
                        ${GameUtils.createImageContainer()}
                        ${GameUtils.createHintPanel()}

                        <!-- Información adicional -->
                        <div class="grid grid-cols-2 gap-3">
                            <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 text-center border border-green-200 dark:border-green-800">
                                <div class="text-xs text-green-600 dark:text-green-400 mb-1">Categoría</div>
                                <div id="word-category" class="text-sm font-medium text-green-700 dark:text-green-300">---</div>
                            </div>
                            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 text-center border border-blue-200 dark:border-blue-800">
                                <div class="text-xs text-blue-600 dark:text-blue-400 mb-1">Letras</div>
                                <div id="word-length" class="text-sm font-medium text-blue-700 dark:text-blue-300">0</div>
                            </div>
                        </div>

                        ${GameUtils.createHintButton('Ver respuesta (-3 puntos)')}
                    </div>

                    <!-- COLUMNA DERECHA - Campo de escritura -->
                    <div class="space-y-6">
                        <!-- Área de escritura -->
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 transition-colors duration-200">
                            <h3 class="text-center text-sm font-medium text-gray-700 dark:text-gray-300 mb-6">
                                <svg class="w-5 h-5 inline mr-2 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                                Escribe el nombre del objeto
                            </h3>
                            
                            <div class="mb-6">
                                <input type="text" 
                                    id="word-input" 
                                    class="w-full px-6 py-4 text-2xl font-bold text-center text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-800 border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent uppercase tracking-wider"
                                    placeholder="ESCRIBE AQUÍ"
                                    autocomplete="off"
                                    spellcheck="false"
                                    maxlength="20">
                            </div>

                            <!-- Indicadores visuales -->
                            <div id="letter-boxes" class="flex justify-center gap-2 mb-6 flex-wrap">
                                <!-- Cajas de letras se generan dinámicamente -->
                            </div>

                            <div class="flex justify-center gap-3">
                                <button id="clear-input-btn" class="px-6 py-3 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg border border-gray-300 dark:border-gray-700 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors font-medium">
                                    <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                    Borrar
                                </button>
                                <button id="check-word-btn" class="px-6 py-3 bg-green-500 dark:bg-green-600 text-white rounded-lg hover:bg-green-600 dark:hover:bg-green-700 transition-colors font-medium shadow-sm">
                                    <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                    </svg>
                                    Verificar
                                </button>
                            </div>
                        </div>
                        
                        <!-- Panel de ayuda -->
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 transition-colors duration-200">
                            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4 text-center">Consejos</h3>
                            
                            <div class="space-y-3">
                                <div class="flex items-start gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                                    <svg class="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <div>
                                        <p class="text-xs font-medium text-blue-700 dark:text-blue-300">Observa bien</p>
                                        <p class="text-xs text-blue-600 dark:text-blue-400">Mira la imagen con atención</p>
                                    </div>
                                </div>

                                <div class="flex items-start gap-3 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                    <svg class="w-5 h-5 text-purple-600 dark:text-purple-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                    <div>
                                        <p class="text-xs font-medium text-purple-700 dark:text-purple-300">Escribe claro</p>
                                        <p class="text-xs text-purple-600 dark:text-purple-400">Usa mayúsculas sin acentos</p>
                                    </div>
                                </div>

                                <div class="flex items-start gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <svg class="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <div>
                                        <p class="text-xs font-medium text-green-700 dark:text-green-300">Tómate tu tiempo</p>
                                        <p class="text-xs text-green-600 dark:text-green-400">Tienes 3 intentos</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        const wordInput = document.getElementById('word-input');
        const checkBtn = document.getElementById('check-word-btn');
        const clearBtn = document.getElementById('clear-input-btn');
        const hintBtn = document.getElementById('show-hint-btn');

        // Input en tiempo real
        wordInput?.addEventListener('input', (e) => {
            e.target.value = e.target.value.toUpperCase().replace(/[^A-ZÑ]/g, '');
            this.updateLetterBoxes(e.target.value);
        });

        // Enter para verificar
        wordInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.checkWord();
            }
        });

        checkBtn?.addEventListener('click', () => this.checkWord());
        clearBtn?.addEventListener('click', () => this.clearInput());
        hintBtn?.addEventListener('click', () => this.showHint());
    }
    
    renderQuestion() {
        if (!this.currentQuestion) return;
        
        this.updateQuestionCounter();
        
        // Cargar imagen
        const imageEl = document.getElementById('question-image');
        imageEl.src = this.currentQuestion.image_path;
        imageEl.alt = this.currentQuestion.hint;
        
        // Mostrar pista
        document.getElementById('hint-text').textContent = this.currentQuestion.hint;
        
        // Mostrar información
        document.getElementById('word-category').textContent = this.currentQuestion.category;
        document.getElementById('word-length').textContent = `${this.currentQuestion.word_length} letras`;
        
        // Actualizar contador de intentos
        this.updateAttemptsCounter();
        
        // Limpiar input y cajas
        this.clearInput();
        this.createLetterBoxes();
        
        // Focus en el input
        setTimeout(() => {
            document.getElementById('word-input')?.focus();
        }, 100);
    }
    
    createLetterBoxes() {
        const container = document.getElementById('letter-boxes');
        container.innerHTML = '';
        
        for (let i = 0; i < this.currentQuestion.word_length; i++) {
            const box = document.createElement('div');
            box.className = `
                letter-box w-12 h-14 border-2 border-gray-300 dark:border-gray-600
                rounded-lg flex items-center justify-center text-xl font-bold
                bg-white dark:bg-gray-800 text-gray-400 dark:text-gray-500
                transition-all duration-200
            `;
            box.dataset.index = i;
            container.appendChild(box);
        }
    }
    
    updateLetterBoxes(value) {
        const boxes = document.querySelectorAll('.letter-box');
        
        boxes.forEach((box, index) => {
            if (index < value.length) {
                box.textContent = value[index];
                box.classList.remove('border-gray-300', 'dark:border-gray-600', 'text-gray-400', 'dark:text-gray-500');
                box.classList.add('border-green-500', 'dark:border-green-600', 'bg-green-50', 'dark:bg-green-900/20', 'text-green-700', 'dark:text-green-300');
            } else {
                box.textContent = '';
                box.classList.remove('border-green-500', 'dark:border-green-600', 'bg-green-50', 'dark:bg-green-900/20', 'text-green-700', 'dark:text-green-300');
                box.classList.add('border-gray-300', 'dark:border-gray-600', 'text-gray-400', 'dark:text-gray-500');
            }
        });
    }
    
    clearInput() {
        const input = document.getElementById('word-input');
        if (input) {
            input.value = '';
            this.updateLetterBoxes('');
        }
    }
    
    checkWord() {
        if (!this.isGameActive) return;
        
        const input = document.getElementById('word-input');
        const userAnswer = input.value.trim().toUpperCase();
        
        if (userAnswer.length === 0) {
            this.showMessage('Por favor escribe una palabra', 'warning');
            return;
        }
        
        const isCorrect = userAnswer === this.currentQuestion.correct_word;
        const responseTime = Date.now() - this.questionStartTime;
        
        this.attempts++;
        this.updateAttemptsCounter();
        
        if (isCorrect) {
            this.handleCorrectAnswerWithBonus(responseTime, userAnswer);
        } else {
            const noMoreAttempts = this.handleIncorrectAnswer(userAnswer, responseTime);
            
            if (noMoreAttempts) {
                this.showCorrectAnswer();
                setTimeout(() => {
                    this.proceedToNext();
                }, 3500);
            } else {
                this.showErrorAnimationInput();
                this.showMessage(`Intento ${this.attempts}/3 - Intenta de nuevo`, 'error');
                
                setTimeout(() => {
                    this.clearInput();
                    document.getElementById('word-input')?.focus();
                }, 1000);
            }
        }
    }
    
    handleCorrectAnswerWithBonus(responseTime, userAnswer) {
        this.correctAnswers++;
        this.stopQuestionTimer();
        this.isGameActive = false;
        
        // Calcular puntos con bonus especial
        const timeBonus = Math.max(0, this.currentQuestion.time_limit - Math.floor(responseTime / 1000));
        let points = this.currentQuestion.points + (timeBonus * this.gameConfig.scoring.time_bonus);
        
        // Bonus por ortografía perfecta en primer intento
        if (this.attempts === 1) {
            points += this.gameConfig.scoring.spelling_bonus || 5;
        }
        
        // Penalización por usar pista
        if (this.hintUsed) {
            points -= this.gameConfig.scoring.hint_penalty;
        }
        
        this.score += Math.max(0, points);
        
        // Animación de éxito
        this.showSuccessAnimation();
        
        // Enviar respuesta
        this.sendQuestionResponse(true, responseTime, userAnswer);
        
        // Actualizar UI
        this.updateScore();
        
        // Continuar al siguiente
        setTimeout(() => {
            this.proceedToNext();
        }, 2500);
    }
    
    showHint() {
        if (this.hintUsed) return;
        
        this.hintUsed = true;
        const hintBtn = document.getElementById('show-hint-btn');
        hintBtn.disabled = true;
        hintBtn.classList.add('opacity-50', 'cursor-not-allowed');
        
        // Mostrar la respuesta en el input temporalmente
        const input = document.getElementById('word-input');
        const originalValue = input.value;
        
        input.value = this.currentQuestion.correct_word;
        input.classList.add('bg-yellow-50', 'dark:bg-yellow-900/30', 'border-yellow-400', 'dark:border-yellow-600');
        this.updateLetterBoxes(this.currentQuestion.correct_word);
        
        this.showMessage('Respuesta mostrada (-3 puntos)', 'warning');
        
        setTimeout(() => {
            input.value = originalValue;
            input.classList.remove('bg-yellow-50', 'dark:bg-yellow-900/30', 'border-yellow-400', 'dark:border-yellow-600');
            this.updateLetterBoxes(originalValue);
            input.focus();
        }, 3000);
    }
    
    showSuccessAnimation() {
        const boxes = document.querySelectorAll('.letter-box');
        boxes.forEach((box, index) => {
            setTimeout(() => {
                box.classList.add('animate-bounce');
                box.classList.add('bg-green-500', 'dark:bg-green-600', 'text-white', 'border-green-600', 'dark:border-green-700');
            }, index * 100);
        });
        
        this.showMessage('¡Correcto! ✨', 'success');
    }
    
    showErrorAnimationInput() {
        const input = document.getElementById('word-input');
        input.style.animation = 'shake 0.5s';
        input.classList.add('border-red-500', 'dark:border-red-600');
        
        setTimeout(() => {
            input.style.animation = '';
            input.classList.remove('border-red-500', 'dark:border-red-600');
        }, 500);
    }
    
    showCorrectAnswer() {
        const input = document.getElementById('word-input');
        input.value = this.currentQuestion.correct_word;
        input.classList.add('bg-blue-50', 'dark:bg-blue-900/30', 'border-blue-500', 'dark:border-blue-600');
        this.updateLetterBoxes(this.currentQuestion.correct_word);
        
        const boxes = document.querySelectorAll('.letter-box');
        boxes.forEach(box => {
            box.classList.add('bg-blue-100', 'dark:bg-blue-900/30', 'border-blue-500', 'dark:border-blue-600', 'text-blue-700', 'dark:text-blue-300');
        });
        
        this.showMessage(`La respuesta correcta era: ${this.currentQuestion.correct_word}`, 'info');
    }
    
    showMessage(text, type = 'info') {
        let messageEl = document.getElementById('game-message');
        
        if (!messageEl) {
            messageEl = document.createElement('div');
            messageEl.id = 'game-message';
            document.body.appendChild(messageEl);
        }
        
        const styles = {
            success: 'bg-green-500 text-white',
            error: 'bg-red-500 text-white',
            warning: 'bg-yellow-500 text-white',
            info: 'bg-blue-500 text-white'
        };
        
        messageEl.className = `fixed top-20 left-1/2 transform -translate-x-1/2 z-50 px-6 py-3 rounded-lg shadow-lg font-medium text-sm ${styles[type]}`;
        messageEl.textContent = text;
        messageEl.style.animation = 'slideUp 0.3s ease-out';
        
        setTimeout(() => {
            messageEl.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => {
                messageEl.remove();
            }, 300);
        }, 2500);
    }
    
    onTimeUp() {
        this.showCorrectAnswer();
        this.showMessage('Se acabó el tiempo ⏰', 'warning');
    }
    
    // Métodos de personalización de UI
    getGameGradient() {
        return 'bg-gradient-to-r from-green-500 to-teal-500';
    }
    
    getSuccessIcon() {
        return `
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        `;
    }
    
    getSuccessMessage() {
        return 'Excelente trabajo escribiendo palabras';
    }
    
    getScoreCardClass() {
        return 'bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800';
    }
    
    getScoreTextClass() {
        return 'text-green-600 dark:text-green-400';
    }
}

// Animaciones CSS adicionales
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translate(-50%, 20px);
        }
        to {
            opacity: 1;
            transform: translate(-50%, 0);
        }
    }
    
    @keyframes fadeOut {
        from { 
            opacity: 1; 
            transform: translate(-50%, 0); 
        }
        to { 
            opacity: 0; 
            transform: translate(-50%, -20px); 
        }
    }
`;
document.head.appendChild(style);

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.gameSessionData !== 'undefined' && typeof window.gameConfig !== 'undefined') {
        window.gameInstance = new EscribeElNombreGame(window.gameSessionData, window.gameConfig);
        window.gameInstance.init();
    } else {
        console.error('❌ Faltan datos de sesión');
    }
});