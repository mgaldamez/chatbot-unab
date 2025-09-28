import streamlit as st
from typing import List, Tuple, Optional
from database_manager import DatabaseManager


class UIComponents:
    def __init__(self, db_manager: DatabaseManager, version: str):
        self.db_manager = db_manager
        self.version = version

    def render_sidebar(self) -> Optional[int]:
        """Renderiza el sidebar con gestión de conversaciones"""
        st.sidebar.title("🗂️ Historial de Chats")
        
        selected_conversation_id = None
        
        # Botón para nueva conversación
        if st.sidebar.button("➕ Nueva Conversación", use_container_width=True):
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.session_state.editing_title = None
            st.rerun()
        
        # Mostrar conversaciones existentes
        conversations = self.db_manager.get_conversations()
        
        if conversations:
            st.sidebar.subheader("Conversaciones guardadas:")
            
            for conv_id, title, created_at, updated_at in conversations:
                self._render_conversation_item(conv_id, title, created_at)
        
        # Estadísticas
        self._render_stats()
        
        return selected_conversation_id
    
    def _render_conversation_item(self, conv_id: int, title: str, created_at: str):
        """Renderiza un elemento de conversación en el sidebar"""
        # Contenedor para la conversación
        container = st.sidebar.container()
        
        with container:
            # Verificar si estamos editando el título de esta conversación
            is_editing = (
                hasattr(st.session_state, 'editing_title') and 
                st.session_state.editing_title == conv_id
            )
            
            if is_editing:
                # Modo edición del título
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    new_title = st.text_input(
                        "Nuevo título:",
                        value=title,
                        key=f"edit_title_{conv_id}",
                        label_visibility="collapsed"
                    )
                
                with col2:
                    if st.button("✅", key=f"save_{conv_id}", help="Guardar"):
                        if new_title.strip():
                            if self.db_manager.update_conversation_title(conv_id, new_title.strip()):
                                st.success("Título actualizado!")
                                st.session_state.editing_title = None
                                st.rerun()
                            else:
                                st.error("Error al actualizar")
                        else:
                            st.warning("El título no puede estar vacío")
                
                with col3:
                    if st.button("❌", key=f"cancel_{conv_id}", help="Cancelar"):
                        st.session_state.editing_title = None
                        st.rerun()
            
            else:
                # Modo normal
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    if st.button(
                        f"💬 {title}",
                        key=f"conv_{conv_id}",
                        use_container_width=True,
                        help=f"Creado: {created_at[:16]}"
                    ):
                        self._load_conversation(conv_id)
                
                with col2:
                    if st.button("✏️", key=f"edit_{conv_id}", help="Editar título"):
                        st.session_state.editing_title = conv_id
                        st.rerun()
                
                with col3:
                    if st.button("🗑️", key=f"del_{conv_id}", help="Eliminar conversación"):
                        self._delete_conversation_with_confirmation(conv_id)
    
    def _load_conversation(self, conv_id: int):
        """Carga una conversación específica"""
        st.session_state.current_conversation_id = conv_id
        st.session_state.editing_title = None
        
        # Cargar mensajes de la conversación
        messages_data = self.db_manager.load_conversation_messages(conv_id)
        st.session_state.messages = []
        
        for role, content, _ in messages_data:
            st.session_state.messages.append({"role": role, "content": content})
        
        st.rerun()
    
    def _delete_conversation_with_confirmation(self, conv_id: int):
        """Elimina una conversación con confirmación"""
        # Crear clave única para el estado de confirmación
        confirm_key = f"confirm_delete_{conv_id}"
        
        if confirm_key not in st.session_state:
            st.session_state[confirm_key] = False
        
        if not st.session_state[confirm_key]:
            st.session_state[confirm_key] = True
            st.rerun()
        else:
            # Eliminar la conversación
            if self.db_manager.delete_conversation(conv_id):
                # Si la conversación eliminada era la activa, resetear
                if (hasattr(st.session_state, 'current_conversation_id') and 
                    st.session_state.current_conversation_id == conv_id):
                    st.session_state.current_conversation_id = None
                    st.session_state.messages = []
                
                # Limpiar estado de confirmación
                del st.session_state[confirm_key]
                st.success("Conversación eliminada")
                st.rerun()
            else:
                st.error("Error al eliminar la conversación")
    
    def _render_stats(self):
        """Renderiza estadísticas en el sidebar"""
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ℹ️ Información")
        
        stats = self.db_manager.get_conversation_stats()
        
        st.sidebar.markdown(f"""
        - **Modelo**: GPT-4
        - **Versión**: U-Tutor v{self.version}
        - **Funciones**: 
          - ✅ Historial persistente
          - ✅ Múltiples conversaciones
          - ✅ Editar títulos
          - ✅ Eliminar conversaciones
          - ✅ Continuar chats anteriores
        """)
        
        if stats['total_conversations'] > 0:
            st.sidebar.markdown(f"**Total de conversaciones**: {stats['total_conversations']}")
            st.sidebar.markdown(f"**Total de mensajes**: {stats['total_messages']}")
    
    def render_main_chat_area(self):
        """Renderiza el área principal de chat"""
        st.title(f"🎓 U-Tutor v{self.version} - Tu asistente universitario")
        
        # Mostrar información de la conversación actual
        if hasattr(st.session_state, 'current_conversation_id') and st.session_state.current_conversation_id:
            conversation = self.db_manager.get_conversation_by_id(st.session_state.current_conversation_id)
            if conversation:
                st.info(f"📝 Conversación: **{conversation[1]}** (#{conversation[0]})")
        else:
            st.info("💭 Nueva conversación - Escribe tu primer mensaje para comenzar")
    
    def render_chat_messages(self, messages: List[dict]):
        """Renderiza los mensajes del chat"""
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    def show_error(self, message: str):
        """Muestra un mensaje de error"""
        st.error(message)
    
    def show_success(self, message: str):
        """Muestra un mensaje de éxito"""
        st.success(message)
    
    def show_spinner(self, text: str = "Procesando..."):
        """Muestra un spinner con texto"""
        return st.spinner(text)