/**
 * Juego: Selecciona la Palabra Correcta
 * Este juego presenta una imagen y 4 opciones de texto donde el usuario debe seleccionar la correcta
 */

class SeleccionaPalabraCorrectaGame extends BaseGame {
    constructor(sessionData, gameConfig) {
        super(sessionData, gameConfig, 'selecciona-palabra-correcta');
    }
    
    createGameInterface() {
        const gameArea = document.getElementById('game-area');
        if (!gameArea) {
            console.error('❌ No se encontró el elemento #game-area');
            return;
        }
        // Usar GameUtils para header y timer
        gameArea.innerHTML = `
            <div class="word-selection-game max-w-7xl mx-auto p-4">
                ${GameUtils.createGameHeader({
                    title: 'Selecciona la Palabra Correcta',
                    iconGradient: GameUtils.gradients.purple,
                    iconSvg: GameUtils.icons.puzzle,
                    currentQuestion: 1,
                    totalQuestions: 5,
                    score: 0
                })}
                <div class="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-3 mb-6 overflow-hidden">
                    <div id="progress-bar" class="h-3 bg-gradient-to-r from-green-400 to-blue-500 transition-all duration-300" style="width:0%"></div>
                </div>
                <div class="grid grid-cols-2 gap-6">
                    <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 transition-colors duration-200">
                        ${GameUtils.createTimerAndAttempts(30, 0)}
                        ${GameUtils.createImageContainer()}
                    </div>
                    <div class="space-y-6">
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 transition-colors duration-200">
                            <h3 id="question-text" class="text-center text-lg font-semibold text-gray-900 dark:text-white">
                                Selecciona la palabra correcta de acuerdo a la imagen
                            </h3>
                        </div>
                        <div class="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 transition-colors duration-200">
                            <div class="grid grid-cols-2 gap-4" id="options-container"></div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    bindEvents() {
        // No hay eventos globales, solo los de las opciones
    }

    renderQuestion() {
        if (!this.currentQuestion) return;
        document.getElementById('current-question').textContent = this.currentQuestionIndex + 1;
        const nivelActualEl = document.getElementById('nivel-actual');
        if (nivelActualEl) nivelActualEl.textContent = this.currentLevel;
        document.getElementById('total-questions').textContent = this.getCurrentLevelQuestions().length;
        document.getElementById('game-score').textContent = this.score;
        document.getElementById('question-timer').textContent = this.currentQuestion.time_limit;
        document.getElementById('attempts-counter').textContent = `${this.attempts}/3`;
        const imageEl = document.getElementById('question-image');
        imageEl.src = this.currentQuestion.image_path;
        imageEl.alt = `Imagen de ${this.currentQuestion.correct_answer}`;
        document.getElementById('question-text').textContent = this.currentQuestion.question;
        this.renderOptions();
    }
    
    renderOptions() {
        const container = document.getElementById('options-container');
        container.innerHTML = '';
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
            optionButton.addEventListener('click', () => this.selectOption(optionButton, option));
            container.appendChild(optionButton);
        });
    }
    
    selectOption(buttonEl, option) {
        if (!this.isGameActive) return;
        const responseTime = Date.now() - this.questionStartTime;
        const isCorrect = option.is_correct;
        this.disableAllOptions();
        if (isCorrect) {
            this.showCorrectAnimation(buttonEl);
            this.handleCorrectAnswer(responseTime, option);
            GameUtils.showToast('¡Correcto!', 'success');
        } else {
            this.showIncorrectAnimation(buttonEl);
            this.highlightCorrectAnswer();
            this.incorrectAnswers++;
            this.sendQuestionResponse(false, responseTime, option);
            this.updateScore();
            this.stopQuestionTimer();
            GameUtils.showToast('Incorrecto', 'error');
        }
        setTimeout(() => this.proceedToNext(), 1000);
    }
    
    disableAllOptions() {
        document.querySelectorAll('.option-button').forEach(btn => {
            btn.disabled = true;
            btn.classList.add('cursor-not-allowed');
            btn.classList.remove('hover:bg-gray-100', 'hover:border-gray-400', 'hover:shadow-md');
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
                        ${GameUtils.icons.check}
                        <span>${originalText}</span>
                    </div>
                `;
            }
        });
    }
    
    showCorrectAnimation(buttonEl) {
        buttonEl.className = `
            option-button p-5 bg-green-500 dark:bg-green-600 text-white border-2 border-green-600 dark:border-green-700
            rounded-xl transition-all duration-200 text-base font-semibold transform scale-105 shadow-lg
        `;
        const originalText = buttonEl.textContent;
        buttonEl.innerHTML = `
            <div class="flex items-center justify-center gap-2">
                ${GameUtils.icons.check}
                <span>${originalText}</span>
            </div>
        `;
    }
    
    showIncorrectAnimation(buttonEl) {
        buttonEl.className = `
            option-button p-5 bg-red-500 dark:bg-red-600 text-white border-2 border-red-600 dark:border-red-700
            rounded-xl transition-all duration-200 text-base font-semibold shadow-lg
        `;
        const originalText = buttonEl.textContent;
        buttonEl.innerHTML = `
            <div class="flex items-center justify-center gap-2">
                ${GameUtils.icons.cross}
                <span>${originalText}</span>
            </div>
        `;
    }
    
    onTimeUp() {
        this.disableAllOptions();
        this.highlightCorrectAnswer();
        document.querySelectorAll('.option-button').forEach(btn => {
            if (btn.dataset.isCorrect !== 'true') {
                btn.style.animation = 'fade-out 0.5s ease-in-out';
            }
        });
        GameUtils.showToast('¡Tiempo agotado!', 'warning');
    }
}

// Inicializar el juego cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    if (typeof window.gameSessionData !== 'undefined' && typeof window.gameConfig !== 'undefined') {
        window.gameInstance = new SeleccionaPalabraCorrectaGame(window.gameSessionData, window.gameConfig);
        window.gameInstance.init();
    } else {
        console.error('❌ Faltan datos de sesión o configuración del juego');
    }
});