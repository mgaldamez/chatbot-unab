# U-TUTOR v5.0 - Aplicación principal optimizada
import os
from dotenv import load_dotenv
import streamlit as st
from functools import lru_cache

# Importar módulos principales
from database_manager import DatabaseManager
from chat_manager import ChatManager
from ui_components import UIComponents
from audio_manager import AudioManager


# Cargar variables de entorno
load_dotenv()


# Cache para DatabaseManager - OPTIMIZACION
@st.cache_resource
def get_db_manager():
    """Cachea el DatabaseManager para evitar reconexiones"""
    return DatabaseManager()


# Cache para AudioManager - OPTIMIZACION
@st.cache_resource
def get_audio_manager():
    """Cachea el AudioManager para evitar reinicializaciones"""
    return AudioManager()


# ============================================
# CACHE DE TEMAS - OPTIMIZACIÓN DE RENDIMIENTO
# ============================================
@lru_cache(maxsize=2)
def get_theme_colors(theme: str = 'blueish') -> dict:
    """
    Retorna colores temáticos con cache para optimizar rendimiento.
    El cache evita recomputar colores en cada render.
    """
    theme_palettes = {
        'lilac': {
            'bg': '#120018',
            'sidebar_bg': '#0b0012',
            'user_bg': '#DDA0DD',
            'user_text': '#4B0082',
            'assistant_bg': '#663399',
            'assistant_text': '#FFFFFF',
            'button_bg': '#663399',
            'button_text': '#FFFFFF',
            'input_bg': '#2a003b',
            'input_text': '#E6E6FA'
        },
        'blueish': {
            'bg': '#0b1116',
            'sidebar_bg': '#05070a',
            'user_bg': '#2b3a4a',
            'user_text': '#a0c4ff',
            'assistant_bg': '#1b2a36',
            'assistant_text': '#a0c4ff',
            'button_bg': '#14232a',
            'button_text': '#dbeefb',
            'input_bg': '#0f1720',
            'input_text': '#E6E6FA'
        }
    }
    return theme_palettes.get(theme, theme_palettes['blueish'])

class UTutorApp:
    def __init__(self):
        """Inicializa la aplicación U-TUTOR v5.0"""
        self.version = os.getenv("VERSION", "5.0")
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

        # Inicializar componentes (usando cache)
        self.db_manager = get_db_manager()
        self.ui_components = UIComponents(self.db_manager, self.version)
        self.audio_manager = get_audio_manager()

        # Hacer audio_manager disponible globalmente
        st.session_state.audio_manager = self.audio_manager
        
        if not self.api_key:
            st.error("❌ Por favor, configura tu OPENAI_API_KEY en el archivo .env")
            st.stop()

        # Inicializar con configuración guardada
        temperature = st.session_state.get('temperature', 1)

        # Crear ChatManager (no se cachea porque el modelo puede cambiar)
        if 'chat_manager_instance' not in st.session_state:
            st.session_state.chat_manager_instance = ChatManager(self.api_key, self.model, temperature)

        self.chat_manager = st.session_state.chat_manager_instance
        st.session_state.chat_manager = self.chat_manager

        # Aplicar personalidad si existe
        if 'personality' in st.session_state:
            self.chat_manager.update_personality(st.session_state.personality)

        # Inicializar estado de la sesión
        self._init_session_state()

        # Aplicar cambios de configuración si los hay (después de inicializar session_state)
        self._apply_settings_changes()     
        action = st.query_params.get("action")
        conv_id = st.query_params.get("id")

        if action and conv_id:
            conv_id = int(conv_id[0])
            action = action[0]
            if action == "download":
                # TODO: Implementar export directo
                pass
            elif action == "rename":
                st.session_state.editing_title = conv_id
                st.rerun()
            elif action == "delete":
                # TODO: Implementar delete directo
                pass
    def _apply_theme(self):
        """Aplica colores temáticos dinámicos - OPTIMIZADO CON CACHE"""
        theme = st.session_state.get('theme', 'blueish')
        colors = get_theme_colors(theme)  # Usa cache para evitar recompilación

        # Aplicar colores dinámicamente
        st.markdown(f"""
        <style>
        .stApp {{
            background: {colors['bg']} !important;
            color: {colors['assistant_text']} !important;
        }}

        [data-testid="stSidebar"] {{
            background: {colors['sidebar_bg']} !important;
        }}

        .stChatMessage[data-testid="user"] .stChatMessage__content {{
            background: {colors['user_bg']} !important;
            color: {colors['user_text']} !important;
        }}

        .stChatMessage[data-testid="assistant"] .stChatMessage__content {{
            background: {colors['assistant_bg']} !important;
            color: {colors['assistant_text']} !important;
        }}

        .stButton > button {{
            background: {colors['button_bg']} !important;
            color: {colors['button_text']} !important;
        }}

        .stTextInput > div > div > input {{
            background: {colors['input_bg']} !important;
            color: {colors['input_text']} !important;
        }}
        </style>
        """, unsafe_allow_html=True)

        # Agregar JavaScript para optimizar sidebar con GPU acceleration
        st.markdown("""
        <script>
        (function optimizeSidebar() {
            try {
                const sidebar = document.querySelector('[data-testid="stSidebar"]');
                if (sidebar) {
                    sidebar.style.willChange = 'width, margin, transform';
                    sidebar.style.transform = 'translateZ(0)';
                    sidebar.style.backfaceVisibility = 'hidden';
                }
            } catch (error) {
                console.log('Sidebar optimization unavailable');
            }
        })();
        </script>
        """, unsafe_allow_html=True)
    
    @staticmethod
    @st.cache_data
    def _load_custom_css_cached():
        """Cachea la carga de CSS para evitar relecturas - OPTIMIZACION"""
        try:
            with open('styles_modern.css', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def _load_custom_css(self):
        """Carga estilos CSS personalizados - U-TUTOR v5.0"""
        css_content = self._load_custom_css_cached()
        if css_content:
            st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)


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

        if "menu_counter" not in st.session_state:
            st.session_state.menu_counter = 0

        # Inicializar flag de espera de respuesta
        if "await_response" not in st.session_state:
            st.session_state.await_response = False

        # PLAN: Flags para cancelación graceful de generación
        if "generation_cancelled" not in st.session_state:
            st.session_state.generation_cancelled = False

        if "cancelled_at_message" not in st.session_state:
            st.session_state.cancelled_at_message = None

        # Inicializar configuración (temperatura y personalidad)
        if "temperature" not in st.session_state:
            st.session_state.temperature = 1

        if "personality" not in st.session_state:
            st.session_state.personality = "Profesional"

        if "settings_changed" not in st.session_state:
            st.session_state.settings_changed = False


        if "show_config_page" not in st.session_state:
            st.session_state.show_config_page = False
    
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
            print("🔵 [LOG] Detectado await_response=True, generando respuesta...")
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
                
                with st.spinner():
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


    # ------------------ MANEJO DE INPUT ------------------
    def _handle_user_input(self):
        """
        Maneja la entrada de texto del usuario con input FIJO en la parte inferior - U-TUTOR v5.0
        FIX: Bloquear input mientras se genera respuesta
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

        # 3️⃣ FIX: Verificar si se está generando respuesta
        is_generating = st.session_state.get("await_response", False)

        # 3️⃣ Renderizar input FIJO al fondo de la pantalla
        st.markdown('<div class="chat-input-fixed-container">', unsafe_allow_html=True)
        st.markdown('<div class="chat-input-fixed-inner">', unsafe_allow_html=True)

        col_input, col_button = st.columns([20, 1], gap="small")

        # 4️⃣ Input de texto - RENDERIZADO FIJO (DESHABILITADO SI SE ESTÁ GENERANDO)
        with col_input:
            # FIX: Deshabilitar input mientras se genera
            prompt = st.text_input(
                label="Mensaje",
                key="user_input",
                placeholder="⏳ Esperando respuesta..." if is_generating else "Escribe tu pregunta...",
                label_visibility="collapsed",
                disabled=is_generating  # 🔴 BLOQUEAR INPUT DURANTE GENERACIÓN
            )

        # 5️⃣ Botón de enviar - RENDERIZADO FIJO (DESHABILITADO SI SE ESTÁ GENERANDO)
        with col_button:
            # FIX: Deshabilitar botón mientras se genera
            send_button = st.button(
                "⏳" if is_generating else "➤",
                use_container_width=True,
                key="send_button",
                help="Esperando respuesta..." if is_generating else "Enviar (Enter)",
                disabled=is_generating  # 🔴 BLOQUEAR BOTÓN DURANTE GENERACIÓN
            )

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 6️⃣ Detectar si el usuario envió el mensaje (NO SI SE ESTÁ GENERANDO)
        if (send_button or (prompt and prompt.strip() != "")) and not is_generating:

            current_prompt = prompt.strip()

            # 7️⃣ Procesar el mensaje
            self._process_user_message(current_prompt)

            # 8️⃣ Limpiar input en el próximo rerun
            st.session_state.clear_input = True

            # 9️⃣ Forzar rerun para actualizar la UI
            st.rerun()


    # ------------------ Procesar mensaje del usuario ------------------
    def _process_user_message(self, prompt: str):
        """
        Procesa un mensaje del usuario (desde texto o voz) - U-TUTOR v5.0
        FIX: Evitar duplicación de mensajes al sincronizar
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
        # FIX: No duplicar si ya está en la sesión
        user_message = {"role": "user", "content": prompt}
        if not any(msg.get("content") == prompt and msg.get("role") == "user" for msg in st.session_state.messages[-3:]):
            st.session_state.messages.append(user_message)

        # 4️⃣ Guardar mensaje en la base de datos
        self.db_manager.save_message(
            st.session_state.current_conversation_id,
            "user",
            prompt
        )

        # 5️⃣ NO sincronizar desde la BD después de guardar
        # Esto causa duplicados. La sesión es la fuente de verdad mientras se está usando.
        # Sincronización solo ocurre al cargar conversaciones existentes.

        # 6️⃣ Marcar que estamos esperando la respuesta del asistente
        st.session_state.await_response = True


    def _generate_assistant_response(self):
        """
        Genera y muestra la respuesta del asistente con streaming - U-TUTOR v5.0
        FIX: Mejor protección contra re-entrancy y duplicación de mensajes
        """
        try:
            # FIX: Proteger contra re-entrancy - si ya estamos generando, salir
            if st.session_state.get('_generating_response', False):
                print("⚠️ [LOG] Ya estamos generando, saliendo...")
                return

            print("🟢 [LOG] Iniciando _generate_assistant_response()")
            st.session_state._generating_response = True
            placeholder = st.empty()  # Placeholder para el spinner / mensaje temporal

            with self.ui_components.show_spinner("🤔 Jake está pensando..."):

                full_response = ""
                print(f"📨 [LOG] Llamando get_response_stream con {len(st.session_state.messages)} mensajes")

                # 1️⃣ Recolectar respuesta en streaming
                for chunk in self.chat_manager.get_response_stream(st.session_state.messages):
                    if hasattr(chunk, 'content') and chunk.content:
                        # Asegurar que es string antes de concatenar
                        content = str(chunk.content) if chunk.content else ""
                        full_response += content

                print(f"✅ [LOG] Respuesta generada ({len(full_response)} caracteres)")

                # 2️⃣ Post-procesar traducción para TTS si aplica
                tts_language = st.session_state.get('tts_language', 'es')
                auto_translate = st.session_state.get('auto_translate', True)

                if tts_language == 'en' and auto_translate:
                    translated_response = self.chat_manager.translate_text(full_response, 'en')
                    audio_response = translated_response if translated_response != full_response else full_response
                else:
                    audio_response = full_response

                # 3️⃣ FIX: Verificar que no haya un mensaje del asistente duplicado
                # (esto puede ocurrir si se hizo rerun antes de limpiar await_response)
                print(f"💾 [LOG] Guardando mensaje en sesión y BD...")

                # Verificar si el último mensaje ya es del asistente (evitar duplicado)
                if (st.session_state.messages and
                    st.session_state.messages[-1].get("role") == "assistant"):
                    print("⚠️ [LOG] Último mensaje ya es del asistente, reemplazando...")
                    st.session_state.messages[-1] = {
                        "role": "assistant",
                        "content": full_response
                    }
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": full_response
                    })

                self.db_manager.save_message(
                    st.session_state.current_conversation_id,
                    "assistant",
                    full_response
                )
                print(f"💾 [LOG] Mensaje guardado. Total mensajes: {len(st.session_state.messages)}")

                # 4️⃣ Marcar que ya no esperamos respuesta y recargar
                st.session_state.await_response = False
                print("🟡 [LOG] await_response establecido a False")
                print("🔄 [LOG] Triggerando st.rerun() para mostrar el nuevo mensaje...")
                st.rerun()  # ✅ FIX: Forzar rerun para renderizar el nuevo mensaje

        except Exception as e:
            print(f"❌ [LOG] Error en _generate_assistant_response: {str(e)}")
            self._handle_api_error(e)
        finally:
            # FIX: Siempre limpiar flag de generación
            st.session_state._generating_response = False
            st.session_state.await_response = False
            print("🔴 [LOG] Finalizando _generate_assistant_response()")

    

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

// FIX: Ajustar layout cuando sidebar se oculta/muestra (MEJORADO PARA DESKTOP)
(function adjustSidebarLayout() {
    function updateLayout() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const main = document.querySelector('[data-testid="stMain"]');
        const appContainer = document.querySelector('[data-testid="stAppViewContainer"]');

        if (!sidebar || !main || !appContainer) return;

        const computedStyle = getComputedStyle(sidebar);
        const sidebarWidth = computedStyle.width;
        const sidebarDisplay = computedStyle.display;
        const sidebarVisibility = computedStyle.visibility;

        // MÚLTIPLES FORMAS EN QUE STREAMLIT OCULTA LA SIDEBAR:
        // 1. En móvil: display: none
        // 2. En desktop (collapsed): width: 0px o visibility: hidden
        // 3. Inline styles pueden variar
        const sidebarHidden =
            sidebarDisplay === 'none' ||
            sidebarWidth === '0px' ||
            sidebarVisibility === 'hidden' ||
            sidebar.style.display === 'none' ||
            sidebar.offsetWidth === 0;

        if (sidebarHidden) {
            // Sidebar oculta: expandir main al 100%
            main.style.flex = '1 1 100%';
            main.style.width = '100%';
            main.style.maxWidth = 'none';
            appContainer.style.gap = '0';
            console.log('📱 Sidebar oculta - Chat expandido al 100%');
        } else {
            // Sidebar visible: layout normal
            main.style.flex = '1 1 auto';
            main.style.width = '100%';
            main.style.maxWidth = '100%';
            appContainer.style.gap = '0';
            console.log('📌 Sidebar visible - Layout normal');
        }
    }

    // Ejecutar inmediatamente
    updateLayout();

    // Observar cambios continuamente
    const observer = new MutationObserver(updateLayout);
    observer.observe(document.body, {
        attributes: true,
        subtree: true,
        attributeFilter: ['style', 'class', 'data-testid'],
        attributeOldValue: true,
        characterData: false
    });

    // Observar también cambios de tamaño (resize)
    window.addEventListener('resize', updateLayout);
})();
</script>
""", unsafe_allow_html=True)


# ============================================
# FUNCIÓN PARA RENDERIZAR INPUT FIJO
# ============================================
def render_fixed_chat_input():
    """
    Renderiza el input de chat fijo al fondo de la pantalla.
    Se renderiza al final, después del contenido del chat.
    El CSS '.chat-input-fixed-container' mantiene el input al fondo.
    """
    st.markdown('<div class="chat-input-fixed-container">', unsafe_allow_html=True)

    col_input, col_button = st.columns([20, 1], gap="small")

    with col_input:
        user_input = st.text_input(
            "",
            placeholder="Escribe tu pregunta aquí...",
            key="chat_input_fixed",
            label_visibility="collapsed"
        )

    with col_button:
        if st.button("📤", key="send_button_fixed", use_container_width=True, help="Enviar mensaje"):
            if user_input.strip():
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input
                })
                st.session_state.chat_input_fixed = ""
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def main():
    """Función principal - U-TUTOR v5.0"""
    app = UTutorApp()
    app.run()


if __name__ == "__main__":
    main()