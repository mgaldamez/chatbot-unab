# U-TUTOR v5.0 - Aplicación principal con funcionalidades de audio, streaming y manejo avanzado de errores
import os
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI

# Importar nuestros módulos
from database_manager import DatabaseManager
from chat_manager import ChatManager
from ui_components import UIComponents
from audio_manager import AudioManager

from PyPDF2 import PdfReader
import docx
import pandas as pd


# Cargar variables de entorno
load_dotenv()

class UTutorApp:
    def __init__(self):
        """Inicializa la aplicación U-TUTOR v5.0"""
        self.version = os.getenv("VERSION", "5s.0")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("MODEL", "gpt-4")

        # Configuración de la aplicación
        st.set_page_config(
            page_title=f"U-Tutor v{self.version}",
            page_icon="🎓", 
            layout="wide",
            initial_sidebar_state="expanded"
        )


        
        # Cargar CSS personalizado
        self._load_custom_css()
        
        # Inicializar componentes
        self.db_manager = DatabaseManager()
        self.ui_components = UIComponents(self.db_manager, self.version)
        self.audio_manager = AudioManager()
        
        # Hacer audio_manager disponible globalmente
        st.session_state.audio_manager = self.audio_manager
        
        if not self.api_key:
            st.error("❌ Por favor, configura tu OPENAI_API_KEY en el archivo .env")
            st.stop()

        # Inicializar con configuración guardada
        temperature = st.session_state.get('temperature', 1)
        
        self.chat_manager = ChatManager(self.api_key, self.model, temperature)
        
        # Hacer chat_manager disponible globalmente para generación de títulos
        st.session_state.chat_manager = self.chat_manager

        # Aplicar personalidad si existe
        if 'personality' in st.session_state:
            self.chat_manager.update_personality(st.session_state.personality)

        # Inicializar estado de la sesión
        self._init_session_state()
        
        # Aplicar cambios de configuración si los hay
        self._apply_settings_changes()     
        action = st.query_params.get("action")
        conv_id = st.query_params.get("id")

        if action and conv_id:
            conv_id = int(conv_id[0])
            action = action[0]
            if action == "download":
                self._export_conversation_direct(conv_id)
            elif action == "rename":
                st.session_state.editing_title = conv_id
                st.rerun()
            elif action == "delete":
                self._delete_conversation_direct(conv_id)
    def _apply_theme(self):
        """Aplica el tema seleccionado - U-TUTOR v5.0"""
        current_theme = st.session_state.get('theme', 'light')
        
        if current_theme == 'dark':
            st.markdown("""
            <style>
            /* Tema Oscuro - Paleta Profesional */
            .stApp {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%) !important;
                color: #e8e8e8 !important;
            }
            
            .main .block-container {
                background: transparent !important;
                color: #e8e8e8 !important;
                z-index: 1;

            }
                        
            .stVerticalBlock{
                gap:8px;
            }
            .st-dl{
                background-color: transparent;
            } 
            .st-aq{
                border-top-right-radius:1rem;
            }
            .st-ap{
                border-bottom-right-radius:1rem;
            }
            .st-ao{
                border-top-left-radius:1rem;
            }
            .st-an{
                border-bottom-left-radius:1rem;
            }
            
            .stChatMessage[data-testid="user"] .stChatMessage__content {
                background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%) !important;
                color: #a0c4ff !important;
                border: 1px solid #4a5568 !important;
                border-radius: 18px 18px 4px 18px !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
                gap:8px;
            }
            
            
            .stChatMessage[data-testid="assistant"] .stChatMessage__content {
                background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%) !important;
                color: #e2e8f0 !important;
                border: 1px solid #4a5568 !important;
                border-radius: 18px 18px 18px 4px !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
            }
            
            /* Sidebar oscuro */
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%) !important;
                border-right: 1px solid #4a5568 !important;
                z-index: 999;

            }
            
            [data-testid="stSidebarContent"] {
                color: #e8e8e8 !important;
                gap:16px !important;
            }
            
            [data-testid="stSidebarUserContent"] {
                color: #e8e8e8 !important;
            }
            
            /* Botones del sidebar oscuro */
            [data-testid="stSidebarContent"] .stButton button {
                background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%) !important;
                color: #a0c4ff !important;
                border: 1px solid #4a5568 !important;
                border-radius: 8px !important;
                font-weight: 500 !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
            }
            
            [data-testid="stSidebarContent"] .stButton button:hover {
                background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%) !important;
                color: #ffffff ;
                box-shadow: 0 4px 12px rgba(160, 196, 255, 0.3) !important;
                transform: translateY(-2px) !important;
            }
                [data-testid="stSidebarContent"] .stDownloadButton button {
                background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%) !important;
                color: #a0c4ff !important;
                border: 1px solid #4a5568 !important;
                border-radius: 8px !important;
                font-weight: 500 !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
            }
            
            [data-testid="stSidebarContent"] .stDownloadButton button:hover {
                background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%) !important;
                color: #ffffff ;
                box-shadow: 0 4px 12px rgba(160, 196, 255, 0.3) !important;
                transform: translateY(-2px) !important;
            }
            
            /* Input del sidebar oscuro */
            [data-testid="stSidebarContent"] .stTextInput input {
                background-color: #2d3748 !important;
                color: #e8e8e8 !important;
                border: 1px solid #4a5568 !important;
                border-radius: 8px !important;
            }
            
            [data-testid="stSidebarContent"] .stTextInput input:focus {
                border-color: #a0c4ff !important;
                box-shadow: 0 0 0 2px rgba(160, 196, 255, 0.2) !important;
            }
            
            /* Selectbox del sidebar oscuro */
            [data-testid="stSidebarContent"] .stSelectbox > div > div {
                background-color: #2d3748 !important;
                color: #e8e8e8 !important;
                border: 1px solid #4a5568 !important;
                border-radius: 8px !important;
            }
            
            /* Slider del sidebar oscuro */
            [data-testid="stSidebarContent"] .stSlider > div > div > div > div {
                background: linear-gradient(90deg, #a0c4ff 0%, #4a5568 100%) !important;
            }
            
            /* Expanders del sidebar oscuro */
            [data-testid="stSidebarContent"] .streamlit-expander {
                background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%) !important;
                border: 1px solid #4a5568 !important;
                border-radius: 8px !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
            }
            
            [data-testid="stSidebarContent"] .streamlit-expander .streamlit-expanderHeader {
                background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%) !important;
                color: #a0c4ff !important;
                border-radius: 8px 8px 0 0 !important;
            }
            
            [data-testid="stSidebarContent"] .streamlit-expander .streamlit-expanderContent {
                background: transparent !important;
                color: #e8e8e8 !important;
            }
            
            /* Texto del sidebar oscuro */
            [data-testid="stSidebarContent"] .stMarkdown {
                color: #e8e8e8 !important;
            }
            
            
                                   
            [data-testid="stSidebarContent"] h1, 
            [data-testid="stSidebarContent"] h2, 
            [data-testid="stSidebarContent"] h3 {
                color: #a0c4ff !important;
            }
            
            /* Chat input oscuro */
            .stChatInput > div > div > div > textarea {
                background-color: #2d3748 !important;
                color: #e8e8e8 !important;
                border: 1px solid #4a5568 !important;
                border-radius: 8px !important;
            }
            
            .stChatInput > div > div > div > textarea:focus {
                border-color: #a0c4ff !important;
                box-shadow: 0 0 0 2px rgba(160, 196, 255, 0.2) !important;
            }
            .st-dl{
                background-color: transparent;
            } 
            .st-aq{
                border-top-right-radius:1rem;
            }
            .st-ap{
                border-bottom-right-radius:1rem;
            }
            .st-ao{
                border-top-left-radius:1rem;
            }
            .st-an{
                border-bottom-left-radius:1rem;
            }
            /* Botones principales oscuros */
            .stButton > button {
                background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%) !important;
                color: #a0c4ff !important;
                border: 1px solid #4a5568 !important;
                border-radius: 8px !important;
                font-weight: 500 !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
            }
            
            .stButton > button:hover {
                background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%) !important;
                color: #ffffff !important;
                box-shadow: 0 4px 12px rgba(160, 196, 255, 0.3) !important;
                transform: translateY(-2px) !important;
            }
            
            /* Métricas oscuras */
            .stMetric {
                background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%) !important;
                border: 1px solid #4a5568 !important;
                border-radius: 8px !important;
                padding: 1rem !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
            }
            </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <style>
            /* Tema Gris - Paleta Profesional */
            [data-testid="stToolbar"]{
                .stAppDeployButton,
                #MainMenu {
                    display: none !important;
                }
                background: #0b1116;

            }
            .stApp {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
                color: #2c3e50 !important;
            }
            
            .main .block-container {
                background: transparent !important;
                color: #2c3e50 !important;
                z-index: 1;

            }
            .stVerticalBlock{
                gap:8px;
            }
            
            .st-dl{
                background-color: transparent;
            } 
            .st-aq{
                border-top-right-radius:1rem;
            }
            .st-ap{
                border-bottom-right-radius:1rem;
            }
            .st-ao{
                border-top-left-radius:1rem;
            }
            .st-an{
                border-bottom-left-radius:1rem;
            }
            .stChatMessage[data-testid="user"] .stChatMessage__content {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                color: #ffffff !important;
                border: 1px solid #5a67d8 !important;
                border-radius: 18px 18px 4px 18px !important;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
            }
            
            .stChatMessage[data-testid="assistant"] .stChatMessage__content {
                background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%) !important;
                color: #2d3748 !important;
                border: 1px solid #e2e8f0 !important;
                border-radius: 18px 18px 18px 4px !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
            }
            
            /* Sidebar gris */
            
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #ffffff 0%, #f7fafc 100%) !important;
                border-right: 1px solid #e2e8f0 !important;
            }
            
            [data-testid="stSidebarContent"] {
                background: transparent !important;
                color: #2d3748 !important;
                gap:16px !important;

            }
            
            [data-testid="stSidebarUserContent"] {
                background: transparent !important;
                color: #2d3748 !important;
            }
            
            /* Botones del sidebar gris */
            [data-testid="stSidebarContent"] .stButton button {
                color: #ffffff !important;
                border-radius: 4px !important;
                font-weight: 500 !important;
                justify-content: space-between;
                text-align: left;
            }
            
            [data-testid="stSidebarContent"] .stButton button:hover,
            [data-testid="stSidebarContent"] .stDownloadButton button:hover {
                background: linear-gradient(135deg, #5a67d8 0%, #667eea 100%) !important;
                color: #ffffff !important;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
                transform: translateY(-2px) !important;
            }
                        
            
            /* Input del sidebar gris */
            [data-testid="stSidebarContent"] .stTextInput input {
                color: #2d3748 !important;
                border: 1px solid #e2e8f0 !important;
                border-radius: 8px !important;
            }
            
            [data-testid="stSidebarContent"] .stTextInput input:focus {
                border-color: #667eea !important;
                box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
            }
            
            /* Selectbox del sidebar gris */
            [data-testid="stSidebarContent"] .stSelectbox > div > div {
                background-color: #ffffff !important;
                color: #2d3748 !important;
                border: 1px solid #e2e8f0 !important;
                border-radius: 8px !important;
            }
            
            /* Slider del sidebar gris */
            [data-testid="stSidebarContent"] .stSlider > div > div > div > div {
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
            }
            
            /* Expanders del sidebar gris */
            [data-testid="stSidebarContent"] .streamlit-expander {
                background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%) !important;
                border: 1px solid #e2e8f0 !important;
                border-radius: 8px !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
            }
            
            [data-testid="stSidebarContent"] .streamlit-expander .streamlit-expanderHeader {
                background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%) !important;
                color: #667eea !important;
                border-radius: 8px 8px 0 0 !important;
            }
            
            [data-testid="stSidebarContent"] .streamlit-expander .streamlit-expanderContent {
                background: transparent !important;
                color: #2d3748 !important;
            }
            
            /* Texto del sidebar gris */
            [data-testid="stSidebarContent"] .stMarkdown {
                color: #2d3748 !important;
            }
            
            [data-testid="stSidebarContent"] h1, 
            [data-testid="stSidebarContent"] h2, 
            [data-testid="stSidebarContent"] h3 {
                color: #667eea !important;
            }
            
            
            
            /* Botones principales grises */
            [data-testid="stBaseButton-secondary"],
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: #ffffff !important;
                border: 1px solid #5a67d8 !important;
                border-radius: 8px !important;
                font-weight: 500 !important;
                box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
            }
            
            .stButton > button:hover {
                background: linear-gradient(135deg, #5a67d8 0%, #667eea 100%) !important;
                color: #ffffff !important;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
                transform: translateY(-2px) !important;
            }
            
            /* Métricas grises */
            .stMetric {
                background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%) !important;
                border: 1px solid #e2e8f0 !important;
                border-radius: 8px !important;
                padding: 1rem !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
            }
            
            /* Responsive Design Mejorado */
            @media (max-width: 768px) {
                .stChatMessage[data-testid="user"] .stChatMessage__content,
                .stChatMessage[data-testid="assistant"] .stChatMessage__content {
                    max-width: 90% !important;
                    font-size: 14px !important;
                }
                
                [data-testid="stSidebarContent"] .stButton button {
                    padding: 0.4rem 0.8rem !important;
                    font-size: 12px !important;
                }
                
                .main .block-container {
                    padding: 0.5rem !important;
                    z-index: 1;

                }
            }
            
            @media (max-width: 480px) {
                .stChatMessage[data-testid="user"] .stChatMessage__content,
                .stChatMessage[data-testid="assistant"] .stChatMessage__content {
                    max-width: 95% !important;
                    padding: 8px 12px !important;
                    font-size: 13px !important;
                }
                
                [data-testid="stSidebarContent"] .stButton button {
                    padding: 0.3rem 0.6rem !important;
                    font-size: 11px !important;
                }
            }
            </style>
            """, unsafe_allow_html=True)
    
    def _load_custom_css(self):
        """Carga estilos CSS personalizados - U-TUTOR v5.0"""
        try:
            with open('styles.css') as f:
                css_content = f.read()
                
                # Aplicar tema dinámico
                current_theme = st.session_state.get('theme', 'light')
                if current_theme == 'dark':
                    css_content = css_content.replace('[data-theme="dark"]', '')
                    css_content += """
                    :root {
                        --light-bg: #1e1e1e;
                        --light-text: #ffffff;
                        --light-border: #404040;
                        --user-bubble-bg: #2d3748;
                        --user-bubble-text: #90cdf4;
                        --assistant-bubble-bg: #2d3748;
                        --assistant-bubble-text: #e2e8f0;
                    }
                    """
                
                st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
        except FileNotFoundError:
            pass  # Si no existe el archivo, continuar sin estilos personalizados
        
        # Atajos de teclado
        st.markdown("""
        <script>
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + N para nueva conversación
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                const newConvBtn = document.querySelector('button[kind="primary"]');
                if (newConvBtn) newConvBtn.click();
            }
            
            // Ctrl/Cmd + K para buscar
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('input[aria-label*="Buscar conversación"]');
                if (searchInput) searchInput.focus();
            }

            // Ctrl/Cmd + / para configuración
            if ((e.ctrlKey || e.metaKey) && e.key === '/') {
                e.preventDefault();
                const configBtn = document.querySelector('button[data-testid="config_button"]');
                if (configBtn) configBtn.click();
            }
        });
        </script>
        """, unsafe_allow_html=True)

    def _apply_settings_changes(self):
        """Aplica cambios de configuración si se modificaron - U-TUTOR v5.0"""
        if st.session_state.get('settings_changed', False):
            # Actualizar temperatura
            self.chat_manager.update_temperature(st.session_state.temperature)
            
            # Actualizar personalidad
            self.chat_manager.update_personality(st.session_state.personality)
            
            # Limpiar flag
            st.session_state.settings_changed = False

    def _init_session_state(self):
        """Inicializa el estado de la sesión - U-TUTOR v5.0"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "current_conversation_id" not in st.session_state:
            st.session_state.current_conversation_id = None
        
        if "editing_title" not in st.session_state:
            st.session_state.editing_title = None
        
        if "pending_message" not in st.session_state:
            st.session_state.pending_message = None
        
        if "current_audio" not in st.session_state:
            st.session_state.current_audio = None
        
        if "voice_input_active" not in st.session_state:
            st.session_state.voice_input_active = False
        
        if "menu_counter" not in st.session_state:
            st.session_state.menu_counter = 0
        # Inicializar flag de espera de respuesta
        if "await_response" not in st.session_state:
            st.session_state.await_response = False
    
    def run(self):
        """Ejecuta la aplicación principal - U-TUTOR v5.0"""
        # Aplicar tema dinámico
        self._apply_theme()
        
        # Renderizar sidebar
        self.ui_components.render_sidebar()
      
        
        # Renderizar área principal de chat
        self.ui_components.render_main_chat_area()
        
        # Renderizar página de configuración si está activa
        self.ui_components.render_config_page()
        
        # Mostrar historial de mensajes (debe mostrarse antes del input)
        self.ui_components.render_chat_messages(st.session_state.messages)

        # Si hay una respuesta pendiente por parte del asistente, generarla aquí
        if st.session_state.get('await_response'):
            # Clear flag first to avoid re-entrancy during generation
            st.session_state.await_response = False
            self._generate_assistant_response()

        # Reproducir audio si está solicitado
        self._handle_audio_playback()

        # Manejar mensaje pendiente de sugerencias
        if st.session_state.pending_message:
            self._process_pending_message()

        # Controles de entrada (texto y voz)
        self._render_input_controls()

    def _handle_audio_playback(self):
        """Maneja la reproducción de audio de mensajes - U-TUTOR v5.0"""
        if st.session_state.current_audio:
            tts_lang = st.session_state.get('tts_language', 'es')
            
            try:
                # Mostrar información sobre el idioma del audio
                lang_name = "Español" if tts_lang == 'es' else "Inglés"
                if tts_lang == 'en':
                    st.info(f"🌐 Reproduciendo audio en {lang_name} (traducido)")
                else:
                    st.info(f"🎵 Reproduciendo audio en {lang_name}")
                
                # Mostrar indicador de generación de audio con información de velocidad
                cache_size = self.audio_manager.get_cache_size()
                if cache_size > 0:
                    st.info(f"⚡ Caché activo: {cache_size} archivos guardados para reproducción rápida")
                
                with st.spinner(f"🎵 Generando audio en {lang_name}..."):
                    import time
                    start_time = time.time()
                    
                    audio_file = self.audio_manager.text_to_speech(
                        st.session_state.current_audio, 
                        lang=tts_lang
                    )
                    
                    generation_time = time.time() - start_time
                    
                    # Mostrar tiempo de generación
                    if generation_time < 2:
                        st.success(f"⚡ Audio generado en {generation_time:.1f}s (rápido)")
                    elif generation_time < 5:
                        st.info(f"⏱️ Audio generado en {generation_time:.1f}s (normal)")
                    else:
                        st.warning(f"🐌 Audio generado en {generation_time:.1f}s (lento - verifica tu conexión)")
                
                if audio_file and os.path.exists(audio_file):
                    # Leer archivo de audio
                    with open(audio_file, 'rb') as audio:
                        audio_bytes = audio.read()
                    
                    # Determinar formato del archivo
                    audio_format = 'audio/wav' if audio_file.endswith('.wav') else 'audio/mp3'
                    
                    # Reproducir audio
                    st.audio(audio_bytes, format=audio_format, autoplay=True)
                    
                    # Mostrar información del archivo
                    file_size = len(audio_bytes)
                    if file_size < 50000:  # Menos de 50KB
                        st.info(f"📁 Archivo pequeño: {file_size} bytes (rápido)")
                    else:
                        st.info(f"📁 Archivo: {file_size} bytes")
                    
                    # Limpiar archivo temporal solo si no está en caché
                    try:
                        # Verificar si está en caché antes de eliminar
                        cache_key = f"{st.session_state.current_audio[:200]}_{tts_lang}"
                        if cache_key not in self.audio_manager.audio_cache:
                            os.remove(audio_file)
                    except:
                        pass
                else:
                    st.error("❌ No se pudo generar el archivo de audio")
                
                # Limpiar después de reproducir
                st.session_state.current_audio = None
                
            except Exception as e:
                st.error(f"❌ Error al reproducir audio: {str(e)}")
                st.session_state.current_audio = None

    def _process_pending_message(self):
        """Procesa mensaje pendiente de sugerencias rápidas - U-TUTOR v5.0"""
        prompt = st.session_state.pending_message
        st.session_state.pending_message = None
        
        # Procesar como mensaje normal
        self._process_user_message(prompt)
        

  # ------------------ Render input y uploader ------------------
    def _render_input_controls(self):
        """Renderiza controles de entrada de texto - U-TUTOR v5.0"""
        
        # No mostrar input si estamos en la página de configuración
        if st.session_state.show_config_page:
            return
        
        # Input de texto normal (sin funcionalidad de voz)
        self._handle_user_input()


    # ------------------ RENDER INPUT Y UPLOADER ------------------
    def _render_input_controls(self):
        """Renderiza controles de entrada de texto - U-TUTOR v5.0"""
        
        # No mostrar input si estamos en la página de configuración
        if st.session_state.show_config_page:
            return
        
        # Input de texto normal (sin funcionalidad de voz)
        self._handle_user_input()


    # ------------------ MANEJO DE INPUT ------------------
    def _handle_user_input(self):
        """
        Maneja la entrada de texto del usuario - U-TUTOR v5.0
        """

        # 1️⃣ No mostrar input si estamos en la página de configuración
        if st.session_state.get("show_config_page"):
            return

        # 2️⃣ Inicializar estados necesarios
        if "user_input" not in st.session_state:
            st.session_state.user_input = ""

        if "clear_input" not in st.session_state:
            st.session_state.clear_input = False

        # Limpiar input si se indicó
        if st.session_state.clear_input:
            st.session_state.user_input = ""
            st.session_state.clear_input = False

        # 3️⃣ Renderizar contenedor del input
        with st.container():
            st.markdown("""
                <div style="display:flex; justify-content:center; width:50%; margin:10px 0;">
                    <div style="width:50%; max-width:10px;">
                """, unsafe_allow_html=True)

            # 4️⃣ Columnas: input ocupa la mayoría del ancho, botón el resto
            col_spacer, col_input, col_button, col_spacer2 = st.columns([3, 6, 1, 2], gap="small")

            # 5️⃣ Input de texto
            with col_input:
                prompt = st.text_input(
                    label="",
                    key="user_input",
                    placeholder="Escribe tu mensaje...",
                    label_visibility="collapsed"
                )

            # 6️⃣ Botón de enviar
            with col_button:
                send_button = st.button("➤", use_container_width=True)

            st.markdown(" ")  # Espaciado extra si hace falta

            # 7️⃣ Detectar si el usuario envió el mensaje
            if (send_button or (prompt and prompt.strip() != "")) and not st.session_state.get("await_response", False):
                
                current_prompt = prompt.strip()

                # 8️⃣ Procesar el mensaje
                self._process_user_message(current_prompt)

                # 9️⃣ Limpiar input en el próximo rerun
                st.session_state.clear_input = True

                # 10️⃣ Forzar rerun para actualizar la UI
                st.rerun()


    # ------------------ Procesar mensaje del usuario ------------------
    def _process_user_message(self, prompt: str):
        """
        Procesa un mensaje del usuario (desde texto o voz) - U-TUTOR v5.0
        """

        # 1️⃣ Validar mensaje
        is_valid, error_message = self.chat_manager.validate_message(prompt)
        if not is_valid:
            self.ui_components.show_error(error_message)
            return

        # 2️⃣ Crear nueva conversación si no existe
        if st.session_state.current_conversation_id is None:
            conversation_title = self.chat_manager.generate_conversation_title(prompt)
            st.session_state.current_conversation_id = self.db_manager.create_conversation(conversation_title)

        # 3️⃣ Agregar mensaje del usuario al historial de la sesión
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # 4️⃣ Guardar mensaje en la base de datos
        self.db_manager.save_message(
            st.session_state.current_conversation_id,
            "user",
            prompt
        )

        # 5️⃣ Sincronizar el historial desde la base de datos
        try:
            messages_data = self.db_manager.load_conversation_messages(
                st.session_state.current_conversation_id
            )
            st.session_state.messages = [
                {"role": role, "content": content} for role, content, _ in messages_data
            ]
        except Exception:
            # Si falla la carga, mantenemos el mensaje en session_state
            pass

        # 6️⃣ Marcar que estamos esperando la respuesta del asistente
        st.session_state.await_response = True


    def _generate_assistant_response(self):
        """
        Genera y muestra la respuesta del asistente con streaming - U-TUTOR v5.0
        """
        try:
            placeholder = st.empty()  # Placeholder para el spinner / mensaje temporal

            with self.ui_components.show_spinner("🤔 Jake está pensando..."):

                full_response = ""

                # 1️⃣ Recolectar respuesta en streaming
                for chunk in self.chat_manager.get_response_stream(st.session_state.messages):
                    if hasattr(chunk, 'content') and chunk.content:
                        full_response += chunk.content

                # 2️⃣ Post-procesar traducción para TTS si aplica
                tts_language = st.session_state.get('tts_language', 'es')
                auto_translate = st.session_state.get('auto_translate', True)

                if tts_language == 'en' and auto_translate:
                    translated_response = self.chat_manager.translate_text(full_response, 'en')
                    audio_response = translated_response if translated_response != full_response else full_response
                else:
                    audio_response = full_response

                # 3️⃣ Guardar mensaje del asistente en sesión y DB
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })
                self.db_manager.save_message(
                    st.session_state.current_conversation_id,
                    "assistant",
                    full_response
                )

                # 4️⃣ Renderizar inmediatamente la burbuja del asistente
                if full_response.strip():
                    try:
                        self.ui_components.render_chat_messages([
                            {"role": "assistant", "content": full_response}
                        ])
                    except Exception:
                        pass

                # 5️⃣ Placeholder para botones de audio si quieres agregar
                col1, col2 = st.columns([1, 10])

        except Exception as e:
            self._handle_api_error(e)

    

    def _handle_api_error(self, error: Exception):
        """Maneja errores de la API con mensajes específicos - U-TUTOR v5.0"""
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        if "rate_limit" in error_str or "429" in error_str:
            st.error("⏳ **Límite de solicitudes alcanzado**")
            st.info("Has realizado demasiadas solicitudes. Por favor, espera unos minutos antes de intentar nuevamente.")
        
        elif "api_key" in error_str or "401" in error_str or "authentication" in error_str:
            st.error("🔑 **Error de autenticación**")
            st.warning("Hay un problema con tu API Key de OpenAI. Verifica tu archivo .env")
        
        elif "timeout" in error_str or "timed out" in error_str:
            st.error("⌛ **Tiempo de espera agotado**")
            st.info("La solicitud tardó demasiado. Intenta con un mensaje más corto o simplifica tu pregunta.")
        
        elif "connection" in error_str or "network" in error_str:
            st.error("🌐 **Error de conexión**")
            st.info("No se pudo conectar con el servidor. Verifica tu conexión a internet.")
        
        elif "quota" in error_str or "insufficient" in error_str:
            st.error("💳 **Cuota excedida**")
            st.warning("Has alcanzado el límite de tu plan de OpenAI. Verifica tu cuenta en OpenAI.")
        
        elif "invalid" in error_str and "model" in error_str:
            st.error("🤖 **Modelo no válido**")
            st.warning(f"El modelo '{self.model}' no está disponible. Verifica tu configuración en .env")
        
        else:
            st.error(f"❌ **Error inesperado**: {error_type}")
            st.warning("Ocurrió un error al procesar tu solicitud. Por favor, intenta nuevamente.")
        
        # Detalles técnicos en expander (para debugging)
        with st.expander("🔧 Detalles técnicos (para desarrolladores)"):
            st.code(f"""
Tipo de error: {error_type}
Mensaje: {str(error)}

Modelo: {self.model}
Temperatura: {st.session_state.get('temperature', 'N/A')}
Conversación ID: {st.session_state.get('current_conversation_id', 'N/A')}
            """)

st.markdown("""
<script>
window.addEventListener('message', event => {
    const data = event.data;
    if (data.type === 'menu_action') {
        fetch(`?action=${data.action}&id=${data.id}`, {method:'POST'});
    }
});
</script>
""", unsafe_allow_html=True)

def main():
    """Función principal - U-TUTOR v5.0"""
    app = UTutorApp()
    app.run()


if __name__ == "__main__":
    main()