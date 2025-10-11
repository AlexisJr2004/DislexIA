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


