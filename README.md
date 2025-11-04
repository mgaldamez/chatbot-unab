
# U-Tutor v5.0

U-Tutor v5.0 es un asistente educativo inteligente diseñado para ayudar a estudiantes con sus dudas académicas. La aplicación está construida con Python y utiliza tecnologías modernas para ofrecer una experiencia de aprendizaje interactiva y personalizada.

> **Nota:** A partir de v5.0, ejecuta la aplicación con: `streamlit run main.py`

## ✨ Funcionalidades Activas

### 🤖 Inteligencia Artificial Avanzada
- **Motor de IA:** Utiliza OpenAI GPT-4 para respuestas inteligentes y contextuales
- **Respuestas en Tiempo Real:** Las respuestas se muestran en streaming para una mejor experiencia de usuario
- **Validación de Mensajes:** Sistema de validación que previene spam y mensajes inválidos
- **Generación de Títulos Inteligentes:** Crea títulos automáticos para las conversaciones usando IA

### 🎨 Personalización del Asistente
- **Control de Creatividad:** Ajusta la temperatura (0.0-1.0) para respuestas más creativas o conservadoras
- **Personalidades Múltiples:** 
  - **Profesional:** Explicaciones formales y académicas
  - **Amigable:** Estilo cercano con ejemplos de la vida cotidiana
  - **Conciso:** Respuestas directas y precisas
  - **Detallado:** Explicaciones exhaustivas con múltiples ejemplos

### 🔊 Funcionalidades de Audio
- **Texto a Voz Optimizado:** Convierte respuestas a audio usando TTS local (pyttsx3) para máxima velocidad
- **Respaldo con gTTS:** Sistema de respaldo con Google Text-to-Speech para compatibilidad
- **Caché de Audio:** Sistema inteligente que guarda el audio generado para reproducción instantánea
- **Múltiples Idiomas:** Soporte para español e inglés
- **Indicadores de Rendimiento:** Muestra el tiempo de generación y el tamaño de los archivos

### 💾 Gestión de Conversaciones
- **Base de Datos SQLite:** Almacenamiento persistente de todas las conversaciones
- **Historial Completo:** Acceso a conversaciones anteriores con búsqueda
- **Gestión Avanzada:** Crear, editar títulos, eliminar y exportar conversaciones
- **Búsqueda Inteligente:** Busca conversaciones por título
- **Context Managers:** Gestión eficiente de conexiones a la base de datos

### 📊 Estadísticas y Análisis
- **Métricas Detalladas:** Contador de conversaciones, mensajes y promedios
- **Estadísticas Avanzadas:** Conversación más larga, fechas de creación, etc.
- **Panel de Control:** Interfaz dedicada para ver estadísticas de uso
- **Exportación de Datos:** Descarga conversaciones en formato Markdown

### 🎨 Interfaz de Usuario Moderna
- **Diseño Profesional:** Interfaz elegante con paleta de colores optimizada
- **Interfaz Responsive:** Adaptable a diferentes tamaños de pantalla
- **Sidebar Intuitivo:** Navegación fácil entre conversaciones
- **Sugerencias Rápidas:** Botones de inicio rápido para temas comunes

### ⚙️ Configuración Avanzada
- **Panel de Configuración:** Interfaz dedicada para ajustar todas las opciones
- **Gestión de Caché:** Limpieza manual del caché de audio
- **Configuración Persistente:** Los ajustes se mantienen entre sesiones
- **Validación de Configuración:** Verificación automática de claves API y dependencias

### 🔧 Características Técnicas
- **Manejo de Errores Robusto:** Mensajes de error específicos y útiles
- **Optimización de Rendimiento:** Caché inteligente y conexiones eficientes
- **Arquitectura Modular:** Código organizado en módulos especializados
- **Logging y Debugging:** Sistema de información detallada para desarrolladores

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3.8+
- **Framework Web:** Streamlit 1.40.0+
- **Motor de IA:** OpenAI GPT-4 (LangChain)
- **Base de Datos:** SQLite con Context Managers
- **Texto a Voz:** pyttsx3 (local) + gTTS (respaldo)
- **Reconocimiento de Voz:** SpeechRecognition
- **Gestión de Estado:** Streamlit Session State
- **Estilos:** CSS personalizado con diseño profesional

## 📁 Estructura del Proyecto

```
chatbot-unab/
├── main.py             # 🚀 PRINCIPAL: Punto de entrada de v5.0 (Streamlit nativo, sin bugs)
├── chat_manager.py            # 🤖 Gestión de IA y respuestas con streaming
├── database_manager.py        # 💾 Gestión de base de datos SQLite
├── TTSManager.py              # 🔊 Gestión de texto a voz (TTS)
├── audio_manager.py           # 🔊 Gestión de reconocimiento de voz
├── requirements.txt           # 📦 Dependencias del proyecto
├── .env                       # 🔑 Variables de entorno (incluye OPENAI_API_KEY)
├── README.md                  # 📖 Documentación del proyecto
├── ESTRUCTURA_FINAL.md        # 📋 Guía de estructura y cleanup
├── QUICK_START.txt            # 🚀 Guía de inicio rápido
├── venv/                      # 🐍 Entorno virtual de Python
└── .git/                      # 📝 Control de versión
```

### 📋 Descripción de Módulos (v5.0)

- **`main.py`** ⭐ **NUEVO:** Aplicación principal completamente rediseñada usando componentes nativos de Streamlit
  - Elimina todos los bugs de sidebar y CSS
  - 600+ líneas, código limpio y organizado en 7 secciones
  - Integra: database_manager, chat_manager, TTSManager, audio_manager

- **`chat_manager.py`**: Motor de IA con streaming, validaciones y generación de títulos inteligentes
- **`database_manager.py`**: Gestión eficiente de SQLite con CRUD completo
- **`TTSManager.py`**: Sistema de texto a voz optimizado con múltiples backends (pyttsx3, edge-tts, gTTS)
- **`audio_manager.py`**: Reconocimiento de voz y gestión de audio

## 🚀 Instalación y Uso

### Prerrequisitos
- Python 3.8 o superior
- Cuenta de OpenAI con clave API válida
- Micrófono (opcional, para funcionalidades de voz)

### Instalación Rápida

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/your-username/chatbot-unab.git
   cd chatbot-unab
   ```

2. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   ```bash
   # Copiar archivo de ejemplo
   copy example.env .env
   # Editar .env y agregar tu clave API
   ```

5. **Ejecutar la aplicación:**
   ```bash
   streamlit run main.py
   ```

   La aplicación se abrirá en: `http://localhost:8501`

### 🔧 Configuración Inicial

1. **Clave API de OpenAI:**
   - Obtén tu clave API en [OpenAI Platform](https://platform.openai.com/api-keys)
   - Agrega la clave al archivo `.env`:
   ```
   OPENAI_API_KEY="tu-clave-api-aqui"
   ```

2. **Configuración Opcional:**
   - `MODEL`: Modelo de IA (por defecto: gpt-4)
   - `VERSION`: Versión de la aplicación (por defecto: 3.0)

### 🎯 Uso Básico

1. **Iniciar Nueva Conversación:** Haz clic en "➕ Nueva Conversación"
2. **Escribir Mensaje:** Usa el campo de texto en la parte inferior
3. **Escuchar Respuesta:** Haz clic en "🔊" junto a las respuestas del asistente
4. **Configurar Asistente:** Usa el botón "⚙️ Configuración" en el sidebar
5. **Gestionar Conversaciones:** Usa el menú "⋮" para editar, exportar o eliminar


## 🔮 Próximas Mejoras

- 🎤 **Conversación de Voz en Tiempo Real:** Interacción completa por voz
- 🌍 **Soporte Multiidioma:** Interfaz y respuestas en múltiples idiomas
- 📚 **Integración Educativa:** Conexión con plataformas de aprendizaje
- 🧠 **Memoria Contextual:** Recordar preferencias y contexto entre sesiones
- 📱 **Aplicación Móvil:** Versión nativa para dispositivos móviles

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si quieres mejorar U-Tutor:

1. Haz fork del proyecto
2. Crea una rama para tu funcionalidad (`git checkout -b feature/FuncionalidadIncreible`)
3. Confirma tus cambios (`git commit -m 'Agregar alguna FuncionalidadIncreible'`)
4. Envía a la rama (`git push origin feature/FuncionalidadIncreible`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---
**Hecho con ❤️ para estudiantes universitarios**

*U-Tutor v3.0 - Tu asistente educativo inteligente*
