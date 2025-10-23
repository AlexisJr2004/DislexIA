// game-alerts.js
// Módulo para mostrar alertas modales reutilizables en los juegos

function showNextGameAlert({ progreso, siguienteUrl }) {
    // Crear overlay
    let overlay = document.createElement('div');
    overlay.id = 'game-alert-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = 0;
    overlay.style.left = 0;
    overlay.style.width = '100vw';
    overlay.style.height = '100vh';
    overlay.style.background = 'rgba(0,0,0,0.4)';
    overlay.style.display = 'flex';
    overlay.style.alignItems = 'center';
    overlay.style.justifyContent = 'center';
    overlay.style.zIndex = 9999;

    // Crear modal
    let modal = document.createElement('div');
    modal.style.background = 'white';
    modal.style.borderRadius = '1.5rem';
    modal.style.boxShadow = '0 8px 32px rgba(0,0,0,0.18)';
    modal.style.padding = '2.5rem 2rem';
    modal.style.maxWidth = '90vw';
    modal.style.width = '400px';
    modal.style.textAlign = 'center';
    modal.innerHTML = `
        <div style="margin-bottom:1.5rem;">
            <svg width="48" height="48" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="color:#10b981;display:inline-block;">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        </div>
        <h2 style="font-size:1.5rem;font-weight:700;color:#111827;">¡Juego completado!</h2>
        <p style="color:#374151;margin:1rem 0 0.5rem;">Progreso: <b>${progreso.completadas}</b> / <b>${progreso.totales}</b> (<b>${progreso.porcentaje}%</b>)</p>
        <p style="color:#6b7280;">Avanzando al siguiente juego...</p>
        <div style="margin-top:2rem;">
            <div class="game-alert-bar" style="height:8px;width:100%;background:#f3f4f6;border-radius:4px;overflow:hidden;">
                <div id="game-alert-bar-fill" style="height:100%;width:0;background:#10b981;transition:width 2s;"></div>
            </div>
        </div>
    `;

    overlay.appendChild(modal);
    document.body.appendChild(overlay);

    // Animar barra de progreso
    setTimeout(() => {
        document.getElementById('game-alert-bar-fill').style.width = '100%';
    }, 100);

    // Redirigir tras 2 segundos
    setTimeout(() => {
        document.body.removeChild(overlay);
        window.location.href = siguienteUrl;
    }, 2000);
}

window.showNextGameAlert = showNextGameAlert;