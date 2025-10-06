# U-TUTOR v3.0 - Nuevo módulo audio_manager.py para funcionalidades de audio
import os
import tempfile
from gtts import gTTS
import speech_recognition as sr
from typing import Optional, Tuple
import streamlit as st

# Importar pyttsx3 para TTS local (más rápido)
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

class AudioManager:
    """Gestor de funcionalidades de audio para U-TUTOR v3.0"""
    
    def __init__(self):
        """Inicializa el gestor de audio"""
        self.recognizer = sr.Recognizer()
        self.temp_dir = tempfile.gettempdir()
        # Cache para evitar regenerar audio del mismo texto
        self.audio_cache = {}
        
        # Inicializar TTS local si está disponible
        self.local_tts = None
        self.available_voices = {}
        if PYTTSX3_AVAILABLE:
            try:
                self.local_tts = pyttsx3.init()
                # Obtener todas las voces disponibles
                voices = self.local_tts.getProperty('voices')
                for voice in voices:
                    voice_name = voice.name.lower()
                    voice_id = voice.id.lower()
                    
                    # Detectar voces en español
                    if any(spanish_word in voice_name or spanish_word in voice_id 
                           for spanish_word in ['spanish', 'español', 'es', 'mexico', 'spain']):
                        self.available_voices['es'] = voice.id
                    
                    # Detectar voces en inglés
                    elif any(english_word in voice_name or english_word in voice_id 
                             for english_word in ['english', 'en', 'us', 'uk', 'american', 'british']):
                        self.available_voices['en'] = voice.id
                
                # Configurar velocidad y volumen
                self.local_tts.setProperty('rate', 180)  # Velocidad de habla
                self.local_tts.setProperty('volume', 0.9)  # Volumen
                
                # Mostrar voces disponibles
                if self.available_voices:
                    st.info(f"🎤 Voces TTS locales disponibles: {list(self.available_voices.keys())}")
                else:
                    st.warning("⚠️ No se encontraron voces TTS locales compatibles")
                    
            except Exception as e:
                st.warning(f"⚠️ TTS local no disponible: {str(e)}")
                self.local_tts = None
    
    def text_to_speech(self, text: str, lang: str = 'es') -> Optional[str]:
        """
        Convierte texto a voz usando TTS local (más rápido) o gTTS como respaldo - U-TUTOR v3.0
        
        Args:
            text: Texto a convertir (texto completo)
            lang: Idioma ('es' para español, 'en' para inglés)
        
        Returns:
            Ruta del archivo de audio generado o None si hay error
        """
        try:
            # Limpiar texto para TTS
            clean_text = text.strip()
            if not clean_text:
                st.warning("⚠️ No hay texto para convertir a audio")
                return None
            
            # Usar texto completo (sin límite artificial)
            st.info("🎵 Generando audio del texto completo...")
            
            # Verificar caché primero
            cache_key = f"{clean_text}_{lang}"
            if cache_key in self.audio_cache:
                cached_file = self.audio_cache[cache_key]
                if os.path.exists(cached_file):
                    st.success("⚡ Usando audio en caché (instantáneo)")
                    return cached_file
                else:
                    del self.audio_cache[cache_key]
            
            # Intentar TTS local primero (más rápido) si hay voz disponible para el idioma
            if self.local_tts and lang in self.available_voices:
                try:
                    import time
                    timestamp = int(time.time() * 1000)
                    audio_file = os.path.join(self.temp_dir, f"ututor_local_{lang}_{timestamp}.wav")
                    
                    # Configurar la voz para el idioma seleccionado
                    self.local_tts.setProperty('voice', self.available_voices[lang])
                    
                    # Generar audio con TTS local
                    self.local_tts.save_to_file(clean_text, audio_file)
                    self.local_tts.runAndWait()
                    
                    if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
                        lang_name = "Español" if lang == 'es' else "Inglés"
                        st.success(f"⚡ Audio generado con TTS local en {lang_name} (súper rápido)")
                        self.audio_cache[cache_key] = audio_file
                        return audio_file
                    else:
                        st.warning("⚠️ TTS local falló, usando gTTS...")
                        
                except Exception as e:
                    st.warning(f"⚠️ TTS local falló: {str(e)}, usando gTTS...")
            
            # Usar gTTS como respaldo
            lang_name = "Español" if lang == 'es' else "Inglés"
            st.info(f"🌐 Generando con gTTS en {lang_name} (requiere internet)...")
            tts = gTTS(text=clean_text, lang=lang, slow=False, tld='com')
            
            import time
            timestamp = int(time.time() * 1000)
            audio_file = os.path.join(self.temp_dir, f"ututor_gtts_{lang}_{timestamp}.mp3")
            
            tts.save(audio_file)
            
            if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
                st.success(f"✅ Audio generado con gTTS en {lang_name}")
                self.audio_cache[cache_key] = audio_file
                return audio_file
            else:
                st.error("❌ No se pudo generar el archivo de audio")
                return None
        
        except Exception as e:
            st.error(f"❌ Error al generar audio: {str(e)}")
            return None
    
    def speech_to_text(self, audio_data) -> Tuple[bool, str]:
        """
        Convierte voz a texto usando el micrófono - U-TUTOR v3.0
        
        Returns:
            Tupla (éxito, texto/mensaje_error)
        """
        try:
            # Reconocer audio
            text = self.recognizer.recognize_google(audio_data, language='es-ES')
            return True, text
        
        except sr.UnknownValueError:
            return False, "No se pudo entender el audio"
        
        except sr.RequestError as e:
            return False, f"Error en el servicio de reconocimiento: {str(e)}"
        
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def record_audio(self, duration: int = 5) -> Optional[sr.AudioData]:
        """
        Graba audio del micrófono - U-TUTOR v3.0
        
        Args:
            duration: Duración máxima de grabación en segundos
        
        Returns:
            Datos de audio o None si hay error
        """
        try:
            # Verificar disponibilidad del micrófono
            try:
                with sr.Microphone() as source:
                    pass
            except Exception as mic_error:
                st.error(f"❌ Error con el micrófono: {str(mic_error)}")
                return None
            
            with sr.Microphone() as source:
                # Ajustar para ruido ambiente (más rápido)
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                # Grabar audio con configuración mejorada
                audio_data = self.recognizer.listen(
                    source, 
                    timeout=duration, 
                    phrase_time_limit=duration
                )
                
                return audio_data
        
        except sr.WaitTimeoutError:
            st.warning("⏰ Tiempo de grabación agotado. Intenta hablar más rápido.")
            return None
        
        except sr.UnknownValueError:
            st.warning("🎤 No se detectó audio. Asegúrate de hablar cerca del micrófono.")
            return None
        
        except Exception as e:
            st.error(f"❌ Error al grabar audio: {str(e)}")
            st.warning("💡 Verifica que tu micrófono esté funcionando y que hayas permitido el acceso.")
            return None
    
    def cleanup_audio_files(self):
        """Limpia archivos de audio temporales - U-TUTOR v3.0"""
        try:
            for file in os.listdir(self.temp_dir):
                if file.startswith("ututor_") and (file.endswith(".mp3") or file.endswith(".wav")):
                    os.remove(os.path.join(self.temp_dir, file))
        except Exception as e:
            pass  # Silenciar errores de limpieza
    
    def clear_audio_cache(self):
        """Limpia el caché de audio para liberar memoria - U-TUTOR v3.0"""
        self.audio_cache.clear()
        st.info("🧹 Caché de audio limpiado")
    
    def get_cache_size(self):
        """Retorna el tamaño del caché de audio - U-TUTOR v3.0"""
        return len(self.audio_cache)
    
    def get_available_voices_info(self):
        """Retorna información sobre las voces TTS disponibles - U-TUTOR v3.0"""
        return {
            'local_tts_available': self.local_tts is not None,
            'available_languages': list(self.available_voices.keys()),
            'voices_count': len(self.available_voices)
        }
