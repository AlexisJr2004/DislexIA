/**
 * Función principal de inicialización
 */
function initializeApplication() {
    initializePreloader();
    
    // Precargar ejemplos en background
    loadExamplesData().catch(console.warn);
}

/**
 * Inicializa el preloader con animación de fade-out
 */
function initializePreloader() {
    const pre = document.getElementById('preloader');
    if (!pre) return;
    
    setTimeout(() => {
        pre.classList.add('fade-out');
        setTimeout(() => { 
            pre.style.display = 'none'; 
        }, 450);
    }, 1000);
}

/**
 * Función que simula la carga de datos de ejemplos
 */
async function loadExamplesData() {
    // Simula carga de datos
    return new Promise(resolve => {
        setTimeout(() => {
            console.log('Ejemplos cargados');
            resolve();
        }, 500);
    });
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initializeApplication);


