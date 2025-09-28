import os
from dotenv import load_dotenv
import streamlit as st

# Importar nuestros módulos
from database_manager import DatabaseManager
from chat_manager import ChatManager
from ui_components import UIComponents

# Cargar variables de entorno
load_dotenv()

class UTutorApp:
    def __init__(self):

        self.version = os.getenv("VERSION", "1.0")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("MODEL", "gpt-4")


        # Configuración de la aplicación
        st.set_page_config(
            page_title=f"U-Tutor v{self.version}",
            page_icon="🎓", 
            layout="wide"
        )
        
        # Inicializar componentes
        self.db_manager = DatabaseManager()
        self.ui_components = UIComponents(self.db_manager, self.version, self.model)
        
        if not self.api_key:
            st.error("❌ Por favor, configura tu OPENAI_API_KEY en el archivo .env")
            st.stop()

        self.chat_manager = ChatManager(self.api_key, self.model)

        # Inicializar estado de la sesión
        self._init_session_state()
    
    def _init_session_state(self):
        """Inicializa el estado de la sesión"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "current_conversation_id" not in st.session_state:
            st.session_state.current_conversation_id = None
        
        if "editing_title" not in st.session_state:
            st.session_state.editing_title = None
    
    def run(self):
        """Ejecuta la aplicación principal"""
        # Renderizar sidebar
        self.ui_components.render_sidebar()
        
        # Renderizar área principal de chat
        self.ui_components.render_main_chat_area()
        
        # Mostrar historial de mensajes
        self.ui_components.render_chat_messages(st.session_state.messages)
        
        # Manejar input del usuario
        self._handle_user_input()
    
    def _handle_user_input(self):
        """Maneja la entrada del usuario y genera respuestas"""
        if prompt := st.chat_input("Escribe tu mensaje..."):
            # Validar mensaje
            if not self.chat_manager.validate_message(prompt):
                self.ui_components.show_error("Por favor, escribe un mensaje válido.")
                return
            
            # Si es una nueva conversación, crearla
            if st.session_state.current_conversation_id is None:
                conversation_title = self.chat_manager.generate_conversation_title(prompt)
                st.session_state.current_conversation_id = self.db_manager.create_conversation(conversation_title)
            
            # Mostrar mensaje del usuario
            st.chat_message("user").markdown(prompt)
            
            # Agregar mensaje del usuario al historial de la sesión
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Guardar mensaje del usuario en la base de datos
            self.db_manager.save_message(
                st.session_state.current_conversation_id, 
                "user", 
                prompt
            )
            
            # Generar y mostrar respuesta del asistente
            self._generate_assistant_response()
    
    def _generate_assistant_response(self):
        """Genera y muestra la respuesta del asistente"""
        with st.chat_message("assistant"):
            with self.ui_components.show_spinner("Jake está pensando..."):
                try:
                    # Obtener respuesta del modelo
                    response = self.chat_manager.get_response(st.session_state.messages)
                    
                    # Mostrar respuesta
                    st.markdown(response)
                    
                    # Agregar respuesta al historial de la sesión
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Guardar respuesta en la base de datos
                    self.db_manager.save_message(
                        st.session_state.current_conversation_id, 
                        "assistant", 
                        response
                    )
                    
                except Exception as e:
                    error_message = f"Error al obtener respuesta: {str(e)}"
                    self.ui_components.show_error(error_message)
                    st.error(f"Detalles técnicos: {e}")


def main():
    """Función principal"""
    app = UTutorApp()
    app.run()


if __name__ == "__main__":
    main()