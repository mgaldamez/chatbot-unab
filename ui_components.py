# U-TUTOR v3.0 - Mejoras en ui_components.py: Sidebar avanzado, configuración y controles de audio
import streamlit as st
import time
import os
from typing import List, Tuple, Optional
from database_manager import DatabaseManager
from TTSManager import TTSManager

class UIComponents:
    def __init__(self, db_manager: DatabaseManager, version: str):
        """Inicializa UIComponents con estados de sesión - U-TUTOR v3.0"""
        self.db_manager = db_manager
        self.version = version
        tts_engine = os.getenv("TTS_ENGINE", "edge-tts")
        self.tts_manager = TTSManager(engine_type=tts_engine)
   
        # Inicializar estados de sesión necesarios
        if 'theme' not in st.session_state:
            st.session_state.theme = 'dark'
        
        if 'show_stats' not in st.session_state:
            st.session_state.show_stats = False
            
        if 'show_config_page' not in st.session_state:
            st.session_state.show_config_page = False
        
        # Configuraciones fijas (sin opciones de inglés)
        if 'tts_language' not in st.session_state:
            st.session_state.tts_language = 'es'
        
        if 'auto_translate' not in st.session_state:
            st.session_state.auto_translate = False

    def render_sidebar(self) -> Optional[int]:
        """Renderiza el sidebar responsivo con gestión de conversaciones - U-TUTOR v3.0"""
        
        # CSS responsivo para el sidebar
        st.markdown("""
        <style>
        @media (max-width: 768px) {
            .sidebar .sidebar-content {
                padding: 1rem 0.5rem;
            }
            .sidebar .stButton > button {
                font-size: 0.8rem;
                padding: 0.3rem 0.6rem;
            }
            .sidebar .stTextInput > div > div > input {
                font-size: 0.8rem;
                padding: 0.3rem 0.6rem;
            }
            /* Botones verticales en móviles */
            .menu-buttons-mobile {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            .menu-buttons-mobile .stButton {
                width: 100%;
            }
        }
        
        @media (min-width: 769px) {
            .sidebar .sidebar-content {
                padding: 1.5rem 1rem;
            }
            .sidebar .stButton > button {
                font-size: 0.9rem;
                padding: 0.4rem 0.8rem;
            }
            .sidebar .stTextInput > div > div > input {
                font-size: 0.9rem;
                padding: 0.4rem 0.8rem;
            }
            /* Botones horizontales en computadoras */
            .menu-buttons-desktop {
                display: flex;
                flex-direction: row;
                gap: 0.5rem;
            }
        }
        
        @media (min-width: 1200px) {
            .sidebar .sidebar-content {
                padding: 2rem 1.5rem;
            }
            .sidebar .stButton > button {
                font-size: 1rem;
                padding: 0.5rem 1rem;
            }
            .sidebar .stTextInput > div > div > input {
                font-size: 1rem;
                padding: 0.5rem 1rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.sidebar.title("🗂️ Historial de Chats")
        
        # Botón de configuración en la parte superior
        if st.sidebar.button("⚙️ Configuración", use_container_width=True, key="config_button"):
            st.session_state.show_config_page = True
            st.rerun()
        
        # Botón para nueva conversación
        if st.sidebar.button("➕ Nueva Conversación", use_container_width=True):
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.session_state.editing_title = None
            # Si estamos en la página de configuración, volver al chat
            if st.session_state.show_config_page:
                st.session_state.show_config_page = False
            st.rerun()
        
        # Búsqueda de conversaciones
        search_query = st.sidebar.text_input(
            "🔍 Buscar conversación", 
            key="search_conv",
            placeholder="Escribe para buscar..."
        )
        
        # Obtener conversaciones
        if search_query:
            conversations = self.db_manager.search_conversations(search_query)
        else:
            conversations = self.db_manager.get_conversations()
        
        # Mostrar conversaciones
        if conversations:
            st.sidebar.subheader(f"📚 {len(conversations)} conversación(es):")
            
            for conv_id, title, created_at, updated_at in conversations:
                self._render_conversation_item(conv_id, title, created_at)
        else:
            if search_query:
                st.sidebar.info("🔍 No se encontraron conversaciones")
            else:
                st.sidebar.info("💬 Aún no hay conversaciones")
        
        # La página de configuración se renderiza independientemente
        
        return None
    
    def _render_conversation_item(self, conv_id: int, title: str, created_at: str):
        """Renderiza un elemento de conversación en el sidebar con mejoras - U-TUTOR v3.0"""
        container = st.sidebar.container()
        
        with container:
            is_editing = (
                hasattr(st.session_state, 'editing_title') and 
                st.session_state.editing_title == conv_id
            )
            
            if is_editing:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    new_title = st.text_input(
                        "Nuevo nombre:",
                        value=title,
                        key=f"edit_title_{conv_id}",
                        label_visibility="collapsed",
                        placeholder="Escribe el nuevo nombre..."
                    )
                
                with col2:
                    if st.button("✅", key=f"save_{conv_id}", help="Guardar cambios"):
                        if new_title.strip():
                            if self.db_manager.update_conversation_title(conv_id, new_title.strip()):
                                st.success("✅ Nombre actualizado!")
                                st.session_state.editing_title = None
                                st.rerun()
                            else:
                                st.error("❌ Error al guardar")
                        else:
                            st.warning("⚠️ El nombre no puede estar vacío")
                
                with col3:
                    if st.button("❌", key=f"cancel_{conv_id}", help="Cancelar"):
                        st.session_state.editing_title = None
                        st.rerun()
            
            else:
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    if st.button(
                        f"💬 {title[:25]}{'...' if len(title) > 25 else ''}",
                        key=f"conv_{conv_id}",
                        use_container_width=True,
                        help=f"Creado: {created_at[:16]}"
                    ):
                        self._load_conversation(conv_id)
                
                with col2:
                    # Botón de menú con tres puntos
                    if st.button("⋮", key=f"menu_{conv_id}", help="Opciones"):
                        self._toggle_conversation_menu(conv_id)
                
                # Mostrar menú desplegable si está activo
                if hasattr(st.session_state, 'active_menu') and st.session_state.active_menu == conv_id:
                    self._render_conversation_menu_simple(conv_id)

    def render_config_page(self):
        """Renderiza página de configuración como ventana separada - U-TUTOR v3.0"""
        if st.session_state.show_config_page:
            # Header de la página de configuración
            col1, col2, col3 = st.columns([1, 6, 1])
            
            with col2:
                st.title("⚙️ Configuración de U-Tutor")
                st.markdown("---")
                
                # Botón para volver al chat
                if st.button("← Volver al Chat", key="back-to-chat"):
                    st.session_state.show_config_page = False
                    st.rerun()
                
                st.markdown("---")
                
                # Tabs para organizar el contenido
                tab1, tab2, tab3 = st.tabs(["🎨 Configuración", "📊 Estadísticas", "ℹ️ Información"])
                
                with tab1:
                    self._render_config_tab()
                
                with tab2:
                    self._render_stats_tab()
                
                with tab3:
                    self._render_info_tab()
                
                st.markdown("---")
                
                # Botón para volver al chat en la parte inferior
                if st.button("🏠 Volver al Chat Principal", use_container_width=True, type="primary"):
                    st.session_state.show_config_page = False
                    st.rerun()
    
    def _render_config_tab(self):
        """Renderiza la pestaña de configuración - U-TUTOR v3.0"""
        st.markdown("### 🎨 Configuración del Asistente")
        
        # Temperatura/Creatividad
        if 'temperature' not in st.session_state:
            st.session_state.temperature = 0.7
        
        temperature = st.slider(
            "🎨 Creatividad",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.temperature,
            step=0.1,
            help="Mayor valor = respuestas más creativas e impredecibles"
        )
        
        # Personalidad
        if 'personality' not in st.session_state:
            st.session_state.personality = "Amigable"
        
        personality = st.selectbox(
            "🎭 Personalidad",
            ["Profesional", "Amigable", "Conciso", "Detallado"],
            index=["Profesional", "Amigable", "Conciso", "Detallado"].index(st.session_state.personality)
        )
        
        # Idioma fijo en español
        st.markdown("### 🗣️ Idioma de voz")
        st.info("🇪🇸 **Español** (fijo para mejor compatibilidad)")
        
        # Mostrar información sobre voces TTS disponibles
        if hasattr(st.session_state, 'audio_manager'):
            voices_info = st.session_state.audio_manager.get_available_voices_info()
            if voices_info['local_tts_available']:
                if voices_info['available_languages']:
                    st.success(f"🎤 TTS Local disponible para: {', '.join(voices_info['available_languages'])}")
                else:
                    st.warning("⚠️ TTS Local disponible pero sin voces compatibles")
            else:
                st.info("ℹ️ Solo gTTS disponible (requiere internet)")
        
        # Tema fijo (solo oscuro)
        st.markdown("### 🌙 Apariencia")
        st.info("🎨 **Tema**: Oscuro (fijo para mejor compatibilidad)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Aplicar Cambios", use_container_width=True, type="primary"):
                st.session_state.temperature = temperature
                st.session_state.personality = personality
                st.session_state.tts_language = 'es'  # Fijo en español
                st.session_state.auto_translate = False  # Deshabilitado
                st.session_state.settings_changed = True
                st.success("✅ Configuración guardada")
                st.rerun()
        
        with col2:
            if st.button("🔄 Resetear", use_container_width=True):
                st.session_state.temperature = 0.7
                st.session_state.personality = "Amigable"
                st.session_state.tts_language = 'es'  # Fijo en español
                st.session_state.auto_translate = False  # Deshabilitado
                st.info("↩️ Valores por defecto")
                st.rerun()
        
        # Botón para limpiar caché de audio
        st.markdown("---")
        if st.button("🧹 Limpiar caché de audio", use_container_width=True, help="Libera memoria eliminando archivos de audio guardados"):
            if hasattr(st.session_state, 'audio_manager'):
                cache_size = st.session_state.audio_manager.get_cache_size()
                st.session_state.audio_manager.clear_audio_cache()
                st.success(f"✅ Caché limpiado ({cache_size} archivos eliminados)")
            else:
                st.info("ℹ️ Caché de audio no disponible")

    def _render_stats_tab(self):
        """Renderiza la pestaña de estadísticas - U-TUTOR v3.0"""
        st.markdown("### 📊 Estadísticas de Uso")
        
        stats = self.db_manager.get_conversation_stats()
        detailed_stats = self.db_manager.get_detailed_stats()
        
        # Métricas principales
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💬 Conversaciones", stats['total_conversations'])
        with col2:
            st.metric("📝 Mensajes", stats['total_messages'])
        
        # Métricas adicionales
        if detailed_stats['avg_messages_per_conv'] > 0:
            st.metric(
                "📊 Promedio mensajes/conversación", 
                f"{detailed_stats['avg_messages_per_conv']:.1f}"
            )
        
        if detailed_stats.get('longest_conversation'):
            st.markdown("### 🏆 Conversación más larga")
            st.info(
                f"**{detailed_stats['longest_conversation'][0][:30]}...** "
                f"({detailed_stats['longest_conversation'][1]} mensajes)"
            )
        
        # Estadísticas de tiempo
        if detailed_stats.get('oldest_conversation') and detailed_stats.get('newest_conversation'):
            st.markdown("### 📅 Historial")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📅 Primera conversación", detailed_stats['oldest_conversation'][:10])
            with col2:
                st.metric("🕒 Última conversación", detailed_stats['newest_conversation'][:10])
        else:
            st.info("📅 No hay conversaciones registradas aún")


    def _render_info_tab(self):
        """Renderiza la pestaña de información - U-TUTOR v3.0"""
        st.markdown("### ℹ️ Información de U-Tutor")
        
        st.markdown(f"""
        **🎓 U-Tutor v{self.version}**
        
        Un asistente educativo inteligente diseñado para ayudar a estudiantes con sus dudas académicas.
        
        ### ✨ Características principales:
        - 🤖 **IA Avanzada**: Respuestas inteligentes y contextuales
        - 🎨 **Personalizable**: Configura creatividad y personalidad
        - 🔊 **Audio**: Texto a voz optimizado
        - 💾 **Persistente**: Historial de conversaciones
        - 🎨 **Temas**: Modo claro y oscuro
        - 📊 **Estadísticas**: Seguimiento de uso
        
        ### 🛠️ Tecnologías:
        - **Streamlit**: Interfaz web
        - **OpenAI GPT**: Motor de IA
        - **SQLite**: Base de datos
        - **pyttsx3/gTTS**: Síntesis de voz
        
        ---
        **Hecho con ❤️ para estudiantes**
        
        *¿Necesitas ayuda? Revisa la documentación o contacta al desarrollador.*
        """)

    def render_main_chat_area(self):
        """Renderiza el área principal de chat mejorada - U-TUTOR v3.0"""
        # No mostrar el área de chat si estamos en la página de configuración
        if st.session_state.show_config_page:
            return
        
        # Título principal
        st.title(f"🎓 U-Tutor v{self.version}")
        
        # Información de la conversación actual
        if hasattr(st.session_state, 'current_conversation_id') and st.session_state.current_conversation_id:
            conversation = self.db_manager.get_conversation_by_id(st.session_state.current_conversation_id)
            if conversation:
                msg_count = len(st.session_state.messages)
                st.markdown(f"""
                <div style='background: linear-gradient(90deg, #2d3748 0%, #4a5568 100%); 
                            padding: 15px; 
                            border-radius: 10px; 
                            margin-bottom: 20px;
                            border-left: 4px solid #a0c4ff;
                            color: #e8e8e8;
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);'>
                    📝 <b>{conversation[1]}</b> | 💬 {msg_count} mensaje{'s' if msg_count != 1 else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            # Sugerencias para nueva conversación
            self._render_quick_suggestions()

    def _render_quick_suggestions(self):
        """Renderiza sugerencias rápidas para iniciar conversación - U-TUTOR v3.0"""
        st.markdown("### 💡 Sugerencias para empezar:")
        
        suggestions = [
            ("📐", "Explícame el teorema de Pitágoras"),
            ("🌱", "¿Cómo funciona la fotosíntesis?"),
            ("➗", "Ayúdame con ecuaciones cuadráticas"),
            ("💻", "¿Qué es la programación orientada a objetos?"),
            ("🧪", "Explica la tabla periódica"),
            ("📊", "¿Qué es la estadística descriptiva?"),
        ]
        
        cols = st.columns(2)
        for idx, (emoji, suggestion) in enumerate(suggestions):
            with cols[idx % 2]:
                if st.button(f"{emoji} {suggestion}", key=f"suggest_{idx}", use_container_width=True):
                    st.session_state.pending_message = suggestion
                    st.rerun()

    def render_audio_controls(self, message_content: str, message_role: str):
        """Renderiza controles de audio para un mensaje - U-TUTOR v3.0"""
        if message_role == "assistant":
            # Botón para reproducir audio
            col1, col2, col3 = st.columns([1, 10, 1])
            with col1:
                if st.button("🔊", key=f"tts_{id(message_content)}", help="Reproducir audio"):
                    st.session_state.play_audio = message_content

    def render_chat_messages(self, messages: List[dict]):
        """Renderiza los mensajes del chat con TTS"""
        # No mostrar mensajes si estamos en la página de configuración
        if st.session_state.show_config_page:
            return
            
        for idx, message in enumerate(messages):
            with st.chat_message(message["role"]):
                # Mostrar el contenido del mensaje
                st.markdown(message["content"])
                
                # NUEVO: Agregar botón TTS solo para mensajes del asistente
                if message["role"] == "assistant":
                    self._add_tts_button(message["content"], idx)
    
    def _add_tts_button(self, text: str, message_index: int):
        """Agrega un botón para reproducir el mensaje con TTS"""
        # Crear identificador único que incluya la conversación actual
        conv_id = st.session_state.get('current_conversation_id', 'new')
        unique_key = f"{conv_id}_{message_index}"
        
        # Usar columnas para alinear los botones horizontalmente
        col1, col2 = st.columns([1, 9])
        
        with col1:
            # Inicializar estado de audio si no existe
            if f'audio_playing_{unique_key}' not in st.session_state:
                st.session_state[f'audio_playing_{unique_key}'] = False
            if f'audio_data_{unique_key}' not in st.session_state:
                st.session_state[f'audio_data_{unique_key}'] = None
            
            # Botón de reproducir/pausar
            if st.session_state[f'audio_playing_{unique_key}']:
                if st.button("⏸️", key=f"pause_{unique_key}", help="Pausar audio", use_container_width=True):
                    st.session_state[f'audio_playing_{unique_key}'] = False
                    st.rerun()
            else:
                if st.button("▶️", key=f"play_{unique_key}", help="Reproducir audio", use_container_width=True):
                    # Mostrar indicador de carga
                    with st.spinner(""):
                        # Preprocesar texto para TTS
                        processed_text = self.tts_manager.preprocess_text_for_tts(text)
                        # Generar audio
                        audio_data = self.tts_manager.text_to_speech_fast(processed_text)
                        if audio_data:
                            # Guardar audio en session state
                            st.session_state[f'audio_data_{unique_key}'] = audio_data
                            st.session_state[f'audio_playing_{unique_key}'] = True
                            st.rerun()
                        else:
                            st.error("❌ Error al generar audio")
        
        # Mostrar reproductor de audio si está disponible
        if st.session_state[f'audio_data_{unique_key}']:
            st.audio(st.session_state[f'audio_data_{unique_key}'], format='audio/mp3')
    
    def _load_conversation(self, conv_id: int):
        """Carga una conversación específica - U-TUTOR v3.0"""
        st.session_state.current_conversation_id = conv_id
        st.session_state.editing_title = None
        
        # Si estamos en la página de configuración, volver al chat
        if st.session_state.show_config_page:
            st.session_state.show_config_page = False
        
        # Cargar mensajes de la conversación
        messages_data = self.db_manager.load_conversation_messages(conv_id)
        st.session_state.messages = []
        
        for role, content, _ in messages_data:
            st.session_state.messages.append({"role": role, "content": content})
        
        st.rerun()
    

    def show_error(self, message: str):
        """Muestra un mensaje de error - U-TUTOR v3.0"""
        st.error(message)
    
    def show_success(self, message: str):
        """Muestra un mensaje de éxito - U-TUTOR v3.0"""
        st.success(message)
    
    def show_spinner(self, text: str = "Procesando..."):
        """Muestra un spinner con texto - U-TUTOR v3.0"""
        return st.spinner(text)
    
    def _toggle_conversation_menu(self, conv_id: int):
        """Alterna el menú desplegable de una conversación - U-TUTOR v3.0"""
        print(f"DEBUG: Toggle menu para conv_id: {conv_id}")
        if hasattr(st.session_state, 'active_menu') and st.session_state.active_menu == conv_id:
            # Si el menú ya está abierto, cerrarlo
            print(f"DEBUG: Cerrando menú para conv_id: {conv_id}")
            del st.session_state.active_menu
        else:
            # Abrir este menú y cerrar otros
            print(f"DEBUG: Abriendo menú para conv_id: {conv_id}")
            st.session_state.active_menu = conv_id
        st.rerun()
    
    def _render_conversation_menu_simple(self, conv_id: int):
        """Renderiza el menú de acción flexible - U-TUTOR v3.0"""
        
        # Diseño flexible: vertical en móviles, horizontal en computadoras
        st.markdown('<div class="menu-buttons-mobile menu-buttons-desktop">', unsafe_allow_html=True)
        
        # Botón de descargar (arriba en móviles)
        if st.button("📥 Descargar", key=f"export_{conv_id}", help="Descargar conversación", use_container_width=True):
            self._export_conversation_direct(conv_id)
            if hasattr(st.session_state, 'active_menu'):
                del st.session_state.active_menu
        
        # Botón de editar (medio)
        if st.button("✏️ Editar", key=f"edit_{conv_id}", help="Cambiar nombre", use_container_width=True):
            st.session_state.editing_title = conv_id
            if hasattr(st.session_state, 'active_menu'):
                del st.session_state.active_menu
            st.rerun()
        
        # Botón de eliminar (abajo en móviles)
        if st.button("🗑️ Eliminar", key=f"del_{conv_id}", help="Borrar conversación", use_container_width=True, type="secondary"):
            self._delete_conversation_direct(conv_id)
            # No cerrar el menú aquí, se cerrará después de la confirmación
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    
    def _export_conversation_direct(self, conv_id: int):
        """Exporta conversación directamente - U-TUTOR v3.0"""
        try:
            md_content = self.db_manager.export_conversation_to_markdown(conv_id)
            conversation = self.db_manager.get_conversation_by_id(conv_id)
            title = conversation[1] if conversation else f"conversacion_{conv_id}"
            
            clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_title = clean_title.replace(' ', '_')
            
            # Descarga directa sin mostrar botón
            st.download_button(
                "⬇️ Descargar",
                md_content,
                file_name=f"{clean_title}.md",
                mime="text/markdown",
                key=f"download_{conv_id}_{hash(md_content) % 10000}",
                help="Descargar conversación"
            )
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    def _delete_conversation_direct(self, conv_id: int):
        """Elimina una conversación directamente - U-TUTOR v3.0"""
        # Eliminar la conversación directamente
        if self.db_manager.delete_conversation(conv_id):
            # Si la conversación eliminada era la activa, resetear
            if (hasattr(st.session_state, 'current_conversation_id') and 
                st.session_state.current_conversation_id == conv_id):
                st.session_state.current_conversation_id = None
                st.session_state.messages = []
            
            # Cerrar menú después de eliminar
            if hasattr(st.session_state, 'active_menu'):
                del st.session_state.active_menu
            
            st.success("✅ Conversación eliminada")
            time.sleep(3)
            st.rerun()
        else:
            st.error("❌ Error al eliminar la conversación")
            # Cerrar menú en caso de error
            if hasattr(st.session_state, 'active_menu'):
                del st.session_state.active_menu
                