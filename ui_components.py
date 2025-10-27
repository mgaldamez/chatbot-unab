# U-TUTOR v5.0 - Mejoras en ui_components.py: Sidebar avanzado, configuración y controles de audio
import io
import streamlit as st
import time
import os
from typing import List, Tuple, Optional
from database_manager import DatabaseManager
from TTSManager import TTSManager

class UIComponents:
    def __init__(self, db_manager: DatabaseManager, version: str):
        """Inicializa UIComponents con estados de sesión - U-TUTOR v5.0"""
        self.db_manager = db_manager
        self.version = os.getenv("VERSION", "5.0")
        tts_engine = os.getenv("TTS_ENGINE", "edge-tts")
        self.tts_manager = TTSManager(engine_type=tts_engine)
   
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
        """Genera CSS según el tema actual en session_state.

        Soporta 'lilac' y 'blueish'. Devuelve reglas con selectores amplios y `!important`
        para evitar que el tema sea sobrescrito por estilos nativos de Streamlit.
        """
        theme = st.session_state.get('theme', 'blueish')
        # Lilac theme: púrpura/lilac
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
        """Inyecta el CSS del tema actual en la página para aplicar el estilo.

        Llamar al inicio de `render_sidebar` / `render_main_chat_area` asegura que el tema se aplique cada rerun.
        """
        try:
            css = self._get_theme_css()
            st.markdown(css, unsafe_allow_html=True)
            # Inject a small, safe JS helper that creates a floating visual clone of the Streamlit form.
            # The clone is only visual (position:fixed). User typing is forwarded to the original hidden input
            # and submission triggers the original Streamlit submit button. This avoids removing nodes
            # from Streamlit's structure while giving a ChatGPT-like fixed input UI.
            safe_js = """
            <script>
            (function(){
                if(window._u_tutor_clone_created) return;

                function createClone(origInput){
                    try{
                        const origForm = origInput.closest('form');
                        const submitBtn = origForm ? (origForm.querySelector('button[type="submit"], button') ) : null;

                        // Floating wrapper
                        const floatWrap = document.createElement('div');
                        floatWrap.id = 'u-tutor-floating-input';
                        Object.assign(floatWrap.style, {
                            position: 'fixed',
                            bottom: '18px',
                            left: '50%',
                            transform: 'translateX(-50%)',
                            width: 'min(1100px, calc(100% - 48px))',
                            zIndex: 14000,
                            display: 'flex',
                            gap: '10px',
                            alignItems: 'center',
                            pointerEvents: 'auto'
                        });

                        // Visible input
                        const visInput = document.createElement('input');
                        visInput.id = 'u_tutor_vis_input';
                        visInput.type = 'text';
                        visInput.placeholder = origInput.placeholder || 'Escribe un mensaje...';
                        // accessibility attributes to avoid browser helper text
                        visInput.setAttribute('title', '');
                        visInput.setAttribute('aria-label', visInput.placeholder);
                        visInput.setAttribute('autocomplete', 'off');
                        visInput.setAttribute('spellcheck', 'false');
                        Object.assign(visInput.style, {
                            flex: '1 1 auto',
                            padding: '10px 12px',
                            borderRadius: '12px',
                            border: '1px solid rgba(0,0,0,0.12)',
                            outline: 'none',
                            minHeight: '42px',
                            boxSizing: 'border-box',
                            textAlign: 'left',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis'
                        });

                        // Visible button
                        const visBtn = document.createElement('button');
                        visBtn.id = 'u_tutor_vis_send';
                        visBtn.type = 'button';
                        visBtn.innerText = 'Enviar';
                        Object.assign(visBtn.style, {
                            borderRadius: '999px',
                            padding: '10px 18px',
                            cursor: 'pointer'
                        });

                        floatWrap.appendChild(visInput);
                        floatWrap.appendChild(visBtn);
                        document.body.appendChild(floatWrap);

                        // Apply theme-aware colors (read CSS variables if present)
                        try{
                            const root = getComputedStyle(document.documentElement);
                            const inputBg = root.getPropertyValue('--u-tutor-input-bg') || root.getPropertyValue('--u-tutor-sidebar-bg') || getComputedStyle(origInput).backgroundColor;
                            const inputColor = root.getPropertyValue('--u-tutor-accent') || getComputedStyle(origInput).color;
                            visInput.style.background = inputBg || '#0f1720';
                            visInput.style.color = (inputColor || '#e6e6e6').trim();
                        }catch(e){}

                        // inject CSS to disable any focus scaling and remove browser helper overlays for this input
                        try{
                            const ss = document.createElement('style');
                            ss.innerHTML = `
                                #u_tutor_vis_input:focus { transform: none !important; box-shadow: 0 0 0 2px rgba(0,0,0,0.08) !important; }
                                #u_tutor_vis_input::placeholder { color: rgba(230,230,250,0.6) !important; }
                                #u_tutor_vis_input { caret-color: auto !important; }
                            `;
                            document.head.appendChild(ss);
                        }catch(e){}

                        // Sync values
                        visInput.value = origInput.value || '';
                        visInput.addEventListener('input', function(e){
                            origInput.value = e.target.value;
                            origInput.dispatchEvent(new Event('input', {bubbles:true}));
                        });
                        origInput.addEventListener('input', function(){
                            if(document.activeElement !== visInput) visInput.value = origInput.value;
                        });

                        // Submit handlers
                        visBtn.addEventListener('click', function(){
                            if(submitBtn) { submitBtn.click(); }
                            else { origInput.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', code:'Enter', keyCode:13, which:13, bubbles:true})); }
                        });
                        visInput.addEventListener('keydown', function(e){ if(e.key === 'Enter'){ e.preventDefault(); visBtn.click(); } });

                        // Keep original accessible but visually hidden to avoid layout shifts
                        origInput.style.opacity = '0';
                        origInput.style.position = 'relative';
                        origInput.style.zIndex = '0';

                        // Adjust padding on chat container so messages don't hide under the fixed input
                        function adjustPadding(){
                            const chat = document.querySelector('.u-tutor-chat') || document.querySelector('.main');
                            if(chat){
                                const extra = floatWrap.offsetHeight + 24;
                                chat.style.paddingBottom = extra + 'px';
                            }
                        }
                        adjustPadding();
                        window.addEventListener('resize', adjustPadding);

                        // Observe size changes to adjust padding
                        const ro = new ResizeObserver(adjustPadding);
                        ro.observe(floatWrap);

                        window._u_tutor_clone_created = true;
                        return true;
                    }catch(err){ console.log('u-tutor clone setup error', err); return false; }
                }

                function trySetup(){
                    const input = document.querySelector('input#custom_prompt') || document.querySelector('form#chat_form input[type="text"]') || document.querySelector('input[aria-label*="Escribe tu mensaje"]') || document.querySelector('input[placeholder*="Escribe tu mensaje"]');
                    if(input) return createClone(input);
                    return false;
                }

                // MutationObserver to wait for Streamlit render
                const observer = new MutationObserver((mut)=>{
                    if(trySetup()){ observer.disconnect(); }
                });
                observer.observe(document.body, {childList:true, subtree:true});

                // Fallback timeouts
                [200,800,1500,3000].forEach(t => setTimeout(()=>{ if(trySetup()) observer.disconnect(); }, t));
            })();
            </script>
            """
            st.markdown(safe_js, unsafe_allow_html=True)
        except Exception:
            # No bloquear la app si la inyección falla
            pass
    def render_model_selector(self):
        import os
        import streamlit as st
        from langchain_openai import ChatOpenAI  # 👈 usa langchain_openai, no langchain.chat_models

        AVAILABLE_MODELS = ["gpt-4", "gpt-4o", "gpt-5", "gpt-5-mini"]
        selected_model = st.sidebar.selectbox("🤖 Modelo de IA", AVAILABLE_MODELS, key="selected_model")

        if "chat_manager" in st.session_state:
            chat_manager = st.session_state.chat_manager
            current_model = getattr(chat_manager.llm, "model", None)

            if selected_model != current_model:
                kwargs = {"model": selected_model, "api_key": os.getenv("OPENAI_API_KEY")}

                # ⚙️ Solo agregar temperatura si el modelo lo soporta
                if not selected_model.startswith("gpt-5"):
                    kwargs["temperature"] = chat_manager.temperature

                # Reemplazar el modelo
                chat_manager.llm = ChatOpenAI(**kwargs)
                chat_manager.model = selected_model  # 👈 sincroniza el modelo interno

                st.sidebar.success(f"Modelo cambiado a {selected_model}")


    def render_sidebar(self) -> Optional[int]:
        """Renderiza el sidebar responsivo con menú popup independiente - U-TUTOR v5.0"""
        self._apply_theme()

        theme = st.session_state.get("theme", "light")
        primary_color = "#4B9CE2" if theme == "light" else "#1E88E5"
        bg_color = "#FFFFFF" if theme == "light" else "#0E1117"
        text_color = "#1E1E1E" if theme == "light" else "#EAEAEA"
        hover_color = primary_color + "33"

        # === CSS general (sidebar + popup) ===
        st.markdown(f"""
        <style>
        .u-tutor-sidebar {{
            background-color: {bg_color};
            color: {text_color};
            padding: 1rem;
            border-right: 1px solid rgba(128,128,128,0.2);
        }}
        .sidebar-menu-button {{
            background: transparent;
            border: none;
            font-size: 1.1rem;
            cursor: pointer;
            color: {text_color};
            transition: all 0.2s ease;
        }}
        .sidebar-menu-button:hover {{
            color: {primary_color};
        }}

        /* === POPUP FLOTANTE === */
        .conversation-popup {{
            position: fixed;
            top: var(--popup-y, 50%);
            left: var(--popup-x, 50%);
            transform: translate(-50%, -50%);
            background: {bg_color};
            border: 1px solid rgba(128,128,128,0.3);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 0.5rem 0.75rem;
            z-index: 9999;
            min-width: 180px;
        }}
        .conversation-popup button {{
            display: block;
            width: 100%;
            background: transparent;
            border: none;
            color: {text_color};
            padding: 6px 10px;
            text-align: left;
            border-radius: 6px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .conversation-popup button:hover {{
            background-color: {hover_color};
            color: {primary_color};
        }}
        /* === Separador gris confiable === */
        .sidebar-separator {{
            height: 2px;
            background-color: #D3D3D3;
            margin: 10px 0;
            border: 0;
        }}
        </style>
        """, unsafe_allow_html=True)

        # === Sidebar principal ===
        st.sidebar.markdown("<div class='u-tutor-sidebar'>", unsafe_allow_html=True)
        st.sidebar.markdown(
    """
    <div style="text-align:justify; margin-bottom:10px;">
        <img src="https://i.ibb.co/Y7MKW6LD/vecteezy-graduation-item-graduation-hat-and-graduation-certificate-13078278.png" width="200">
    </div>
    """,
    unsafe_allow_html=True
)
        st.sidebar.markdown(
    """
    <div style="text-align:center;">
        <h2>U - TUTOR<br>
        Tu Asistente Academico</h2>
    </div>
    """,
    unsafe_allow_html=True
)

       # Línea divisoria gruesa gris dentro del sidebar
        
        st.sidebar.markdown("<div class='sidebar-separator'>__________________________</div>", unsafe_allow_html=True)
        st.sidebar.markdown("" \
        "")
        
        # Botones generales
        st.sidebar.markdown("ㅤ")
        st.sidebar.markdown("## 🔧 Configuraciones")

        if st.sidebar.button("⚙️ Ajustes", key="config_button"):
            st.session_state.show_config_page = True
            st.rerun()

        self.render_model_selector()
        
        st.sidebar.markdown("<div class='sidebar-separator'>__________________________</div>", unsafe_allow_html=True)
        st.sidebar.markdown("" \
        "")
        st.sidebar.markdown("ㅤ")
        st.sidebar.markdown("## 📁 Chats")
        if st.sidebar.button("➕&nbsp;&nbsp;Nueva conversación", key="new_conv_button"):
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
                    if st.button(
                        f"{title[:25]}{'...' if len(title) > 25 else ''}",
                        key=f"sidebar_chat_{conv_id}",
                        use_container_width=True,
                        help=f"Creado: {created_at[:16]}"
                    ):
                        self._load_conversation(conv_id)

                with col_menu:
                    if st.button("⋮", key=f"menu_btn_{conv_id}", help="Opciones"):
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
                                background-color: rgba(0,0,0,0.03);
                                border-radius: 8px;
                                padding: 8px;
                                margin: 5px 0 10px 0;
                                border: 1px solid rgba(0,0,0,0.1);
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
                        conv_title, file_content = export_conversation()
                        if file_content:
                            st.download_button(
                                label=f"📥 Descargar {conv_title}",
                                data=file_content,
                                file_name=f"{conv_title}.md",
                                mime="text/markdown",
                                key=f"download_{conv_id}"
                            )

                        # ===== EDITAR =====
                        if not st.session_state.get(f"editing_{conv_id}", False):
                            if st.button("✏️ Editar nombre", key=f"edit_btn_{conv_id}"):
                                st.session_state[f"editing_{conv_id}"] = True
                        else:
                            new_name = st.text_input(
                                "Nuevo nombre",
                                value=conv_title,
                                key=f"edit_input_{conv_id}"
                            )
                            c1, c2 = st.columns([1, 1])
                            if c1.button("💾 Guardar", key=f"save_edit_{conv_id}"):
                                if new_name.strip() and new_name != conv_title:
                                    edit_conversation(new_name)
                                else:
                                    st.warning("⚠️ Ingresa un nombre diferente")
                            if c2.button("❌ Cancelar", key=f"cancel_edit_{conv_id}"):
                                st.session_state[f"editing_{conv_id}"] = False

                        # ===== ELIMINAR =====
                        if st.button("🗑️ Eliminar", key=f"del_btn_{conv_id}"):
                            delete_conversation()

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
            if voices_info['local_tts_available']:
                if voices_info['available_languages']:
                    st.success(f"🎤 TTS Local disponible para: {', '.join(voices_info['available_languages'])}")
                else:
                    st.warning("⚠️ TTS Local disponible pero sin voces compatibles")
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
        """Renderiza sugerencias rápidas para iniciar conversación - U-TUTOR v5.0"""
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


    def render_chat_messages(self, messages: List[dict]):
        """Renderiza los mensajes del chat centrado y limpio - U-TUTOR v5.0"""
        if st.session_state.show_config_page:
            return

        # Aplicar tema antes de mostrar mensajes
        self._apply_theme()

         # Contenedor principal
        chat_container = st.container()

        # 💅 CSS local para centrar el chat
        st.markdown("""
        <style>
        /* Contenedor general del chat */
        .u-tutor-messages {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            position: relative;
            width: 100%;
            max-width: 900px;
            margin: 0 auto;              /* Centra el chat */
            z-index: 1;
        }

        /* Cada mensaje ocupa toda la línea */
        .u-tutor-message {
            width: 100%;
            display: flex;
            justify-content: center;
            margin: 10px 0;
        }

        /* Mensaje del asistente */
.u-tutor-message.assistant > div {
    display: flex;
    align-items: flex-start;
    justify-content: center;
    width: 80%;
    max-width: 700px;
    gap: 4px;
}

/* Bloque de texto del asistente */
.u-tutor-message.assistant > div > div:not(.u-tutor-avatar) {
    text-align: justify;
    margin: 15px 20px;
    font-size: 14px;
    line-height: 1.4;
    color: var(--text-color, #eaeaea);
    background: rgba(255,255,255,0.03);
    padding: 15px;
    border-radius: 10px;
    border-left: 4px solid #a0c4ff;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    flex: 1;
}

        /* Mensaje del usuario */
        .u-tutor-bubble-user {
            background-color: #0078D4;
            color: white;
            padding: 10px 14px;
            border-radius: 16px 16px 4px 16px;
            max-width: 70%;
            text-align: left;
            word-wrap: break-word;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }

        /* Avatar usuario */
        .u-tutor-avatar.user {
            font-size: 20px;
            margin-left: 8px;
        }
                    

        /*  🔹 Responsivo para móviles */
        @media (max-width: 768px) {
            .u-tutor-messages {
                max-width: 95%;
                padding: 10px 0 80px 0;
            }
            .u-tutor-message.assistant div {
                font-size: 13px;
                margin: 10px 12px;
                line-height: 1.4;
            }
            .u-tutor-bubble-user {
                font-size: 13px;
                max-width: 85%;
            }
                    
        }
        </style>
        """, unsafe_allow_html=True)

        # 🧩 Renderizado de los mensajes
        with chat_container:
            st.markdown("<div class='u-tutor-messages'>", unsafe_allow_html=True)

            for idx, message in enumerate(messages):
                role = message.get("role", "user")
                content = message.get("content", "")

                if role == "user":
                    html = f"""
                    <div class='u-tutor-message user' 
                    style='display: flex; justify-content: center; width: 100%;'>
                    <div style='display: flex; align-items: center; gap: 8px; margin: 15px 0;
                            justify-content: flex-end; flex-direction: row; width: 80%; max-width: 700px;'>
                        <div class='u-tutor-bubble-user'>{content}</div>
                        <div class='u-tutor-avatar user'>👤</div>
                    </div>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)
                else:
                    html = f"""
    <div class='u-tutor-message assistant'>
    <div>
        <div class='u-tutor-avatar assistant'>🎓</div>
        <div>{content}</div>
    </div>
</div>
                    """

                    st.markdown(html, unsafe_allow_html=True)
                    self._add_tts_button(content, idx)
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

    
    def _add_tts_button(self, text: str, message_index: int):
        conv_id = st.session_state.get('current_conversation_id', 'new')
        unique_key = f"{conv_id}_{message_index}"

        # Inicializar estado
        if f'audio_playing_{unique_key}' not in st.session_state:
            st.session_state[f'audio_playing_{unique_key}'] = False
        if f'audio_data_{unique_key}' not in st.session_state:
            st.session_state[f'audio_data_{unique_key}'] = None

        # CSS del botón (solo estilo visual)
        

# Contenedor con el id correcto



        # 🔹 Crear layout con columnas dentro del flujo del mensaje
        col_spaceaudio,col_text, col_tts,col_spaceaudio2 = st.columns([1,1,5,1], gap="small")
        with col_text:
            pass  # Aquí no ponemos nada, solo usamos el ancho visual

        with col_tts:
            # Contenedor único del botón
            with st.container():
                
                st.markdown('<div id="tts-button">', unsafe_allow_html=True)
                if st.session_state[f'audio_playing_{unique_key}']:
                    if st.button("⏸️", key=f"pause_{unique_key}", help="Pausar audio"):
                        st.session_state[f'audio_playing_{unique_key}'] = False
                        st.rerun()
                else:
                    if st.button("▶️", key=f"play_{unique_key}", help="Reproducir audio"):
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

        # 🔊 Reproduce el audio si está listo
        if st.session_state[f'audio_data_{unique_key}']:
            st.audio(st.session_state[f'audio_data_{unique_key}'], format='audio/mp3')


    
    def _load_conversation(self, conv_id: int):
        """Carga una conversación específica - U-TUTOR v5.0"""
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
                