/**
 * Juego: Ordenar Palabras
 * El jugador debe ordenar letras desordenadas para formar la palabra correcta
 */

class OrdenarPalabrasGame {
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
        this.selectedLetters = [];
        this.availableLetters = [];
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
            <div class="word-order-game max-w-7xl mx-auto p-4">
                <!-- Encabezado del juego -->
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 mb-6 transition-colors duration-200">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <div class="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center">
                                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                                </svg>
                            </div>
                            <div>
                                <h2 class="text-xl font-bold text-gray-900 dark:text-white">Ordenar Palabras</h2>
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
                                <span id="question-timer" class="font-semibold">45</span>
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

                    <!-- COLUMNA DERECHA - Construcción de palabra y letras -->
                    <div class="space-y-6">
                        <!-- Área de construcción de palabra -->
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 transition-colors duration-200">
                            <h3 class="text-center text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">Palabra que estás formando</h3>
                            <div id="word-builder" class="flex justify-center gap-2 mb-6 min-h-[60px] flex-wrap">
                                <!-- Las letras seleccionadas aparecen aquí -->
                            </div>
                            
                            <div class="flex justify-center gap-3">
                                <button id="clear-word-btn" class="px-6 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg border border-gray-300 dark:border-gray-700 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors font-medium">
                                    <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                    Limpiar
                                </button>
                                <button id="check-word-btn" class="px-6 py-2 bg-green-500 dark:bg-green-600 text-white rounded-lg hover:bg-green-600 dark:hover:bg-green-700 transition-colors font-medium shadow-sm">
                                    <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                                    </svg>
                                    Verificar
                                </button>
                            </div>
                        </div>
                        
                        <!-- Letras disponibles -->
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 transition-colors duration-200">
                            <h3 class="text-center text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">Letras disponibles</h3>
                            <div id="letters-container" class="flex justify-center gap-2 flex-wrap">
                                <!-- Las letras desordenadas aparecen aquí -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        // Eventos para los botones principales
        document.getElementById('clear-word-btn')?.addEventListener('click', () => {
            this.clearWord();
        });
        
        document.getElementById('check-word-btn')?.addEventListener('click', () => {
            this.checkWord();
        });

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
        this.selectedLetters = [];
        this.availableLetters = this.shuffleArray([...this.currentQuestion.scrambled_letters]);
        
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
        
        // Renderizar letras disponibles
        this.renderAvailableLetters();
        this.renderWordBuilder();
    }
    
    renderAvailableLetters() {
        const container = document.getElementById('letters-container');
        container.innerHTML = '';
        
        this.availableLetters.forEach((letter, index) => {
            const letterBtn = document.createElement('button');
            letterBtn.className = `
                letter-btn w-14 h-14 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/50
                border-2 border-blue-200 dark:border-blue-800 rounded-lg text-xl font-bold
                text-blue-600 dark:text-blue-400 transition-all duration-200
                hover:scale-110 active:scale-95 shadow-sm
            `;
            letterBtn.textContent = letter;
            letterBtn.dataset.index = index;
            
            letterBtn.addEventListener('click', () => {
                this.selectLetter(index);
            });
            
            container.appendChild(letterBtn);
        });
    }
    
    renderWordBuilder() {
        const container = document.getElementById('word-builder');
        container.innerHTML = '';
        
        if (this.selectedLetters.length === 0) {
            container.innerHTML = '<p class="text-gray-400 dark:text-gray-500 text-sm">Selecciona letras para formar la palabra</p>';
            return;
        }
        
        this.selectedLetters.forEach((letter, index) => {
            const letterBox = document.createElement('button');
            letterBox.className = `
                selected-letter w-14 h-14 bg-green-50 dark:bg-green-900/30
                border-2 border-green-500 dark:border-green-600 rounded-lg text-xl font-bold
                text-green-700 dark:text-green-300 transition-all duration-200
                hover:scale-110 active:scale-95 shadow-md
            `;
            letterBox.textContent = letter;
            letterBox.dataset.index = index;
            
            letterBox.addEventListener('click', () => {
                this.removeLetter(index);
            });
            
            container.appendChild(letterBox);
        });
    }
    
    selectLetter(index) {
        if (!this.isGameActive) return;
        
        const letter = this.availableLetters[index];
        this.selectedLetters.push(letter);
        this.availableLetters.splice(index, 1);
        
        this.renderAvailableLetters();
        this.renderWordBuilder();
    }
    
    removeLetter(index) {
        if (!this.isGameActive) return;
        
        const letter = this.selectedLetters[index];
        this.availableLetters.push(letter);
        this.selectedLetters.splice(index, 1);
        
        this.renderAvailableLetters();
        this.renderWordBuilder();
    }
    
    clearWord() {
        this.availableLetters = [...this.availableLetters, ...this.selectedLetters];
        this.selectedLetters = [];
        this.renderAvailableLetters();
        this.renderWordBuilder();
    }
    
    checkWord() {
        if (!this.isGameActive || this.selectedLetters.length === 0) return;
        
        const formedWord = this.selectedLetters.join('');
        const isCorrect = formedWord === this.currentQuestion.correct_word;
        const responseTime = Date.now() - this.questionStartTime;
        
        this.attempts++;
        document.getElementById('attempts-counter').textContent = `${this.attempts}/3`;
        
        if (isCorrect) {
            this.handleCorrectAnswer(responseTime);
        } else {
            this.handleIncorrectAnswer();
        }
    }
    
    handleCorrectAnswer(responseTime) {
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
        
        // Animación de éxito
        this.showSuccessAnimation();
        
        // Enviar respuesta
        this.sendQuestionResponse(true, responseTime, this.selectedLetters.join(''));
        
        // Actualizar UI
        this.updateScore();
        
        // Continuar al siguiente
        setTimeout(() => {
            this.proceedToNext();
        }, 2000);
    }
    
    handleIncorrectAnswer() {
        if (this.attempts >= 3) {
            this.incorrectAnswers++;
            this.stopQuestionTimer();
            this.isGameActive = false;
            
            // Mostrar respuesta correcta
            this.showCorrectWord();
            
            const responseTime = Date.now() - this.questionStartTime;
            this.sendQuestionResponse(false, responseTime, this.selectedLetters.join(''));
            
            setTimeout(() => {
                this.proceedToNext();
            }, 3000);
        } else {
            // Mostrar animación de error y permitir reintentar
            this.showErrorAnimation();
            
            // Reordenar letras si está configurado
            if (this.gameConfig.game_mechanics.shuffle_on_wrong) {
                setTimeout(() => {
                    this.clearWord();
                    this.availableLetters = this.shuffleArray(this.availableLetters);
                    this.renderAvailableLetters();
                }, 500);
            }
        }
    }
    
    showHint() {
        if (this.hintUsed) return;
        
        this.hintUsed = true;
        const hintBtn = document.getElementById('show-hint-btn');
        hintBtn.disabled = true;
        hintBtn.classList.add('opacity-50', 'cursor-not-allowed');
        
        // Mostrar la palabra correcta temporalmente
        const wordBuilder = document.getElementById('word-builder');
        wordBuilder.innerHTML = `
            <div class="text-center p-4 bg-yellow-50 dark:bg-yellow-900/30 rounded-lg border-2 border-yellow-300 dark:border-yellow-700">
                <p class="text-2xl font-bold text-yellow-700 dark:text-yellow-300 tracking-widest">${this.currentQuestion.correct_word}</p>
                <p class="text-xs text-yellow-600 dark:text-yellow-400 mt-2">-5 puntos de penalización</p>
            </div>
        `;
        
        setTimeout(() => {
            this.renderWordBuilder();
        }, 3000);
    }
    
    showSuccessAnimation() {
        const wordBuilder = document.getElementById('word-builder');
        wordBuilder.innerHTML = `
            <div class="text-center p-6 bg-green-50 dark:bg-green-900/30 rounded-xl border-2 border-green-500 dark:border-green-600 animate-pulse">
                <svg class="w-16 h-16 text-green-500 dark:text-green-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="text-xl font-bold text-green-700 dark:text-green-300">¡Correcto!</p>
                <p class="text-sm text-green-600 dark:text-green-400 mt-1">${this.currentQuestion.correct_word}</p>
            </div>
        `;
    }
    
    showErrorAnimation() {
        const wordBuilder = document.getElementById('word-builder');
        const originalContent = wordBuilder.innerHTML;
        
        wordBuilder.innerHTML = `
            <div class="text-center p-4 bg-red-50 dark:bg-red-900/30 rounded-lg border-2 border-red-500 dark:border-red-600 animate-shake">
                <svg class="w-12 h-12 text-red-500 dark:text-red-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                <p class="text-lg font-bold text-red-700 dark:text-red-300">Intenta de nuevo</p>
            </div>
        `;
        
        setTimeout(() => {
            this.renderWordBuilder();
        }, 1000);
    }
    
    showCorrectWord() {
        const wordBuilder = document.getElementById('word-builder');
        wordBuilder.innerHTML = `
            <div class="text-center p-6 bg-blue-50 dark:bg-blue-900/30 rounded-xl border-2 border-blue-500 dark:border-blue-600">
                <p class="text-sm text-blue-600 dark:text-blue-400 mb-2">La palabra correcta era:</p>
                <p class="text-3xl font-bold text-blue-700 dark:text-blue-300 tracking-widest">${this.currentQuestion.correct_word}</p>
            </div>
        `;
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
                        <div class="w-20 h-20 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                            </svg>
                        </div>
                        <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">¡Nivel ${this.currentLevel} Completado!</h2>
                        <p class="text-gray-500 dark:text-gray-400">Excelente trabajo ordenando palabras</p>
                    </div>
                    
                    <hr class="bg-gray-200 dark:bg-gray-700 my-6">
                    
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-xl p-4 text-center">
                            <div class="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-1">${this.score}</div>
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
    
    finishGame() {
        const totalTime = Math.floor((Date.now() - this.startTime) / 1000);
        this.sendGameResults(totalTime);
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
        document.getElementById('progress-bar').style.width = `${progress}%`;
    }
    
    startQuestionTimer() {
        const timerEl = document.getElementById('question-timer');
        let timeLeft = this.currentQuestion.time_limit;
        
        this.questionTimer = setInterval(() => {
            timeLeft--;
            timerEl.textContent = timeLeft;
            
            if (timeLeft <= 10) {
                timerEl.parentElement.classList.add('bg-red-100', 'dark:bg-red-900/50', 'text-red-800', 'dark:text-red-300');
                timerEl.parentElement.classList.remove('bg-orange-100', 'dark:bg-orange-900/30');
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
        
        this.showCorrectWord();
        
        const responseTime = this.currentQuestion.time_limit * 1000;
        this.sendQuestionResponse(false, responseTime, this.selectedLetters.join(''));
        
        setTimeout(() => {
            this.proceedToNext();
        }, 3000);
    }
    
    // API calls
    async sendQuestionResponse(isCorrect, responseTime, selectedWord) {
        const data = {
            session_url: this.sessionData.url_sesion,
            question_id: this.currentQuestion.id,
            level: this.currentLevel,
            is_correct: isCorrect,
            response_time_ms: responseTime,
            selected_option: selectedWord,
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
                alert('¡Juego finalizado!');
                window.location.href = this.sessionData.api_urls.game_list;
            }
        } catch (error) {
            console.error('❌ Error:', error);
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

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.gameSessionData !== 'undefined' && typeof window.gameConfig !== 'undefined') {
        window.gameInstance = new OrdenarPalabrasGame(window.gameSessionData, window.gameConfig);
    } else {
        console.error('❌ Faltan datos de sesión');
    }
});
