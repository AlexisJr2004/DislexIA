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
        // Agregar totales generales
        this.totalCorrectAnswers = 0;
        this.totalIncorrectAnswers = 0;
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
            <div class="word-selection-game max-w-7xl mx-auto p-4">
                <!-- Encabezado del juego -->
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 mb-6 transition-colors duration-200">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-3">
                            <div class="w-12 h-12 bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
                                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                            <div>
                                <h2 class="text-xl font-bold text-gray-900 dark:text-white">Selecciona la Palabra Correcta</h2>
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
                    <!-- COLUMNA IZQUIERDA - Imagen y timer -->
                    <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 transition-colors duration-200">
                        <!-- Timer -->
                        <div class="flex justify-center mb-6">
                            <div class="inline-flex items-center gap-2 bg-orange-50 dark:bg-orange-900/30 text-orange-600 dark:text-orange-400 px-4 py-2 rounded-lg border border-orange-200 dark:border-orange-800">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span id="question-timer" class="font-semibold">30</span>
                                <span class="text-sm">segundos</span>
                            </div>
                        </div>
                        
                        <!-- Imagen -->
                        <div class="flex justify-center">
                            <div class="relative">
                                <img id="question-image" 
                                    src="" 
                                    alt="Imagen de la palabra" 
                                    class="w-80 h-64 object-contain rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 shadow-sm">
                            </div>
                        </div>
                    </div>

                    <!-- COLUMNA DERECHA - Pregunta y opciones -->
                    <div class="space-y-6">
                        <!-- Pregunta -->
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 transition-colors duration-200">
                            <h3 id="question-text" class="text-center text-lg font-semibold text-gray-900 dark:text-white">
                                Selecciona la palabra correcta de acuerdo a la imagen
                            </h3>
                        </div>
                        
                        <!-- Opciones de respuesta -->
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 transition-colors duration-200">
                            <div class="grid grid-cols-2 gap-4" id="options-container">
                                <!-- Las opciones se generan dinámicamente -->
                            </div>
                        </div>
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
                option-button p-5 bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 
                border-2 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600 
                rounded-xl transition-all duration-200 text-base font-medium text-gray-900 dark:text-white
                focus:outline-none focus:ring-2 focus:ring-purple-500 hover:shadow-md
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
                btn.className = `
                    option-button p-5 bg-green-50 dark:bg-green-900/30 border-2 border-green-500 dark:border-green-600
                    text-green-800 dark:text-green-300 rounded-xl text-base font-semibold shadow-sm
                `;
                const originalText = btn.textContent;
                btn.innerHTML = `
                    <div class="flex items-center justify-center gap-2">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                        </svg>
                        <span>${originalText}</span>
                    </div>
                `;
            }
        });
    }
    
    showCorrectAnimation(buttonEl) {
        // Limpiar estilos previos y aplicar animación de respuesta correcta
        buttonEl.className = `
            option-button p-5 bg-green-500 dark:bg-green-600 text-white border-2 border-green-600 dark:border-green-700
            rounded-xl transition-all duration-200 text-base font-semibold transform scale-105 shadow-lg
        `;
        
        // Mostrar checkmark temporal
        const originalText = buttonEl.textContent;
        buttonEl.innerHTML = `
            <div class="flex items-center justify-center gap-2">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <span>${originalText}</span>
            </div>
        `;
    }
    
    showIncorrectAnimation(buttonEl) {
        // Limpiar estilos previos y aplicar animación de respuesta incorrecta
        buttonEl.className = `
            option-button p-5 bg-red-500 dark:bg-red-600 text-white border-2 border-red-600 dark:border-red-700
            rounded-xl transition-all duration-200 text-base font-semibold shadow-lg
        `;
        
        // Mostrar X temporal
        const originalText = buttonEl.textContent;
        buttonEl.innerHTML = `
            <div class="flex items-center justify-center gap-2">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
                <span>${originalText}</span>
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
        this.loadCurrentQuestion();
    }
    
    finishLevel() {
        this.isGameActive = false;
        // Acumular totales antes de mostrar resultados
        this.totalCorrectAnswers += this.correctAnswers;
        this.totalIncorrectAnswers += this.incorrectAnswers;
        this.showLevelResults();
    }
    
    showLevelResults() {
        const questions = this.getCurrentLevelQuestions();
        const totalQuestions = questions.length;
        const accuracy = Math.round((this.correctAnswers / totalQuestions) * 100);
        
        const gameArea = document.getElementById('game-area');
        gameArea.innerHTML = `
            <div class="level-results max-w-3xl mx-auto">
                <!-- Encabezado de resultados -->
                <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 mb-6 transition-colors duration-200">
                    <div class="text-center mb-6">
                        <div class="w-20 h-20 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                            </svg>
                        </div>
                        <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">¡Nivel ${this.currentLevel} Completado!</h2>
                        <p class="text-gray-500 dark:text-gray-400">Excelente trabajo, aquí están tus resultados</p>
                    </div>
                    
                    <hr class="bg-gray-200 dark:bg-gray-700 my-6">
                    
                    <!-- Estadísticas -->
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div class="bg-purple-50 dark:bg-purple-900/30 border border-purple-200 dark:border-purple-800 rounded-xl p-4 text-center">
                            <div class="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-1">${this.score}</div>
                            <div class="text-xs font-medium text-gray-600 dark:text-gray-400">Puntos Totales</div>
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
                
                <!-- Botones de acción -->
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
            // Mostrar mensaje de finalización completa del juego con totales generales
            setTimeout(() => {
                alert('🎉 ¡Felicidades! Has completado todos los niveles disponibles.\n\n' +
                      `✨ Puntuación final: ${this.score} puntos\n` +
                      `🎯 Niveles completados: ${this.currentLevel - 1}\n` +
                      `✅ Total de aciertos: ${this.totalCorrectAnswers}\n` +
                      `❌ Total de errores: ${this.totalIncorrectAnswers}`);
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
        // Actualizar el puntaje en el encabezado del juego
        const gameScoreEl = document.getElementById('game-score');
        if (gameScoreEl) {
            gameScoreEl.textContent = this.score;
        }
        
        // Actualizar el puntaje en el panel lateral
        const puntajeActualEl = document.getElementById('puntaje-actual');
        if (puntajeActualEl) {
            puntajeActualEl.textContent = this.score;
            // Animación de actualización
            puntajeActualEl.style.animation = 'pulse 0.3s ease-in-out';
            setTimeout(() => {
                puntajeActualEl.style.animation = '';
            }, 300);
        }
        
        // Llamar a la función global si existe
        if (typeof window.updateScore === 'function') {
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
            total_correct: this.totalCorrectAnswers,
            total_incorrect: this.totalIncorrectAnswers,
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
