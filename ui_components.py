# U-TUTOR v5.0 - Mejoras en ui_components.py: Sidebar avanzado, configuración y controles de audio
import io
import streamlit as st
import time
import os
from typing import List, Tuple, Optional
from database_manager import DatabaseManager
from TTSManager import TTSManager

@st.cache_resource
def get_tts_manager():
    """Cachea el TTSManager para evitar reinicializaciones - OPTIMIZACION"""
    tts_engine = os.getenv("TTS_ENGINE", "edge-tts")
    return TTSManager(engine_type=tts_engine)

class UIComponents:
    def __init__(self, db_manager: DatabaseManager, version: str):
        """Inicializa UIComponents con estados de sesión - U-TUTOR v5.0"""
        self.db_manager = db_manager
        self.version = os.getenv("VERSION", "5.0")
        self.tts_manager = get_tts_manager()
        # Inicializar estados de sesión necesarios
        if 'theme' not in st.session_state:
            st.session_state.theme = 'blueish'
        
        if 'show_stats' not in st.session_state:
            st.session_state.show_stats = False
            
        if 'show_config_page' not in st.session_state:
            st.session_state.show_config_page = False
        
        # Configuraciones fijas (sin opciones de inglés)
        if 'tts_language' not in st.session_state:
            st.session_state.tts_language = 'es'
        
        if 'auto_translate' not in st.session_state:
            st.session_state.auto_translate = False

    def _get_theme_css(self) -> str:
        """Genera CSS minimal - ahora delegado a styles_modern.css"""
        # Los estilos están en styles_modern.css - este método solo retorna estilos de tema
        return ""  # Vacío porque main.py maneja los temas ahora

    def _get_theme_css_legacy(self) -> str:
        """Mantener legacy solo como referencia"""
        theme = st.session_state.get('theme', 'blueish')

        if theme == 'lilac':
            return """
            <style>
            :root{ --u-tutor-bg: #120018; --u-tutor-sidebar-bg: #0b0012; --u-tutor-accent: #DA70D6; --u-tutor-input-bg: #2a003b; }
            html, body, .stApp, .block-container, [data-testid="stAppViewContainer"] {
                background: var(--u-tutor-bg) !important;
                color: #E6E6FA !important;
            }
            /* Sidebar and left panel selectors (multiple fallbacks for Streamlit class names) */
            /* Force a darker sidebar background and remove inner white cards/shadows so the panel is visually consistent */
            .sidebar .sidebar-content, [data-testid="stSidebar"], .stSidebar, nav[aria-label="Sidebar"], div[role="complementary"], .css-1avcm0n, .css-1lcbmhc, .css-1y0tads, .css-1d391kg, [data-testid="stSidebarContent"], [data-testid="stSidebarUserContent"] {
                background-color: #0b0012 !important; /* darker variant of theme background */
                color: #E6E6FA !important;
            }
            /* Make inner Streamlit cards and containers transparent so the sidebar color shows through */
            [data-testid="stSidebar"] > div, .stSidebar > div, .sidebar .sidebar-content *, [data-testid="stSidebarContent"] *, [data-testid="stSidebarUserContent"] * {
                background: transparent !important;
                color: inherit !important;
            }
            .stInfo{ background-color: #2a003b !important; color: #E6E6FA !important; }
            .u-tutor-chat-header { background: linear-gradient(90deg, #663399 0%, #8A2BE2 100%) !important; color: #FFFFFF !important; border-radius:10px; padding:12px; }
            .u-tutor-bubble-user { background: #DDA0DD !important; color: #4B0082 !important; border-radius:12px; padding:10px; display:inline-block; }
            .u-tutor-bubble-assistant { background: #663399 !important; color: #FFFFFF !important; border-radius:12px; padding:10px; display:inline-block; }
            button[role="button"], .stButton>button { background-color: #663399 !important; color: #FFFFFF !important; border-radius:6px; }
            .u-tutor-accent { color: #DA70D6 !important; }
            /* Inputs, textareas, chat input area */
            input, textarea, .stTextInput>div>div>input, .stTextArea>div>div>textarea, [data-testid="stTextInput"] input {
                background: #2a003b !important;
                color: #E6E6FA !important;
                border-color: #663399 !important;
            }
            /* Form input (st.text_input inside our form) */
            /* target multiple possible wrappers and the explicit custom_prompt id */
            input#custom_prompt, input[id^="custom_prompt"], div[data-baseweb="input"] input, .stTextInput>div>div>input, .stTextInput input, input[type="text"] {
                background: #2a003b !important;
                color: #E6E6FA !important;
                border: 1px solid #663399 !important;
                border-radius: 20px !important;
                padding: 10px !important;
                box-shadow: none !important;
            }
            /* Chat message input (Streamlit specific) */
            [data-testid="stChatMessageInput-area"], [data-testid="stChatMessageInput"] {
                background: transparent !important;
            }
            /* Hide Streamlit's 'Press Enter to submit form' helper and similar tooltips */
            .stTextInput small, .stForm small, .stForm div[role="status"], .stTextInput .css-.* { display: none !important; }
            .stForm [title*="Press Enter"], [data-testid="stForm"] [title*="Press Enter"] { display: none !important; }
            /* Bottom bar / send button */
            .stButton>button, button[role="button"] { background-color: #663399 !important; color: #FFFFFF !important; }

            /* Sidebar search/input in Lilac theme */
            [data-testid="stSidebarContent"] .stTextInput input, [data-testid="stSidebarContent"] input[placeholder] {
                background: var(--u-tutor-input-bg) !important;
                color: #E6E6FA !important;
                border: 1px solid #663399 !important;
                border-radius: 8px !important;
                padding: 8px !important;
            }
            [data-testid="stSidebarContent"] .stTextInput input::placeholder,
            [data-testid="stSidebarContent"] input[placeholder]::placeholder {
                color: rgba(230,230,250,0.6) !important;
            }

            /* Fix form to bottom so it behaves like chat_input */
            /* Keep chat wrapper padded so content doesn't hide behind the bottom input area */
            /* Let the form stay in its container; style the input to look like a fixed bar without moving it in the DOM */
            .u-tutor-chat .stForm, .u-tutor-chat form, form#chat_form, form[data-testid="stForm"] {
                width: min(1100px, calc(100% - 48px)) !important;
                margin: 0 auto !important;
                display:flex !important;
                gap:10px !important;
                align-items:center !important;
                background: transparent !important;
            }
            .u-tutor-chat .stTextInput>div>div>input#custom_prompt, .u-tutor-chat input#custom_prompt { flex: 1 1 auto !important; }
            .u-tutor-chat .stButton>button { flex: 0 0 auto !important; border-radius: 999px !important; padding: 10px 18px !important; }

            /* Chat layout: grid with two columns so left/right bubbles align vertically */
            .u-tutor-chat { max-width: 1100px; margin: 0 auto; }
            .u-tutor-chat .u-tutor-messages { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 12px; width: 100%; padding: 8px 12px 24px 12px; box-sizing: border-box; align-items: start; }
            /* Each message is a grid child; place assistant messages in column 1 and user messages in column 2 */
            .u-tutor-chat .u-tutor-message { display: block; width: 100%; margin: 0; box-sizing: border-box; }
            .u-tutor-chat .u-tutor-message.assistant { grid-column: 1; justify-self: start; }
            .u-tutor-chat .u-tutor-message.user { grid-column: 2; justify-self: end; }
            /* Inner row groups avatar + bubble; for user rows we reverse direction so avatar sits at the right-start */
            .u-tutor-chat .u-tutor-message .row-inner { display:flex; align-items:center; gap:8px; }
            .u-tutor-chat .u-tutor-message.user .row-inner { flex-direction: row-reverse; }
            /* Set max-width to 75% for both bubble types and keep compact spacing */
            .u-tutor-chat .u-tutor-bubble-user, .u-tutor-chat .u-tutor-bubble-assistant { max-width: 75%; word-break: break-word; padding: 12px 14px; border-radius: 14px; position: relative; box-shadow: 0 6px 18px rgba(6,10,33,0.08); display: inline-block; }
            /* Slightly flatten the inner corner to feel like a chat tail */
            .u-tutor-chat .u-tutor-bubble-user { border-bottom-right-radius: 6px !important; }
            .u-tutor-chat .u-tutor-bubble-assistant { border-bottom-left-radius: 6px !important; }

            /* Add subtle pseudo-element 'tail' for clearer speaker direction */
            .u-tutor-chat .u-tutor-bubble-assistant::after, .u-tutor-chat .u-tutor-bubble-user::after {
                content: "";
                position: absolute;
                width: 12px;
                height: 12px;
                bottom: 6px;
                transform: rotate(45deg);
                box-shadow: 0 6px 18px rgba(6,10,33,0.06);
            }
            .u-tutor-chat .u-tutor-bubble-assistant::after { left: -6px; background: inherit; }
            .u-tutor-chat .u-tutor-bubble-user::after { right: -6px; background: inherit; }

            /* Reduce top/bottom spacing and make bubbles compact */
            .u-tutor-chat .u-tutor-message { align-items: center; }
            .u-tutor-chat .u-tutor-messages { gap: 6px; }

            /* Avatars for assistant and user */
            .u-tutor-chat .u-tutor-avatar { width: 36px; height: 36px; flex: 0 0 36px; border-radius: 50%; display:flex; align-items:center; justify-content:center; font-size:16px; color: inherit; background: rgba(255,255,255,0.02); }
            .u-tutor-chat .u-tutor-avatar.assistant { margin-right: 10px; }
            .u-tutor-chat .u-tutor-avatar.user { margin-left: 10px; }

            /* Force sidebar hard overrides to prevent Streamlit default white panels */
            [data-testid="stSidebar"], [data-testid="stSidebar"] > div, [data-testid="stSidebarContent"], [data-testid="stSidebarUserContent"], .stSidebar, .sidebar, .css-1y0tads, .css-1avcm0n, .css-1lcbmhc, .css-1d391kg {
                background-color: var(--u-tutor-sidebar-bg) !important;
                background-image: none !important;
                color: #E6E6FA !important;
                box-shadow: none !important;
            }

            [data-testid="stSidebarContent"] *, [data-testid="stSidebarUserContent"] * {
                background: transparent !important;
                color: inherit !important;
                box-shadow: none !important;
                border: none !important;
            }
            /* Force main content background to the theme background (override earlier transparent rules) */
            body .stApp .main .block-container, body .stApp .block-container, .main .block-container {
                background: var(--u-tutor-bg) !important;
                min-height: 100vh !important;
                color: inherit !important;
                box-shadow: none !important;
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
            /* Métricas visibles con contraste - Lilac */
            [data-testid="stMetric"] {
                background: linear-gradient(135deg, #663399 0%, #8A2BE2 100%) !important;
                border: 1px solid #DA70D6 !important;
                border-radius: 8px !important;
                padding: 1rem !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
            }
            [data-testid="stMetricLabel"] {
                color: #DDA0DD !important;
            }
            [data-testid="stMetricValue"] {
                color: #FFFFFF !important;
                font-size: 1.5rem !important;
                font-weight: bold !important;
            }
            </style>
            """

        # Blueish theme: oscuro/azulado (predeterminado)
        if theme == 'blueish':
            return """
            <style>
            :root{ --u-tutor-bg: #0b1116; --u-tutor-sidebar-bg: #05070a; --u-tutor-accent: #a0c4ff; --u-tutor-input-bg: #0f1720; }
            html, body, .stApp, .block-container, [data-testid="stAppViewContainer"] {
                background: var(--u-tutor-bg) !important;
                color: #E6E6FA !important;
            }
            /* Sidebar: darker variant for blueish theme */
            .sidebar .sidebar-content, [data-testid="stSidebar"], .stSidebar, nav[aria-label="Sidebar"], div[role="complementary"], .css-1avcm0n, .css-1lcbmhc, .css-1y0tads, .css-1d391kg, [data-testid="stSidebarContent"], [data-testid="stSidebarUserContent"] {
                background-color: #05070a !important; /* darker variant of blueish bg */
                color: #E6E6FA !important;
            }
            [data-testid="stSidebar"] > div, .stSidebar > div, .sidebar .sidebar-content *, [data-testid="stSidebarContent"] *, [data-testid="stSidebarUserContent"] * {
                background: transparent !important;
                color: inherit !important;
            }
            .stInfo,{ background-color: #12202a !important; color: #dbeefb !important; }
            .u-tutor-chat-header { background: linear-gradient(90deg, #2d3748 0%, #4a5568 100%) !important; color: #e8e8e8 !important; border-radius:10px; padding:12px; }
            .u-tutor-bubble-user { background: #2b3a4a !important; color: #a0c4ff !important; border-radius:12px; padding:10px; display:inline-block; }
            .u-tutor-bubble-assistant { background: #1b2a36 !important; color: #a0c4ff !important; border-radius:12px; padding:10px; display:inline-block; }
            button[role="button"], .stButton>button { background-color: #14232a !important; color: #dbeefb !important; border-radius:6px; }
            .u-tutor-accent { color: #a0c4ff !important; }
            /* Inputs, textareas, chat input area */
            input, textarea, .stTextInput>div>div>input, .stTextArea>div>div>textarea, [data-testid="stTextInput"] input {
                background: #0f1720 !important;
                color: #E6E6FA !important;
                border-color: #2d3748 !important;
            }
            /* Form input (st.text_input inside our form) */
            div[data-baseweb="input"] input, .stTextInput>div>div>input#custom_prompt {
                background: #0f1720 !important;
                color: #E6E6FA !important;
                border: 1px solid #2d3748 !important;
                border-radius: 20px !important;
                padding: 10px !important;
            }
            /* Chat message input (Streamlit specific) */
            [data-testid="stChatMessageInput-area"], [data-testid="stChatMessageInput"] {
                background: transparent !important;
            }
            /* Hide Streamlit's 'Press Enter to submit form' helper and similar tooltips */
            .stTextInput small, .stForm small, .stForm div[role="status"], .stTextInput .css-.* { display: none !important; }
            .stForm [title*="Press Enter"], [data-testid="stForm"] [title*="Press Enter"] { display: none !important; }
            /* Bottom bar / send button */
            .stButton>button, button[role="button"] { background-color: #14232a !important; color: #dbeefb !important; }

            /* Sidebar search/input in Blueish theme */
            [data-testid="stSidebarContent"] .stTextInput input, [data-testid="stSidebarContent"] input[placeholder] {
                background: var(--u-tutor-input-bg) !important;
                color: #E6E6FA !important;
                border: 1px solid #2d3748 !important;
                border-radius: 8px !important;
                padding: 8px !important;
            }
            [data-testid="stSidebarContent"] .stTextInput input::placeholder,
            [data-testid="stSidebarContent"] input[placeholder]::placeholder {
                color: rgba(230,230,250,0.55) !important;
            }

            /* Fix form to bottom so it behaves like chat_input */
            /* Keep chat wrapper padded so content doesn't hide behind the bottom input area */
            /* Let the form stay in its container; style the input to look like a fixed bar without moving it in the DOM */
            .u-tutor-chat .stForm, .u-tutor-chat form, form#chat_form, form[data-testid="stForm"] {
                width: min(1100px, calc(100% - 48px)) !important;
                margin: 0 auto !important;
                display:flex !important;
                gap:10px !important;
                align-items:center !important;
                background: transparent !important;
            }
            .u-tutor-chat .stTextInput>div>div>input#custom_prompt, .u-tutor-chat input#custom_prompt { flex: 1 1 auto !important; }
            .u-tutor-chat .stButton>button { flex: 0 0 auto !important; border-radius: 999px !important; padding: 10px 18px !important; }

            /* Force sidebar hard overrides to prevent Streamlit default white panels */
            [data-testid="stSidebar"], [data-testid="stSidebar"] > div, [data-testid="stSidebarContent"], [data-testid="stSidebarUserContent"], .stSidebar, .sidebar, .css-1y0tads, .css-1avcm0n, .css-1lcbmhc, .css-1d391kg {
                background-color: var(--u-tutor-sidebar-bg) !important;
                background-image: none !important;
                color: #E6E6FA !important;
                box-shadow: none !important;
                border: none !important;
            }

            [data-testid="stSidebarContent"] *, [data-testid="stSidebarUserContent"] * {
                background: transparent !important;
                color: inherit !important;
                box-shadow: none !important;
                border: none !important;
            }

            /* Métricas visibles con contraste */
            [data-testid="stMetric"] {
                background: linear-gradient(135deg, #1b2a36 0%, #2d3748 100%) !important;
                border: 1px solid #4a5568 !important;
                border-radius: 8px !important;
                padding: 1rem !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
            }
            [data-testid="stMetricLabel"] {
                color: #a0c4ff !important;
            }
            [data-testid="stMetricValue"] {
                color: #e8e8e8 !important;
                font-size: 1.5rem !important;
                font-weight: bold !important;
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
            /* Force main content background to the theme background (override earlier transparent rules) */
            body .stApp .main .block-container, body .stApp .block-container, .main .block-container {
                background: var(--u-tutor-bg) !important;
                min-height: 100vh !important;
                color: inherit !important;
                box-shadow: none !important;
            }
            </style>
            """

        # Fallback ligero
        return """
        <style>
        html, body, .stApp, .block-container { background: #E6E6FA !important; color: #4B0082 !important; }
        .u-tutor-bubble-user { background: #DDA0DD !important; color: #4B0082 !important; }
        .u-tutor-bubble-assistant { background: #663399 !important; color: #FFFFFF !important; }
        </style>
        """

    def _apply_theme(self):
        """Aplica el tema actual - Delegado a main.py"""
        # El tema ahora se aplica desde main.py
        pass
    def render_model_selector(self):
        import os
        import streamlit as st
        from langchain_openai import ChatOpenAI

        # Lista de modelos: se puede personalizar desde .env con AVAILABLE_MODELS
        default_models = [
            "gpt-4-turbo",
            "gpt-4",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
        ]

        # Permitir personalización desde variable de entorno
        custom_models = os.getenv("AVAILABLE_MODELS", "")
        if custom_models:
            AVAILABLE_MODELS = [m.strip() for m in custom_models.split(",")]
        else:
            AVAILABLE_MODELS = default_models

        # FIX: Verificar si se está generando para deshabilitar selector
        is_generating = st.session_state.get('await_response', False)

        selected_model = st.sidebar.selectbox(
            "🤖 Modelo de IA",
            AVAILABLE_MODELS,
            key="selected_model",
            disabled=is_generating  # 🔴 BLOQUEAR DURANTE GENERACIÓN
        )

        if "chat_manager" in st.session_state:
            chat_manager = st.session_state.chat_manager
            current_model = getattr(chat_manager.llm, "model_name", None)

            if selected_model != current_model:
                kwargs = {
                    "model_name": selected_model,
                    "api_key": os.getenv("OPENAI_API_KEY")
                }

                # Agregar temperatura (todos los modelos la soportan)
                kwargs["temperature"] = chat_manager.temperature

                try:
                    # Reemplazar el modelo
                    chat_manager.llm = ChatOpenAI(**kwargs)
                    chat_manager.model = selected_model

                    # Limpiar el chat actual para empezar uno nuevo con el nuevo modelo
                    st.session_state.current_conversation_id = None
                    st.session_state.messages = []
                    st.session_state.editing_title = None

                    st.sidebar.success(f"✅ Modelo cambiado a {selected_model}")
                    st.sidebar.info("💡 Chat limpiado - Inicia un nuevo chat con este modelo")
                    st.rerun()
                except Exception as e:
                    # FIX: Manejador mejorado de errores por modelo no disponible
                    error_str = str(e).lower()

                    # Detectar error de modelo no disponible
                    if "model_not_found" in error_str or "does not exist" in error_str or "not available" in error_str:
                        st.sidebar.error(f"🚫 **Modelo No Disponible**")
                        st.sidebar.warning(f"""
                        El modelo **{selected_model}** no está disponible o no tienes acceso a él.

                        **Opciones:**
                        1. Verifica tu plan de OpenAI (algunos modelos requieren acceso especial)
                        2. Usa un modelo disponible: gpt-4o, gpt-4o-mini, gpt-3.5-turbo
                        3. Revisa tu API key en el archivo .env
                        """)

                    # Detectar error de autenticación/API key
                    elif "api_key" in error_str or "401" in error_str or "authentication" in error_str:
                        st.sidebar.error("🔑 **Error de Autenticación**")
                        st.sidebar.warning("""
                        Tu API key de OpenAI es inválida o ha expirado.

                        **Solución:**
                        1. Ve a https://platform.openai.com/api-keys
                        2. Crea una nueva API key
                        3. Actualiza tu archivo .env con: `OPENAI_API_KEY=tu_nueva_key`
                        4. Reinicia la aplicación
                        """)

                    # Error genérico
                    else:
                        st.sidebar.error(f"❌ Error al cambiar modelo")
                        st.sidebar.warning(f"""
                        **Detalles técnicos:** {str(e)[:100]}...

                        **Intenta:**
                        1. Selecciona otro modelo
                        2. Revisa tu conexión a internet
                        3. Verifica los logs de error
                        """)


    def render_sidebar(self) -> Optional[int]:
        """Renderiza el sidebar responsivo - U-TUTOR v5.0"""
        self._apply_theme()
        # CSS del sidebar ahora está en styles_modern.css

        # === Sidebar principal ===
        st.sidebar.markdown("<div class='u-tutor-sidebar'>", unsafe_allow_html=True)
        st.sidebar.markdown(
    """
    <div style="text-align:center;">
        <h2>U - TUTOR<br>
        Tu Asistente Academico</h2>
    </div>
    """,
    unsafe_allow_html=True
)

        # FIX: Verificar si se está generando respuesta
        is_generating = st.session_state.get('await_response', False)

        # Botones generales
        st.sidebar.markdown("## 🔧 Configuraciones")

        # FIX: Deshabilitar ajustes mientras se genera
        if st.sidebar.button("⚙️ Ajustes", key="config_button", disabled=is_generating):
            st.session_state.show_config_page = True
            st.rerun()

        self.render_model_selector()

        st.sidebar.markdown("## 📁 Chats")

        # FIX: Mostrar advertencia si se intenta hacer algo mientras se genera
        if is_generating:
            st.sidebar.warning("⏳ **Generando respuesta...**\nEspera a que termine para cambiar de chat")

        # FIX: Deshabilitar botón de nueva conversación mientras se genera
        if st.sidebar.button("➕&nbsp;&nbsp;Nueva conversación", key="new_conv_button", disabled=is_generating):
            # Detener generación en progreso
            st.session_state.await_response = False
            st.session_state._generating_response = False
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.session_state.editing_title = None
            st.session_state.show_config_page = False
            st.rerun()

        # Buscar
        search_query = st.sidebar.text_input(
            "Buscar conversación",
            key="sidebar_search_conv",
            placeholder="Escribe para buscar...",
        )
        

        if search_query.strip():
            conversations = self.db_manager.search_conversations(search_query.strip())
        else:
            conversations = self.db_manager.get_conversations()

        # Mostrar conversaciones como botones

        if conversations:
            for conv_id, title, created_at, updated_at in conversations:
                col_chat, col_menu = st.sidebar.columns([4, 1], gap="small")

                with col_chat:
                    # FIX: Deshabilitar botones de conversación mientras se genera
                    if st.button(
                        f"{title[:25]}{'...' if len(title) > 25 else ''}",
                        key=f"sidebar_chat_{conv_id}",
                        use_container_width=True,
                        help=f"Creado: {created_at[:16]}" if not is_generating else "Espera a que termine la generación",
                        disabled=is_generating  # 🔴 BLOQUEAR DURANTE GENERACIÓN
                    ):
                        self._load_conversation(conv_id)

                with col_menu:
                    # FIX: Deshabilitar menú de opciones mientras se genera
                    if st.button("⋮", key=f"menu_btn_{conv_id}", help="Opciones" if not is_generating else "Espera a que termine", disabled=is_generating):
                        if st.session_state.get("active_menu") == conv_id:
                            st.session_state["active_menu"] = None
                        else:
                            st.session_state["active_menu"] = conv_id

                # Menú desplegable debajo del chat seleccionado
                if st.session_state.get("active_menu") == conv_id:
                    with st.sidebar.container():
                        st.markdown(
                            f"""
                            <div style="
                                background-color: rgba(100,150,255,0.15);
                                border-radius: 8px;
                                padding: 10px;
                                margin: 8px 0 12px 0;
                                border: 2px solid rgba(100,150,255,0.4);
                            ">
                            """, unsafe_allow_html=True
                        )

                        # ===== FUNCIONES INTERNAS =====
                        def export_conversation():
                            try:
                                conv_data = self.db_manager.get_conversation_by_id(conv_id)
                                conv_title = conv_data[1] if conv_data else f"chat_{conv_id}"
                                messages = self.db_manager.load_conversation_messages(conv_id)  # <--- CORREGIDO

                                import io
                                output = io.StringIO()
                                for msg in messages:
                                    role = msg[0].capitalize()  # load_conversation_messages devuelve (role, content, timestamp)
                                    content = msg[1]
                                    output.write(f"{role}: {content}\n\n")

                                file_content = output.getvalue()
                                output.close()
                                return conv_title, file_content
                            except Exception as e:
                                st.error(f"❌ Error al preparar la descarga: {e}")
                                return None, None

                        def edit_conversation(new_name):
                            try:
                                self.db_manager.update_conversation_title(conv_id, new_name)
                                st.success(f"✅ Conversación renombrada a: {new_name}")
                                st.session_state[f"editing_{conv_id}"] = False
                                st.session_state["active_menu"] = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al renombrar: {e}")

                        def delete_conversation():
                            try:
                                self.db_manager.delete_conversation(conv_id)
                                st.warning(f"🗑️ Conversación {conv_id} eliminada.")
                                st.session_state["active_menu"] = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al eliminar: {e}")

                        # ===== DESCARGAR =====
                        if st.button("📥 Descargar", key=f"prepare_download_{conv_id}", use_container_width=True):
                            conv_title, file_content = export_conversation()
                            if file_content:
                                st.session_state[f"download_data_{conv_id}"] = (conv_title, file_content)

                        # Mostrar botón de descarga solo si hay datos
                        if st.session_state.get(f"download_data_{conv_id}"):
                            conv_title, file_content = st.session_state[f"download_data_{conv_id}"]
                            st.download_button(
                                label=f"✅ {conv_title[:20]}...",
                                data=file_content,
                                file_name=f"{conv_title}.md",
                                mime="text/markdown",
                                key=f"download_actual_{conv_id}",
                                use_container_width=True
                            )

                        # ===== EDITAR =====
                        if not st.session_state.get(f"editing_{conv_id}", False):
                            if st.button("✏️ Editar nombre", key=f"edit_btn_{conv_id}", use_container_width=True):
                                st.session_state[f"editing_{conv_id}"] = True
                                st.rerun()
                        else:
                            st.markdown("**✏️ Renombrar conversación:**")
                            # Obtener el título actual de la conversación
                            conv_data = self.db_manager.get_conversation_by_id(conv_id)
                            current_title = conv_data[1] if conv_data else title
                            new_name = st.text_input(
                                "Nuevo nombre",
                                value=current_title,
                                key=f"edit_input_{conv_id}",
                                placeholder="Escribe el nuevo nombre..."
                            )
                            c1, c2 = st.columns([1, 1], gap="small")
                            with c1:
                                if st.button("💾 Guardar", key=f"save_edit_{conv_id}", use_container_width=True):
                                    # FIX: Validar que new_name no es None y aplicar strip()
                                    if new_name and isinstance(new_name, str) and new_name.strip() and new_name.strip() != current_title:
                                        edit_conversation(new_name.strip())
                                    else:
                                        st.warning("⚠️ Ingresa un nombre diferente")
                            with c2:
                                if st.button("❌ Cancelar", key=f"cancel_edit_{conv_id}", use_container_width=True):
                                    st.session_state[f"editing_{conv_id}"] = False
                                    st.rerun()

                        # ===== ELIMINAR con Confirmación (Opción B+C) =====
                        # PLAN PASO 4: Confirmación al eliminar
                        if not st.session_state.get(f"confirm_delete_{conv_id}", False):
                            # Primer click: mostrar advertencia
                            if st.button("🗑️ Eliminar Chat", key=f"del_btn_{conv_id}", use_container_width=True):
                                st.session_state[f"confirm_delete_{conv_id}"] = True
                                st.rerun()
                        else:
                            # Segundo click: confirmar eliminación
                            st.warning(f"⚠️ **¿Estás seguro?** Este chat será eliminado permanentemente y no se puede recuperar.")

                            col_confirm1, col_confirm2 = st.columns([1, 1], gap="small")
                            with col_confirm1:
                                if st.button("🗑️ Sí, Eliminar", key=f"confirm_del_{conv_id}", use_container_width=True):
                                    with st.spinner("Eliminando..."):
                                        delete_conversation()
                            with col_confirm2:
                                if st.button("❌ Cancelar", key=f"cancel_del_{conv_id}", use_container_width=True):
                                    st.session_state[f"confirm_delete_{conv_id}"] = False
                                    st.rerun()

                        st.markdown("</div>", unsafe_allow_html=True)

                # Línea divisoria visual
                st.sidebar.markdown("<hr style='margin:4px 0;'>", unsafe_allow_html=True)
        else:
            st.sidebar.info("💬 No hay conversaciones todavía.")


    def render_config_page(self):
        """Renderiza página de configuración como ventana separada - U-TUTOR v5.0"""
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
                st.markdown("ㅤ")
                
                # Botón para volver al chat en la parte inferior
                if st.button("🏠 Volver al Chat Principal", use_container_width=True, type="primary"):
                    st.session_state.show_config_page = False
                    st.rerun()
    
    def _render_config_tab(self):
        """Renderiza la pestaña de configuración - U-TUTOR v5.0"""
        st.markdown("ㅤ")
        st.markdown("### 🎨 Configuración del Asistente")
        
    
        # Personalidad
        if 'personality' not in st.session_state:
            st.session_state.personality = "Amigable"
        
        personality = st.selectbox(
            "🎭 Personalidad",
            ["Profesional", "Amigable", "Conciso", "Detallado"],
            index=["Profesional", "Amigable", "Conciso", "Detallado"].index(st.session_state.personality)
        )
        
        # Idioma fijo en español
        st.markdown("ㅤ")
        st.markdown("### 🗣️ Idioma de voz")
        st.info("🇪🇸 **Español** (fijo para mejor compatibilidad)")
        
        # Mostrar información sobre voces TTS disponibles
        if hasattr(st.session_state, 'audio_manager'):
            voices_info = st.session_state.audio_manager.get_available_voices_info()
            # Edge-TTS es considerado "local" porque no requiere APIs externas complejas
            if voices_info.get('edge_tts_available', False):
                if voices_info.get('available_languages'):
                    st.success(f"🎤 Edge-TTS disponible para: {', '.join(voices_info['available_languages'])}")
                else:
                    st.warning("⚠️ Edge-TTS disponible pero sin voces compatibles")
            else:
                st.info("ℹ️ Solo gTTS disponible (requiere internet)")
        
        # Apariencia / Tema (Lilac / Blueish)
        st.markdown("ㅤ")
        st.markdown("### 🌙 Apariencia")
        st.info("Elige el tema para la interfaz:")

        # Inicializar tema por defecto si no existe
        if 'theme' not in st.session_state:
            st.session_state.theme = 'blueish'

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Lilac", use_container_width=True, key='btn_theme_lilac'):
                st.session_state.theme = 'lilac'
                self._apply_theme()
                st.success("Tema Lilac aplicado 🌸")
        with c2:
            if st.button("Blueish", use_container_width=True, key='btn_theme_blueish'):
                st.session_state.theme = 'blueish'
                self._apply_theme()
                st.success("Tema Blueish aplicado 🌊")

        # Mostrar tema actual
        st.write(f"Tema actual: **{st.session_state.get('theme','blueish').upper()}**")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Aplicar Cambios", use_container_width=True, type="primary"):
                st.session_state.personality = personality
                st.session_state.tts_language = 'es'  # Fijo en español
                st.session_state.auto_translate = False  # Deshabilitado
                st.session_state.settings_changed = True
                st.success("✅ Configuración guardada")
                st.rerun()

        with col2:
            if st.button("🔄 Resetear", use_container_width=True):
                st.session_state.personality = "Amigable"
                st.session_state.tts_language = 'es'  # Fijo en español
                st.session_state.auto_translate = False  # Deshabilitado
                st.info("↩️ Valores por defecto")
                st.rerun()
        
        # Botón para limpiar caché de audio
        st.markdown("---")
        st.markdown("ㅤ")
        if st.button("🧹 Limpiar caché de audio", use_container_width=True, help="Libera memoria eliminando archivos de audio guardados"):
            if hasattr(st.session_state, 'audio_manager'):
                cache_size = st.session_state.audio_manager.get_cache_size()
                st.session_state.audio_manager.clear_audio_cache()
                st.success(f"✅ Caché limpiado ({cache_size} archivos eliminados)")
            else:
                st.info("ℹ️ Caché de audio no disponible")

    def _render_stats_tab(self):
        """Renderiza la pestaña de estadísticas - U-TUTOR v5.0"""
        st.markdown("ㅤ")
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
            st.markdown("ㅤ")
            st.markdown("### 🏆 Conversación más larga")
            st.info(
                f"**{detailed_stats['longest_conversation'][0][:30]}...** "
                f"({detailed_stats['longest_conversation'][1]} mensajes)"
            )
        
        # Estadísticas de tiempo
        if detailed_stats.get('oldest_conversation') and detailed_stats.get('newest_conversation'):
            st.markdown("ㅤ")
            st.markdown("### 📅 Historial")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📅 Primera conversación", detailed_stats['oldest_conversation'][:10])
            with col2:
                st.metric("🕒 Última conversación", detailed_stats['newest_conversation'][:10])
        else:
            st.info("📅 No hay conversaciones registradas aún")


    def _render_info_tab(self):
        """Renderiza la pestaña de información - U-TUTOR v5.0"""
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
        """Renderiza el área principal de chat mejorada - U-TUTOR v5.0"""
        # No mostrar el área de chat si estamos en la página de configuración
        if st.session_state.show_config_page:
            return

        # Aplicar tema al área principal también
        self._apply_theme()
        # Abrir wrapper del área de chat para estilos específicos
        st.markdown("<div class='u-tutor-chat'>", unsafe_allow_html=True)
        st.markdown("""
            <style>
            div[data-testid="stMarkdownContainer"] h1 {
                color: #FFFFF !important;
                margin-top: -15px !important;
                margin-bottom: 0px !important;
                text-align: left !important;
            }
            </style>
            """, unsafe_allow_html=True)

        # FIX: Mostrar indicador visual si se está generando respuesta
        is_generating = st.session_state.get('await_response', False)
        if is_generating:
            st.markdown("""
            <div style="
                background: linear-gradient(90deg, rgba(160, 196, 255, 0.2) 0%, rgba(41, 128, 185, 0.2) 100%);
                border-left: 4px solid #a0c4ff;
                border-radius: 8px;
                padding: 12px 16px;
                margin-bottom: 16px;
                animation: pulse 1.5s infinite;
            ">
                <span style="color: #a0c4ff; font-weight: bold;">⏳ Generando respuesta...</span>
            </div>
            <style>
            @keyframes pulse {
                0%, 100% { opacity: 0.8; }
                50% { opacity: 1; }
            }
            </style>
            """, unsafe_allow_html=True)

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
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);'>
                    📝 <b>{conversation[1]}</b> | 💬 {msg_count} mensaje{'s' if msg_count != 1 else ''}
                </div>
                """, unsafe_allow_html=True)
        else:
            # Sugerencias para nueva conversación
            self._render_quick_suggestions()

        # Cerrar wrapper del área de chat
        st.markdown("</div>", unsafe_allow_html=True)

    def _render_quick_suggestions(self):
        """
        Renderiza sugerencias en expander colapsable para ahorrar espacio.
        El usuario puede expandir solo si desea ver las sugerencias.
        """
        with st.expander("💡 Ver sugerencias de conversación", expanded=False):
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
                    if st.button(
                        f"{emoji} {suggestion}",
                        key=f"suggest_{idx}",
                        use_container_width=True
                    ):
                        st.session_state.pending_message = suggestion
                        st.rerun()


    def render_chat_messages(self, messages: List[dict]):
        """Renderiza los mensajes del chat - CSS en styles_modern.css"""
        if st.session_state.show_config_page:
            return

        # Aplicar tema
        self._apply_theme()

        # Mostrar alerta si generación fue cancelada
        if st.session_state.get('generation_cancelled', False):
            st.warning("⚠️ **Generación Interrumpida** - Cambiste de chat mientras se generaba la respuesta")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🔄 Regenerar Respuesta", use_container_width=True, key="continue_generation_btn"):
                    # Limpiar flags y esperar nueva respuesta
                    st.session_state.generation_cancelled = False
                    st.session_state._generating_response = False
                    st.session_state.await_response = True
                    print("🔄 [LOG] Regenerando después de interrupción")
                    st.rerun()
            with col2:
                if st.button("✅ Descartar", use_container_width=True, key="acknowledge_cancel_btn"):
                    # Descartar la generación interrumpida
                    st.session_state.generation_cancelled = False
                    st.rerun()
            st.markdown("---")

        # Contenedor principal
        chat_container = st.container()

        # Renderizado de los mensajes
        with chat_container:
            st.markdown("<div class='u-tutor-messages'>", unsafe_allow_html=True)

            # Mostrar solo los ultimos 50 mensajes para optimizar rendimiento
            messages_to_display = messages[-50:] if len(messages) > 50 else messages

            # Verificar si el último mensaje es del asistente (para habilitar regenerar)
            last_is_assistant = st.session_state.messages and st.session_state.messages[-1].get("role") == "assistant"

            # FIX: Verificar si estamos esperando respuesta o si fue interrumpida
            awaiting_response = st.session_state.get('await_response', False)
            generation_cancelled = st.session_state.get('generation_cancelled', False)

            for idx, message in enumerate(messages_to_display):
                role = message.get("role", "user")
                content = message.get("content", "")

                # Calcular índice real en la lista completa
                real_idx = len(messages) - len(messages_to_display) + idx

                if role == "user":
                    html = f"""
                    <div class='u-tutor-message user'>
                    <div style='display: flex; align-items: flex-end; gap: 8px;
                            justify-content: flex-end; flex-direction: row-reverse;'>
                        <div class='u-tutor-bubble-user'>{content}</div>
                        <div class='u-tutor-avatar user'>👤</div>
                    </div>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)

                    # FIX: Mostrar botón de regenerar junto al último mensaje del usuario si:
                    # 1. Estamos esperando respuesta (generación en progreso)
                    # 2. O la generación fue interrumpida
                    is_last_message = (real_idx == len(st.session_state.messages) - 1)
                    if is_last_message and (awaiting_response or generation_cancelled):
                        col_space, col_regen = st.columns([8, 1], gap="small")
                        with col_regen:
                            if st.button("🔄", key=f"regen_on_user_{idx}", help="Regenerar respuesta", use_container_width=True):
                                # FIX: Reenviar el mensaje del usuario para regenerar la respuesta
                                # 1. Extraer el contenido del mensaje del usuario
                                user_content = content

                                # 2. Eliminar el mensaje del usuario y la respuesta anterior del asistente
                                if st.session_state.messages and st.session_state.messages[-1].get("role") == "user":
                                    st.session_state.messages.pop()
                                    print(f"🔄 [LOG] Mensaje del usuario removido para reenvío")

                                if st.session_state.messages and st.session_state.messages[-1].get("role") == "assistant":
                                    st.session_state.messages.pop()
                                    print(f"🔄 [LOG] Respuesta del asistente removida")

                                # 3. Guardar el mensaje para ser reenviado en el siguiente ciclo
                                st.session_state.pending_message = user_content
                                st.session_state.generation_cancelled = False
                                st.session_state._generating_response = False
                                print(f"🔄 [LOG] Mensaje del usuario reenviado para regeneración")
                                st.rerun()
                else:
                    html = f"""
    <div class='u-tutor-message assistant'>
    <div style='display: flex; align-items: flex-start; gap: 8px;'>
        <div class='u-tutor-avatar assistant'>🎓</div>
        <div style='flex: 1;'>{content}</div>
    </div>
</div>
                    """

                    st.markdown(html, unsafe_allow_html=True)

                    # Mostrar botón de regenerar solo en el último mensaje del asistente
                    is_last_message = (real_idx == len(st.session_state.messages) - 1)
                    self._add_tts_button(content, idx, show_regenerate=is_last_message and last_is_assistant)

            scroll_marker = st.empty()
            scroll_marker.markdown("<div id='scroll-target'></div>", unsafe_allow_html=True)
            st.markdown("""
            <script>
            const target = document.getElementById('scroll-target');
            if (target) {
                target.scrollIntoView({behavior: 'smooth'});
            }
            </script>
            """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)


    def _add_tts_button(self, text: str, message_index: int, show_regenerate: bool = False):
        """Renderiza botón de TTS + Regenerar - CSS movido a styles_modern.css"""
        conv_id = st.session_state.get('current_conversation_id', 'new')
        unique_key = f"{conv_id}_{message_index}"

        # Inicializar estado
        if f'audio_playing_{unique_key}' not in st.session_state:
            st.session_state[f'audio_playing_{unique_key}'] = False
        if f'audio_data_{unique_key}' not in st.session_state:
            st.session_state[f'audio_data_{unique_key}'] = None

        # 🔹 Crear layout del botón con contenedor responsivo
        container_class = f"tts-button-container-{unique_key.replace('_', '-')}"
        st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)

        # Si es el último mensaje del asistente, mostrar dos botones (Audio + Regenerar)
        if show_regenerate:
            col_audio, col_regen, col_space = st.columns([1.2, 1.5, 10], gap="medium")

            # ✅ Botón de Audio
            with col_audio:
                if st.session_state[f'audio_playing_{unique_key}']:
                    if st.button("⏸️", key=f"pause_{unique_key}", help="Pausar audio", use_container_width=True):
                        st.session_state[f'audio_playing_{unique_key}'] = False
                        st.rerun()
                else:
                    if st.button("▶️", key=f"play_{unique_key}", help="Reproducir audio", use_container_width=True):
                        with st.spinner("Generando audio..."):
                            processed_text = self.tts_manager.preprocess_text_for_tts(text)
                            audio_data = self.tts_manager.text_to_speech_fast(processed_text)
                            if audio_data:
                                st.session_state[f'audio_data_{unique_key}'] = audio_data
                                st.session_state[f'audio_playing_{unique_key}'] = True
                                st.rerun()
                            else:
                                st.error("❌ Error al generar audio")

            # ✅ Botón Regenerar Respuesta
            with col_regen:
                if st.button("🔄", key=f"regen_{unique_key}", help="Regenerar esta respuesta", use_container_width=True):
                    # FIX: Eliminar el último mensaje del asistente de forma segura
                    if st.session_state.messages and st.session_state.messages[-1].get("role") == "assistant":
                        removed_message = st.session_state.messages.pop()
                        print(f"🔄 [LOG] Mensaje regenerado removido: {len(removed_message.get('content', ''))} caracteres")

                    # FIX: Limpiar flags antes de regenerar para evitar conflictos
                    st.session_state._generating_response = False
                    st.session_state.await_response = True
                    print(f"🔄 [LOG] Esperando nueva respuesta. Total mensajes: {len(st.session_state.messages)}")
                    st.rerun()
        else:
            # Solo botón de audio (sin regenerar)
            col_audio, col_space = st.columns([1.2, 10], gap="small")

            with col_audio:
                if st.session_state[f'audio_playing_{unique_key}']:
                    if st.button("⏸️", key=f"pause_{unique_key}", help="Pausar audio", use_container_width=True):
                        st.session_state[f'audio_playing_{unique_key}'] = False
                        st.rerun()
                else:
                    if st.button("▶️", key=f"play_{unique_key}", help="Reproducir audio", use_container_width=True):
                        with st.spinner("Generando audio..."):
                            processed_text = self.tts_manager.preprocess_text_for_tts(text)
                            audio_data = self.tts_manager.text_to_speech_fast(processed_text)
                            if audio_data:
                                st.session_state[f'audio_data_{unique_key}'] = audio_data
                                st.session_state[f'audio_playing_{unique_key}'] = True
                                st.rerun()
                            else:
                                st.error("❌ Error al generar audio")

        st.markdown('</div>', unsafe_allow_html=True)

        # 🔊 Reproduce el audio si está listo (con contenedor responsivo)
        if st.session_state[f'audio_data_{unique_key}']:
            audio_container_class = f"tts-audio-container-{unique_key.replace('_', '-')}"
            st.markdown(f'<div class="{audio_container_class}">', unsafe_allow_html=True)
            st.audio(st.session_state[f'audio_data_{unique_key}'], format='audio/mp3')
            st.markdown('</div>', unsafe_allow_html=True)


    
    def _load_conversation(self, conv_id: int):
        """Carga una conversación específica - U-TUTOR v5.0"""
        # PLAN PASO 1: Detener generación gracefully con flag
        was_generating = st.session_state.get('await_response', False)

        # Detener generación
        st.session_state.await_response = False
        st.session_state._generating_response = False

        # Marcar que fue cancelada
        if was_generating:
            st.session_state.generation_cancelled = True
            st.session_state.cancelled_at_message = len(st.session_state.messages)

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
        """Muestra un mensaje de error - U-TUTOR v5.0"""
        st.error(message)
    
    def show_success(self, message: str):
        """Muestra un mensaje de éxito - U-TUTOR v5.0"""
        st.success(message)
    
    def show_spinner(self, text: str = "Procesando..."):
        """Muestra un spinner con texto - U-TUTOR v5.0"""
        return st.spinner(text)
    
    
    
    def _delete_conversation_direct(self, conv_id: int):
        """Elimina una conversación directamente - U-TUTOR v5.0"""
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
                
                