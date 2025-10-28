/**
 * Juego: Encuentra el Error (Refactorizado)
 * Extiende BaseGame para reutilizar funcionalidad común
 */

class EncuentraElErrorGame extends BaseGame {
    constructor(sessionData, gameConfig) {
        super(sessionData, gameConfig, 'Encuentra el Error');
    }
    
    createGameInterface() {
        const gameArea = document.getElementById('game-area');
        if (!gameArea) {
            console.error('❌ No se encontró el elemento #game-area');
            return;
        }

        // Usar GameUtils para construir la interfaz
        gameArea.innerHTML = `
            <div class="find-error-game max-w-7xl mx-auto p-4">
                ${GameUtils.createGameHeader({
                    title: 'Encuentra el Error',
                    iconGradient: GameUtils.gradients.red,
                    iconSvg: GameUtils.icons.warning,
                    currentQuestion: this.currentQuestionIndex + 1,
                    totalQuestions: this.getCurrentLevelQuestions().length,
                    score: this.score
                })}
                <div class="grid grid-cols-2 gap-6">
                    <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 transition-colors duration-200">
                        ${GameUtils.createTimerAndAttempts(this.currentQuestion?.time_limit || 40, this.attempts)}
                        ${GameUtils.createImageContainer()}
                        ${GameUtils.createHintPanel()}
                        <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-center">
                            <p class="text-sm text-red-700 dark:text-red-300 font-medium">
                                <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                                Haz clic en la letra incorrecta
                            </p>
                        </div>
                        <div class="text-center mt-4">
                            ${GameUtils.createHintButton('Mostrar error (-5 puntos)')}
                        </div>
                    </div>
                    <div class="space-y-6">
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 transition-colors duration-200">
                            <h3 class="text-center text-sm font-medium text-gray-700 dark:text-gray-300 mb-6">Encuentra la letra incorrecta</h3>
                            <div id="word-display" class="flex justify-center gap-3 mb-8 flex-wrap"></div>
                            <div class="text-center text-xs text-gray-500 dark:text-gray-400">Haz clic en la letra que crees que está mal escrita</div>
                        </div>
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
        this.updateAttemptsCounter();
        
        if (isCorrect) {
            this.handleCorrectAnswer(responseTime, selectedIndex);
            this.showResult(true, selectedIndex);

            // Mostrar toast de éxito
            GameUtils.showToast('¡Correcto!', 'success');
            
            setTimeout(() => {
                this.proceedToNext();
            }, 3000);
        } else {
            const noMoreAttempts = this.handleIncorrectAnswer(selectedIndex, responseTime);

            // Mostrar toast de error
            GameUtils.showToast('Letra incorrecta', 'error');
            
            if (noMoreAttempts) {
                this.showResult(false, selectedIndex);
                setTimeout(() => {
                    this.proceedToNext();
                }, 4000);
            } else {
                this.showErrorAnimationOnLetter(selectedIndex);
            }
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
                    border-red-500 dark:border-red-600 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400
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
        correctWord.split('').forEach((letter) => {
            const letterBox = document.createElement('div');
            letterBox.className = `

                w-16 h-20 border-2 border-green-500 dark:border-green-600
                rounded-xl flex items-center justify-center text-3xl font-bold
                bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400
            `;
            letterBox.textContent = letter;
            correctLettersDiv.appendChild(letterBox);
        });
        correctDiv.appendChild(correctLettersDiv);
        container.appendChild(correctDiv);
    }

    showHint() {
        if (this.hintUsed) return;

        this.hintUsed = true;
        const hintBtn = document.getElementById('show-hint-btn');
        hintBtn.disabled = true;
        hintBtn.classList.add('opacity-50', 'cursor-not-allowed');

        // Descontar puntos inmediatamente
        this.score = Math.max(0, this.score - (this.gameConfig.scoring?.hint_penalty || 5));
        this.updateScore();

        // Mostrar la letra incorrecta resaltada temporalmente
        const container = document.getElementById('word-display');
        const word = this.currentQuestion.incorrect_word;
        const errorPosition = this.currentQuestion.error_position;
        const originalHTML = container.innerHTML;

        container.innerHTML = '';
        word.split('').forEach((letter, index) => {
            const letterBox = document.createElement('div');
            if (index === errorPosition) {
                letterBox.className = `
                    w-16 h-20 border-2 rounded-xl flex items-center justify-center text-3xl font-bold animate-pulse
                    border-red-500 dark:border-red-600 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400
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

        // Mensaje de penalización
        const msgDiv = document.createElement('div');
        msgDiv.className = 'mt-4 text-center text-xs text-red-600 dark:text-red-400';
        msgDiv.textContent = '-5 puntos de penalización';
        container.appendChild(msgDiv);

        setTimeout(() => {
            container.innerHTML = originalHTML;
            // Restaurar los botones y eventos correctamente
            this.renderWord();
        }, 3000);
    }

    showErrorAnimationOnLetter(selectedIndex) {
        const optionButtons = document.querySelectorAll('.letter-btn');
        optionButtons.forEach(btn => {
            if (parseInt(btn.dataset.index) === selectedIndex) {
                btn.classList.add('bg-red-100', 'dark:bg-red-900/50', 'border-red-500', 'dark:border-red-600');
                btn.style.animation = 'shake 0.5s';
                GameUtils.showToast('¡Intenta de nuevo!', 'error');
                setTimeout(() => {
                    btn.style.animation = '';
                    btn.classList.remove('bg-red-100', 'dark:bg-red-900/50', 'border-red-500', 'dark:border-red-600');
                }, 500);
            }
        });
    }

    onTimeUp() {
        this.showResult(false, null);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.gameSessionData !== 'undefined' && typeof window.gameConfig !== 'undefined') {
        window.gameInstance = new EncuentraElErrorGame(window.gameSessionData, window.gameConfig);
        window.gameInstance.init();
    } else {
        console.error('❌ Faltan datos de sesión');
    }
});