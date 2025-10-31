/**
 * Juego: Completa la Palabra (Refactorizado)
 * Extiende BaseGame para reutilizar funcionalidad común
 */

class CompletaLaPalabraGame extends BaseGame {
    constructor(sessionData, gameConfig) {
        super(sessionData, gameConfig, 'Completa la Palabra');
    }
    
    createGameInterface() {
        const gameArea = document.getElementById('game-area');
        if (!gameArea) {
            console.error('❌ No se encontró el elemento #game-area');
            return;
        }

        // Usar GameUtils para construir la interfaz
        gameArea.innerHTML = `
            <div class="complete-word-game max-w-7xl mx-auto p-4">
                ${GameUtils.createGameHeader({
                    title: 'Completa la Palabra',
                    iconGradient: GameUtils.gradients.purple,
                    iconSvg: GameUtils.icons.edit,
                    currentQuestion: this.currentQuestionIndex + 1,
                    totalQuestions: this.getCurrentLevelQuestions().length,
                    score: this.score
                })}
                <!-- Barra de progreso -->
                <div class="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-3 mb-6 overflow-hidden">
                    <div id="progress-bar" class="h-3 bg-gradient-to-r from-green-400 to-blue-500 transition-all duration-300" style="width:0%"></div>
                </div>
                <div class="grid grid-cols-2 gap-6">
                    <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 transition-colors duration-200">
                        ${GameUtils.createTimerAndAttempts(this.currentQuestion?.time_limit || 30, this.attempts)}
                        ${GameUtils.createImageContainer()}
                        ${GameUtils.createHintPanel()}
                        <div class="text-center">
                            ${GameUtils.createHintButton('Ver palabra completa (-5 puntos)')}
                        </div>
                    </div>
                    <div class="space-y-6">
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 transition-colors duration-200">
                            <h3 class="text-center text-sm font-medium text-gray-700 dark:text-gray-300 mb-6">Completa la palabra</h3>
                            <div id="word-display" class="flex justify-center gap-3 mb-8 flex-wrap"></div>
                        </div>
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 transition-colors duration-200">
                            <h3 class="text-center text-sm font-medium text-gray-700 dark:text-gray-300 mb-6">Selecciona la letra correcta</h3>
                            <div id="options-container" class="grid grid-cols-4 gap-4"></div>
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

        // Limpiar mensaje de resultado anterior si existe
        const wordDisplayParent = document.getElementById('word-display')?.parentElement;
        if (wordDisplayParent) {
            const oldResultMsg = wordDisplayParent.querySelector('.mt-6.text-center.p-4.rounded-xl');
            if (oldResultMsg) oldResultMsg.remove();
        }

        // Cargar imagen
        const imageEl = document.getElementById('question-image');
        imageEl.src = this.currentQuestion.image_path;
        imageEl.alt = this.currentQuestion.hint;

        // Mostrar pista
        document.getElementById('hint-text').textContent = this.currentQuestion.hint;

        // Actualizar contador de intentos
        this.updateAttemptsCounter();

        // Renderizar palabra incompleta
        this.renderWord();

        // Renderizar opciones
        this.renderOptions();
    }
    
    renderWord() {
        const container = document.getElementById('word-display');
        container.innerHTML = '';
        
        const word = this.currentQuestion.incomplete_word;
        
        word.split('').forEach((letter) => {
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
        this.updateAttemptsCounter();
        
        if (isCorrect) {
            this.handleCorrectAnswer(responseTime, selectedLetter);
            this.showCompleteWord(true);

            // Mostrar toast de éxito
            GameUtils.showToast('¡Correcto!', 'success');
            
            setTimeout(() => {
                this.proceedToNext();
            }, 2500);
        } else {
            const noMoreAttempts = this.handleIncorrectAnswer(selectedLetter, responseTime);

            // Mostrar toast de error
            GameUtils.showToast('Letra incorrecta', 'error');
            
            if (noMoreAttempts) {
                this.showCompleteWord(false);
                setTimeout(() => {
                    this.proceedToNext();
                }, 3000);
            } else {
                this.showErrorAnimationOnOption(selectedLetter);
            }
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
    }
    
    showErrorAnimationOnOption(selectedLetter) {
        const optionButtons = document.querySelectorAll('.option-btn');
        
        optionButtons.forEach(btn => {
            if (btn.dataset.letter === selectedLetter) {
                this.showErrorAnimation(btn);
            }
        });
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
    
    onTimeUp() {
        this.showCompleteWord(false);
    }
    
    // Métodos de personalización de UI
    getGameGradient() {
        return 'bg-gradient-to-r from-purple-500 to-pink-500';
    }
    
    getSuccessMessage() {
        return 'Excelente trabajo completando palabras';
    }
    
    getScoreCardClass() {
        return 'bg-purple-50 dark:bg-purple-900/30 border border-purple-200 dark:border-purple-800';
    }
    
    getScoreTextClass() {
        return 'text-purple-600 dark:text-purple-400';
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.gameSessionData !== 'undefined' && typeof window.gameConfig !== 'undefined') {
        window.gameInstance = new CompletaLaPalabraGame(window.gameSessionData, window.gameConfig);
        window.gameInstance.init();
    } else {
        console.error('❌ Faltan datos de sesión');
    }
});