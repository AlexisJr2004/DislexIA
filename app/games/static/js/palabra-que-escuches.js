/**
 * Juego: Palabra que Escuches (Refactorizado)
 * Extiende BaseGame para reutilizar funcionalidad común
 */

class PalabraQueEscuchesGame extends BaseGame {
    constructor(sessionData, gameConfig) {
        super(sessionData, gameConfig, 'Palabra que Escuches');
        
        // Estado específico del juego
        this.audioReplays = 0;
        this.audioElement = null;
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
                ${GameUtils.createGameHeader({
                    title: 'Palabra que Escuches',
                    iconGradient: 'from-indigo-500 to-purple-500',
                    iconSvg: `
                        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                        </svg>
                    `
                })}

                <!-- Contenedor de dos columnas -->
                <div class="grid grid-cols-2 gap-6">
                    <!-- COLUMNA IZQUIERDA - Imagen y controles de audio -->
                    <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 transition-colors duration-200">
                        ${GameUtils.createTimerAndAttempts(30)}

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
                        ${this.createTipsPanel()}
                    </div>
                </div>
            </div>
        `;
    }
    
    createTipsPanel() {
        return `
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
        `;
    }
    
    bindEvents() {
        document.getElementById('play-audio-btn')?.addEventListener('click', () => {
            this.playAudio();
        });
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
        
        this.updateQuestionCounter();
        
        // Cargar imagen
        const imageEl = document.getElementById('question-image');
        imageEl.src = this.currentQuestion.image_path;
        imageEl.alt = this.currentQuestion.hint;
        
        // Mostrar pista
        document.getElementById('hint-text').textContent = this.currentQuestion.hint;
        
        // Actualizar contadores
        this.updateAttemptsCounter();
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
        const maxReplays = this.gameConfig.game_mechanics?.max_audio_replays || 3;
        
        if (this.audioReplays >= maxReplays) {
            GameUtils.showToast('Has alcanzado el límite de reproducciones', 'warning');
            return;
        }
        
        // Crear o reproducir audio
        if (!this.audioElement) {
            this.audioElement = new Audio(this.currentQuestion.audio_path);
        }
        
        this.audioReplays++;
        document.getElementById('replay-counter').textContent = `${this.audioReplays}/${maxReplays}`;
        
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
            playBtnText.textContent = this.audioReplays >= maxReplays 
                ? 'Sin reproducciones' 
                : 'Reproducir de nuevo';
            audioIcon.classList.remove('animate-pulse');
            
            if (this.audioReplays >= maxReplays) {
                playBtn.disabled = true;
                playBtn.classList.add('opacity-50', 'cursor-not-allowed');
            }
        };
        
        this.audioElement.onerror = () => {
            playBtn.disabled = false;
            playBtn.classList.remove('opacity-75');
            playBtnText.textContent = 'Error al reproducir';
            audioIcon.classList.remove('animate-pulse');
            GameUtils.showToast('Error al cargar el audio', 'error');
        };
    }
    
    checkAnswer(selectedWord) {
        if (!this.isGameActive) return;
        
        const isCorrect = selectedWord === this.currentQuestion.correct_word;
        const responseTime = Date.now() - this.questionStartTime;
        
        this.attempts++;
        this.updateAttemptsCounter();
        
        if (isCorrect) {
            this.handleCorrectAnswerWithAudio(responseTime, selectedWord);
        } else {
            const noMoreAttempts = this.handleIncorrectAnswer(selectedWord, responseTime);
            
            if (noMoreAttempts) {
                this.showResultAudio(false, selectedWord);
                setTimeout(() => {
                    this.proceedToNext();
                }, 3000);
            } else {
                this.showErrorAnimationOption(selectedWord);
                GameUtils.showToast(`Intento ${this.attempts}/3 - Intenta de nuevo`, 'error');
            }
        }
    }
    
    handleCorrectAnswerWithAudio(responseTime, selectedWord) {
        this.correctAnswers++;
        this.stopQuestionTimer();
        this.isGameActive = false;
        
        // Detener audio
        if (this.audioElement) {
            this.audioElement.pause();
        }
        
        // Calcular puntos con penalización por reproducciones extra
        const timeBonus = Math.max(0, this.currentQuestion.time_limit - Math.floor(responseTime / 1000));
        let points = this.currentQuestion.points + (timeBonus * this.gameConfig.scoring.time_bonus);
        
        // Penalización por reproducciones extra
        if (this.audioReplays > 1) {
            const penalty = (this.audioReplays - 1) * (this.gameConfig.scoring.replay_audio_penalty || 2);
            points -= penalty;
        }
        
        this.score += Math.max(0, points);
        
        // Mostrar resultado
        this.showResultAudio(true, selectedWord);
        
        // Enviar respuesta con audio_replays
        this.sendQuestionResponse(true, responseTime, selectedWord);
        
        // Actualizar UI
        this.updateScore();
        
        // Continuar al siguiente
        setTimeout(() => {
            this.proceedToNext();
        }, 2500);
    }
    
    showResultAudio(isCorrect, selectedWord) {
        const container = document.getElementById('options-container');
        container.innerHTML = `
            <div class="col-span-2 text-center p-8 rounded-2xl ${
                isCorrect 
                    ? 'bg-green-50 dark:bg-green-900/30 border-2 border-green-500 dark:border-green-600' 
                    : 'bg-red-50 dark:bg-red-900/30 border-2 border-red-500 dark:border-red-600'
            }">
                <div class="flex items-center justify-center gap-2 mb-4">
                    ${isCorrect ? GameUtils.icons.check : GameUtils.icons.cross}
                </div>
                <p class="text-2xl font-bold ${isCorrect ? 'text-green-700 dark:text-green-300' : 'text-red-700 dark:text-red-300'} mb-2">
                    ${isCorrect ? '¡Correcto!' : '¡Incorrecto!'}
                </p>
                ${!isCorrect ? `<p class="text-lg text-red-600 dark:text-red-400 mb-2">La palabra correcta era:</p>` : ''}
                <p class="text-3xl font-bold ${isCorrect ? 'text-green-800 dark:text-green-200' : 'text-red-800 dark:text-red-200'} tracking-wider">
                    ${this.currentQuestion.correct_word}
                </p>
                ${this.audioReplays > 1 ? `<p class="text-sm text-gray-600 dark:text-gray-400 mt-3">Reproducciones usadas: ${this.audioReplays}</p>` : ''}
            </div>
        `;
    }
    
    showErrorAnimationOption(selectedWord) {
        const optionButtons = document.querySelectorAll('.option-btn');
        
        optionButtons.forEach(btn => {
            if (btn.dataset.word === selectedWord) {
                this.showErrorAnimation(btn);
            }
        });
    }
    
    onTimeUp() {
        if (this.audioElement) {
            this.audioElement.pause();
        }
        
        this.showResultAudio(false, '');
        GameUtils.showToast('Se acabó el tiempo ⏰', 'warning');
    }
    
    // Override sendQuestionResponse para incluir audio_replays
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
    
    // Métodos de personalización de UI
    getGameGradient() {
        return 'bg-gradient-to-r from-indigo-500 to-purple-500';
    }
    
    getSuccessMessage() {
        return 'Excelente trabajo escuchando palabras';
    }
    
    getScoreCardClass() {
        return 'bg-indigo-50 dark:bg-indigo-900/30 border border-indigo-200 dark:border-indigo-800';
    }
    
    getScoreTextClass() {
        return 'text-indigo-600 dark:text-indigo-400';
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.gameSessionData !== 'undefined' && typeof window.gameConfig !== 'undefined') {
        window.gameInstance = new PalabraQueEscuchesGame(window.gameSessionData, window.gameConfig);
        window.gameInstance.init();
    } else {
        console.error('❌ Faltan datos de sesión');
    }
});