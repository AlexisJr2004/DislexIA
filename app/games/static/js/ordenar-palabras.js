/**
 * Juego: Ordenar Palabras (Refactorizado)
 * Extiende BaseGame para reutilizar funcionalidad común
 */

class OrdenarPalabrasGame extends BaseGame {
    constructor(sessionData, gameConfig) {
        super(sessionData, gameConfig, 'Ordenar Palabras');
        
        // Estado específico del juego
        this.selectedLetters = [];
        this.availableLetters = [];
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
                ${GameUtils.createGameHeader({
                    title: 'Ordenar Palabras',
                    iconGradient: 'from-blue-500 to-cyan-500',
                    iconSvg: `
                        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                        </svg>
                    `
                })}

                <!-- Contenedor de dos columnas -->
                <div class="grid grid-cols-2 gap-6">
                    <!-- COLUMNA IZQUIERDA - Imagen y timer/intentos -->
                    <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 transition-colors duration-200">
                        ${GameUtils.createTimerAndAttempts(45)}
                        ${GameUtils.createImageContainer()}
                        ${GameUtils.createHintPanel()}
                        ${GameUtils.createHintButton('Ver palabra completa (-5 puntos)')}
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
        
        // Inicializar letras para este juego
        this.selectedLetters = [];
        this.availableLetters = this.shuffleArray([...this.currentQuestion.scrambled_letters]);
        
        this.renderQuestion();
        this.startQuestionTimer();
        this.updateProgress();
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
        
        // Actualizar contador de intentos
        this.updateAttemptsCounter();
        
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
        this.updateAttemptsCounter();
        
        if (isCorrect) {
            this.handleCorrectAnswer(responseTime, formedWord);
            this.showSuccessAnimation();
            
            setTimeout(() => {
                this.proceedToNext();
            }, 2000);
        } else {
            const noMoreAttempts = this.handleIncorrectAnswer(formedWord, responseTime);
            
            if (noMoreAttempts) {
                this.showCorrectWord();
                setTimeout(() => {
                    this.proceedToNext();
                }, 3000);
            } else {
                this.showErrorAnimation();
                
                // Reordenar letras si está configurado
                if (this.gameConfig.game_mechanics?.shuffle_on_wrong) {
                    setTimeout(() => {
                        this.clearWord();
                        this.availableLetters = this.shuffleArray(this.availableLetters);
                        this.renderAvailableLetters();
                    }, 500);
                }
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
                ${GameUtils.icons.check}
                <p class="text-xl font-bold text-green-700 dark:text-green-300">¡Correcto!</p>
                <p class="text-sm text-green-600 dark:text-green-400 mt-1">${this.currentQuestion.correct_word}</p>
            </div>
        `;
    }
    
    showErrorAnimation() {
        const wordBuilder = document.getElementById('word-builder');
        
        wordBuilder.innerHTML = `
            <div class="text-center p-4 bg-red-50 dark:bg-red-900/30 rounded-lg border-2 border-red-500 dark:border-red-600 animate-shake">
                ${GameUtils.icons.cross}
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
    
    onTimeUp() {
        this.showCorrectWord();
    }
    
    // Métodos de personalización de UI
    getGameGradient() {
        return 'bg-gradient-to-r from-blue-500 to-cyan-500';
    }
    
    getSuccessIcon() {
        return `
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
        `;
    }
    
    getSuccessMessage() {
        return 'Excelente trabajo ordenando palabras';
    }
    
    getScoreCardClass() {
        return 'bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800';
    }
    
    getScoreTextClass() {
        return 'text-blue-600 dark:text-blue-400';
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.gameSessionData !== 'undefined' && typeof window.gameConfig !== 'undefined') {
        window.gameInstance = new OrdenarPalabrasGame(window.gameSessionData, window.gameConfig);
        window.gameInstance.init();
    } else {
        console.error('❌ Faltan datos de sesión');
    }
});