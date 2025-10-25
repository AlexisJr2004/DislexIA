/**
 * Juego: Escribe el Nombre del Objeto
 * El jugador debe escribir correctamente el nombre del objeto mostrado en la imagen
 */

class EscribeElNombreGame {
    constructor(sessionData, gameConfig) {
        this.sessionData = sessionData;
        this.gameConfig = gameConfig;
        this.currentLevel = 1;
        this.currentQuestionIndex = 0;
        this.currentQuestion = null;
        this.score = 0;
        this.correctAnswers = 0;
        this.incorrectAnswers = 0;
        this.startTime = Date.now();
        this.questionStartTime = null;
        this.isGameActive = false;
        this.selectedQuestions = null;
        this.attempts = 0;
        this.hintUsed = false;
        this.init();
    }
    
    init() {
        this.createGameInterface();
        this.bindEvents();
        this.startGame();
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
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 mb-6 transition-colors duration-200">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <div class="w-12 h-12 bg-gradient-to-r from-green-500 to-teal-500 rounded-xl flex items-center justify-center">
                                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                </svg>
                            </div>
                            <div>
                                <h2 class="text-xl font-bold text-gray-900 dark:text-white">Escribe el Nombre</h2>
                                <p class="text-sm text-gray-500 dark:text-gray-400">Nivel 1 • Pregunta <span id="current-question">1</span> de <span id="total-questions">5</span></p>
                            </div>
                        </div>
                        <div class="text-right">
                            <div class="text-3xl font-bold text-gray-900 dark:text-white" id="game-score">0</div>
                            <div class="text-xs font-medium text-gray-500 dark:text-gray-400">Puntos</div>
                        </div>
                    </div>
                </div>

                <!-- Contenedor de dos columnas -->
                <div class="grid grid-cols-2 gap-6">
                    <!-- COLUMNA IZQUIERDA - Imagen y timer/intentos -->
                    <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 transition-colors duration-200">
                        <!-- Timer e intentos -->
                        <div class="flex justify-center gap-4 mb-6">
                            <div class="inline-flex items-center gap-2 bg-orange-50 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 px-4 py-2 rounded-lg border border-orange-200 dark:border-orange-800">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span id="question-timer" class="font-semibold">60</span>
                                <span class="text-sm">seg</span>
                            </div>
                            <div class="inline-flex items-center gap-2 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 px-4 py-2 rounded-lg border border-blue-200 dark:border-blue-800">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span class="text-sm">Intentos: <span id="attempts-counter" class="font-semibold">0/3</span></span>
                            </div>
                        </div>
                        
                        <!-- Imagen -->
                        <div class="flex justify-center mb-6">
                            <div class="relative">
                                <img id="question-image" 
                                    src="" 
                                    alt="Objeto a identificar" 
                                    class="w-96 h-72 object-contain rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 shadow-lg">
                            </div>
                        </div>
                        
                        <!-- Pista -->
                        <div class="text-center mb-4">
                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">Pista</p>
                            <p id="hint-text" class="text-lg font-medium text-gray-900 dark:text-white"></p>
                        </div>

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

                        <!-- Botón de pista adicional -->
                        <div class="text-center mt-4">
                            <button id="show-hint-btn" class="px-4 py-2 bg-yellow-50 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400 rounded-lg border border-yellow-200 dark:border-yellow-800 hover:bg-yellow-100 dark:hover:bg-yellow-900/50 transition-colors text-sm font-medium">
                                <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Ver respuesta (-3 puntos)
                            </button>
                        </div>
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
    
    startGame() {
        this.isGameActive = true;
        this.loadCurrentQuestion();
    }
    
    getCurrentLevelQuestions() {
        const level = this.gameConfig.levels.find(l => l.level === this.currentLevel);
        if (!level || !level.questions) return [];
        
        if (!this.selectedQuestions || this.selectedQuestions.level !== this.currentLevel) {
            this.selectedQuestions = {
                level: this.currentLevel,
                questions: this.getRandomQuestions(level.questions, 5)
            };
        }
        
        return this.selectedQuestions.questions;
    }
    
    getRandomQuestions(questions, count) {
        const shuffled = [...questions];
        
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        
        return shuffled.slice(0, Math.min(count, shuffled.length));
    }
    
    loadCurrentQuestion() {
        const questions = this.getCurrentLevelQuestions();
        
        if (this.currentQuestionIndex >= questions.length) {
            this.finishLevel();
            return;
        }
        
        this.currentQuestion = questions[this.currentQuestionIndex];
        this.questionStartTime = Date.now();
        this.attempts = 0;
        this.hintUsed = false;
        
        this.renderQuestion();
        this.startQuestionTimer();
        this.updateProgress();
    }
    
    renderQuestion() {
        if (!this.currentQuestion) return;
        
        // Actualizar contador de preguntas
        document.getElementById('current-question').textContent = this.currentQuestionIndex + 1;
        document.getElementById('total-questions').textContent = this.getCurrentLevelQuestions().length;
        
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
        document.getElementById('attempts-counter').textContent = `${this.attempts}/3`;
        
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
        document.getElementById('attempts-counter').textContent = `${this.attempts}/3`;
        
        if (isCorrect) {
            this.handleCorrectAnswer(responseTime, userAnswer);
        } else {
            this.handleIncorrectAnswer(userAnswer);
        }
    }
    
    handleCorrectAnswer(responseTime, userAnswer) {
        this.correctAnswers++;
        this.stopQuestionTimer();
        this.isGameActive = false;
        
        // Calcular puntos
        const timeBonus = Math.max(0, this.currentQuestion.time_limit - Math.floor(responseTime / 1000));
        let points = this.currentQuestion.points + (timeBonus * this.gameConfig.scoring.time_bonus);
        
        // Bonus por ortografía perfecta en primer intento
        if (this.attempts === 1) {
            points += this.gameConfig.scoring.spelling_bonus;
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
    
    handleIncorrectAnswer(userAnswer) {
        if (this.attempts >= 3) {
            this.incorrectAnswers++;
            this.stopQuestionTimer();
            this.isGameActive = false;
            
            // Mostrar respuesta correcta
            this.showCorrectAnswer();
            
            const responseTime = Date.now() - this.questionStartTime;
            this.sendQuestionResponse(false, responseTime, userAnswer);
            
            setTimeout(() => {
                this.proceedToNext();
            }, 3500);
        } else {
            // Mostrar animación de error
            this.showErrorAnimation();
            this.showMessage(`Intento ${this.attempts}/3 - Intenta de nuevo`, 'error');
            
            // Limpiar input después de un momento
            setTimeout(() => {
                this.clearInput();
                document.getElementById('word-input')?.focus();
            }, 1000);
        }
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
    
    showErrorAnimation() {
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
        // Crear o actualizar mensaje
        let messageEl = document.getElementById('game-message');
        
        if (!messageEl) {
            messageEl = document.createElement('div');
            messageEl.id = 'game-message';
            messageEl.className = 'fixed top-20 left-1/2 transform -translate-x-1/2 z-50 px-6 py-3 rounded-lg shadow-lg font-medium text-sm';
            document.body.appendChild(messageEl);
        }
        
        // Estilos según tipo
        const styles = {
            success: 'bg-green-500 text-white',
            error: 'bg-red-500 text-white',
            warning: 'bg-yellow-500 text-white',
            info: 'bg-blue-500 text-white'
        };
        
        messageEl.className = `fixed top-20 left-1/2 transform -translate-x-1/2 z-50 px-6 py-3 rounded-lg shadow-lg font-medium text-sm ${styles[type]}`;
        messageEl.textContent = text;
        messageEl.style.animation = 'slideUp 0.3s ease-out';
        
        // Auto ocultar
        setTimeout(() => {
            messageEl.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => {
                messageEl.remove();
            }, 300);
        }, 2500);
    }
    
    proceedToNext() {
        const questions = this.getCurrentLevelQuestions();
        const isLastQuestion = this.currentQuestionIndex >= questions.length - 1;
        
        if (isLastQuestion) {
            this.finishLevel();
        } else {
            this.nextQuestion();
        }
    }
    
    nextQuestion() {
        this.currentQuestionIndex++;
        this.isGameActive = true;
        this.loadCurrentQuestion();
    }
    
    finishLevel() {
        this.isGameActive = false;
        
        // ⭐ NUEVO: Diferenciar entre evaluación IA y juego individual
        if (this.sessionData.es_evaluacion_ia) {
            this.finishGame();
        } else {
            this.showLevelResults();
        }
    }
    
    showLevelResults() {
        const questions = this.getCurrentLevelQuestions();
        const totalQuestions = questions.length;
        const accuracy = Math.round((this.correctAnswers / totalQuestions) * 100);
        
        const gameArea = document.getElementById('game-area');
        gameArea.innerHTML = `
            <div class="level-results max-w-3xl mx-auto">
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 mb-6 transition-colors duration-200">
                    <div class="text-center mb-6">
                        <div class="w-20 h-20 bg-gradient-to-r from-green-500 to-teal-500 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">¡Nivel ${this.currentLevel} Completado!</h2>
                        <p class="text-gray-500 dark:text-gray-400">Excelente trabajo escribiendo palabras</p>
                    </div>
                    
                    <hr class="bg-gray-200 dark:bg-gray-700 my-6">
                    
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-xl p-4 text-center">
                            <div class="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">${this.score}</div>
                            <div class="text-xs font-medium text-gray-600 dark:text-gray-400">Puntos</div>
                        </div>
                        <div class="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-xl p-4 text-center">
                            <div class="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-1">${this.correctAnswers}</div>
                            <div class="text-xs font-medium text-gray-600 dark:text-gray-400">Aciertos</div>
                        </div>
                        <div class="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl p-4 text-center">
                            <div class="text-3xl font-bold text-red-600 dark:text-red-400 mb-1">${this.incorrectAnswers}</div>
                            <div class="text-xs font-medium text-gray-600 dark:text-gray-400">Errores</div>
                        </div>
                        <div class="bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-800 rounded-xl p-4 text-center">
                            <div class="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mb-1">${accuracy}%</div>
                            <div class="text-xs font-medium text-gray-600 dark:text-gray-400">Precisión</div>
                        </div>
                    </div>
                </div>
                
                <div class="flex flex-col sm:flex-row gap-4 justify-center">
                    <button id="btn-next-level" class="px-6 py-3 bg-green-500 hover:bg-green-600 dark:bg-green-600 dark:hover:bg-green-700 text-white rounded-xl transition-all duration-200 font-semibold flex items-center justify-center gap-2 shadow-sm hover:shadow-md">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                        Siguiente Nivel
                    </button>
                    <button id="btn-finish-level" class="px-6 py-3 bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl transition-all duration-200 font-semibold flex items-center justify-center gap-2 border border-gray-300 dark:border-gray-700">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                        Finalizar
                    </button>
                </div>
            </div>
        `;
        
        document.getElementById('btn-next-level')?.addEventListener('click', () => this.nextLevel());
        document.getElementById('btn-finish-level')?.addEventListener('click', () => this.finishGame());
        
        this.sendLevelResults();
    }
    
    nextLevel() {
        this.currentLevel++;
        this.currentQuestionIndex = 0;
        
        const nextLevel = this.gameConfig.levels.find(l => l.level === this.currentLevel);
        if (!nextLevel) {
            setTimeout(() => {
                alert('🎉 ¡Felicidades! Has completado todos los niveles.\n\n' +
                    `✨ Puntuación final: ${this.score} puntos\n` +
                    `🎯 Niveles completados: ${this.currentLevel - 1}\n` +
                    `✅ Aciertos: ${this.correctAnswers}\n` +
                    `❌ Errores: ${this.incorrectAnswers}`);
                
                // ⭐ NUEVO: Solo llamar finishGame si es evaluación IA
                if (this.sessionData.es_evaluacion_ia) {
                    this.finishGame();
                } else {
                    // Si es juego individual, redirigir a lista de juegos
                    window.location.href = this.sessionData.api_urls.game_list;
                }
            }, 500);
            return;
        }
        
        this.correctAnswers = 0;
        this.incorrectAnswers = 0;
        this.selectedQuestions = null;
        
        this.createGameInterface();
        this.bindEvents();
        this.startGame();
    }
    
    async finishGame() {
        const totalTime = Math.floor((Date.now() - this.startTime) / 1000);
        
        const result = await this.sendGameResults(totalTime);
        
        if (result && result.success) {
            console.log('✅ [Escribe Nombre] Juego finalizado correctamente');
        } else {
            alert('Error al finalizar el juego: ' + (result ? result.error : 'Error desconocido'));
        }
    }
    
    updateScore() {
        document.getElementById('game-score').textContent = this.score;
        if (window.updateScore) {
            window.updateScore(this.score);
        }
    }
    
    updateProgress() {
        const questions = this.getCurrentLevelQuestions();
        const progress = ((this.currentQuestionIndex + 1) / questions.length) * 100;
        const progressBar = document.getElementById('progress-bar');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
    }
    
    startQuestionTimer() {
        const timerEl = document.getElementById('question-timer');
        let timeLeft = this.currentQuestion.time_limit;
        
        this.questionTimer = setInterval(() => {
            timeLeft--;
            timerEl.textContent = timeLeft;
            
            if (timeLeft <= 10) {
                timerEl.parentElement.classList.add('bg-red-100', 'dark:bg-red-900/50', 'text-red-800', 'dark:text-red-300', 'border-red-300', 'dark:border-red-700');
                timerEl.parentElement.classList.remove('bg-orange-50', 'dark:bg-orange-900/30', 'border-orange-200', 'dark:border-orange-800');
            }
            
            if (timeLeft <= 0) {
                this.timeUp();
            }
        }, 1000);
    }
    
    stopQuestionTimer() {
        if (this.questionTimer) {
            clearInterval(this.questionTimer);
            this.questionTimer = null;
        }
    }
    
    timeUp() {
        if (!this.isGameActive) return;
        
        this.stopQuestionTimer();
        this.isGameActive = false;
        this.incorrectAnswers++;
        
        this.showCorrectAnswer();
        this.showMessage('Se acabó el tiempo ⏰', 'warning');
        
        const responseTime = this.currentQuestion.time_limit * 1000;
        this.sendQuestionResponse(false, responseTime, '');
        
        setTimeout(() => {
            this.proceedToNext();
        }, 3500);
    }
    
    // API calls
    async sendQuestionResponse(isCorrect, responseTime, userAnswer) {
        const data = {
            session_url: this.sessionData.url_sesion,
            question_id: this.currentQuestion.id,
            level: this.currentLevel,
            is_correct: isCorrect,
            response_time_ms: responseTime,
            selected_option: userAnswer,
            points_earned: isCorrect ? this.currentQuestion.points : 0,
            attempts: this.attempts,
            hint_used: this.hintUsed
        };
        
        try {
            const response = await fetch(this.sessionData.api_urls.question_response, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                console.error('❌ Error al enviar respuesta');
            }
        } catch (error) {
            console.error('❌ Error de red:', error);
        }
    }
    
    async sendLevelResults() {
        const data = {
            session_url: this.sessionData.url_sesion,
            level: this.currentLevel,
            total_questions: this.getCurrentLevelQuestions().length,
            correct_answers: this.correctAnswers,
            incorrect_answers: this.incorrectAnswers,
            total_score: this.score
        };
        
        try {
            await fetch(this.sessionData.api_urls.level_complete, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });
        } catch (error) {
            console.error('❌ Error:', error);
        }
    }
    
    async sendGameResults(totalTimeSeconds) {
        // === CALCULAR MÉTRICAS AGREGADAS DEL MINIJUEGO ===
        const totalClicks = this.correctAnswers + this.incorrectAnswers;
        
        const data = {
            session_url: this.sessionData.url_sesion,
            total_score: this.score,
            total_correct: this.correctAnswers,
            total_incorrect: this.incorrectAnswers,
            total_time_seconds: totalTimeSeconds,
            levels_completed: this.currentLevel,
            
            // === NUEVAS MÉTRICAS PARA EL MODELO IA ===
            total_clicks: totalClicks,
            total_hits: this.correctAnswers,
            total_misses: this.incorrectAnswers
        };
        
        console.log('📤 [Escribe Nombre] Enviando resultados finales:', data);
        
        const finishUrl = this.sessionData.api_urls.finish_game;
        
        try {
            const response = await fetch(finishUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Error del servidor:', errorText);
                return { 
                    success: false, 
                    error: `Error del servidor (${response.status}): ${response.statusText}` 
                };
            }
            const result = await response.json();
            if (result.success) {
                if (result.evaluacion_completada) {
                    alert(`🎉 ¡Evaluación completa! ${result.final_stats.sesiones_completadas}/${result.final_stats.sesiones_totales} sesiones`);
                    window.location.href = result.redirect_url;
                    return { success: true };
                } else if (result.siguiente_url) {
                    const progreso = result.progreso;
                    if (window.showNextGameAlert) {
                        window.showNextGameAlert({ progreso, siguienteUrl: result.siguiente_url });
                    } else {
                        const script = document.createElement('script');
                        script.src = '/static/js/game-alerts.js';
                        script.onload = () => {
                            if (window.showNextGameAlert) {
                                window.showNextGameAlert({ progreso, siguienteUrl: result.siguiente_url });
                            } else {
                                alert(`✅ Juego completado!\n\nProgreso: ${progreso.completadas}/${progreso.totales} (${progreso.porcentaje}%)\n\n🎮 Avanzando al siguiente juego...`);
                                setTimeout(() => {
                                    window.location.href = result.siguiente_url;
                                }, 2000);
                            }
                        };
                        document.body.appendChild(script);
                    }
                    return { success: true };
                } else {
                    window.location.href = result.redirect_url || `/games/results/${this.sessionData.evaluacion_id}/`;
                    return { success: true };
                }
            } else {
                return { success: false, error: result.error };
            }
        } catch (error) {
            console.error('❌ Error al finalizar juego:', error);
            return { success: false, error: 'Error de conexión al finalizar el juego' };
        }
    }
    
    getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }
}

// Animaciones CSS adicionales
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; transform: translate(-50%, 0); }
        to { opacity: 0; transform: translate(-50%, -20px); }
    }
`;
document.head.appendChild(style);

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.gameSessionData !== 'undefined' && typeof window.gameConfig !== 'undefined') {
        window.gameInstance = new EscribeElNombreGame(window.gameSessionData, window.gameConfig);
    } else {
        console.error('❌ Faltan datos de sesión');
    }
});
