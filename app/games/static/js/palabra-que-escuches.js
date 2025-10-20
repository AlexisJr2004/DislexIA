/**
 * Juego: Palabra que Escuches
 * El jugador debe identificar la palabra correcta después de escuchar el audio
 */

class PalabraQueEscuchesGame {
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
        this.audioReplays = 0;
        this.audioElement = null;
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
            <div class="audio-word-game max-w-7xl mx-auto p-4">
                <!-- Encabezado del juego -->
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 mb-6 transition-colors duration-200">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <div class="w-12 h-12 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl flex items-center justify-center">
                                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                                </svg>
                            </div>
                            <div>
                                <h2 class="text-xl font-bold text-gray-900 dark:text-white">Palabra que Escuches</h2>
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
                    <!-- COLUMNA IZQUIERDA - Imagen y controles de audio -->
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

                        <!-- Reproductor de audio -->
                        <div class="mb-6">
                            <div class="bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/30 dark:to-purple-900/30 rounded-2xl p-8 border-2 border-indigo-200 dark:border-indigo-800">
                                <div class="text-center mb-6">
                                    <div class="w-24 h-24 bg-white dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
                                        <svg id="audio-icon" class="w-12 h-12 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                                        </svg>
                                    </div>
                                    <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">Escucha con atención</h3>
                                    <p class="text-sm text-gray-600 dark:text-gray-400">Reproduce el audio para escuchar la palabra</p>
                                </div>

                                <button id="play-audio-btn" class="w-full py-4 bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-800 text-white rounded-xl font-semibold flex items-center justify-center gap-2 transition-all shadow-md hover:shadow-lg">
                                    <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                                    </svg>
                                    <span id="play-btn-text">Reproducir Audio</span>
                                </button>

                                <div class="mt-4 flex items-center justify-between text-sm">
                                    <span class="text-gray-600 dark:text-gray-400">Reproducciones: <span id="replay-counter" class="font-semibold">0/3</span></span>
                                    <span class="text-gray-500 dark:text-gray-500 text-xs">-2 pts por reproducción extra</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Imagen de pista -->
                        <div class="mb-4">
                            <img id="question-image" 
                                src="" 
                                alt="Pista visual" 
                                class="w-full h-48 object-contain rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 shadow-sm">
                        </div>

                        <!-- Pista -->
                        <div class="text-center p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
                            <p class="text-xs text-indigo-600 dark:text-indigo-400 mb-1">Pista</p>
                            <p id="hint-text" class="text-sm font-medium text-gray-900 dark:text-white"></p>
                        </div>
                    </div>

                    <!-- COLUMNA DERECHA - Opciones de palabras -->
                    <div class="space-y-6">
                        <!-- Instrucción -->
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 transition-colors duration-200">
                            <div class="flex items-center gap-3 mb-4">
                                <div class="w-10 h-10 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg flex items-center justify-center">
                                    <svg class="w-5 h-5 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                                <div>
                                    <h3 class="text-sm font-bold text-gray-900 dark:text-white">Instrucción</h3>
                                    <p class="text-xs text-gray-600 dark:text-gray-400">Selecciona la palabra que escuchaste</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Opciones de palabras -->
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 transition-colors duration-200">
                            <h3 class="text-center text-sm font-medium text-gray-700 dark:text-gray-300 mb-6">¿Qué palabra escuchaste?</h3>
                            <div id="options-container" class="grid grid-cols-2 gap-4">
                                <!-- Las opciones aparecen aquí -->
                            </div>
                        </div>

                        <!-- Consejos -->
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 transition-colors duration-200">
                            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4 text-center">Consejos</h3>
                            
                            <div class="space-y-3">
                                <div class="flex items-start gap-3 p-3 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg">
                                    <svg class="w-5 h-5 text-indigo-600 dark:text-indigo-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                                    </svg>
                                    <div>
                                        <p class="text-xs font-medium text-indigo-700 dark:text-indigo-300">Escucha bien</p>
                                        <p class="text-xs text-indigo-600 dark:text-indigo-400">Presta atención a cada sonido</p>
                                    </div>
                                </div>

                                <div class="flex items-start gap-3 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                                    <svg class="w-5 h-5 text-purple-600 dark:text-purple-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                    </svg>
                                    <div>
                                        <p class="text-xs font-medium text-purple-700 dark:text-purple-300">Puedes repetir</p>
                                        <p class="text-xs text-purple-600 dark:text-purple-400">Hasta 3 veces el audio</p>
                                    </div>
                                </div>

                                <div class="flex items-start gap-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                    <svg class="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <div>
                                        <p class="text-xs font-medium text-green-700 dark:text-green-300">Usa la pista</p>
                                        <p class="text-xs text-green-600 dark:text-green-400">La imagen puede ayudarte</p>
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
        document.getElementById('play-audio-btn')?.addEventListener('click', () => {
            this.playAudio();
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
        this.audioReplays = 0;
        
        // Limpiar audio anterior
        if (this.audioElement) {
            this.audioElement.pause();
            this.audioElement = null;
        }
        
        this.renderQuestion();
        this.startQuestionTimer();
        this.updateProgress();
        
        // Auto-reproducir el audio al inicio
        setTimeout(() => {
            this.playAudio();
        }, 500);
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
        
        // Actualizar contadores
        document.getElementById('attempts-counter').textContent = `${this.attempts}/3`;
        document.getElementById('replay-counter').textContent = `${this.audioReplays}/3`;
        
        // Renderizar opciones
        this.renderOptions();
    }
    
    renderOptions() {
        const container = document.getElementById('options-container');
        container.innerHTML = '';
        
        const shuffledOptions = this.shuffleArray(this.currentQuestion.options);
        
        shuffledOptions.forEach(option => {
            const optionBtn = document.createElement('button');
            optionBtn.className = `
                option-btn p-6 bg-gradient-to-br from-gray-50 to-gray-100
                dark:from-gray-800 dark:to-gray-900
                hover:from-indigo-50 hover:to-purple-50
                dark:hover:from-indigo-900/30 dark:hover:to-purple-900/30
                border-2 border-gray-200 dark:border-gray-700
                hover:border-indigo-400 dark:hover:border-indigo-600
                rounded-xl text-xl font-bold text-gray-700 dark:text-gray-300
                transition-all duration-200 hover:scale-105 active:scale-95
                shadow-sm hover:shadow-md
            `;
            optionBtn.textContent = option;
            optionBtn.dataset.word = option;
            
            optionBtn.addEventListener('click', () => {
                if (this.isGameActive) {
                    this.checkAnswer(option);
                }
            });
            
            container.appendChild(optionBtn);
        });
    }
    
    playAudio() {
        if (this.audioReplays >= this.gameConfig.game_mechanics.max_audio_replays) {
            this.showMessage('Has alcanzado el límite de reproducciones', 'warning');
            return;
        }
        
        // Crear o reproducir audio
        if (!this.audioElement) {
            this.audioElement = new Audio(this.currentQuestion.audio_path);
        }
        
        this.audioReplays++;
        document.getElementById('replay-counter').textContent = `${this.audioReplays}/3`;
        
        const playBtn = document.getElementById('play-audio-btn');
        const playBtnText = document.getElementById('play-btn-text');
        const audioIcon = document.getElementById('audio-icon');
        
        // Cambiar estado a "reproduciendo"
        playBtn.disabled = true;
        playBtn.classList.add('opacity-75');
        playBtnText.textContent = 'Reproduciendo...';
        audioIcon.classList.add('animate-pulse');
        
        this.audioElement.play();
        
        this.audioElement.onended = () => {
            playBtn.disabled = false;
            playBtn.classList.remove('opacity-75');
            playBtnText.textContent = this.audioReplays >= this.gameConfig.game_mechanics.max_audio_replays 
                ? 'Sin reproducciones' 
                : 'Reproducir de nuevo';
            audioIcon.classList.remove('animate-pulse');
            
            if (this.audioReplays >= this.gameConfig.game_mechanics.max_audio_replays) {
                playBtn.disabled = true;
                playBtn.classList.add('opacity-50', 'cursor-not-allowed');
            }
        };
        
        this.audioElement.onerror = () => {
            playBtn.disabled = false;
            playBtn.classList.remove('opacity-75');
            playBtnText.textContent = 'Error al reproducir';
            audioIcon.classList.remove('animate-pulse');
            this.showMessage('Error al cargar el audio', 'error');
        };
    }
    
    checkAnswer(selectedWord) {
        if (!this.isGameActive) return;
        
        const isCorrect = selectedWord === this.currentQuestion.correct_word;
        const responseTime = Date.now() - this.questionStartTime;
        
        this.attempts++;
        document.getElementById('attempts-counter').textContent = `${this.attempts}/3`;
        
        if (isCorrect) {
            this.handleCorrectAnswer(responseTime, selectedWord);
        } else {
            this.handleIncorrectAnswer(selectedWord);
        }
    }
    
    handleCorrectAnswer(responseTime, selectedWord) {
        this.correctAnswers++;
        this.stopQuestionTimer();
        this.isGameActive = false;
        
        // Detener audio
        if (this.audioElement) {
            this.audioElement.pause();
        }
        
        // Calcular puntos
        const timeBonus = Math.max(0, this.currentQuestion.time_limit - Math.floor(responseTime / 1000));
        let points = this.currentQuestion.points + (timeBonus * this.gameConfig.scoring.time_bonus);
        
        // Penalización por reproducciones extra
        if (this.audioReplays > 1) {
            points -= (this.audioReplays - 1) * this.gameConfig.scoring.replay_audio_penalty;
        }
        
        this.score += Math.max(0, points);
        
        // Mostrar resultado
        this.showResult(true, selectedWord);
        
        // Enviar respuesta
        this.sendQuestionResponse(true, responseTime, selectedWord);
        
        // Actualizar UI
        this.updateScore();
        
        // Continuar al siguiente
        setTimeout(() => {
            this.proceedToNext();
        }, 2500);
    }
    
    handleIncorrectAnswer(selectedWord) {
        if (this.attempts >= 3) {
            this.incorrectAnswers++;
            this.stopQuestionTimer();
            this.isGameActive = false;
            
            // Detener audio
            if (this.audioElement) {
                this.audioElement.pause();
            }
            
            // Mostrar respuesta correcta
            this.showResult(false, selectedWord);
            
            const responseTime = Date.now() - this.questionStartTime;
            this.sendQuestionResponse(false, responseTime, selectedWord);
            
            setTimeout(() => {
                this.proceedToNext();
            }, 3000);
        } else {
            // Mostrar animación de error
            this.showErrorAnimation(selectedWord);
            this.showMessage(`Intento ${this.attempts}/3 - Intenta de nuevo`, 'error');
        }
    }
    
    showResult(isCorrect, selectedWord) {
        const container = document.getElementById('options-container');
        container.innerHTML = `
            <div class="col-span-2 text-center p-8 rounded-2xl ${
                isCorrect 
                    ? 'bg-green-50 dark:bg-green-900/30 border-2 border-green-500 dark:border-green-600' 
                    : 'bg-red-50 dark:bg-red-900/30 border-2 border-red-500 dark:border-red-600'
            }">
                <div class="flex items-center justify-center gap-2 mb-4">
                    ${isCorrect 
                        ? '<svg class="w-16 h-16 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>' 
                        : '<svg class="w-16 h-16 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'}
                </div>
                <p class="text-2xl font-bold ${isCorrect ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'} mb-2">
                    ${isCorrect ? '¡Correcto!' : '¡Incorrecto!'}
                </p>
                ${!isCorrect ? `<p class="text-lg ${isCorrect ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'} mb-2">La palabra correcta era:</p>` : ''}
                <p class="text-3xl font-bold ${isCorrect ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'} tracking-wider">
                    ${this.currentQuestion.correct_word}
                </p>
                ${this.audioReplays > 1 ? `<p class="text-sm text-gray-600 dark:text-gray-400 mt-3">Reproducciones usadas: ${this.audioReplays}</p>` : ''}
            </div>
        `;
    }
    
    showErrorAnimation(selectedWord) {
        const optionButtons = document.querySelectorAll('.option-btn');
        
        optionButtons.forEach(btn => {
            if (btn.dataset.word === selectedWord) {
                btn.classList.add('bg-red-100', 'dark:bg-red-900/50', 'border-red-500', 'dark:border-red-600');
                btn.style.animation = 'shake 0.5s';
                
                setTimeout(() => {
                    btn.style.animation = '';
                    btn.classList.remove('bg-red-100', 'dark:bg-red-900/50', 'border-red-500', 'dark:border-red-600');
                }, 500);
            }
        });
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
            setTimeout(() => messageEl.remove(), 300);
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
                        <div class="w-20 h-20 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        </div>
                        <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">¡Nivel ${this.currentLevel} Completado!</h2>
                        <p class="text-gray-500 dark:text-gray-400">Excelente trabajo escuchando palabras</p>
                    </div>
                    
                    <hr class="bg-gray-200 dark:bg-gray-700 my-6">
                    
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="bg-indigo-50 dark:bg-indigo-900/30 border border-indigo-200 dark:border-indigo-800 rounded-xl p-4 text-center">
                            <div class="text-3xl font-bold text-indigo-600 dark:text-indigo-400 mb-1">${this.score}</div>
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
        
        const result = await this.sendGameResults(totalTime);
        
        if (result && result.success) {
            console.log('✅ [Palabra Escuches] Juego finalizado correctamente');
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
        
        if (this.audioElement) {
            this.audioElement.pause();
        }
        
        this.showResult(false, '');
        this.showMessage('Se acabó el tiempo ⏰', 'warning');
        
        const responseTime = this.currentQuestion.time_limit * 1000;
        this.sendQuestionResponse(false, responseTime, '');
        
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
            audio_replays: this.audioReplays
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
        
        console.log('📤 [Palabra Escuches] Enviando resultados finales:', data);
        
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
            console.log('📥 [Palabra Escuches] Respuesta del servidor:', result);
            
            if (result.success) {
                // === MANEJAR RESPUESTA DEL BACKEND ===
                if (result.evaluacion_completada) {
                    alert(`🎉 ¡Evaluación completa! ${result.final_stats.sesiones_completadas}/${result.final_stats.sesiones_totales} sesiones`);
                    window.location.href = result.redirect_url;
                    return { success: true };
                } else if (result.siguiente_url) {
                    const progreso = result.progreso;
                    alert(`✅ Juego completado!\n\nProgreso: ${progreso.completadas}/${progreso.totales} (${progreso.porcentaje}%)\n\n🎮 Avanzando al siguiente juego...`);
                    
                    setTimeout(() => {
                        window.location.href = result.siguiente_url;
                    }, 2000);
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
        window.gameInstance = new PalabraQueEscuchesGame(window.gameSessionData, window.gameConfig);
    } else {
        console.error('❌ Faltan datos de sesión');
    }
});
