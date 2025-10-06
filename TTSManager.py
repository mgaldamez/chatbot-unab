import pyttsx3
import asyncio
import threading
from queue import Queue
import streamlit as st
from typing import Optional
import tempfile
import os
import pygame
from gtts import gTTS
import edge_tts
import io

class TTSManager:
    """Gestor optimizado de Text-to-Speech con múltiples motores y caché"""
    
    def __init__(self, engine_type: str = "pyttsx3"):
        """
        Inicializa el gestor TTS
        
        Args:
            engine_type: Tipo de motor TTS ('pyttsx3', 'gtts', 'edge-tts')
        """
        self.engine_type = engine_type
        self.cache = {}  # Caché en memoria para respuestas comunes
        self.audio_queue = Queue()
        self.is_processing = False
        
        # Inicializar el motor seleccionado
        if engine_type == "pyttsx3":
            self._init_pyttsx3()
        elif engine_type == "edge-tts":
            self._init_edge_tts()
        
        # Inicializar pygame para reproducción de audio
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    
    def _init_pyttsx3(self):
        """Inicializa y optimiza pyttsx3"""
        try:
            self.engine = pyttsx3.init()
            
            # Optimizaciones para velocidad
            self.engine.setProperty('rate', 180)  # Velocidad de habla
            self.engine.setProperty('volume', 0.9)
            
            # Seleccionar voz en español si está disponible
            voices = self.engine.getProperty('voices')
            spanish_voice = None
            
            for voice in voices:
                if 'spanish' in voice.name.lower() or 'es' in voice.id.lower():
                    spanish_voice = voice
                    break
            
            if spanish_voice:
                self.engine.setProperty('voice', spanish_voice.id)
        except Exception as e:
            st.error(f"Error al inicializar pyttsx3: {e}")
            self.engine = None
    
    def _init_edge_tts(self):
        """Inicializa Edge TTS (más rápido y mejor calidad)"""
        # Edge TTS es asíncrono, no requiere inicialización especial
        self.voice = "es-ES-AlvaroNeural"  # Voz masculina española
        # Alternativas: "es-ES-ElviraNeural" (femenina)
    
    async def _generate_edge_tts_async(self, text: str) -> bytes:
        """Genera audio con Edge TTS de forma asíncrona"""
        communicate = edge_tts.Communicate(text, self.voice)
        
        # Generar audio en memoria
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        return audio_data
    
    def text_to_speech_fast(self, text: str, use_cache: bool = True) -> Optional[bytes]:
        """
        Convierte texto a voz de forma optimizada
        
        Args:
            text: Texto a convertir
            use_cache: Si usar caché para textos repetidos
        
        Returns:
            Datos de audio en bytes o None si hay error
        """
        # Verificar caché
        if use_cache and text in self.cache:
            return self.cache[text]
        
        try:
            audio_data = None
            
            if self.engine_type == "pyttsx3" and self.engine:
                # pyttsx3: Rápido pero calidad básica
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                    self.engine.save_to_file(text, tmp_file.name)
                    self.engine.runAndWait()
                    
                    with open(tmp_file.name, 'rb') as f:
                        audio_data = f.read()
                    
                    os.unlink(tmp_file.name)
            
            elif self.engine_type == "gtts":
                # gTTS: Requiere internet pero buena calidad
                tts = gTTS(text=text, lang='es', slow=False)
                
                # Guardar en memoria en lugar de archivo
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                audio_data = fp.read()
            
            elif self.engine_type == "edge-tts":
                # Edge TTS: Mejor balance calidad/velocidad
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                audio_data = loop.run_until_complete(
                    self._generate_edge_tts_async(text)
                )
                loop.close()
            
            # Guardar en caché si es exitoso
            if audio_data and use_cache:
                # Limitar tamaño del caché
                if len(self.cache) > 50:
                    # Eliminar el elemento más antiguo
                    self.cache.pop(next(iter(self.cache)))
                
                self.cache[text] = audio_data
            
            return audio_data
            
        except Exception as e:
            st.error(f"Error en TTS: {e}")
            return None
    
    def process_in_background(self, text: str):
        """Procesa TTS en segundo plano para no bloquear la UI"""
        def _process():
            audio_data = self.text_to_speech_fast(text)
            if audio_data:
                self.audio_queue.put(audio_data)
        
        thread = threading.Thread(target=_process, daemon=True)
        thread.start()
    
    def play_audio(self, audio_data: bytes):
        """Reproduce audio de forma no bloqueante"""
        try:
            # Cargar audio desde bytes
            audio_stream = io.BytesIO(audio_data)
            pygame.mixer.music.load(audio_stream)
            pygame.mixer.music.play()
        except Exception as e:
            st.error(f"Error al reproducir audio: {e}")
    
    def get_optimal_engine(self) -> str:
        """Determina el mejor motor TTS disponible"""
        # Prioridad: edge-tts > pyttsx3 > gtts
        try:
            import edge_tts
            return "edge-tts"
        except ImportError:
            pass
        
        try:
            import pyttsx3
            pyttsx3.init()
            return "pyttsx3"
        except:
            pass
        
        try:
            import gtts
            return "gtts"
        except ImportError:
            pass
        
        return None
    
    def preprocess_text_for_tts(self, text: str) -> str:
        """
        Preprocesa el texto para optimizar TTS
        
        - Elimina markdown
        - Acorta URLs
        - Simplifica caracteres especiales
        """
        import re
        
        # Eliminar markdown
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)  # Italic
        text = re.sub(r'```[^`]*```', '', text)  # Code blocks
        text = re.sub(r'`([^`]+)`', r'\1', text)  # Inline code
        
        # Acortar URLs
        text = re.sub(r'https?://\S+', 'enlace web', text)
        
        # Simplificar listas
        text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)
        
        # Limitar longitud solo para respuestas extremadamente largas (más de 2000 caracteres)
        max_length = 2000
        if len(text) > max_length:
            text = text[:max_length] + "... [audio truncado]"
        
        return text.strip()


class StreamlitTTSIntegration:
    """Integración de TTS con la UI de Streamlit"""
    
    def __init__(self, tts_manager: TTSManager):
        self.tts = tts_manager
    
    def add_tts_button(self, text: str, key: str):
        """
        Añade un botón de TTS a un mensaje
        
        Args:
            text: Texto a convertir
            key: Clave única para el botón
        """
        col1, col2 = st.columns([10, 1])
        
        with col2:
            if st.button("🔊", key=f"tts_{key}", help="Escuchar mensaje"):
                with st.spinner("Generando audio..."):
                    # Preprocesar texto
                    processed_text = self.tts.preprocess_text_for_tts(text)
                    
                    # Generar audio
                    audio_data = self.tts.text_to_speech_fast(processed_text)
                    
                    if audio_data:
                        # Opción 1: Reproducir directamente
                        self.tts.play_audio(audio_data)
                        
                        # Opción 2: Mostrar reproductor de audio en Streamlit
                        st.audio(audio_data, format='audio/mp3')
                    else:
                        st.error("No se pudo generar el audio")
    
    def render_message_with_tts(self, message: dict, index: int):
        """
        Renderiza un mensaje con opción de TTS
        
        Args:
            message: Diccionario con 'role' y 'content'
            index: Índice del mensaje para generar key única
        """
        with st.chat_message(message["role"]):
            # Contenedor para el mensaje y botón TTS
            msg_container = st.container()
            
            with msg_container:
                col1, col2 = st.columns([20, 1])
                
                with col1:
                    st.markdown(message["content"])
                
                with col2:
                    # Solo mostrar TTS para mensajes del asistente
                    if message["role"] == "assistant":
                        if st.button("🔊", key=f"tts_{index}", 
                                   help="Escuchar respuesta"):
                            with st.spinner("🎵"):
                                processed = self.tts.preprocess_text_for_tts(
                                    message["content"]
                                )
                                audio = self.tts.text_to_speech_fast(processed)
                                if audio:
                                    st.audio(audio, format='audio/mp3')


# Ejemplo de integración con tu chat_manager.py
def integrate_tts_with_chat(chat_manager_instance):
    """
    Integra TTS con el ChatManager existente
    
    Modifica tu chat_manager.py para incluir TTS
    """
    # Detectar mejor motor disponible
    tts_manager = TTSManager()
    optimal_engine = tts_manager.get_optimal_engine()
    
    if optimal_engine:
        st.info(f"✅ TTS activado con: {optimal_engine}")
        tts_manager = TTSManager(engine_type=optimal_engine)
        return tts_manager
    else:
        st.warning("⚠️ TTS no disponible. Instala: pip install pyttsx3 edge-tts pygame")
        return None