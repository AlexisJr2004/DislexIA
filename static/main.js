// ============ Inicialización de la aplicación ============
document.addEventListener('DOMContentLoaded', function() {
    initializeApplication();
});

// Función principal de inicialización
function initializeApplication() {
    initializePreloader();
    initializeFontSettings();
    initializeFontFamilySettings();
    initializeLanguageSettings();
    
    // Precargar ejemplos en background
    loadExamplesData().catch(console.warn);
}

// Inicializa el preloader con animación de fade-out
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

// Función que simula la carga de datos de ejemplos
async function loadExamplesData() {
    return new Promise(resolve => {
        setTimeout(() => {
            console.log('Ejemplos cargados');
            resolve();
        }, 200);
    });
}

// ============ Sistema Global de Configuración de Fuentes ============
function initializeFontSettings() {
    'use strict';

    // Función para cargar y aplicar configuraciones de fuente
    function loadFontSettings() {
        // Cargar tamaño de fuente guardado
        const savedFontSize = localStorage.getItem('font-size-setting') || 'medium';
        
        // Aplicar clase al body
        document.body.classList.remove('font-size-small', 'font-size-medium', 'font-size-large', 'font-size-xlarge');
        
        if (savedFontSize !== 'medium') {
            document.body.classList.add(`font-size-${savedFontSize}`);
        }
        
        console.log(`Configuración de fuente aplicada: ${savedFontSize}`);
    }

    // Función global para cambiar tamaño de fuente programáticamente
    window.setFontSize = function(size) {
        const validSizes = ['small', 'medium', 'large', 'xlarge'];
        
        if (!validSizes.includes(size)) {
            console.error('Tamaño de fuente no válido:', size);
            return false;
        }
        
        // Guardar en localStorage
        localStorage.setItem('font-size-setting', size);
        
        // Aplicar inmediatamente
        document.body.classList.remove('font-size-small', 'font-size-medium', 'font-size-large', 'font-size-xlarge');
        
        if (size !== 'medium') {
            document.body.classList.add(`font-size-${size}`);
        }
        
        console.log(`Tamaño de fuente cambiado a: ${size}`);
        return true;
    };

    // Función global para obtener el tamaño de fuente actual
    window.getCurrentFontSize = function() {
        return localStorage.getItem('font-size-setting') || 'medium';
    };

    // Cargar configuraciones al inicializar
    loadFontSettings();

    // Escuchar cambios en localStorage desde otras pestañas
    window.addEventListener('storage', function(e) {
        if (e.key === 'font-size-setting') {
            loadFontSettings();
        }
    });
}

// ============ Sistema Global de Configuración de Familia de Fuentes ============
function initializeFontFamilySettings() {
    'use strict';

    // Función para cargar y aplicar familia de fuente
    function loadFontFamilySettings() {
        const savedFontFamily = localStorage.getItem('font-family-setting') || 'default';
        
        // Aplicar clase al body
        document.body.classList.remove('font-family-default', 'font-family-lexend', 'font-family-comic', 'font-family-opendyslexic');
        document.body.classList.add(`font-family-${savedFontFamily}`);
        
        console.log(`Familia de fuente aplicada: ${savedFontFamily}`);
    }

    // Función global para cambiar familia de fuente programáticamente
    window.setFontFamily = function(family) {
        const validFamilies = ['default', 'lexend', 'comic', 'opendyslexic'];
        
        if (!validFamilies.includes(family)) {
            console.error('Familia de fuente no válida:', family);
            return false;
        }
        
        // Guardar en localStorage
        localStorage.setItem('font-family-setting', family);
        
        // Aplicar inmediatamente
        document.body.classList.remove('font-family-default', 'font-family-lexend', 'font-family-comic', 'font-family-opendyslexic');
        document.body.classList.add(`font-family-${family}`);
        
        console.log(`Familia de fuente cambiada a: ${family}`);
        return true;
    };

    // Función global para obtener la familia de fuente actual
    window.getCurrentFontFamily = function() {
        return localStorage.getItem('font-family-setting') || 'default';
    };

    // Función global para activar/desactivar fuente para dislexia
    window.setDyslexiaFont = function(enabled) {
        if (enabled) {
            // Activar OpenDyslexic por defecto
            window.setFontFamily('opendyslexic');
        } else {
            // Volver a la fuente por defecto
            window.setFontFamily('default');
        }
        
        console.log(`Fuente para dislexia: ${enabled ? 'ACTIVADA' : 'DESACTIVADA'}`);
        return true;
    };

    // Cargar configuraciones al inicializar
    loadFontFamilySettings();

    // Escuchar cambios en localStorage desde otras pestañas
    window.addEventListener('storage', function(e) {
        if (e.key === 'font-family-setting') {
            loadFontFamilySettings();
        }
    });
}

// ============ Sistema de persistencia de idioma ============
function initializeLanguageSettings() {
    'use strict';
    
    // Guardar idioma seleccionado en localStorage
    const languageForm = document.getElementById('languageForm');
    if (languageForm) {
        languageForm.addEventListener('submit', function(e) {
            const selectedLang = this.querySelector('button[type="submit"]:focus').value || this.querySelector('select[name="language"]')?.value;
            if (selectedLang) {
                localStorage.setItem('preferred-language', selectedLang);
                console.log(`Idioma cambiado a: ${selectedLang}`);
            }
        });
    }
    
    // Cargar idioma preferido
    const preferredLang = localStorage.getItem('preferred-language');
    const currentLang = document.documentElement.lang;
    
    if (preferredLang && preferredLang !== currentLang) {
        console.log(`Idioma preferido detectado: ${preferredLang}`);
    }
}

// ============ Sistema Global de Notificaciones Toast ============
/**
 * Sistema de notificaciones Toast moderno
 * Disponible globalmente en todas las páginas
 * Uso: mostrarToast('success', 'Mensaje aquí', 4000)
 */
(function initToastSystem() {
    'use strict';

    /**
     * Muestra una notificación toast
     * @param {string} tipo - Tipo de notificación: 'success', 'error', 'warning', 'info'
     * @param {string} mensaje - Mensaje a mostrar
     * @param {number} duracion - Duración en ms (0 = no auto-cerrar)
     */
    window.mostrarToast = function(tipo, mensaje, duracion = 4000) {
        const toast = document.getElementById('toast-notification');
        const icon = document.getElementById('toast-icon');
        const messageEl = document.getElementById('toast-message');

        if (!toast || !icon || !messageEl) {
            console.error('Elementos del toast no encontrados en el DOM');
            return;
        }

        // Configurar el icono y color según el tipo
        const configs = {
            'success': {
                className: 'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 bg-green-100 dark:bg-green-900/30',
                iconHTML: '<i class="fas fa-check text-green-600 dark:text-green-400"></i>'
            },
            'error': {
                className: 'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 bg-red-100 dark:bg-red-900/30',
                iconHTML: '<i class="fas fa-exclamation-circle text-red-600 dark:text-red-400"></i>'
            },
            'warning': {
                className: 'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 bg-yellow-100 dark:bg-yellow-900/30',
                iconHTML: '<i class="fas fa-exclamation-triangle text-yellow-600 dark:text-yellow-400"></i>'
            },
            'info': {
                className: 'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 bg-blue-100 dark:bg-blue-900/30',
                iconHTML: '<i class="fas fa-info-circle text-blue-600 dark:text-blue-400"></i>'
            }
        };

        const config = configs[tipo] || configs['info'];
        icon.className = config.className;
        icon.innerHTML = config.iconHTML;

        // Establecer el mensaje
        messageEl.textContent = mensaje;

        // Mostrar el toast
        toast.classList.remove('hidden');
        
        // Auto-ocultar después de la duración especificada
        if (duracion > 0) {
            setTimeout(() => {
                cerrarToast();
            }, duracion);
        }
    };

    /**
     * Cierra la notificación toast con animación
     */
    window.cerrarToast = function() {
        const toast = document.getElementById('toast-notification');
        if (!toast) return;

        toast.style.transition = 'all 0.3s ease-out';
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        
        setTimeout(() => {
            toast.classList.add('hidden');
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        }, 300);
    };

    /**
     * Procesa y muestra mensajes de Django desde el template
     * @param {Array} messages - Array de objetos {tags: string, message: string}
     */
    window.procesarMensajesDjango = function(messages) {
        if (!messages || messages.length === 0) return;
        
        messages.forEach((msg, index) => {
            setTimeout(() => {
                mostrarToast(msg.tags, msg.message);
            }, index * 500); // Delay entre mensajes múltiples
        });
    };

    console.log('✓ Sistema de Notificaciones Toast cargado correctamente');
})();


