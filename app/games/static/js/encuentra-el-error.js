/**
 * Juego: Encuentra el Error
 * El jugador debe identificar qué letra está incorrecta en la palabra
 */

class EncuentraElErrorGame {
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
            <div class="find-error-game max-w-7xl mx-auto p-4">
                <!-- Encabezado del juego -->
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 mb-6 transition-colors duration-200">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <div class="w-12 h-12 bg-gradient-to-r from-red-500 to-orange-500 rounded-xl flex items-center justify-center">
                                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                            </div>
                            <div>
                                <h2 class="text-xl font-bold text-gray-900 dark:text-white">Encuentra el Error</h2>
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
                                <span id="question-timer" class="font-semibold">40</span>
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
                                    alt="Pista visual" 
                                    class="w-80 h-64 object-contain rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 shadow-sm">
                            </div>
                        </div>
                        
                        <!-- Pista -->
                        <div class="text-center mb-4">
                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">Pista</p>
                            <p id="hint-text" class="text-lg font-medium text-gray-900 dark:text-white"></p>
                        </div>

                        <!-- Instrucción -->
                        <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-center">
                            <p class="text-sm text-red-700 dark:text-red-300 font-medium">
                                <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                                Haz clic en la letra incorrecta
                            </p>
                        </div>

                        <!-- Botón de pista adicional -->
                        <div class="text-center mt-4">
                            <button id="show-hint-btn" class="px-4 py-2 bg-yellow-50 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400 rounded-lg border border-yellow-200 dark:border-yellow-800 hover:bg-yellow-100 dark:hover:bg-yellow-900/50 transition-colors text-sm font-medium">
                                <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Mostrar error (-5 puntos)
                            </button>
                        </div>
                    </div>

                    <!-- COLUMNA DERECHA - Palabra con error -->
                    <div class="space-y-6">
                        <!-- Palabra incorrecta -->
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 transition-colors duration-200">
                            <h3 class="text-center text-sm font-medium text-gray-700 dark:text-gray-300 mb-6">
                                Encuentra la letra incorrecta
                            </h3>
                            <div id="word-display" class="flex justify-center gap-3 mb-8 flex-wrap">
                                <!-- Las letras de la palabra aparecen aquí -->
                            </div>
                            <div class="text-center text-xs text-gray-500 dark:text-gray-400">
                                Haz clic en la letra que crees que está mal escrita
                            </div>
                        </div>
                        
                        <!-- Panel informativo -->
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 transition-colors duration-200">
                            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4 text-center">Tipo de error</h3>
                            <div id="error-type-info" class="text-center">
                                <div class="inline-flex items-center gap-2 px-4 py-2 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                                    <svg class="w-5 h-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <span class="text-sm text-gray-600 dark:text-gray-400" id="error-type-text">Encuentra el error primero</span>
                                </div>
                            </div>
                            
                            <div class="mt-6 grid grid-cols-2 gap-3">
                                <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 text-center border border-blue-200 dark:border-blue-800">
                                    <div class="text-xs text-blue-600 dark:text-blue-400 mb-1">Sustitución</div>
                                    <div class="text-sm font-medium text-blue-700 dark:text-blue-300">r ↔ l, m ↔ n</div>
                                </div>
                                <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3 text-center border border-purple-200 dark:border-purple-800">
                                    <div class="text-xs text-purple-600 dark:text-purple-400 mb-1">Inversión</div>
                                    <div class="text-sm font-medium text-purple-700 dark:text-purple-300">b ↔ d, p ↔ q</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        document.getElementById('show-hint-btn')?.addEventListener('click', () => {
            this.showHint();
        });
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
        
        // Actualizar contador de intentos
        document.getElementById('attempts-counter').textContent = `${this.attempts}/3`;
        
        // Renderizar palabra con error
        this.renderWord();
    }
    
    renderWord() {
        const container = document.getElementById('word-display');
        container.innerHTML = '';
        
        const word = this.currentQuestion.incorrect_word;
        
        word.split('').forEach((letter, index) => {
            const letterBtn = document.createElement('button');
            letterBtn.className = `
                letter-btn w-16 h-20 border-2 border-gray-300 dark:border-gray-600
                rounded-xl flex items-center justify-center text-3xl font-bold
                bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300
                transition-all duration-200 hover:scale-110 hover:border-red-400
                dark:hover:border-red-600 hover:bg-red-50 dark:hover:bg-red-900/20
                active:scale-95 cursor-pointer
            `;
            letterBtn.textContent = letter;
            letterBtn.dataset.index = index;
            
            letterBtn.addEventListener('click', () => {
                if (this.isGameActive) {
                    this.checkAnswer(index);
                }
            });
            
            container.appendChild(letterBtn);
        });
    }
    
    checkAnswer(selectedIndex) {
        if (!this.isGameActive) return;
        
        const isCorrect = selectedIndex === this.currentQuestion.error_position;
        const responseTime = Date.now() - this.questionStartTime;
        
        this.attempts++;
        document.getElementById('attempts-counter').textContent = `${this.attempts}/3`;
        
        if (isCorrect) {
            this.handleCorrectAnswer(responseTime, selectedIndex);
        } else {
            this.handleIncorrectAnswer(selectedIndex);
        }
    }
    
    handleCorrectAnswer(responseTime, selectedIndex) {
        this.correctAnswers++;
        this.stopQuestionTimer();
        this.isGameActive = false;
        
        // Calcular puntos
        const timeBonus = Math.max(0, this.currentQuestion.time_limit - Math.floor(responseTime / 1000));
        let points = this.currentQuestion.points + (timeBonus * this.gameConfig.scoring.time_bonus);
        
        // Penalización por usar pista
        if (this.hintUsed) {
            points -= this.gameConfig.scoring.hint_penalty;
        }
        
        this.score += Math.max(0, points);
        
        // Mostrar resultado correcto
        this.showResult(true, selectedIndex);
        
        // Enviar respuesta
        this.sendQuestionResponse(true, responseTime, selectedIndex);
        
        // Actualizar UI
        this.updateScore();
        
        // Continuar al siguiente
        setTimeout(() => {
            this.proceedToNext();
        }, 3000);
    }
    
    handleIncorrectAnswer(selectedIndex) {
        if (this.attempts >= 3) {
            this.incorrectAnswers++;
            this.stopQuestionTimer();
            this.isGameActive = false;
            
            // Mostrar respuesta correcta
            this.showResult(false, selectedIndex);
            
            const responseTime = Date.now() - this.questionStartTime;
            this.sendQuestionResponse(false, responseTime, selectedIndex);
            
            setTimeout(() => {
                this.proceedToNext();
            }, 4000);
        } else {
            // Mostrar animación de error
            this.showErrorAnimation(selectedIndex);
        }
    }
    
    showResult(isCorrect, selectedIndex) {
        const container = document.getElementById('word-display');
        container.innerHTML = '';
        
        const incorrectWord = this.currentQuestion.incorrect_word;
        const correctWord = this.currentQuestion.correct_word;
        const errorPosition = this.currentQuestion.error_position;
        
        // Mostrar palabra incorrecta con error marcado
        const incorrectDiv = document.createElement('div');
        incorrectDiv.className = 'mb-8';
        incorrectDiv.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400 mb-3 text-center">Palabra incorrecta:</p>';
        
        const incorrectLettersDiv = document.createElement('div');
        incorrectLettersDiv.className = 'flex justify-center gap-3 mb-4';
        
        incorrectWord.split('').forEach((letter, index) => {
            const letterBox = document.createElement('div');
            
            if (index === errorPosition) {
                letterBox.className = `
                    w-16 h-20 border-2 rounded-xl flex items-center justify-center
                    text-3xl font-bold animate-pulse
                    ${isCorrect 
                        ? 'border-red-500 dark:border-red-600 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400' 
                        : 'border-red-500 dark:border-red-600 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400'}
                `;
            } else {
                letterBox.className = `
                    w-16 h-20 border-2 border-gray-300 dark:border-gray-600
                    rounded-xl flex items-center justify-center text-3xl font-bold
                    bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300
                `;
            }
            
            letterBox.textContent = letter;
            incorrectLettersDiv.appendChild(letterBox);
        });
        
        incorrectDiv.appendChild(incorrectLettersDiv);
        container.appendChild(incorrectDiv);
        
        // Mostrar palabra correcta
        const correctDiv = document.createElement('div');
        correctDiv.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400 mb-3 text-center">Palabra correcta:</p>';
        
        const correctLettersDiv = document.createElement('div');
        correctLettersDiv.className = 'flex justify-center gap-3';
        
        correctWord.split('').forEach((letter, index) => {
            const letterBox = document.createElement('div');
            
            if (index === errorPosition) {
                letterBox.className = `
                    w-16 h-20 border-2 rounded-xl flex items-center justify-center
                    text-3xl font-bold animate-bounce
                    border-green-500 dark:border-green-600 bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400
                `;
            } else {
                letterBox.className = `
                    w-16 h-20 border-2 border-gray-300 dark:border-gray-600
                    rounded-xl flex items-center justify-center text-3xl font-bold
                    bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300
                `;
            }
            
            letterBox.textContent = letter;
            correctLettersDiv.appendChild(letterBox);
        });
        
        correctDiv.appendChild(correctLettersDiv);
        container.appendChild(correctDiv);
        
        // Mensaje de resultado
        const messageDiv = document.createElement('div');
        messageDiv.className = `mt-6 p-4 rounded-xl ${
            isCorrect 
                ? 'bg-green-50 dark:bg-green-900/30 border-2 border-green-500 dark:border-green-600' 
                : 'bg-orange-50 dark:bg-orange-900/30 border-2 border-orange-500 dark:border-orange-600'
        }`;
        messageDiv.innerHTML = `
            <div class="text-center">
                <div class="flex items-center justify-center gap-2 mb-2">
                    ${isCorrect 
                        ? '<svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' 
                        : '<svg class="w-8 h-8 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'}
                </div>
                <p class="text-xl font-bold ${isCorrect ? 'text-green-700 dark:text-green-300' : 'text-orange-700 dark:text-orange-300'} mb-2">
                    ${isCorrect ? '¡Encontraste el error!' : 'El error estaba aquí:'}
                </p>
                <p class="text-sm ${isCorrect ? 'text-green-600 dark:text-green-400' : 'text-orange-600 dark:text-orange-400'}">
                    "${this.currentQuestion.error_letter}" debería ser "${this.currentQuestion.correct_letter}"
                </p>
                <div class="mt-3 inline-flex items-center gap-2 px-3 py-1 bg-white/50 dark:bg-gray-800/50 rounded-lg">
                    <span class="text-xs font-medium text-gray-600 dark:text-gray-400">Tipo de error:</span>
                    <span class="text-xs font-bold text-gray-700 dark:text-gray-300">${this.getErrorTypeName(this.currentQuestion.error_type)}</span>
                </div>
            </div>
        `;
        
        container.appendChild(messageDiv);
    }
    
    getErrorTypeName(errorType) {
        const types = {
            'sustitucion_letras': 'Sustitución',
            'inversion_letras': 'Inversión',
            'omision_letras': 'Omisión',
            'inversion_silabas': 'Inversión de sílabas'
        };
        return types[errorType] || errorType;
    }
    
    showErrorAnimation(selectedIndex) {
        const letterButtons = document.querySelectorAll('.letter-btn');
        const btn = letterButtons[selectedIndex];
        
        if (btn) {
            btn.classList.add('bg-red-100', 'dark:bg-red-900/50', 'border-red-500', 'dark:border-red-600');
            btn.style.animation = 'shake 0.5s';
            
            setTimeout(() => {
                btn.style.animation = '';
                btn.classList.remove('bg-red-100', 'dark:bg-red-900/50', 'border-red-500', 'dark:border-red-600');
            }, 500);
        }
    }
    
    showHint() {
        if (this.hintUsed) return;
        
        this.hintUsed = true;
        const hintBtn = document.getElementById('show-hint-btn');
        hintBtn.disabled = true;
        hintBtn.classList.add('opacity-50', 'cursor-not-allowed');
        
        // Destacar la letra incorrecta
        const letterButtons = document.querySelectorAll('.letter-btn');
        const errorBtn = letterButtons[this.currentQuestion.error_position];
        
        if (errorBtn) {
            errorBtn.classList.add('animate-pulse', 'border-yellow-400', 'dark:border-yellow-600', 'bg-yellow-50', 'dark:bg-yellow-900/30');
            
            setTimeout(() => {
                errorBtn.classList.remove('animate-pulse', 'border-yellow-400', 'dark:border-yellow-600', 'bg-yellow-50', 'dark:bg-yellow-900/30');
            }, 3000);
        }
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
        this.showLevelResults();
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
                        <div class="w-20 h-20 bg-gradient-to-r from-red-500 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">¡Nivel ${this.currentLevel} Completado!</h2>
                        <p class="text-gray-500 dark:text-gray-400">Excelente trabajo encontrando errores</p>
                    </div>
                    
                    <hr class="bg-gray-200 dark:bg-gray-700 my-6">
                    
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl p-4 text-center">
                            <div class="text-3xl font-bold text-red-600 dark:text-red-400 mb-1">${this.score}</div>
                            <div class="text-xs font-medium text-gray-600 dark:text-gray-400">Puntos</div>
                        </div>
                        <div class="bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-xl p-4 text-center">
                            <div class="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">${this.correctAnswers}</div>
                            <div class="text-xs font-medium text-gray-600 dark:text-gray-400">Aciertos</div>
                        </div>
                        <div class="bg-orange-50 dark:bg-orange-900/30 border border-orange-200 dark:border-orange-800 rounded-xl p-4 text-center">
                            <div class="text-3xl font-bold text-orange-600 dark:text-orange-400 mb-1">${this.incorrectAnswers}</div>
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
                this.finishGame();
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

        // Enviar datos finales al backend
        const result = await this.sendGameResults(totalTime);

        if (result && result.success) {
            // Obtener la lista de juegos y el índice del juego actual
            const juegos = this.sessionData.juegos;
            const juegoActualIndex = juegos.findIndex(juego => juego.slug === this.sessionData.juego_slug);

            // Verificar si hay un siguiente juego
            if (juegoActualIndex >= 0 && juegoActualIndex < juegos.length - 1) {
                const siguienteJuego = juegos[juegoActualIndex + 1];
                setTimeout(() => {
                    window.location.href = siguienteJuego.init_url;
                }, 1000); // Redirigir después de 1 segundo
            } else {
                // Si no hay más juegos, redirigir a resultados de evaluación secuencial
                setTimeout(() => {
                    window.location.href = `/games/results/${this.sessionData.evaluacion_id}/`;
                }, 1000);
            }
        } else {
            // Mostrar error si falló
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
        
        this.showResult(false, -1);
        
        const responseTime = this.currentQuestion.time_limit * 1000;
        this.sendQuestionResponse(false, responseTime, -1);
        
        setTimeout(() => {
            this.proceedToNext();
        }, 4000);
    }
    
    // API calls
    async sendQuestionResponse(isCorrect, responseTime, selectedIndex) {
        const data = {
            session_url: this.sessionData.url_sesion,
            question_id: this.currentQuestion.id,
            level: this.currentLevel,
            is_correct: isCorrect,
            response_time_ms: responseTime,
            selected_option: selectedIndex,
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
        const data = {
            session_url: this.sessionData.url_sesion,
            total_score: this.score,
            total_correct: this.correctAnswers,
            total_incorrect: this.incorrectAnswers,
            total_time_seconds: totalTimeSeconds,
            levels_completed: this.currentLevel
        };
        
        try {
            const response = await fetch(this.sessionData.api_urls.finish_game, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                return { success: true };
            } else {
                return { success: false, error: result.error };
            }
        } catch (error) {
            console.error('❌ Error:', error);
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

// Animación de shake
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.gameSessionData !== 'undefined' && typeof window.gameConfig !== 'undefined') {
        window.gameInstance = new EncuentraElErrorGame(window.gameSessionData, window.gameConfig);
    } else {
        console.error('❌ Faltan datos de sesión');
    }
});
