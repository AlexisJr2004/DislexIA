<div align="center">
  <img src="static/img/favicon.ico" alt="DislexIA Logo" width="120" height="120">
  
  # DislexIA
  
  ### Tu neuropsicólogo amigo
  
  Una plataforma web interactiva diseñada para apoyar a personas con dislexia mediante juegos educativos, seguimiento de progreso y recursos digitales.

  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
  [![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
  [![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
  [![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

</div>

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Características](#-características)
- [Cumplimiento GDPR](#-cumplimiento-gdpr)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Módulos Principales](#-módulos-principales)
- [Capturas de Pantalla](#-capturas-de-pantalla)
- [Contribución](#-contribución)
- [Licencia](#-licencia)
- [Contacto](#-contacto)

---

## 🎯 Descripción

**DislexIA** es una plataforma web educativa especializada en el apoyo a personas con dislexia. El sistema ofrece una experiencia integral que combina:

- 🎮 Juegos interactivos diseñados específicamente para mejorar habilidades cognitivas
- 📊 Dashboard con análisis detallado del progreso del usuario
- 📅 Sistema de calendario para seguimiento de actividades diarias
- 📚 Biblioteca de recursos digitales descargables
- ⚙️ Panel de configuración personalizable
- 💬 Centro de soporte con FAQ y múltiples canales de contacto

El proyecto está diseñado con una arquitectura modular que facilita la navegación mediante Single Page Application (SPA), ofreciendo una experiencia fluida sin recargas de página.

---

## ✨ Características

### 🎮 Juegos de Entrenamiento

- **Quiz Interactivo**: Preguntas de opción múltiple para practicar comprensión lectora
- **Búsqueda de Palabras**: Sopa de letras para mejorar reconocimiento visual
- **Ordenar Oraciones**: Ejercicios de sintaxis y gramática

Cada juego incluye:
- Sistema de puntuación y logros
- Seguimiento de progreso individual
- Niveles de dificultad adaptables
- Estadísticas detalladas de rendimiento

### 📊 Dashboard Inteligente

- Visualización de métricas de rendimiento
- Gráficos de progreso temporal
- Indicadores de cursos completados
- Tracker de tiempo de práctica
- Lista de tareas y notas
- Estado de actividades

### 📅 Calendario de Actividades

- Vista mensual interactiva
- Registro de sesiones de entrenamiento
- Estadísticas rápidas (sesiones, tiempo, puntos)
- Modal para agregar nuevas actividades
- Historial completo de ejercicios realizados

### 📚 Biblioteca de Recursos

- Guías descargables en PDF
- Hojas de trabajo (worksheets)
- Herramientas de seguimiento de progreso
- Material educativo categorizado
- Sistema de filtrado y búsqueda
- Estadísticas de recursos más descargados

### ⚙️ Configuración Personalizable

- **Preferencias de usuario**: Idioma, tema, zona horaria
- **Accesibilidad**: Tamaño de fuente, comandos de voz, alto contraste
- **Notificaciones**: Recordatorios, logros, actualizaciones
- **Privacidad**: Control de datos y visibilidad de perfil

---

## 🔒 Cumplimiento GDPR

**DislexIA cumple al 100% con el Reglamento General de Protección de Datos (GDPR)**

[![GDPR Compliant](https://img.shields.io/badge/GDPR-Compliant-success)](GDPR_README.md)
[![Privacy](https://img.shields.io/badge/Privacy-Protected-blue)](templates/legal/privacy_policy.html)

### ✅ Implementaciones GDPR

- **Consentimiento Explícito** (Art. 6 & 7): Checkbox obligatorio en registro
- **Protección de Menores** (Art. 8): Consentimiento de tutores legales
- **Derecho al Olvido** (Art. 17): Eliminación permanente de cuenta
- **Portabilidad de Datos** (Art. 20): Exportación en formato JSON
- **Auditoría Completa** (Art. 30): Registro de todos los accesos
- **Seguridad Avanzada** (Art. 32): HTTPS, cookies seguras, cifrado
- **Política de Privacidad Completa** (Art. 13): Documentación legal detallada
- **Retención de Datos**: Políticas automáticas de limpieza

### 📄 Documentos Legales

- [Política de Privacidad](templates/legal/privacy_policy.html)
- [Términos y Condiciones](templates/legal/terms_conditions.html)
- [Guía Completa GDPR](GDPR_README.md)

### 🛡️ Características de Seguridad

- ✅ Cifrado SSL/TLS obligatorio en producción
- ✅ Contraseñas hasheadas con PBKDF2
- ✅ Cookies HTTP-only y Secure
- ✅ Protección CSRF y XSS
- ✅ Auditoría automática de accesos
- ✅ Logging de seguridad en archivos separados
- ✅ Sesiones con expiración configurable

**Para más información**: Consulta [GDPR_README.md](GDPR_README.md)

### 💬 Centro de Soporte

- Preguntas frecuentes (FAQ) con acordeón interactivo
- Contacto por WhatsApp
- Soporte por email
- Horarios de atención
- Recursos adicionales y guías

---

## 📁 Estructura del Proyecto

```
DislexIA/
│
├── index.html                    # Página principal (SPA container)
├── README.md                     # Documentación del proyecto
├── .env                         # Variables de entorno
├── .env.example                 # Ejemplo de variables de entorno
├── .gitignore                   # Archivos ignorados por Git
├── manage.py                    # Script de gestión Django
├── requirements.txt             # Dependencias Python
│
├── static/                      # Archivos estáticos
│   ├── main.js                 # JavaScript principal
│   ├── style.css               # Estilos globales
│   └── img/                    # Imágenes y recursos gráficos
│       ├── favicon.ico
│       ├── profile.png
│       └── carga.gif
│
├── templates/                   # Templates base
│   ├── base.html
│   ├── index.html
│   └── auth/                   # Templates de autenticación
│
├── pages/                       # Módulos de la aplicación
│   ├── dashboard.html          # Panel principal
│   ├── games.html              # Catálogo de juegos
│   ├── calendar.html           # Calendario de actividades
│   ├── documents.html          # Biblioteca de recursos
│   ├── profile.html            # Perfil de usuario
│   ├── settings.html           # Configuración
│   └── support.html            # Centro de soporte
│
├── games/                       # Juegos individuales
│   ├── quiz-interactivo.html
│   ├── buscar-palabras.html
│   └── ordenar-palabras.html
│
├── app/                         # Aplicación Django
│   ├── core/                   # App principal
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   ├── admin.py
│   │   ├── constants.py
│   │   └── migrations/
│   │
│   ├── dashboard/              # Módulo dashboard
│   └── games/                  # Módulo juegos
│
├── config/                      # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
└── media/                       # Archivos subidos por usuarios
    ├── games/
    └── profesionales/
```

---

## 🛠️ Tecnologías Utilizadas

### Frontend
- **HTML5**: Estructura semántica
- **CSS3**: Estilos y animaciones
- **JavaScript (ES6+)**: Lógica de aplicación
- **Tailwind CSS**: Framework de utilidades CSS
- **Font Awesome**: Iconografía

### Backend (Preparado para Django)
- **Python**: Lenguaje de programación
- **Django**: Framework web
- **SQLite/PostgreSQL**: Base de datos

### Herramientas y Librerías
- **SPA Router**: Navegación sin recarga de página
- **IIFE Pattern**: Encapsulación de código JavaScript
- **Responsive Design**: Diseño adaptable a todos los dispositivos
- **Git**: Control de versiones

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes Python)
- Navegador web moderno (Chrome, Firefox, Edge)

### Pasos de Instalación

1. **Clonar el repositorio**

```bash
git clone https://github.com/tu-usuario/dislexia.git
cd dislexia
```

2. **Crear entorno virtual**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Ejecutar migraciones**

```bash
python manage.py migrate
```

6. **Crear superusuario**

```bash
python manage.py createsuperuser
```

7. **Iniciar servidor de desarrollo**

```bash
python manage.py runserver
```

8. **Abrir en navegador**

```
http://localhost:8000
```

---

## 💻 Uso

### Navegación Principal

La aplicación utiliza un sistema de navegación SPA (Single Page Application):

1. **Acceso al Dashboard**: Vista general del progreso y actividades
2. **Juegos**: Selecciona y juega los ejercicios interactivos
3. **Calendario**: Revisa tu historial y programa sesiones
4. **Recursos**: Descarga materiales educativos
5. **Perfil**: Visualiza y edita tu información personal
6. **Configuración**: Personaliza la experiencia de usuario
7. **Soporte**: Obtén ayuda y resuelve dudas

### Funcionalidades Clave

#### Jugar un Juego

```javascript
// Los juegos se cargan dinámicamente
1. Click en "Juegos" en el sidebar
2. Selecciona un juego de la galería
3. El juego se carga en la misma página
4. Completa el ejercicio
5. Revisa tu puntuación y estadísticas
```

#### Registrar Actividad

```javascript
// Desde el calendario
1. Click en "Calendario"
2. Selecciona una fecha
3. Click en "Nueva Actividad"
4. Completa el formulario
5. Guarda la actividad
```

#### Descargar Recursos

```javascript
// Desde la biblioteca
1. Click en "Recursos Digitales"
2. Usa filtros o búsqueda
3. Click en "Download" del recurso deseado
4. El archivo se descarga automáticamente
```

---

## 📦 Módulos Principales

### 1. Sistema de Navegación SPA

El archivo [`index.html`](index.html) implementa un router personalizado:

```javascript
// Navegación dinámica sin recarga
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const page = this.getAttribute('data-page');
        loadPage(page);
    });
});
```

**Características:**
- Carga dinámica de contenido
- Gestión de estilos y scripts por página
- Historial de navegación
- Transiciones suaves

### 2. Sistema de Juegos

Ubicación: [`pages/games.html`](pages/games.html)

**Componentes:**
- Galería de juegos con filtros
- Sistema de búsqueda
- Tarjetas interactivas con información
- Estadísticas de progreso

### 3. Calendario de Actividades

Ubicación: [`pages/calendar.html`](pages/calendar.html)

**Funcionalidades:**
- Renderizado dinámico del calendario
- Gestión de actividades por fecha
- Estadísticas mensuales
- Modal de creación de actividades

### 4. Dashboard Analítico

Ubicación: [`pages/dashboard.html`](pages/dashboard.html)

**Componentes:**
- Gráficos de progreso
- Cards de métricas
- Time tracker
- Lista de tareas
- Status tracker

### 5. Biblioteca de Recursos

Ubicación: [`pages/documents.html`](pages/documents.html)

**Características:**
- Sistema de filtrado por categoría
- Búsqueda de recursos
- Descargas simuladas
- Estadísticas de biblioteca

---

## 📸 Capturas de Pantalla

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)
*Vista principal con métricas y gráficos de progreso*

### Juegos
![Juegos](docs/screenshots/games.png)
*Catálogo interactivo de juegos educativos*

### Calendario
![Calendario](docs/screenshots/calendar.png)
*Sistema de seguimiento de actividades diarias*

### Recursos
![Recursos](docs/screenshots/resources.png)
*Biblioteca de materiales descargables*

---

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Si deseas colaborar:

1. **Fork** el proyecto
2. Crea una **rama** para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. Abre un **Pull Request**

### Guías de Estilo

- **HTML**: Usar indentación de 4 espacios
- **CSS**: Seguir convenciones de Tailwind CSS
- **JavaScript**: Usar ES6+, IIFE para encapsulación
- **Python**: Seguir PEP 8

### Áreas de Mejora

- [ ] Implementar más juegos educativos
- [ ] Agregar sistema de logros y recompensas
- [ ] Desarrollar API REST completa
- [ ] Integrar sistema de autenticación
- [ ] Añadir tests unitarios y de integración
- [ ] Implementar modo offline (PWA)
- [ ] Agregar soporte multiidioma
- [ ] Desarrollar versión móvil nativa

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

```
MIT License

Copyright (c) 2024 DislexIA

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions...
```

---

## 👥 Contacto

**Equipo DislexIA**

- 📧 Email: [soporte@dislexia.com](mailto:soporte@dislexia.com)
- 💬 WhatsApp: +593 99 999 9999
- 🌐 Website: [www.dislexia.com](https://www.dislexia.com)
- 📍 Ubicación: Guayaquil, Ecuador

**Desarrollador Principal**

- 👨‍💻 Dr. Alexis Durán
- 📧 [snietod@unemi.edu.ec](mailto:snietod@unemi.edu.ec)

---

## 🙏 Agradecimientos

- A la comunidad de desarrolladores open source
- A los profesionales de neuropsicología que asesoraron el proyecto
- A las familias y usuarios que han probado y mejorado la plataforma
- A los contribuidores del proyecto

---

## 📚 Documentación Adicional

- [Guía de Usuario](docs/user-guide.md)
- [Documentación de API](docs/api-docs.md)
- [Guía de Desarrollo](docs/dev-guide.md)
- [Changelog](CHANGELOG.md)

---

<div align="center">
  
  **Hecho con ❤️ para la comunidad con dislexia**
  
  ⭐ Si este proyecto te ayuda, considera darle una estrella en GitHub
  
</div>