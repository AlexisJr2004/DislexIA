/**
 * Juego: Completa la Palabra
 * El jugador debe seleccionar la letra correcta para completar la palabra
 */

class CompletaLaPalabraGame {
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
            <div class="complete-word-game max-w-7xl mx-auto p-4">
                <!-- Encabezado del juego -->
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 mb-6 transition-colors duration-200">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <div class="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                            </div>
                            <div>
                                <h2 class="text-xl font-bold text-gray-900 dark:text-white">Completa la Palabra</h2>
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
                                <span id="question-timer" class="font-semibold">30</span>
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

                        <!-- Botón de pista adicional -->
                        <div class="text-center">
                            <button id="show-hint-btn" class="px-4 py-2 bg-yellow-50 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400 rounded-lg border border-yellow-200 dark:border-yellow-800 hover:bg-yellow-100 dark:hover:bg-yellow-900/50 transition-colors text-sm font-medium">
                                <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Ver palabra completa (-5 puntos)
                            </button>
                        </div>
                    </div>

                    <!-- COLUMNA DERECHA - Palabra incompleta y opciones -->
                    <div class="space-y-6">
                        <!-- Palabra incompleta -->
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 transition-colors duration-200">
                            <h3 class="text-center text-sm font-medium text-gray-700 dark:text-gray-300 mb-6">Completa la palabra</h3>
                            <div id="word-display" class="flex justify-center gap-3 mb-8 flex-wrap">
                                <!-- Las letras de la palabra aparecen aquí -->
                            </div>
                        </div>
                        
                        <!-- Opciones de letras -->
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 transition-colors duration-200">
                            <h3 class="text-center text-sm font-medium text-gray-700 dark:text-gray-300 mb-6">Selecciona la letra correcta</h3>
                            <div id="options-container" class="grid grid-cols-4 gap-4">
                                <!-- Las opciones de letras aparecen aquí -->
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
    
    shuffleArray(array) {
        const shuffled = [...array];
        
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        
        return shuffled;
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
        
        // Renderizar palabra incompleta
        this.renderWord();
        
        // Renderizar opciones
        this.renderOptions();
    }
    
    renderWord() {
        const container = document.getElementById('word-display');
        container.innerHTML = '';
        
        const word = this.currentQuestion.incomplete_word;
        
        word.split('').forEach((letter, index) => {
            const letterBox = document.createElement('div');
            
            if (letter === '_') {
                letterBox.className = `
                    w-16 h-20 border-4 border-dashed border-purple-400 dark:border-purple-600
                    rounded-xl flex items-center justify-center text-3xl font-bold
                    bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400
                    animate-pulse
                `;
                letterBox.innerHTML = '<span class="text-purple-400 dark:text-purple-500">?</span>';
            } else {
                letterBox.className = `
                    w-16 h-20 border-2 border-gray-300 dark:border-gray-600
                    rounded-xl flex items-center justify-center text-3xl font-bold
                    bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300
                `;
                letterBox.textContent = letter;
            }
            
            container.appendChild(letterBox);
        });
    }
    
    renderOptions() {
        const container = document.getElementById('options-container');
        container.innerHTML = '';
        
        const shuffledOptions = this.shuffleArray(this.currentQuestion.options);
        
        shuffledOptions.forEach(option => {
            const optionBtn = document.createElement('button');
            optionBtn.className = `
                option-btn w-full h-20 bg-gradient-to-br from-blue-50 to-cyan-50
                dark:from-blue-900/30 dark:to-cyan-900/30
                hover:from-blue-100 hover:to-cyan-100
                dark:hover:from-blue-900/50 dark:hover:to-cyan-900/50
                border-2 border-blue-200 dark:border-blue-800
                rounded-xl text-3xl font-bold text-blue-600 dark:text-blue-400
                transition-all duration-200 hover:scale-105 active:scale-95
                shadow-sm hover:shadow-md
            `;
            optionBtn.textContent = option;
            optionBtn.dataset.letter = option;
            
            optionBtn.addEventListener('click', () => {
                if (this.isGameActive) {
                    this.checkAnswer(option);
                }
            });
            
            container.appendChild(optionBtn);
        });
    }
    
    checkAnswer(selectedLetter) {
        if (!this.isGameActive) return;
        
        const isCorrect = selectedLetter === this.currentQuestion.missing_letter;
        const responseTime = Date.now() - this.questionStartTime;
        
        this.attempts++;
        document.getElementById('attempts-counter').textContent = `${this.attempts}/3`;
        
        if (isCorrect) {
            this.handleCorrectAnswer(responseTime, selectedLetter);
        } else {
            this.handleIncorrectAnswer(selectedLetter);
        }
    }
    
    handleCorrectAnswer(responseTime, selectedLetter) {
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
        
        // Mostrar palabra completa
        this.showCompleteWord(true);
        
        // Enviar respuesta
        this.sendQuestionResponse(true, responseTime, selectedLetter);
        
        // Actualizar UI
        this.updateScore();
        
        // Continuar al siguiente
        setTimeout(() => {
            this.proceedToNext();
        }, 2500);
    }
    
    handleIncorrectAnswer(selectedLetter) {
        if (this.attempts >= 3) {
            this.incorrectAnswers++;
            this.stopQuestionTimer();
            this.isGameActive = false;
            
            // Mostrar respuesta correcta
            this.showCompleteWord(false);
            
            const responseTime = Date.now() - this.questionStartTime;
            this.sendQuestionResponse(false, responseTime, selectedLetter);
            
            setTimeout(() => {
                this.proceedToNext();
            }, 3000);
        } else {
            // Mostrar animación de error
            this.showErrorAnimation(selectedLetter);
        }
    }
    
    showCompleteWord(isCorrect) {
        const container = document.getElementById('word-display');
        container.innerHTML = '';
        
        const word = this.currentQuestion.complete_word;
        const missingPosition = this.currentQuestion.missing_position;
        
        word.split('').forEach((letter, index) => {
            const letterBox = document.createElement('div');
            
            if (index === missingPosition) {
                letterBox.className = `
                    w-16 h-20 border-2 rounded-xl flex items-center justify-center
                    text-3xl font-bold animate-bounce
                    ${isCorrect 
                        ? 'border-green-500 dark:border-green-600 bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400' 
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
            container.appendChild(letterBox);
        });
        
        // Mensaje de resultado
        const messageDiv = document.createElement('div');
        messageDiv.className = `mt-6 text-center p-4 rounded-xl ${
            isCorrect 
                ? 'bg-green-50 dark:bg-green-900/30 border-2 border-green-500 dark:border-green-600' 
                : 'bg-red-50 dark:bg-red-900/30 border-2 border-red-500 dark:border-red-600'
        }`;
        messageDiv.innerHTML = `
            <div class="flex items-center justify-center gap-2 mb-2">
                ${isCorrect 
                    ? '<svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' 
                    : '<svg class="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'}
            </div>
            <p class="text-xl font-bold ${isCorrect ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'}">
                ${isCorrect ? '¡Correcto!' : 'Palabra correcta:'}
            </p>
            <p class="text-2xl font-bold ${isCorrect ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'} mt-1">
                ${word}
            </p>
        `;
        
        container.parentElement.appendChild(messageDiv);

        // Eliminar el mensaje y la palabra después de un tiempo
        setTimeout(() => {
            if (messageDiv.parentElement) {
                messageDiv.parentElement.removeChild(messageDiv);
            }
            container.innerHTML = '';
        }, isCorrect ? 2500 : 3000);
    }
    
    showErrorAnimation(selectedLetter) {
        const optionButtons = document.querySelectorAll('.option-btn');
        
        optionButtons.forEach(btn => {
            if (btn.dataset.letter === selectedLetter) {
                btn.classList.add('bg-red-100', 'dark:bg-red-900/50', 'border-red-500', 'dark:border-red-600');
                btn.classList.remove('hover:scale-105');
                
                // Animación de shake
                btn.style.animation = 'shake 0.5s';
                
                setTimeout(() => {
                    btn.style.animation = '';
                    btn.classList.remove('bg-red-100', 'dark:bg-red-900/50', 'border-red-500', 'dark:border-red-600');
                    btn.classList.add('hover:scale-105');
                }, 500);
            }
        });
    }
    
    showHint() {
        if (this.hintUsed) return;
        
        this.hintUsed = true;
        const hintBtn = document.getElementById('show-hint-btn');
        hintBtn.disabled = true;
        hintBtn.classList.add('opacity-50', 'cursor-not-allowed');
        
        // Mostrar la palabra completa temporalmente
        const container = document.getElementById('word-display');
        const originalHTML = container.innerHTML;
        
        container.innerHTML = `
            <div class="w-full text-center p-6 bg-yellow-50 dark:bg-yellow-900/30 rounded-xl border-2 border-yellow-300 dark:border-yellow-700">
                <p class="text-sm text-yellow-700 dark:text-yellow-300 mb-2">Palabra completa:</p>
                <p class="text-4xl font-bold text-yellow-800 dark:text-yellow-200 tracking-widest">${this.currentQuestion.complete_word}</p>
                <p class="text-xs text-yellow-600 dark:text-yellow-400 mt-2">-5 puntos de penalización</p>
            </div>
        `;
        
        setTimeout(() => {
            container.innerHTML = originalHTML;
        }, 3000);
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
                        <div class="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                            </svg>
                        </div>
                        <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">¡Nivel ${this.currentLevel} Completado!</h2>
                        <p class="text-gray-500 dark:text-gray-400">Excelente trabajo completando palabras</p>
                    </div>
                    
                    <hr class="bg-gray-200 dark:bg-gray-700 my-6">
                    
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="bg-purple-50 dark:bg-purple-900/30 border border-purple-200 dark:border-purple-800 rounded-xl p-4 text-center">
                            <div class="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-1">${this.score}</div>
                            <div class="text-xs font-medium text-gray-600 dark:text-gray-400">Puntos</div>
                        </div>
                        <div class="bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-xl p-4 text-center">
                            <div class="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">${this.correctAnswers}</div>
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
        
        // Enviar datos finales al backend
        const result = await this.sendGameResults(totalTime);
        
        if (result && result.success) {
            // El backend ya maneja la redirección automática
            console.log('✅ [Completa Palabra] Juego finalizado correctamente');
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
        
        this.showCompleteWord(false);
        
        const responseTime = this.currentQuestion.time_limit * 1000;
        this.sendQuestionResponse(false, responseTime, '');
        
        setTimeout(() => {
            this.proceedToNext();
        }, 3000);
    }
    
    // API calls
    async sendQuestionResponse(isCorrect, responseTime, selectedOption) {
        const data = {
            session_url: this.sessionData.url_sesion,
            question_id: this.currentQuestion.id,
            level: this.currentLevel,
            is_correct: isCorrect,
            response_time_ms: responseTime,
            selected_option: selectedOption,
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
        
        console.log('📤 [Completa Palabra] Enviando resultados finales:', data);
        
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
            console.log('📥 [Completa Palabra] Respuesta del servidor:', result);
            
            if (result.success) {
                // === MANEJAR RESPUESTA DEL BACKEND ===
                if (result.evaluacion_completada) {
                    // Todas las 32 sesiones completadas
                    alert(`🎉 ¡Evaluación completa! ${result.final_stats.sesiones_completadas}/${result.final_stats.sesiones_totales} sesiones`);
                    window.location.href = result.redirect_url;
                    return { success: true };
                } else if (result.siguiente_url) {
                    // Hay más juegos por completar
                    const progreso = result.progreso;
                    alert(`✅ Juego completado!\n\nProgreso: ${progreso.completadas}/${progreso.totales} (${progreso.porcentaje}%)\n\n🎮 Avanzando al siguiente juego...`);
                    
                    setTimeout(() => {
                        window.location.href = result.siguiente_url;
                    }, 2000);
                    return { success: true };
                } else {
                    // Fallback - ir a resultados
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
        window.gameInstance = new CompletaLaPalabraGame(window.gameSessionData, window.gameConfig);
    } else {
        console.error('❌ Faltan datos de sesión');
    }
});
