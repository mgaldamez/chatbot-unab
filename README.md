# 🎓 U-Tutor - Tu asistente universitario con IA

U-Tutor es una aplicación de chat inteligente construida con Streamlit y OpenAI GPT que actúa como un tutor universitario empático y profesional llamado Jake.

## ✨ Características

- 💾 **Historial persistente** con SQLite
- 🗂️ **Múltiples conversaciones** organizadas por fecha
- ✏️ **Editar títulos** de conversaciones
- 🗑️ **Eliminar conversaciones** con confirmación
- 📊 **Estadísticas** de uso
- 🎨 **Interfaz intuitiva** con navegación lateral
- 🔄 **Continuar conversaciones** anteriores

## 🚀 Instalación

### Requisitos
- Python 3.8+
- API Key de OpenAI

### Pasos

1. **Descargar el proyecto**
```bash
git clone [url-del-repo]
cd ututor
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar API Key**
```bash
# Crear archivo .env
echo "OPENAI_API_KEY=tu_api_key_aquí" > .env
```

4. **Ejecutar**
```bash
streamlit run main.py
```

Abre tu navegador en `http://localhost:8501`

## 🎯 Uso

### Chat básico
1. Escribe tu pregunta en el chat
2. Jake responderá como tu tutor universitario

### Gestión de conversaciones
- **Nueva conversación**: Botón "➕ Nueva Conversación"
- **Cargar conversación**: Clic en cualquier conversación del historial
- **Editar título**: Botón "✏️" junto a cada conversación
- **Eliminar**: Botón "🗑️" con confirmación

## 🏗️ Estructura del proyecto

```
ututor/
├── main.py                 # Aplicación principal
├── database_manager.py     # Gestión de SQLite
├── chat_manager.py         # Lógica del chat y OpenAI API
├── ui_components.py        # Componentes de interfaz
├── requirements.txt        # Dependencias
├── .env                    # Variables de entorno
└── chat_history.db        # Base de datos (se crea automáticamente)
```

## 🗄️ Base de datos

### Tabla `conversations`
- `id` - Identificador único
- `title` - Título de la conversación (editable)
- `created_at` - Fecha de creación
- `updated_at` - Última actualización

### Tabla `messages`
- `id` - Identificador único
- `conversation_id` - Referencia a la conversación
- `role` - 'user' o 'assistant'
- `content` - Contenido del mensaje
- `timestamp` - Marca de tiempo

## ⚙️ Configuración

### Variables de entorno (.env)
```env
OPENAI_API_KEY=sk-...tu_api_key_de_openai
VERSION={versionNumber}
MODEL={gpt-model}
```

### Personalizar el modelo
En `chat_manager.py`:
```python
ChatOpenAI(
    model=model,          # Cambiar modelo si es necesario
    temperature=0,          # Ajustar creatividad (0-1)
    api_key=api_key
)
```

### Personalizar a Jake
En `chat_manager.py`, modificar:
```python
self.system_message = """Tu prompt personalizado aquí"""
```

## 📈 Historial de cambios

### v2.1 (Actual)
- ✏️ Edición de títulos de conversaciones
- 🏗️ Arquitectura modular (4 archivos separados)
- 📊 Estadísticas mejoradas
- 🎨 Interfaz refinada

### v2.0
- 💾 Persistencia con SQLite
- 🗂️ Múltiples conversaciones
- 🗑️ Eliminación de conversaciones
- 📈 Sistema de estadísticas

### v1.0
- 💬 Chat básico con GPT-4
- 🧠 Memoria de sesión temporal
- 🎓 Personalidad de tutor (Jake)

## 🚀 Próximas características

- 🔍 Búsqueda en conversaciones
- 📤 Exportar conversaciones (PDF/TXT)
- 🏷️ Etiquetas y categorías
- 🌙 Modo oscuro
- ⚙️ Configuraciones de usuario

## 🛠️ Desarrollo

### Agregar nuevas características
1. **Datos**: Agregar métodos en `DatabaseManager`
2. **Lógica**: Modificar `ChatManager`
3. **UI**: Agregar componentes en `UIComponents`
4. **Integrar**: Conectar en `main.py`


## 🆘 Problemas comunes

**Error de API Key:**
```
❌ Por favor, configura tu OPENAI_API_KEY en el archivo .env
```
**Solución:** Verificar que el archivo .env existe con la API key correcta.

**Base de datos bloqueada:**
```
sqlite3.OperationalError: database is locked
```
**Solución:** Cerrar otras instancias de la aplicación.

## 📄 Licencia

MIT License - ver archivo `LICENSE` para detalles.

---

**¡Disfruta aprendiendo con Jake! 🎓**