/**
 * Juego: Selecciona la Palabra Correcta
 * Este juego presenta una imagen y 4 opciones de texto donde el usuario debe seleccionar la correcta
 */

class SeleccionaPalabraCorrectaGame {
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
        this.selectedQuestions = null; // Para almacenar las preguntas aleatorias del nivel actual
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
            <div class="word-selection-game">
                <!-- Encabezado del juego -->
                <div class="game-header bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 rounded-lg mb-6">
                    <div class="flex justify-between items-center">
                        <div>
                            <h2 class="text-2xl font-bold mb-2">🎯 Selecciona la Palabra Correcta</h2>
                            <p class="text-purple-100">Nivel ${this.currentLevel} - Pregunta <span id="current-question">1</span> de <span id="total-questions">5</span></p>
                            <p class="text-purple-200 text-sm mt-1">🎲 Ejercicios seleccionados aleatoriamente</p>
                        </div>
                        <div class="text-right">
                            <div class="text-3xl font-bold" id="game-score">${this.score}</div>
                            <div class="text-sm text-purple-200">Puntos</div>
                        </div>
                    </div>
                </div>
                
                <!-- Progreso -->
                <div class="progress-bar bg-gray-200 rounded-full h-3 mb-6">
                    <div class="progress-fill bg-gradient-to-r from-green-400 to-blue-500 h-3 rounded-full transition-all duration-500" 
                         style="width: 0%" id="progress-bar"></div>
                </div>
                
                <!-- Área de la pregunta -->
                <div class="question-area bg-white rounded-xl shadow-lg p-8 mb-6">
                    <div class="text-center">
                        <!-- Timer -->
                        <div class="timer-container mb-4">
                            <div class="inline-flex items-center gap-2 bg-orange-100 text-orange-800 px-4 py-2 rounded-full">
                                <i class="fas fa-clock"></i>
                                <span id="question-timer">30</span>s
                            </div>
                        </div>
                        
                        <!-- Imagen -->
                        <div class="image-container mb-6">
                            <img id="question-image" 
                                 src="" 
                                 alt="Imagen de la palabra" 
                                 class="mx-auto max-w-xs h-48 object-contain rounded-lg border-4 border-gray-200 shadow-md">
                        </div>
                        
                        <!-- Pregunta -->
                        <h3 id="question-text" class="text-xl font-semibold text-gray-800 mb-6">
                            Selecciona la palabra correcta de acuerdo a la imagen.
                        </h3>
                    </div>
                </div>
                
                <!-- Opciones de respuesta -->
                <div class="options-area">
                    <div class="grid grid-cols-2 gap-4" id="options-container">
                        <!-- Las opciones se generan dinámicamente -->
                    </div>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        // No necesitamos eventos para botones ya que el juego continúa automáticamente
    }
    
    startGame() {
        this.isGameActive = true;
        this.loadCurrentQuestion();
    }
    
    getCurrentLevelQuestions() {
        const level = this.gameConfig.levels.find(l => l.level === this.currentLevel);
        if (!level || !level.questions) return [];
        
        // Si no hemos seleccionado preguntas para este nivel, hacerlo ahora
        if (!this.selectedQuestions || this.selectedQuestions.level !== this.currentLevel) {
            this.selectedQuestions = {
                level: this.currentLevel,
                questions: this.getRandomQuestions(level.questions, 5)
            };
        }
        
        return this.selectedQuestions.questions;
    }
    
    // Función para seleccionar preguntas aleatorias
    getRandomQuestions(questions, count) {
        // Crear una copia del array para no modificar el original
        const shuffled = [...questions];
        
        // Algoritmo Fisher-Yates para mezclar aleatoriamente
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        
        // Retornar solo la cantidad solicitada
        const selected = shuffled.slice(0, Math.min(count, shuffled.length));        
        return selected;
    }
    
    // Función para mezclar un array (algoritmo Fisher-Yates)
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
        
        this.renderQuestion();
        this.startQuestionTimer();
        this.updateProgress();
    }
    
    renderQuestion() {
        if (!this.currentQuestion) return;
        
        // Actualizar contador de preguntas
        document.getElementById('current-question').textContent = this.currentQuestionIndex + 1;
        
        // Cargar imagen
        const imageEl = document.getElementById('question-image');
        imageEl.src = this.currentQuestion.image_path;
        imageEl.alt = `Imagen de ${this.currentQuestion.correct_answer}`;
        
        // Cargar pregunta
        document.getElementById('question-text').textContent = this.currentQuestion.question;
        
        // Generar opciones
        this.renderOptions();
    }
    
    renderOptions() {
        const container = document.getElementById('options-container');
        container.innerHTML = '';
        
        // Crear una copia de las opciones y mezclarlas aleatoriamente
        const shuffledOptions = this.shuffleArray([...this.currentQuestion.options]);
        
        shuffledOptions.forEach((option, index) => {
            const optionButton = document.createElement('button');
            optionButton.className = `
                option-button p-4 bg-gray-50 hover:bg-gray-100 border-2 border-gray-300 
                hover:border-gray-400 rounded-lg transition-all duration-200 text-lg font-medium
                focus:outline-none focus:ring-2 focus:ring-gray-400 hover:shadow-md
            `;
            optionButton.textContent = option.text;
            optionButton.dataset.optionIndex = index;
            optionButton.dataset.isCorrect = option.is_correct;
            optionButton.dataset.confusionType = option.confusion_type || '';
            
            optionButton.addEventListener('click', () => {
                this.selectOption(optionButton, option);
            });
            
            container.appendChild(optionButton);
        });
    }
    
    selectOption(buttonEl, option) {
        if (!this.isGameActive) return;
        
        const responseTime = Date.now() - this.questionStartTime;
        const isCorrect = option.is_correct;
        
        // Deshabilitar todas las opciones
        this.disableAllOptions();
        
        // Mostrar animación de respuesta
        if (isCorrect) {
            this.correctAnswers++;
            
            // Calcular puntos (base + bonus por tiempo)
            const timeBonus = Math.max(0, this.currentQuestion.time_limit - Math.floor(responseTime / 1000));
            const points = this.currentQuestion.points + (timeBonus * this.gameConfig.scoring.time_bonus);
            this.score += points;
            
            // Animación de respuesta correcta
            this.showCorrectAnimation(buttonEl);
        } else {
            this.incorrectAnswers++;
            
            // Animación de respuesta incorrecta y mostrar respuesta correcta
            this.showIncorrectAnimation(buttonEl);
            this.highlightCorrectAnswer();
        }
        
        // Enviar datos de la respuesta al backend
        this.sendQuestionResponse(isCorrect, responseTime, option);
        
        // Actualizar UI
        this.updateScore();
        this.stopQuestionTimer();
        
        // Continuar automáticamente después de la animación
        setTimeout(() => {
            this.proceedToNext();
        }, 1000);
    }
    
    disableAllOptions() {
        document.querySelectorAll('.option-button').forEach(btn => {
            btn.disabled = true;
            btn.classList.add('cursor-not-allowed');
            // Remover efectos de hover para opciones deshabilitadas
            btn.classList.remove('hover:bg-gray-100', 'hover:border-gray-400', 'hover:shadow-md');
            
            // Si no es la opción seleccionada ni la correcta, aplicar estilo deshabilitado
            if (!btn.classList.contains('bg-green-500') && !btn.classList.contains('bg-red-500') && !btn.classList.contains('bg-green-100')) {
                btn.classList.add('opacity-50', 'bg-gray-100');
            }
        });
    }
    
    highlightCorrectAnswer() {
        document.querySelectorAll('.option-button').forEach(btn => {
            if (btn.dataset.isCorrect === 'true') {
                btn.classList.remove('bg-gray-50', 'bg-gray-100', 'border-gray-300', 'border-gray-400');
                btn.classList.add('bg-green-100', 'border-green-500', 'text-green-800', 'font-semibold');
                btn.innerHTML = `<i class="fas fa-check-circle mr-2 text-green-600"></i>${btn.textContent}`;
            }
        });
    }
    
    showCorrectAnimation(buttonEl) {
        // Limpiar estilos previos y aplicar animación de respuesta correcta
        buttonEl.classList.remove('bg-gray-50', 'bg-gray-100', 'border-gray-300', 'border-gray-400');
        buttonEl.classList.add('bg-green-500', 'text-white', 'border-green-600', 'transform', 'scale-105', 'shadow-lg');
        
        // Crear efecto de pulso
        buttonEl.style.animation = 'pulse 0.6s ease-in-out';
        
        // Mostrar checkmark temporal
        const originalText = buttonEl.textContent;
        buttonEl.innerHTML = `<i class="fas fa-check-circle mr-2"></i>${originalText}`;
    }
    
    showIncorrectAnimation(buttonEl) {
        // Limpiar estilos previos y aplicar animación de respuesta incorrecta
        buttonEl.classList.remove('bg-gray-50', 'bg-gray-100', 'border-gray-300', 'border-gray-400');
        buttonEl.classList.add('bg-red-500', 'text-white', 'border-red-600', 'shadow-lg');
        
        // Crear efecto de shake
        buttonEl.style.animation = 'shake 0.6s ease-in-out';
        
        // Mostrar X temporal
        const originalText = buttonEl.textContent;
        buttonEl.innerHTML = `<i class="fas fa-times-circle mr-2"></i>${originalText}`;
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
            <div class="level-results text-center">
                <div class="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-8 rounded-xl mb-6">
                    <h2 class="text-3xl font-bold mb-4">🎉 ¡Nivel ${this.currentLevel} Completado!</h2>
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div class="bg-white bg-opacity-20 rounded-lg p-4">
                            <div class="text-2xl font-bold">${this.score}</div>
                            <div class="text-sm">Puntos Totales</div>
                        </div>
                        <div class="bg-white bg-opacity-20 rounded-lg p-4">
                            <div class="text-2xl font-bold text-green-300">${this.correctAnswers}</div>
                            <div class="text-sm">Aciertos</div>
                        </div>
                        <div class="bg-white bg-opacity-20 rounded-lg p-4">
                            <div class="text-2xl font-bold text-red-300">${this.incorrectAnswers}</div>
                            <div class="text-sm">Errores</div>
                        </div>
                        <div class="bg-white bg-opacity-20 rounded-lg p-4">
                            <div class="text-2xl font-bold text-yellow-300">${accuracy}%</div>
                            <div class="text-sm">Precisión</div>
                        </div>
                    </div>
                </div>
                
                <div class="flex gap-4 justify-center">
                    <button id="btn-next-level" class="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors">
                        <i class="fas fa-arrow-up mr-2"></i>
                        Siguiente Nivel
                    </button>
                    <button id="btn-finish-level" class="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors">
                        <i class="fas fa-stop mr-2"></i>
                        Finalizar Juego
                    </button>
                </div>
            </div>
        `;
        
        // Bind events para botones de resultados
        document.getElementById('btn-next-level')?.addEventListener('click', () => {
            this.nextLevel();
        });
        
        document.getElementById('btn-finish-level')?.addEventListener('click', () => {
            this.finishGame();
        });
        
        // Enviar resultados del nivel
        this.sendLevelResults();
    }
    
    nextLevel() {
        this.currentLevel++;
        this.currentQuestionIndex = 0;
        
        // Verificar si existe el siguiente nivel
        const nextLevel = this.gameConfig.levels.find(l => l.level === this.currentLevel);
        if (!nextLevel) {
            // Mostrar mensaje de finalización completa del juego
            setTimeout(() => {
                alert('🎉 ¡Felicidades! Has completado todos los niveles disponibles.\n\n' +
                      `✨ Puntuación final: ${this.score} puntos\n` +
                      `🎯 Niveles completados: ${this.currentLevel - 1}\n` +
                      `✅ Total de aciertos: ${this.correctAnswers}\n` +
                      `❌ Total de errores: ${this.incorrectAnswers}`);
                this.finishGame();
            }, 500);
            return;
        }
        
        // Reiniciar contadores de respuestas para el nuevo nivel
        this.correctAnswers = 0;
        this.incorrectAnswers = 0;
        
        // Limpiar las preguntas seleccionadas para forzar nueva selección aleatoria
        this.selectedQuestions = null;
        
        // Reiniciar interfaz para el nuevo nivel
        this.createGameInterface();
        this.bindEvents();
        this.startGame();
    }
    
    finishGame() {
        const totalTime = Math.floor((Date.now() - this.startTime) / 1000);
        
        // Enviar datos finales al backend
        this.sendGameResults(totalTime);
    }
    
    updateScore() {
        document.getElementById('game-score').textContent = this.score;
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
            
            if (timeLeft <= 5) {
                timerEl.parentElement.classList.add('bg-red-100', 'text-red-800');
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
        this.disableAllOptions();
        this.highlightCorrectAnswer();
        this.incorrectAnswers++;
        
        // Mostrar animación de tiempo agotado en todas las opciones
        document.querySelectorAll('.option-button').forEach(btn => {
            if (btn.dataset.isCorrect !== 'true') {
                btn.style.animation = 'fade-out 0.5s ease-in-out';
            }
        });
        
        // Enviar respuesta como incorrecta por tiempo
        this.sendQuestionResponse(false, this.currentQuestion.time_limit * 1000, null);
        
        // Continuar automáticamente después de mostrar la respuesta correcta
        setTimeout(() => {
            this.proceedToNext();
        }, 1000);
    }
    
    // API calls al backend
    async sendQuestionResponse(isCorrect, responseTime, selectedOption) {
        const data = {
            session_url: this.sessionData.url_sesion,
            question_id: this.currentQuestion.id,
            level: this.currentLevel,
            is_correct: isCorrect,
            response_time_ms: responseTime,
            selected_option: selectedOption ? selectedOption.text : null,
            confusion_type: selectedOption ? selectedOption.confusion_type : null,
            points_earned: isCorrect ? this.currentQuestion.points : 0
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
                console.error('❌ Error al enviar respuesta:', response.statusText);
                const errorText = await response.text();
                console.error('❌ Detalle del error:', errorText);
            } else {
                // Respuesta exitosa
                console.log('✅ Respuesta enviada correctamente');
            }
        } catch (error) {
            console.error('❌ Error de red al enviar respuesta:', error);
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
            const response = await fetch(this.sessionData.api_urls.level_complete, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                console.error('❌ Error al enviar resultados de nivel:', response.statusText);
                const errorText = await response.text();
                console.error('❌ Detalle del error:', errorText);
            } else {
                console.log('✅ Resultados de nivel enviados correctamente');
            }
        } catch (error) {
            console.error('❌ Error de red al enviar resultados:', error);
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
                alert(`Error del servidor (${response.status}): ${response.statusText}`);
                return;
            }
            
            const result = await response.json();
            
            if (result.success) {
                alert('¡Juego finalizado exitosamente!');
                window.location.href = this.sessionData.api_urls.game_list;
            } else {
                alert('Error al finalizar el juego: ' + result.error);
            }
        } catch (error) {
            console.error('❌ Error al finalizar juego:', error);
            if (error instanceof SyntaxError) {
                alert('Error: El servidor devolvió una respuesta inválida. Revisa la consola para más detalles.');
            } else {
                alert('Error de conexión al finalizar el juego');
            }
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

// Inicializar el juego cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Verificar que existan los datos necesarios (se pasan desde el template)
    if (typeof window.gameSessionData !== 'undefined' && typeof window.gameConfig !== 'undefined') {
        window.gameInstance = new SeleccionaPalabraCorrectaGame(window.gameSessionData, window.gameConfig);
    } else {
        console.error('❌ Faltan datos de sesión o configuración del juego');
    }
});
