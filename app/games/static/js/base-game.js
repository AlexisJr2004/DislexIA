/**
 * Clase Base para Minijuegos de Dislexia
 * Maneja funcionalidad común: timer, puntuación, niveles, API calls
 */

class BaseGame {
    constructor(sessionData, gameConfig, gameName) {
        this.sessionData = sessionData;
        this.gameConfig = gameConfig;
        this.gameName = gameName;
        
        // Estado del juego
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
        this.questionTimer = null;
        this.pausedTimeLeft = 0; // Para guardar tiempo restante al pausar
    }
    
    // ============================================
    // MÉTODOS DE INICIALIZACIÓN
    // ============================================
    
    init() {
        this.createGameInterface();
        this.bindEvents();
        this.startGame();
    }
    
    // Método abstracto - debe ser implementado por clases hijas
    createGameInterface() {
        throw new Error('createGameInterface() debe ser implementado por la clase hija');
    }
    
    // Método abstracto - debe ser implementado por clases hijas
    bindEvents() {
        throw new Error('bindEvents() debe ser implementado por la clase hija');
    }
    
    startGame() {
        this.isGameActive = true;
        this.loadCurrentQuestion();
    }
    
    // ============================================
    // GESTIÓN DE PREGUNTAS
    // ============================================
    
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
        const shuffled = this.shuffleArray([...questions]);
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
    
    // Método abstracto
    renderQuestion() {
        throw new Error('renderQuestion() debe ser implementado por la clase hija');
    }
    
    // ============================================
    // GESTIÓN DE RESPUESTAS
    // ============================================
    
    handleCorrectAnswer(responseTime, selectedOption, points = null) {
        this.correctAnswers++;
        this.stopQuestionTimer();
        this.isGameActive = false;
        
        // Calcular puntos
        if (points === null) {
            const timeBonus = Math.max(0, this.currentQuestion.time_limit - Math.floor(responseTime / 1000));
            points = this.currentQuestion.points + (timeBonus * this.gameConfig.scoring.time_bonus);
            
            if (this.hintUsed) {
                points -= this.gameConfig.scoring.hint_penalty;
            }
        }
        
        this.score += Math.max(0, points);
        
        // Enviar respuesta
        this.sendQuestionResponse(true, responseTime, selectedOption);
        
        // Actualizar UI
        this.updateScore();
    }
    
    handleIncorrectAnswer(selectedOption, responseTime = null) {
        if (this.attempts >= 3) {
            this.incorrectAnswers++;
            this.stopQuestionTimer();
            this.isGameActive = false;
            
            const finalResponseTime = responseTime || (Date.now() - this.questionStartTime);
            this.sendQuestionResponse(false, finalResponseTime, selectedOption);
            
            return true; // Indica que se acabaron los intentos
        }
        
        return false; // Aún quedan intentos
    }
    
    // ============================================
    // NAVEGACIÓN DE NIVELES
    // ============================================
    
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
        gameArea.innerHTML = this.getLevelResultsHTML(accuracy);
        
        document.getElementById('btn-next-level')?.addEventListener('click', () => this.nextLevel());
        document.getElementById('btn-finish-level')?.addEventListener('click', () => this.finishGame());
        
        this.sendLevelResults();
    }
    
    getLevelResultsHTML(accuracy) {
        return `
            <div class="level-results max-w-3xl mx-auto">
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 mb-6 transition-colors duration-200">
                    <div class="text-center mb-6">
                        <div class="w-20 h-20 ${this.getGameGradient()} rounded-full flex items-center justify-center mx-auto mb-4">
                            ${this.getSuccessIcon()}
                        </div>
                        <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">¡Nivel ${this.currentLevel} Completado!</h2>
                        <p class="text-gray-500 dark:text-gray-400">${this.getSuccessMessage()}</p>
                    </div>
                    
                    <hr class="bg-gray-200 dark:bg-gray-700 my-6">
                    
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="${this.getScoreCardClass()} rounded-xl p-4 text-center">
                            <div class="text-3xl font-bold ${this.getScoreTextClass()} mb-1">${this.score}</div>
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
    }
    
    // Métodos para personalizar por juego
    getGameGradient() {
        return 'bg-gradient-to-r from-purple-500 to-pink-500';
    }
    
    getSuccessIcon() {
        return `
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
        `;
    }
    
    getSuccessMessage() {
        return 'Excelente trabajo';
    }
    
    getScoreCardClass() {
        return 'bg-purple-50 dark:bg-purple-900/30 border border-purple-200 dark:border-purple-800';
    }
    
    getScoreTextClass() {
        return 'text-purple-600 dark:text-purple-400';
    }
    
    nextLevel() {
        this.currentLevel++;
        this.currentQuestionIndex = 0;
        
        const nextLevel = this.gameConfig.levels.find(l => l.level === this.currentLevel);
        if (!nextLevel) {
            this.showFinalCompletion();
            return;
        }
        
        this.correctAnswers = 0;
        this.incorrectAnswers = 0;
        this.selectedQuestions = null;
        
        this.createGameInterface();
        this.bindEvents();
        this.startGame();
    }
    
    showFinalCompletion() {
        setTimeout(() => {
            alert('🎉 ¡Felicidades! Has completado todos los niveles.\n\n' +
                `✨ Puntuación final: ${this.score} puntos\n` +
                `🎯 Niveles completados: ${this.currentLevel - 1}\n` +
                `✅ Aciertos: ${this.correctAnswers}\n` +
                `❌ Errores: ${this.incorrectAnswers}`);
            
            if (this.sessionData.es_evaluacion_ia) {
                this.finishGame();
            } else {
                window.location.href = this.sessionData.api_urls.game_list;
            }
        }, 500);
    }
    
    async finishGame() {
        const totalTime = Math.floor((Date.now() - this.startTime) / 1000);
        const result = await this.sendGameResults(totalTime);
        
        if (result && result.success) {
            console.log(`✅ [${this.gameName}] Juego finalizado correctamente`);
        } else {
            alert('Error al finalizar el juego: ' + (result ? result.error : 'Error desconocido'));
        }
    }
    
    // ============================================
    // UI UPDATES
    // ============================================
    
    updateScore() {
        const scoreEl = document.getElementById('game-score');
        if (scoreEl) scoreEl.textContent = this.score;
        
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
    
    updateQuestionCounter() {
        const currentEl = document.getElementById('current-question');
        const totalEl = document.getElementById('total-questions');
        const questions = this.getCurrentLevelQuestions();
        
        if (currentEl) currentEl.textContent = this.currentQuestionIndex + 1;
        if (totalEl) totalEl.textContent = questions.length;
    }
    
    updateAttemptsCounter() {
        const attemptsEl = document.getElementById('attempts-counter');
        if (attemptsEl) attemptsEl.textContent = `${this.attempts}/3`;
    }
    
    // ============================================
    // PAUSA Y REANUDACIÓN
    // ============================================
    
    pauseGame() {
        // Detener el timer de la pregunta actual
        if (this.questionTimer) {
            clearInterval(this.questionTimer);
            this.questionTimer = null;
        }
        
        // Guardar el tiempo restante de la pregunta actual
        const timerEl = document.getElementById('question-timer');
        if (timerEl) {
            this.pausedTimeLeft = parseInt(timerEl.textContent) || 0;
        }
        
        console.log('⏸️ Juego pausado. Tiempo restante:', this.pausedTimeLeft);
    }
    
    resumeGame() {
        // Reanudar el timer de la pregunta desde donde se quedó
        const timerEl = document.getElementById('question-timer');
        if (!timerEl || !this.currentQuestion) return;
        
        let timeLeft = this.pausedTimeLeft || this.currentQuestion.time_limit;
        timerEl.textContent = timeLeft;
        
        console.log('▶️ Juego reanudado. Continuando desde:', timeLeft);
        
        this.questionTimer = setInterval(() => {
            timeLeft--;
            timerEl.textContent = timeLeft;
            
            if (timeLeft <= 10) {
                this.applyTimerWarning(timerEl.parentElement);
            }
            
            if (timeLeft <= 0) {
                this.timeUp();
            }
        }, 1000);
    }
    
    // ============================================
    // TIMER
    // ============================================
    
    startQuestionTimer() {
        const timerEl = document.getElementById('question-timer');
        if (!timerEl || !this.currentQuestion) return;
        
        let timeLeft = this.currentQuestion.time_limit;
        timerEl.textContent = timeLeft;
        
        this.questionTimer = setInterval(() => {
            timeLeft--;
            timerEl.textContent = timeLeft;
            
            if (timeLeft <= 10) {
                this.applyTimerWarning(timerEl.parentElement);
            }
            
            if (timeLeft <= 0) {
                this.timeUp();
            }
        }, 1000);
    }
    
    applyTimerWarning(element) {
        if (!element) return;
        element.classList.add('bg-red-100', 'dark:bg-red-900/50', 'text-red-800', 'dark:text-red-300', 'border-red-300', 'dark:border-red-700');
        element.classList.remove('bg-orange-50', 'dark:bg-orange-900/30', 'border-orange-200', 'dark:border-orange-800');
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
        
        this.onTimeUp();
        
        const responseTime = this.currentQuestion.time_limit * 1000;
        this.sendQuestionResponse(false, responseTime, '');
        
        setTimeout(() => {
            this.proceedToNext();
        }, 3000);
    }
    
    // Método abstracto
    onTimeUp() {
        throw new Error('onTimeUp() debe ser implementado por la clase hija');
    }
    
    // ============================================
    // ANIMACIONES
    // ============================================
    
    showErrorAnimation(element) {
        if (!element) return;
        
        element.classList.add('bg-red-100', 'dark:bg-red-900/50', 'border-red-500', 'dark:border-red-600');
        element.style.animation = 'shake 0.5s';
        
        setTimeout(() => {
            element.style.animation = '';
            element.classList.remove('bg-red-100', 'dark:bg-red-900/50', 'border-red-500', 'dark:border-red-600');
        }, 500);
    }
    
    // ============================================
    // API CALLS
    // ============================================
    
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
        const totalClicks = this.correctAnswers + this.incorrectAnswers;
        
        const data = {
            session_url: this.sessionData.url_sesion,
            total_score: this.score,
            total_correct: this.correctAnswers,
            total_incorrect: this.incorrectAnswers,
            total_time_seconds: totalTimeSeconds,
            levels_completed: this.currentLevel,
            total_clicks: totalClicks,
            total_hits: this.correctAnswers,
            total_misses: this.incorrectAnswers
        };
        
        console.log(`📤 [${this.gameName}] Enviando resultados finales:`, data);
        
        try {
            const response = await fetch(this.sessionData.api_urls.finish_game, {
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
            console.log(`📥 [${this.gameName}] Respuesta del servidor:`, result);
            
            if (result.success) {
                return this.handleGameFinishResponse(result);
            } else {
                return { success: false, error: result.error };
            }
            
        } catch (error) {
            console.error('❌ Error al finalizar juego:', error);
            return { success: false, error: 'Error de conexión al finalizar el juego' };
        }
    }
    
    handleGameFinishResponse(result) {
        if (result.evaluacion_completada) {
            alert(`🎉 ¡Evaluación completa! ${result.final_stats.sesiones_completadas}/${result.final_stats.sesiones_totales} sesiones`);
            window.location.href = result.redirect_url;
            return { success: true };
        } else if (result.siguiente_url) {
            const progreso = result.progreso;
            
            if (window.showNextGameAlert) {
                window.showNextGameAlert({ progreso, siguienteUrl: result.siguiente_url });
            } else {
                this.loadGameAlertsScript(progreso, result.siguiente_url);
            }
            return { success: true };
        } else {
            window.location.href = result.redirect_url || `/games/results/${this.sessionData.evaluacion_id}/`;
            return { success: true };
        }
    }
    
    loadGameAlertsScript(progreso, siguienteUrl) {
        const script = document.createElement('script');
        script.src = '/static/js/game-alerts.js';
        script.onload = () => {
            if (window.showNextGameAlert) {
                window.showNextGameAlert({ progreso, siguienteUrl });
            } else {
                alert(`✅ Juego completado!\n\nProgreso: ${progreso.completadas}/${progreso.totales} (${progreso.porcentaje}%)\n\n🎮 Avanzando al siguiente juego...`);
                setTimeout(() => {
                    window.location.href = siguienteUrl;
                }, 2000);
            }
        };
        document.body.appendChild(script);
    }
    
    getCsrfToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }
}

// ============================================
// ESTILOS COMPARTIDOS
// ============================================
const sharedStyles = document.createElement('style');
sharedStyles.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
`;
document.head.appendChild(sharedStyles);