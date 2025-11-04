import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI

load_dotenv()

# Configuración de la base de datos
DB_PATH = "chat_history.db"

def init_database():
    """Inicializa la base de datos SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Crear tabla para conversaciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crear tabla para mensajes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_new_conversation(title):
    """Crea una nueva conversación"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO conversations (title) VALUES (?)",
        (title,)
    )
    
    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return conversation_id

def get_conversations():
    """Obtiene todas las conversaciones ordenadas por fecha de actualización"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, title, created_at, updated_at 
        FROM conversations 
        ORDER BY updated_at DESC
    ''')
    
    conversations = cursor.fetchall()
    conn.close()
    
    return conversations

def save_message(conversation_id, role, content):
    """Guarda un mensaje en la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Insertar mensaje
    cursor.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
        (conversation_id, role, content)
    )
    
    # Actualizar timestamp de la conversación
    cursor.execute(
        "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (conversation_id,)
    )
    
    conn.commit()
    conn.close()

def load_conversation(conversation_id):
    """Carga el historial de una conversación"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT role, content, timestamp 
        FROM messages 
        WHERE conversation_id = ? 
        ORDER BY timestamp ASC
    ''', (conversation_id,))
    
    messages = cursor.fetchall()
    conn.close()
    
    return messages

def delete_conversation(conversation_id):
    """Elimina una conversación y todos sus mensajes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    
    conn.commit()
    conn.close()

def generate_conversation_title(first_message):
    """Genera un título para la conversación basado en el primer mensaje"""
    # Tomar las primeras 50 caracteres y agregar "..." si es más largo
    if len(first_message) > 50:
        return first_message[:50] + "..."
    return first_message

# Configuración de la aplicación
st.set_page_config(page_title="U-Tutor v2", page_icon=None, layout="wide")

# Inicializar base de datos
init_database()

# Cargar API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("Por favor, configura tu OPENAI_API_KEY en el archivo .env")
    st.stop()

# Inicializar LLM (sin especificar api_key explícitamente - usa la variable de entorno)
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Sidebar para gestión de conversaciones
st.sidebar.title("Historial de Chats")

# Botón para nueva conversación
if st.sidebar.button("Nueva Conversación", use_container_width=True):
    st.session_state.current_conversation_id = None
    st.session_state.messages = []
    st.rerun()

# Mostrar conversaciones existentes
conversations = get_conversations()

if conversations:
    st.sidebar.subheader("Conversaciones guardadas:")
    
    for conv_id, title, created_at, updated_at in conversations:
        col1, col2 = st.sidebar.columns([4, 1])
        
        with col1:
            if st.button(
                f"{title}", 
                key=f"conv_{conv_id}",
                use_container_width=True,
                help=f"Creado: {created_at[:16]}"
            ):
                st.session_state.current_conversation_id = conv_id
                # Cargar mensajes de la conversación
                messages_data = load_conversation(conv_id)
                st.session_state.messages = []
                for role, content, _ in messages_data:
                    st.session_state.messages.append({"role": role, "content": content})
                st.rerun()
        
        with col2:
            if st.button("Eliminar", key=f"del_{conv_id}", help="Eliminar conversación"):
                delete_conversation(conv_id)
                if hasattr(st.session_state, 'current_conversation_id') and st.session_state.current_conversation_id == conv_id:
                    st.session_state.current_conversation_id = None
                    st.session_state.messages = []
                st.rerun()

# Área principal
st.title("U-Tutor v2 - Tu asistente universitario")

# Mensaje de sistema (contexto para la IA)
system_message = """Eres Jake, un tutor universitario empático y profesional. 
Ayuda al estudiante con sus dudas, habla como humano y nunca reveles que eres una IA."""

# Inicializar variables de sesión
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None

# Mostrar información de la conversación actual
if st.session_state.current_conversation_id:
    st.info(f"Conversación #{st.session_state.current_conversation_id}")
else:
    st.info("Nueva conversación - Escribe tu primer mensaje para comenzar")

# Mostrar historial de chat (alineado a la derecha para ambos roles)
for message in st.session_state.messages:
    role = message.get("role", "user")
    with st.chat_message(role):
        st.markdown(message["content"])

# Input del chat
if prompt := st.chat_input("Escribe tu mensaje..."):
    # Si es una nueva conversación, crearla
    if st.session_state.current_conversation_id is None:
        conversation_title = generate_conversation_title(prompt)
        st.session_state.current_conversation_id = create_new_conversation(conversation_title)
    
    # Mostrar mensaje del usuario
    st.chat_message("user").markdown(prompt)
    
    # Agregar mensaje del usuario al historial de la sesión
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Guardar mensaje del usuario en la base de datos
    save_message(st.session_state.current_conversation_id, "user", prompt)
    
    # Preparar mensajes para la API (incluyendo el contexto del sistema)
    api_messages = [("system", system_message)]
    for msg in st.session_state.messages:
        role = "human" if msg["role"] == "user" else "assistant"
        api_messages.append((role, msg["content"]))
    
    # Obtener respuesta de Jake
    with st.chat_message("assistant"):
        with st.spinner("Jake está pensando..."):
            try:
                response = llm.invoke(api_messages).content
                st.markdown(response)

                # Agregar respuesta del asistente al historial de la sesión
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Guardar respuesta del asistente en la base de datos
                save_message(st.session_state.current_conversation_id, "assistant", response)

            except Exception as e:
                st.error(f"Error al obtener respuesta: {str(e)}")

# Información adicional en el sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Información")
st.sidebar.markdown("""
- **Modelo**: GPT-5
- **Versión**: U-Tutor v2
- **Funciones**: 
    - Historial persistente
    - Múltiples conversaciones
    - Eliminar conversaciones
    - Continuar chats anteriores
""")

# Mostrar estadísticas
if conversations:
    st.sidebar.markdown(f"**Total de conversaciones**: {len(conversations)}")